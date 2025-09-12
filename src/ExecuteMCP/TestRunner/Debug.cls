/// Debug utilities for TestRunner diagnostics
Class ExecuteMCP.TestRunner.Debug Extends %RegisteredObject
{

/// Test the Manager passing pattern
ClassMethod TestManagerPassingPattern() As %String
{
    Try {
        Set result = {}
        
        ; Create Manager instance
        Set manager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set result.managerCreated = $ISOBJECT(manager)
        Set result.managerOID = manager.%Oid()
        
        ; Test 1: Direct pass to TestCase
        Set testInstance = ##class(ExecuteMCP.Test.SimpleTest).%New(manager)
        Set result.testCreatedWithManager = $ISOBJECT(testInstance)
        
        ; Check if Manager property is accessible
        Try {
            ; The Manager property is PRIVATE in %UnitTest.TestCase
            ; We can't access it directly, but we can test if assertions work
            Set assertResult = testInstance.AssertEquals(1, 1, "Test assertion")
            Set result.assertionWorks = 1
        }
        Catch ex {
            Set result.assertionError = ex.DisplayString()
        }
        
        Return result.%ToJSON()
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Test direct instantiation with Manager
ClassMethod TestDirectInstantiation() As %String
{
    Try {
        Set result = {}
        
        ; Create Manager
        Set manager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set result.managerCreated = 1
        
        ; Use $CLASSMETHOD to instantiate with Manager
        Set className = "ExecuteMCP.Test.SimpleTest"
        Set testInstance = $CLASSMETHOD(className, "%New", manager)
        Set result.instanceCreated = $ISOBJECT(testInstance)
        
        ; Try to run a test method
        Try {
            Do testInstance.TestCalculations()
            Set result.methodExecuted = 1
        }
        Catch ex {
            Set result.methodError = ex.DisplayString()
        }
        
        Return result.%ToJSON()
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Test if Manager is being passed as object or string
ClassMethod DiagnoseParameterType() As %String
{
    Try {
        Set result = {}
        
        ; Create Manager
        Set manager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        
        ; Store in global (this will serialize it)
        Set ^TestRunnerManager = manager
        
        ; Check what's in the global
        Set globalValue = ^TestRunnerManager
        Set result.globalIsObject = $ISOBJECT(globalValue)
        Set result.globalValue = globalValue
        
        ; Now test direct pass
        Set result.managerIsObject = $ISOBJECT(manager)
        Set result.managerOID = manager.%Oid()
        
        ; Clean up
        Kill ^TestRunnerManager
        
        Return result.%ToJSON()
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Debug the TestCase constructor behavior
ClassMethod DebugTestCaseConstructor() As %String
{
    Try {
        Set result = {}
        
        ; Create Manager
        Set manager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set result.step1 = "Manager created"
        
        ; Test different parameter types
        Set result.tests = []
        
        ; Test 1: Pass Manager object directly
        Set test1 = {}
        Set test1.type = "Direct Manager object"
        Try {
            Set instance1 = ##class(ExecuteMCP.Test.SimpleTest).%New(manager)
            Set test1.success = $ISOBJECT(instance1)
        }
        Catch ex {
            Set test1.error = ex.DisplayString()
        }
        Do result.tests.%Push(test1)
        
        ; Test 2: Pass empty string
        Set test2 = {}
        Set test2.type = "Empty string"
        Try {
            Set instance2 = ##class(ExecuteMCP.Test.SimpleTest).%New("")
            Set test2.success = $ISOBJECT(instance2)
        }
        Catch ex {
            Set test2.error = ex.DisplayString()
        }
        Do result.tests.%Push(test2)
        
        ; Test 3: Pass nothing
        Set test3 = {}
        Set test3.type = "No parameter"
        Try {
            Set instance3 = ##class(ExecuteMCP.Test.SimpleTest).%New()
            Set test3.success = $ISOBJECT(instance3)
        }
        Catch ex {
            Set test3.error = ex.DisplayString()
        }
        Do result.tests.%Push(test3)
        
        Return result.%ToJSON()
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Test complete flow with simplified Manager approach
ClassMethod TestSimplifiedFlow() As %String
{
    Try {
        Set result = {}
        Set result.timestamp = $ZDATETIME($NOW(), 3)
        
        ; Create Manager
        Set manager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set result.managerCreated = 1
        
        ; Initialize Context
        If '$ISOBJECT(manager.Context) {
            Set manager.Context = ##class(ExecuteMCP.TestRunner.Context).%New()
        }
        Set manager.Context.StartTime = $ZTIMESTAMP
        
        ; Start test class
        Do manager.Context.StartClass("ExecuteMCP.Test.SimpleTest")
        
        ; Create test instance with Manager
        Set testInstance = ##class(ExecuteMCP.Test.SimpleTest).%New(manager)
        Set result.testInstanceCreated = $ISOBJECT(testInstance)
        
        ; Run a simple test method
        Do manager.Context.StartMethod("TestCalculations")
        
        Set methodStatus = $$$OK
        Try {
            Do testInstance.TestCalculations()
            Set result.testExecuted = 1
        }
        Catch ex {
            Set methodStatus = ex.AsStatus()
            Set result.testError = ex.DisplayString()
        }
        
        Do manager.Context.EndMethod(methodStatus)
        Do manager.Context.EndClass()
        
        ; Get results
        Set manager.Context.EndTime = $ZTIMESTAMP
        Set result.results = manager.Context.GetResults()
        
        Return result.%ToJSON()
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

}
