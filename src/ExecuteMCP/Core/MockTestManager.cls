/// ExecuteMCP.Core.MockTestManager - Minimal mock manager for DirectTestRunner
/// Provides just enough functionality for assertion macros to work
Class ExecuteMCP.Core.MockTestManager Extends %RegisteredObject
{

/// Track assertion results
Property AssertionsFailed As %Integer [ InitialExpression = 0 ];

Property AssertionsPassed As %Integer [ InitialExpression = 0 ];

Property Debug As %Integer [ InitialExpression = 0 ];

Property CurrentTestClass As %String;

Property CurrentTestMethod As %String;

/// Required by %UnitTest.TestCase.GetSourceLocation
Property OriginNS As %String [ InitialExpression = "HSCUSTOM" ];

/// Mock CurrentDir for file-based assertions
Property CurrentDir As %String;

/// Mock UserParam for debug features
Property UserParam As %String;

/// Mock GetSourceLocation method required by assertion macros
Method GetSourceLocation() As %String
{
    ; Return a simple location string
    Return "DirectTestRunner"
}

/// Mock LogAssert method to track assertion results
Method LogAssert(pResult As %Boolean, pAction As %String, pDescription As %String = "", pExtra1 As %String = "", pExtra2 As %String = "") As %Boolean
{
    If pResult {
        Set ..AssertionsPassed = ..AssertionsPassed + 1
    } Else {
        Set ..AssertionsFailed = ..AssertionsFailed + 1
    }
    Return pResult
}

/// Mock IncludeFile method (does nothing)
Method IncludeFile(pFilename As %String) As %Status
{
    Return $$$OK
}

/// Mock LogMessage method (does nothing in mock)
Method LogMessage(pMessage As %String, pLocation As %String = "") As %Status
{
    ; Could store messages if needed for debugging
    Return $$$OK
}

}
