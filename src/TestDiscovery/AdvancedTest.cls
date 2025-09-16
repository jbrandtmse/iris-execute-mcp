/// Another test class to debug discovery issues
Class TestDiscovery.AdvancedTest Extends %UnitTest.TestCase
{

/// Test string operations
Method TestStringConcat() As %Status
{
    Set tSC = $$$OK
    Do $$$AssertEquals("Hello" _ " " _ "World", "Hello World", "String concatenation test")
    Quit tSC
}

/// Test boolean logic
Method TestBooleanLogic() As %Status
{
    Set tSC = $$$OK
    Do $$$AssertTrue(1 && 1, "AND operation test")
    Do $$$AssertNotTrue(0 || 0, "OR operation test")
    Quit tSC
}

/// Test list operations
Method TestListOperations() As %Status
{
    Set tSC = $$$OK
    Set tList = $LISTBUILD("A", "B", "C")
    Do $$$AssertEquals($LISTLENGTH(tList), 3, "List length test")
    Do $$$AssertEquals($LISTGET(tList, 2), "B", "List get test")
    Quit tSC
}

/// Test date operations
Method TestDateOperations() As %Status
{
    Set tSC = $$$OK
    Set tToday = +$HOROLOG
    Do $$$AssertTrue(tToday > 0, "Date is positive number")
    Quit tSC
}

/// Test numeric comparison
Method TestNumericComparison() As %Status
{
    Set tSC = $$$OK
    Do $$$AssertTrue(10 > 5, "Greater than test")
    Do $$$AssertTrue(5 < 10, "Less than test")
    Do $$$AssertEquals(5, 5, "Equality test")
    Quit tSC
}

}
