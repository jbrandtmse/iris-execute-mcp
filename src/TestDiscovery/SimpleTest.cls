/// Simple test class to debug discovery issues
Class TestDiscovery.SimpleTest Extends %UnitTest.TestCase
{

/// Test method 1
Method TestAddition() As %Status
{
    Set tSC = $$$OK
    Do $$$AssertEquals(2 + 2, 4, "Basic addition test")
    Quit tSC
}

/// Test method 2  
Method TestSubtraction() As %Status
{
    Set tSC = $$$OK
    Do $$$AssertEquals(5 - 3, 2, "Basic subtraction test")
    Quit tSC
}

/// Test method 3
Method TestMultiplication() As %Status
{
    Set tSC = $$$OK
    Do $$$AssertEquals(3 * 4, 12, "Basic multiplication test")
    Quit tSC
}

}
