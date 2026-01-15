import json
from typing import List, Optional

import google.generativeai as genai
from steamship import Block, Tag
from steamship.agents.schema import ChatLLM, Tool
from steamship.data.tags.tag_constants import RoleTag, TagKind

class GeminiLLM(ChatLLM):
    """LLM implementation that uses Google Gemini."""

    api_key: str
    model_name: str = "gemini-1.5-flash"

    def __init__(self, client, api_key: str, model_name: str = "gemini-1.5-flash", **kwargs):
        super().__init__(client=client, **kwargs)
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=self.api_key)

    def chat(
        self, messages: List[Block], tools: Optional[List[Tool]], **kwargs
    ) -> List[Block]:

        # 1. Convert tools to Gemini tools
        gemini_tools = None
        if tools:
            gemini_tools = self._convert_tools(tools)

        # 2. Convert messages to Gemini history
        # We need to extract the last message as the new input prompt?
        # No, generate_content can take a list of contents.
        # But we need to separate system instruction if we want to use it properly,
        # or just prepend it.

        system_instruction = self._extract_system_prompt(messages)
        contents = self._convert_history(messages)

        # 3. Call Gemini
        # We use GenerativeModel directly.
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction
        )

        # If we have function calling, we pass tools.
        # Note: If tools is empty list, pass None.
        tool_config = None
        if gemini_tools:
            # gemini_tools is a list of FunctionDeclaration compatible dicts?
            # Or we wrap it in 'tools' kwarg.
            pass

        try:
            response = model.generate_content(
                contents=contents,
                tools=gemini_tools if gemini_tools else None,
                tool_config={'function_calling_config': {'mode': 'AUTO'}} if gemini_tools else None
            )
        except Exception as e:
            # Handle potential errors (e.g., safety, or invalid history)
            # Just return error block or try to recover
            return [Block(text=f"Error calling Gemini: {e}")]

        # 4. Parse response
        return self._convert_response(response)

    def _convert_tools(self, tools: List[Tool]):
        # Gemini expects a list of function declarations.
        # Steamship Tool has name, human_description.
        # We assume they take a single argument 'text' or 'uuid'.
        funcs = []
        for tool in tools:
            funcs.append({
                "name": tool.name,
                "description": tool.human_description,
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "text": {
                            "type": "STRING",
                            "description": "The input text for the tool."
                        },
                        "uuid": {
                            "type": "STRING",
                            "description": "The UUID argument for the tool."
                        }
                    },
                    "required": ["text"]
                }
            })
        return funcs

    def _extract_system_prompt(self, messages: List[Block]) -> Optional[str]:
        for msg in messages:
            if msg.chat_role == RoleTag.SYSTEM:
                return msg.text
        return None

    def _convert_history(self, messages: List[Block]):
        contents = []
        for msg in messages:
            role = msg.chat_role
            if role == RoleTag.SYSTEM:
                continue # handled separately

            if role == RoleTag.USER:
                contents.append({"role": "user", "parts": [msg.text]})

            elif role == RoleTag.ASSISTANT:
                # Check if it was a function call
                is_func_call = False
                for tag in msg.tags:
                    if tag.kind == TagKind.FUNCTION_SELECTION:
                        is_func_call = True
                        try:
                            # Msg text is JSON: {"name": "...", "arguments": "..."}
                            # Gemini needs FunctionCall part
                            data = json.loads(msg.text)
                            fc_name = data.get("name")
                            # Steamship/OpenAI arguments is a stringified JSON
                            fc_args_str = data.get("arguments", "{}")
                            fc_args = json.loads(fc_args_str)

                            part = {
                                "function_call": {
                                    "name": fc_name,
                                    "args": fc_args
                                }
                            }
                            contents.append({"role": "model", "parts": [part]})
                        except:
                             # If parsing fails, just send text
                             contents.append({"role": "model", "parts": [msg.text]})
                        break

                if not is_func_call:
                    contents.append({"role": "model", "parts": [msg.text]})

            elif role == RoleTag.FUNCTION:
                # Function result
                # We need the name of the function.
                func_name = "unknown"
                # Steamship FunctionsBasedAgent stores name in a tag
                for tag in msg.tags:
                    if tag.name and tag.kind == "name":
                         func_name = tag.name
                         break
                    if tag.kind == RoleTag.FUNCTION and tag.value:
                         func_name = tag.value.get(TagKind.STRING_VALUE, "unknown")

                part = {
                    "function_response": {
                        "name": func_name,
                        "response": {"result": msg.text}
                    }
                }
                # Gemini often expects this in a 'function' role or 'user' role.
                # 'function' role is supported in API.
                contents.append({"role": "function", "parts": [part]})

        return contents

    def _convert_response(self, response) -> List[Block]:
        try:
            # Gemini response might have parts.
            # We check for function call first.
            if not response.parts:
                return [Block(text="")]

            part = response.parts[0]

            if fn := part.function_call:
                # Convert to OpenAI/Steamship format
                # {"function_call": {"name": "...", "arguments": "..."}}
                args_dict = dict(fn.args)
                args_str = json.dumps(args_dict)

                fc_payload = {
                    "function_call": {
                        "name": fn.name,
                        "arguments": args_str
                    }
                }
                # IMPORTANT: We must NOT add the TagKind.FUNCTION_SELECTION here directly because
                # FunctionsBasedAgent's output parser looks for the text pattern.
                # HOWEVER, Steamship's ecosystem might expect role tags.
                # ChatOpenAI returns blocks with RoleTag.ASSISTANT.

                block = Block(text=json.dumps(fc_payload))
                block.set_chat_role(RoleTag.ASSISTANT)
                return [block]
            else:
                block = Block(text=part.text)
                block.set_chat_role(RoleTag.ASSISTANT)
                return [block]

        except Exception as e:
            return [Block(text=f"Error parsing Gemini response: {e}")]
