Class ExecuteMCP.Test.SampleUnitTest Extends %UnitTest.TestCase
{

/// Test that always passes
Method TestAlwaysPass()
{
    Do $$$AssertTrue(1=1, "This test should always pass")
    Do $$$AssertEquals("hello", "hello", "String equality test")
}

/// Test that always fails
Method TestAlwaysFail()
{
    Do $$$AssertTrue(1=2, "This test should always fail")
    Do $$$AssertEquals("hello", "world", "This string comparison should fail")
}

/// Test with some calculations
Method TestCalculations()
{
    Set result = 2 + 2
    Do $$$AssertEquals(4, result, "Basic arithmetic should work")
    
    Set result = 10 / 2
    Do $$$AssertEquals(5, result, "Division should work")
}

}
