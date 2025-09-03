Class ExecuteMCP.Test.ErrorTest Extends %RegisteredObject
{

ClassMethod TestMethod() As %Status
{
    Set tSC = $$$OK
    // Fixed the missing closing brace - this was originally a test for error handling
    Quit tSC
}

}
