# Unit Testing Feature - Design and Implementation Plan

## 1. Overview

This document outlines the design and implementation plan for adding unit testing capabilities to the `iris-execute-mcp` server. The goal is to provide a set of tools that allow an AI agent to discover, execute, and review the results of InterSystems IRIS unit tests programmatically.

The implementation will leverage the existing, standard `%UnitTest.Manager` framework provided by InterSystems IRIS.

## 2. Architecture

The feature will be built following the existing architectural pattern of the `iris-execute-mcp` server: a Python MCP server that communicates with a dedicated IRIS backend class via the Native API.

### 2.1. IRIS Backend Class: `ExecuteMCP.Core.UnitTest`

A new ObjectScript class will be created at `src/ExecuteMCP/Core/UnitTest.cls`. This class will encapsulate all logic related to unit testing.

**Key Responsibilities:**

*   Provide a clean API for the MCP server to call.
*   Interact with `%UnitTest.Manager`.
*   Manage the `^UnitTestRoot` global setting.
*   Query and parse the `^UnitTest.Result` global for test outcomes.
*   Format results into structured JSON for the client.

**Methods:**

*   **`ListTests(pTestRoot As %String) As %DynamicObject`**:
    *   **Description**: Discovers all test suites, classes, and methods.
    *   **Logic**:
        1.  Sets `^UnitTestRoot = pTestRoot`.
        2.  Uses `%UnitTest.Manager.GetSubDirectories()` logic to find all test directories (suites).
        3.  For each suite, finds all classes that extend `%UnitTest.TestCase`.
        4.  For each class, uses `%UnitTest.Manager.getTestMethods()` to get all methods starting with "Test".
        5.  Constructs and returns a JSON object representing the test hierarchy.
*   **`RunTests(pTestSpec As %String, pQualifiers As %String, pTestRoot As %String) As %DynamicObject`**:
    *   **Description**: Executes a set of unit tests.
    *   **Logic**:
        1.  Sets `^UnitTestRoot = pTestRoot`.
        2.  Calls `##class(%UnitTest.Manager).RunTest(pTestSpec, pQualifiers, .userparam)`.
        3.  The `%UnitTest.Manager` instance will have a `ResultId` property after the run.
        4.  Returns a JSON object containing the `ResultId` and a confirmation message.
*   **`GetTestResult(pResultId As %Integer) As %DynamicObject`**:
    *   **Description**: Retrieves and formats the results of a specific test run.
    *   **Logic**:
        1.  Traverses the `^UnitTest.Result(pResultId, ...)` global.
        2.  Parses the `$LISTBUILD` data at each level (suite, class, method, assertion).
        3.  Identifies failures by checking status flags and failure/error counts.
        4.  Constructs a detailed JSON report, including failed assertions and error messages.

### 2.2. Python MCP Server: `iris_execute_fastmcp.py`

The existing MCP server will be extended to include three new tool definitions. These tools will call the corresponding methods in the `ExecuteMCP.Core.UnitTest` backend class.

**New Tools:**

*   **`list_unit_tests(test_root_path: str)`**:
    *   **Description**: Lists all available unit tests found at the specified root path.
    *   **Backend Call**: `ExecuteMCP.Core.UnitTest.ListTests`
*   **`run_unit_tests(test_spec: str, qualifiers: str, test_root_path: str)`**:
    *   **Description**: Runs unit tests.
    *   `test_spec`: A string defining what to run (e.g., "MySuite:MyClass:MyMethod").
    *   `qualifiers`: A string for flags (e.g., "/recursive/nodelete").
    *   **Backend Call**: `ExecuteMCP.Core.UnitTest.RunTests`
*   **`get_unit_test_results(result_id: int)`**:
    *   **Description**: Fetches the results for a given test run ID.
    *   **Backend Call**: `ExecuteMCP.Core.UnitTest.GetTestResult`

## 3. Implementation Steps

1.  **Create `src/ExecuteMCP/Core/UnitTest.cls`**: Implement the `ListTests`, `RunTests`, and `GetTestResult` methods as designed above.
2.  **Update `iris_execute_fastmcp.py`**:
    *   Add the three new tool definitions (`list_unit_tests`, `run_unit_tests`, `get_unit_test_results`).
    *   Implement the logic within each tool to call the corresponding `ExecuteMCP.Core.UnitTest` method using the `iris-execute-mcp`'s `execute_classmethod` tool.
3.  **Update `activeContext.md` and `progress.md`**: Reflect the new feature development in the memory bank.
4.  **Testing**: Create a sample unit test class to use for validating the new tools end-to-end.
