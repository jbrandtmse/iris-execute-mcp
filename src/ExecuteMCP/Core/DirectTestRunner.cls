/// ExecuteMCP.Core.DirectTestRunner - Ultra-simple test runner
/// Completely bypasses %UnitTest framework to avoid timeout issues
Class ExecuteMCP.Core.DirectTestRunner Extends %RegisteredObject
{

/// Run tests directly without any %UnitTest framework
ClassMethod RunTests(pTestSpec As %String, pNamespace As %String = "HSCUSTOM") As %String
{
    Try {
        ; Initialize result structure
        Set tResult = {}
        Set tResult.status = "success"
        Set tResult.summary = {}
        Set tResult.summary.passed = 0
        Set tResult.summary.failed = 0
        Set tResult.summary.errors = 0
        Set tResult.summary.skipped = 0
        Set tResult.summary.total = 0
        Set tResult.tests = []
        Set tResult.startTime = $ZTIMESTAMP
        
        ; Parse test spec (package, class, or class:method)
        If pTestSpec [ ":" {
            Set tClassName = $PIECE(pTestSpec, ":", 1)
            Set tMethodFilter = $PIECE(pTestSpec, ":", 2)
        } Else {
            Set tClassName = pTestSpec
            Set tMethodFilter = ""
        }
        
        ; For now, just handle single class
        If $CLASSMETHOD(tClassName, "%Extends", "%UnitTest.TestCase") {
            ; Get test methods
            Set tMethods = ..GetTestMethods(tClassName)
            
            ; Run each test method directly
            Set tMethodIter = tMethods.%GetIterator()
            While tMethodIter.%GetNext(.tKey, .tMethodName) {
                ; Apply method filter if specified
                If (tMethodFilter '= "") && (tMethodName '= tMethodFilter) {
                    Continue
                }
                
                Set tTest = {}
                Set tTest.className = tClassName
                Set tTest.method = tMethodName
                Set tResult.summary.total = tResult.summary.total + 1
                
                ; Run test in isolated context
                Set tTestResult = ..RunSingleTest(tClassName, tMethodName)
                Set tTest.status = tTestResult.status
                Set tTest.message = tTestResult.message
                Set tTest.duration = tTestResult.duration
                
                ; Update summary
                If tTest.status = "passed" {
                    Set tResult.summary.passed = tResult.summary.passed + 1
                } ElseIf tTest.status = "failed" {
                    Set tResult.summary.failed = tResult.summary.failed + 1
                } ElseIf tTest.status = "error" {
                    Set tResult.summary.errors = tResult.summary.errors + 1
                } Else {
                    Set tResult.summary.skipped = tResult.summary.skipped + 1
                }
                
                Do tResult.tests.%Push(tTest)
            }
        } Else {
            ; Not a test class
            Set tResult.status = "error"
            Set tResult.error = "Class "_tClassName_" is not a test class"
        }
        
        ; Calculate execution time
        Set tResult.endTime = $ZTIMESTAMP
        Set tResult.executionTime = ($PIECE(tResult.endTime, ",", 2) - $PIECE(tResult.startTime, ",", 2)) * 1000
        Set tResult.executionTime = $FNUMBER(tResult.executionTime, "", 0) _ "ms"
        
        Return tResult.%ToJSON()
    }
    Catch ex {
        Return "{""status"":""error"",""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Run a single test method in isolation
ClassMethod RunSingleTest(pClassName As %String, pMethodName As %String) As %DynamicObject [ Private ]
{
    Set tResult = {}
    Set tStartTime = $ZTIMESTAMP
    
    Try {
        ; Create a new instance with a mock manager
        ; This avoids complex Manager initialization
        New %testmanager
        Set %testmanager = ..CreateMockManager()
        
        ; Create test instance and pass the mock manager as initvalue
        ; %UnitTest.TestCase %OnNew expects the Manager as the first parameter
        Set tTestInstance = $CLASSMETHOD(pClassName, "%New", %testmanager)
        
        If '$ISOBJECT(tTestInstance) {
            Set tResult.status = "error"
            Set tResult.message = "Failed to create test instance"
            Return tResult
        }
        
        ; Run the test method
        Set tMethodResult = $METHOD(tTestInstance, pMethodName)
        
        ; Check result
        If $DATA(tMethodResult) && $SYSTEM.Status.IsError(tMethodResult) {
            Set tResult.status = "failed"
            Set tResult.message = $SYSTEM.Status.GetErrorText(tMethodResult)
        } Else {
            ; Check if there were any assertion failures
            If %testmanager.AssertionsFailed > 0 {
                Set tResult.status = "failed"
                Set tResult.message = %testmanager.AssertionsFailed_" assertion(s) failed"
            } Else {
                Set tResult.status = "passed"
                Set tResult.message = "Test passed"
            }
        }
    }
    Catch ex {
        Set tResult.status = "error"
        Set tResult.message = ex.DisplayString()
    }
    
    ; Calculate duration
    Set tEndTime = $ZTIMESTAMP
    Set tResult.duration = ($PIECE(tEndTime, ",", 2) - $PIECE(tStartTime, ",", 2)) * 1000
    
    Return tResult
}

/// Create a minimal mock manager for assertions
ClassMethod CreateMockManager() As %RegisteredObject [ Private ]
{
    ; Use the MockTestManager class that has proper methods
    Return ##class(ExecuteMCP.Core.MockTestManager).%New()
}

/// Get test methods for a class
ClassMethod GetTestMethods(pClassName As %String) As %DynamicArray [ Private ]
{
    Set tMethods = []
    
    Try {
        ; Query for test methods
        Set tSQL = "SELECT Name FROM %Dictionary.CompiledMethod "_
                  "WHERE parent->ID = ? "_
                  "AND Name %STARTSWITH 'Test' "_
                  "ORDER BY Name"
        
        Set tStatement = ##class(%SQL.Statement).%New()
        Set tSC = tStatement.%Prepare(tSQL)
        If $$$ISERR(tSC) Return tMethods
        
        Set tResultSet = tStatement.%Execute(pClassName)
        
        While tResultSet.%Next() {
            Do tMethods.%Push(tResultSet.%Get("Name"))
        }
    }
    Catch ex {
        ; Return empty array on error
    }
    
    Return tMethods
}

/// Test the direct runner
ClassMethod TestDirectRunner() As %String
{
    Try {
        Return ..RunTests("ExecuteMCP.Test.SampleUnitTest")
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

}
