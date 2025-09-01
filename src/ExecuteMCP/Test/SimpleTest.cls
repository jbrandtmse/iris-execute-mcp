/// ExecuteMCP.Test.SimpleTest
/// Simple test class that works with async execution without %UnitTest.TestCase dependencies
Class ExecuteMCP.Test.SimpleTest Extends %RegisteredObject
{

/// Test that always passes
Method TestAlwaysPass() As %Boolean
{
    Return (1=1)
}

/// Test that always fails  
Method TestAlwaysFail() As %Boolean
{
    Return (1=2)
}

/// Test with calculations
Method TestCalculations() As %Boolean
{
    Set result = 2 + 2
    If result '= 4 Return 0
    
    Set result = 10 / 2
    If result '= 5 Return 0
    
    Return 1
}

/// Test with string operations
Method TestStringOperations() As %Boolean
{
    Set str1 = "Hello"
    Set str2 = "World"
    Set combined = str1_" "_str2
    
    Return (combined = "Hello World")
}

}
