```markdown
# AGENTS.md - Guidelines for AI Coding Agents

These guidelines outline the approach to developing AI coding agents. Compliance with these principles ensures code maintainability, reliability, and efficiency.

**1. DRY (Don't Repeat Yourself)**

*   All logic, data handling, and utility functions should be encapsulated within reusable components.
*   Avoid duplicating code. When a component needs to be modified, the relevant functionality should be updated in the component itself, rather than being duplicated.
*   Favor composition over inheritance where possible.

**2. KISS (Keep It Simple, Stupid)**

*   Prioritize clarity and readability above all else.
*   Keep functions and classes as short and focused as possible.
*   Minimize complexity.  Each element should have a single, well-defined purpose.
*   Avoid overly clever or convoluted solutions.  Simplicity is key.

**3. SOLID Principles**

*   **Single Responsibility Principle:** Each class or function should have a single, well-defined purpose.
*   **Open/Closed Principle:** The system should be extensible through well-defined interfaces, without modifying the existing implementation.
*   **Liskov Substitution Principle:**  Subclasses should be substitutable for their base classes without affecting the correctness of the program.
*   **Interface Segregation Principle:** Client code should not be forced to depend on methods it does not use.
*   **Dependency Inversion Principle:** Higher-level modules should not depend on lower-level modules.  Interfaces should define contracts.

**4. YAGNI (You Aren't Gonna Need It)**

*   Implement only what is absolutely necessary to fulfill the current requirements.
*   Avoid adding features or functionality that are not currently required.
*   Refactor only when there is a demonstrable need for increased complexity or clarity.

**5. Code Structure & Best Practices**

*   **Modular Design:**  Break down the agent into logical modules or components.
*   **Parameterization:**  Use parameters to make the agent configurable and reusable.
*   **Error Handling:** Implement robust error handling, providing informative error messages and logging.
*   **Data Structures:** Choose appropriate data structures for efficient data storage and retrieval.
*   **Logging:**  Use logging extensively to track agent behavior, errors, and important events.
*   **Configuration:**  Store configuration parameters outside of the core agent logic for easy modification.
*   **Versioning:**  Employ a version control system (e.g., Git) for tracking code changes and allowing for rollback.
*   **Documentation:**  Include clear and concise documentation for each function and class.
*   **Testing:** Implement comprehensive unit and integration tests.

**6.  Testing & Coverage**

*   **Test-Driven Development (TDD):**  Write tests *before* writing code.
*   **Unit Tests:**  Create unit tests for each component or function.
*   **Integration Tests:**  Test the interaction between components.
*   **Coverage Report:**  Use a coverage tool (e.g., Coverage.py) to measure code coverage and identify areas for improvement.  Aim for 80% or higher coverage across unit and integration tests.
*   **Automated Tests:**  Implement automated testing as part of the development pipeline.

**7. File Size Limit**

*   Maximum file size: 180 lines of code.

**8.  Specific Considerations**

*   **Data Persistence:**  Design data storage mechanisms (e.g., databases, files) in a way that is consistent and secure.
*   **Agent State Management:** Employ a robust state management system to track the agent's current state and dependencies.
*   **Algorithm Design:**  When designing algorithms, prioritize readability and modularity.

**9.  Development Workflow**

*   **Small, Incremental Changes:**  Make small, focused changes to the code.
*   **Frequent Commits:**  Commit changes frequently to a shared repository.
*   **Code Reviews:**  Conduct code reviews to identify potential issues.

**10.  Tools & Technologies**

*   [Specify preferred tools/frameworks here - e.g., Python, PyTorch, TensorFlow]

These guidelines are intended as a starting point.  Ongoing refinement and adaptation may be necessary as the agent development progresses.  Any changes to these guidelines should be discussed and agreed upon by all team members.
```