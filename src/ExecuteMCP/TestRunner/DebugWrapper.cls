Class ExecuteMCP.TestRunner.DebugWrapper Extends %RegisteredObject
{

ClassMethod TestWithString() As %String
{
    // Hardcode the spec to avoid parameter issues
    Set spec = "ExecuteMCP.Test.SimpleTest:TestCalculations"
    Set namespace = "HSCUSTOM"
    Return ##class(ExecuteMCP.TestRunner.Manager).RunTestSpec(spec, namespace)
}

ClassMethod TestParamType(pParam As %String) As %String
{
    // Test what we're receiving
    Set result = {}
    Set result.paramValue = pParam
    Set result.paramType = $CLASSNAME(pParam)
    Set result.isObject = $ISOBJECT(pParam)
    Set result.isString = ($DATA(pParam) && ('$ISOBJECT(pParam)))
    
    If $ISOBJECT(pParam) {
        Try {
            Set result.objectClass = pParam.%ClassName(1)
        } Catch {
            Set result.objectClass = "Unknown"
        }
    }
    
    Return result.%ToJSON()
}

}
