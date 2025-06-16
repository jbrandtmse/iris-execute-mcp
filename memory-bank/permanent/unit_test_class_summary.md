# Unit Test Class Summary for IRIS ObjectScript

This document summarizes the macros available from the %outUnitTest.inc include file and provides guidelines for their usage when writing IRIS ObjectScript unit tests. All test classes should extend %UnitTest.TestCase, which already includes the necessary unit testing macros.

## Available Macros and Their Usage

- **AssertEquals(%args)**  
  Compares two values for equality. It is implemented via the macro call to ..AssertEqualsViaMacro.  
  **Usage Example:**  
  `Do $$$AssertEquals(expectedValue, actualValue, "Values did not match")`

- **AssertNotEquals(%args)**  
  Checks that two values are not equal.  
  **Usage Example:**  
  `Do $$$AssertNotEquals(unexpectedValue, actualValue, "Values should not match")`

- **AssertTrue(%args)**  
  Evaluates an expression; returns true if the expression is true.  
  **Usage Example:**  
  `Do $$$AssertTrue($Find(result, "expected substring")>0, "The expected substring was not found")`

- **AssertNotTrue(%args)**  
  Returns true if the expression evaluates to false.  
  **Usage Example:**  
  `Do $$$AssertNotTrue(expression, "Expression should not be true")`

- **AssertStatusOK(%args)**  
  Verifies that a status value indicates success (typically $$$OK).  
  **Usage Example:**  
  `Do $$$AssertStatusOK(tStatus, "Method did not return $$$OK")`

- **AssertStatusNotOK(%args)**  
  Verifies that a status value indicates an error.  
  **Usage Example:**  
  `Do $$$AssertStatusNotOK(tStatus, "Method unexpectedly returned $$$OK")`

- **AssertStatusEquals(%args)**  
  Compares a returned status with an expected status.  
  **Usage Example:**  
  `Do $$$AssertStatusEquals(expectedStatus, tStatus, "Status does not match the expected value")`

- **AssertFilesSame(%args)**  
  Compares the contents of two files to ensure they are identical. Useful when testing file outputs.  
  **Usage Example:**  
  `Do $$$AssertFilesSame(file1, file2, "Generated file does not match expected content")`

- **AssertFilesSQLUnorderedSame(%args)**  
  Compares SQL output files where the order of rows is not significant.  
  **Usage Example:**  
  `Do $$$AssertFilesSQLUnorderedSame(file1, file2, "SQL files differ in content")`

- **LogMessage(%message)**  
  Logs a message during test execution. This is helpful for debugging or providing context in test reports.  
  **Usage Example:**  
  `Do $$$LogMessage("Starting test for method X")`

- **AssertSuccess(%message)**  
  Indicates that a test has succeeded, typically used within complex test flows.  
  **Usage Example:**  
  `Do $$$AssertSuccess("Test executed successfully")`

- **AssertFailure(%message)**  
  Marks a test as failed with a provided message.  
  **Usage Example:**  
  `Do $$$AssertFailure("Test failed due to unexpected error")`

- **AssertSkipped(%message)**  
  Used to denote that a test was skipped.  
  **Usage Example:**  
  `Do $$$AssertSkipped("Test skipped because prerequisites were not met")`

## Guidelines for Use in Unit Tests

- **Test Class Inheritance:**  
  Always create test classes by extending `%UnitTest.TestCase`. This class already includes the macros defined in `%outUnitTest.inc`, so you do not need to include them manually.

- **Test Method Structure:**  
  Each test should be defined as a method that returns a `%Status`. Use descriptive method names that typically begin with "Test" (e.g., TestDefault, TestCustom). Make sure each test method is well-documented with comments explaining its purpose.

- **Local Variable Declaration:**  
  Follow established naming conventions: use a "t" prefix for temporary variables (e.g., tResult, tInput). Avoid unnecessary use of the `New` keyword if the project conventions advise an alternative approach.

- **Assertion Macro Syntax:**  
  Every assertion macro call must be preceded by a `Do` command. For example:  
  `Do $$$AssertTrue(expression, "Description if the expression is false")`  
  This ensures proper execution and error reporting.

- **Descriptive Failure Messages:**  
  Always include clear, descriptive messages in your assertions to aid in diagnosing issues when a test fails.

- **Running Tests:**  
  Execute your unit tests using the %UnitTest.Manager (e.g., `Do ##class(%UnitTest.Manager).Run()`) to ensure that all tests are processed correctly.

## Additional Best Practices and Tips

- **Consistency Across Projects:**  
  Apply these guidelines uniformly in all IRIS ObjectScript projects to maintain reliable and maintainable unit tests.

- **Documentation and Maintenance:**  
  Keep unit test classes and methods well-documented. Regularly update this document whenever there are changes to the unit testing framework conventions or when new macros are introduced in `%outUnitTest.inc`.

- **Avoiding Common Pitfalls:**  
  Ensure that every assertion macro is used with the proper syntax (i.e., always use a `Do` command in front of the macro). Follow naming conventions strictly to avoid compile errors.

- **Test Execution Reporting:**  
  Utilize logging macros, such as $$$LogMessage, to provide detailed output during test runs, which is valuable for understanding test flows and outcomes.

- **Error Handling:**  
  In test methods, structure your code so that any unexpected errors result in clear, actionable failure messages. This practice makes debugging test failures more efficient.

- **Regular Review:**  
  Periodically review and update unit tests and this summary to reflect improvements in testing practices and updates to the IRIS unit testing framework.

- **Additional Recommendations:**  
  - **Short and Focused Tests:** Write each test to validate a specific behavior. This granularity helps isolate issues and simplifies maintenance.  
  - **Integration with CI/CD:** Consider integrating unit tests into your continuous integration process to ensure that tests run automatically with every code change.  
  - **Refactoring:** Regularly refactor tests to eliminate redundancy and improve clarity. Ensure tests remain aligned with the behavior of the code under test.
  
By adhering to these guidelines and using the macros as described, you will create robust, readable, and maintainable unit tests in InterSystems IRIS ObjectScript.
