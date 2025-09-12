/// ExecuteMCP.Core.SimpleUnitTest - Simplified unit test runner
/// Bypasses complex TestRunner architecture for direct execution
Class ExecuteMCP.Core.SimpleUnitTest Extends %RegisteredObject
{

/// Run unit tests with simplified approach
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
        
        ; Check if it's a package or class
        If tClassName '[ "." {
            ; It's a package, discover all test classes
            Set tPackage = tClassName
            Set tClasses = ..DiscoverTestClasses(tPackage)
        } Else {
            ; It's a specific class
            Set tClasses = []
            Do tClasses.%Push(tClassName)
        }
        
        ; Process each test class
        Set tClassIter = tClasses.%GetIterator()
        While tClassIter.%GetNext(.tKey, .tClassName) {
            ; Run tests for this class
            Set tClassResult = ..RunClassTests(tClassName, tMethodFilter)
            
            ; Merge results
            Set tTestIter = tClassResult.tests.%GetIterator()
            While tTestIter.%GetNext(.tTestKey, .tTest) {
                Do tResult.tests.%Push(tTest)
                
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
            }
        }
        
        ; Calculate execution time
        Set tResult.endTime = $ZTIMESTAMP
        Set tResult.executionTime = ($PIECE(tResult.endTime, ",", 2) - $PIECE(tResult.startTime, ",", 2)) * 1000
        Set tResult.executionTime = $FNUMBER(tResult.executionTime, "", 0) _ "ms"
        
        Return tResult.%ToJSON()
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Run tests for a single class
ClassMethod RunClassTests(pClassName As %String, pMethodFilter As %String = "") As %DynamicObject [ Private ]
{
    Set tResult = {}
    Set tResult.tests = []
    
    Try {
        ; Create a simple manager for assertions
        Set tManager = ##class(%UnitTest.Manager).%New()
        
        ; Create test instance - pass Manager directly
        Set tTestInstance = $CLASSMETHOD(pClassName, "%New", tManager)
        
        If '$ISOBJECT(tTestInstance) {
            ; Failed to create instance
            Set tTest = {}
            Set tTest.className = pClassName
            Set tTest.method = "INSTANTIATION"
            Set tTest.status = "error"
            Set tTest.message = "Failed to create test instance"
            Do tResult.tests.%Push(tTest)
            Return tResult
        }
        
        ; Get test methods
        Set tMethods = ..GetTestMethods(pClassName)
        
        ; Run each test method
        Set tMethodIter = tMethods.%GetIterator()
        While tMethodIter.%GetNext(.tKey, .tMethodName) {
            ; Apply method filter if specified
            If (pMethodFilter '= "") && (tMethodName '= pMethodFilter) {
                Continue
            }
            
            Set tTest = {}
            Set tTest.className = pClassName
            Set tTest.method = tMethodName
            
            Try {
                ; Run the test method
                Set tMethodResult = $METHOD(tTestInstance, tMethodName)
                
                ; Check for errors
                If $DATA(tMethodResult) && $SYSTEM.Status.IsError(tMethodResult) {
                    Set tTest.status = "failed"
                    Set tTest.message = $SYSTEM.Status.GetErrorText(tMethodResult)
                } Else {
                    Set tTest.status = "passed"
                    Set tTest.message = "Test passed"
                }
            }
            Catch exMethod {
                Set tTest.status = "error"
                Set tTest.message = exMethod.DisplayString()
            }
            
            Do tResult.tests.%Push(tTest)
        }
    }
    Catch ex {
        Set tTest = {}
        Set tTest.className = pClassName
        Set tTest.method = "UNKNOWN"
        Set tTest.status = "error"
        Set tTest.message = ex.DisplayString()
        Do tResult.tests.%Push(tTest)
    }
    
    Return tResult
}

/// Discover test classes in a package
ClassMethod DiscoverTestClasses(pPackage As %String) As %DynamicArray [ Private ]
{
    Set tClasses = []
    
    Try {
        ; Query for test classes
        Set tSQL = "SELECT Name FROM %Dictionary.CompiledClass "_
                  "WHERE Name %STARTSWITH ? "_
                  "AND Super [ '%UnitTest.TestCase' "_
                  "ORDER BY Name"
        
        Set tStatement = ##class(%SQL.Statement).%New()
        Set tSC = tStatement.%Prepare(tSQL)
        If $$$ISERR(tSC) Return tClasses
        
        Set tResultSet = tStatement.%Execute(pPackage_".")
        
        While tResultSet.%Next() {
            Do tClasses.%Push(tResultSet.%Get("Name"))
        }
    }
    Catch ex {
        ; Return empty array on error
    }
    
    Return tClasses
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

/// Test the simple runner
ClassMethod TestSimpleRunner() As %String
{
    Try {
        Return ..RunTests("ExecuteMCP.Test.SampleUnitTest")
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

}
