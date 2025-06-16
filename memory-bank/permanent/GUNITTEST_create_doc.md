# %UnitTest Framework Setup Documentation

This document is sourced from the Intersystems documentation at:

https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=GUNITTEST_create

---

## Contents

* [Extend TestCase](#GUNITTEST_testcase)
* [%UnitTest Macros](#GUNITTEST_macros)
* [Prep & Cleanup](#GUNITTEST_prepcleanup)

---

## General Workflow for Setting Up Unit Tests

This is the general workflow to set up unit tests using the %UnitTest framework:

1. **Extend the %UnitTest.TestCase Class:**  
   Extend the [%UnitTest.TestCase](../documatic/%25CSP.Documatic.cls?LIBRARY=%25SYS&CLASSNAME=%25UnitTest.TestCase) class, adding one test method for each method to be tested. Test method names must begin with the word **Test**.  
   See [Extending the %UnitTest.TestCase Class](about:blank/DocBook.UI.Page.cls?KEY=GUNITTEST_create#GUNITTEST_testcase) for guidance.

2. **Multiple Tests in a Single Method:**  
   A single test method can contain multiple tests. Typically, a test method will include one test for each aspect of the method to be tested. Within each test method, devise one or more tests using the $$$AssertX macros. The macro will call the method being tested and compare its output to some expected value.  
   Refer to [Macros of the %UnitTest.TestCase Class](about:blank/DocBook.UI.Page.cls?KEY=GUNITTEST_create#GUNITTEST_macros) for details.

3. **Preparation and Cleanup Methods:**  
   Add code to the preparation and cleanup methods to perform necessary tasks. For example, if a test seeks to delete an element from a list, that list must first exist and contain the element to be deleted.  
   See [%UnitTest.TestCase Class Preparation and Cleanup Methods](about:blank/DocBook.UI.Page.cls?KEY=GUNITTEST_create#GUNITTEST_prepcleanup).

   **Note:**  
   Preparation methods and cleanup methods are also often called setup methods and teardown methods.

---

## Extending the %UnitTest.TestCase Class

Create a class that extends [%UnitTest.TestCase](../documatic/%25CSP.Documatic.cls?LIBRARY=%25SYS&CLASSNAME=%25UnitTest.TestCase) to contain the test methods that execute your unit tests. This process is designed to be flexible to accommodate your particular testing needs.

- **Test Methods:**  
  Most likely, you will add test methods and possibly properties as well. Test methods will be executed by the RunTest() method from the [%UnitTest.Manager](../documatic/%25CSP.Documatic.cls?LIBRARY=%25SYS&CLASSNAME=%25UnitTest.Manager) class, which looks for and executes methods whose names begin with ‘Test’.  
  You can add other helper methods to your class, but only methods that begin with ‘Test’ will be run as unit tests.

- **Execution Order:**  
  Test methods are executed in alphabetical order. For example, `TestAssess()` would be executed before `TestCreate()`.

- **Using $$$AssertX Macros:**  
  Within a test method, create one or more tests using a $$$AssertX macro for each testable aspect.  
  See [Macros of the %UnitTest.TestCase Class](about:blank/DocBook.UI.Page.cls?KEY=GUNITTEST_create#GUNITTEST_macros) for detailed instructions on the available macros.

- **Granular Testing:**  
  You may create a test method for each class method you wish to test. For example, if your class `MyPackage.MyClassToBeTested` contains a method `Add()`, which requires multiple tests, you might create a test method `MyTests.TestAdd()` to encompass these tests.

- **Testing Object Instances:**  
  Alternatively, you might create a method like `MyTests.TestMyObject()` to test the properties and functionality of object instances.

- **Properties in Extended Classes:**  
  If your test requires sharing information between methods, declare custom properties in the class itself.  
  - Set these properties by adding code to the preparation methods `OnBeforeOneTest()` and `OnBeforeAllTests()` using the `..<property>` syntax.
  - Access these properties in your test and cleanup methods similarly.

  **Example:**  
  If your custom property is called `PropertyValue`, it is accessed via `..PropertyValue`.

---

## Example: Extended %UnitTest.TestCase Class

```objectscript
Class MyPackage.MyClassToBeTested
{
  Method Add(Addend1 as %Integer, Addend2 as %Integer) As %Integer
  {
    Set Sum = Addend1 + Addend2
    Return Sum
  }
}

Class MyPackage.MyTests Extends %UnitTest.TestCase
{
  Method TestAdd()
  {
    do $$$AssertEquals(##class(MyPackage.MyClassToBeTested).Add(2,3),5, "Test 2+3=5")
    do $$$AssertNotEquals(##class(MyPackage.MyClassToBeTested).Add(3,4),5, "Test 3+4 '^= 5")
  }
}
```

---

## Macros of the %UnitTest.TestCase Class

Within each of your test methods, use one of the following $$$AssertX macros to test each aspect of the method under test:

- **$$$AssertEquals(arg1, arg2, test_description):**  
  Returns true if `arg1` and `arg2` are equal.
  
  ```objectscript
  do $$$AssertEquals(##class(MyPackage.MyClassToBeTested).Add(2,3), 5, "Test Add(2,3) = 5")
  ```

- **$$$AssertNotEquals(arg1, arg2, test_description):**  
  Returns true if `arg1` and `arg2` are not equal.
  
  ```objectscript
  do $$$AssertNotEquals(##class(MyPackage.MyClassToBeTested).Add(3,4), 5, "Test Add(3,4) '^= 5")
  ```

- **$$$AssertStatusOK(arg1, test_description):**  
  Returns true if the returned status code is 1.

- **$$$AssertStatusNotOK(arg1, test_description):**  
  Returns true if the returned status code is not 1.

- **$$$AssertTrue(arg1, test_description):**  
  Returns true if the expression is true.

- **$$$AssertNotTrue(arg1, test_description):**  
  Returns true if the expression is not true.

- **$$$AssertFilesSame(arg1, arg2, test_description):**  
  Returns true if two files are identical.

- **$$$AssertFilesSQLUnorderedSame(arg1, arg2, test_description):**  
  Returns true if two files containing SQL query results contain the same unordered results.

- **$$$AssertSuccess(test_description):**  
  Unconditionally logs success.

- **$$$AssertFailure(test_description):**  
  Unconditionally logs failure.

- **$$$AssertSkipped(test_description):**  
  Logs that a test was skipped, usually due to unmet preconditions.

- **$$$LogMessage(message):**  
  Writes a log entry independent of any particular test.
  
  ```objectscript
  do $$$LogMessage("-- ALL TEST OBJECTS CREATED --")
  ```

---

## %UnitTest.TestCase Class Preparation and Cleanup Methods

- **OnBeforeOneTest():** Executes immediately before each test method in the test class.
- **OnBeforeAllTests():** Executes once before any test methods in the class.
- **OnAfterOneTest():** Executes immediately after each test method.
- **OnAfterAllTests():** Executes once after all test methods have finished.

### Example: Preparation Method

```objectscript
Method OnBeforeAllTests()
{
  Do ##class(MyPackage.Contact).Populate(1)
  Return $$$OK
}
```

### Example: Cleanup Method

```objectscript
Method OnAfterAllTests()
{
  Do ##class(MyPackage.Contact).%KillExtent()
  Return $$$OK
}
```

---

*This documentation outlines the workflow, extension process, macros, and lifecycle management necessary to set up unit tests using the %UnitTest framework. It serves as a guide for developers to create and manage unit tests effectively.*
