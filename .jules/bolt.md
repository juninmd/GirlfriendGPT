## 2026-02-18 - Optimized SelfieTool Client Reuse

**Learning:** Initializing `google.genai.Client` is not free. Reusing the client instance across tool executions (lazy loading) significantly reduces object churn and potentially connection overhead. Also, using `client.aio` enables true async execution for IO-bound operations in LangChain tools, preventing the event loop from blocking.

**Action:** When implementing LangChain tools that wrap external API clients, always cache the client instance (lazy load) instead of creating it in `_run`. Also ensure `_arun` uses the async version of the client methods (`aio`) if available.
