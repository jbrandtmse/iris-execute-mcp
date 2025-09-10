/// ExecuteMCP.Test.SimpleTest
/// Simple test class that extends ExecuteMCP.TestRunner.TestCase for TestRunner compatibility
Class ExecuteMCP.Test.SimpleTest Extends ExecuteMCP.TestRunner.TestCase
{

/// Test that always passes
Method TestAlwaysPass() As %Status
{
    Do $$$AssertEquals(1, 1, "One equals one")
    Quit $$$OK
}

/// Test that always fails  
Method TestAlwaysFail() As %Status
{
    Do $$$AssertEquals(1, 2, "One should not equal two")
    Quit $$$OK
}

/// Test with calculations
Method TestCalculations() As %Status
{
    Set result = 2 + 2
    Do $$$AssertEquals(result, 4, "2 + 2 = 4")
    
    Set result = 10 / 2
    Do $$$AssertEquals(result, 5, "10 / 2 = 5")
    
    Quit $$$OK
}

/// Test with string operations
Method TestStringOperations() As %Status
{
    Set str1 = "Hello"
    Set str2 = "World"
    Set combined = str1_" "_str2
    
    Do $$$AssertEquals(combined, "Hello World", "String concatenation")
    
    Quit $$$OK
}

}
