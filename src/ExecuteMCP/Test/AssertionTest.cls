Class ExecuteMCP.Test.AssertionTest Extends %UnitTest.TestCase
{

/// Test various assertion macros
Method TestAssertions() As %Status
{
    Do $$$AssertEquals(1, 1, "One equals one")
    Do $$$AssertTrue(1, "True assertion")
    Do $$$AssertNotEquals(1, 2, "One does not equal two")
    Do $$$AssertStatusOK($$$OK, "Status is OK")
    
    // Test a failing assertion
    Do $$$AssertEquals(1, 2, "This should fail")
    
    Quit $$$OK
}

}
