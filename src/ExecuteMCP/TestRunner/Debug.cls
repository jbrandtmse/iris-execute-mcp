Class ExecuteMCP.TestRunner.Debug
{

ClassMethod TestManagerInjection() As %String
{
    Set result = {}
    Set result.steps = []
    
    Try {
        ; Step 1: Create Manager instance
        Do result.steps.%Push("Creating Manager instance")
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Do result.steps.%Push("Manager created: "_$ISOBJECT(tManager))
        
        ; Step 2: Create test instance
        Do result.steps.%Push("Creating test instance")
        Set tTestInstance = ##class(ExecuteMCP.Test.SimpleTest).%New("")
        Do result.steps.%Push("Test instance created: "_$ISOBJECT(tTestInstance))
        
        ; Step 3: Inject Manager
        Do result.steps.%Push("Injecting Manager property")
        Set tTestInstance.Manager = tManager
        Do result.steps.%Push("Manager injected: "_$ISOBJECT(tTestInstance.Manager))
        
        ; Step 4: Try to call a test method with assertion
        Do result.steps.%Push("Calling test method")
        Set tSC = tTestInstance.TestAlwaysPass()
        Do result.steps.%Push("Test method called: "_$$$ISOK(tSC))
        
        Set result.success = 1
    }
    Catch ex {
        Set result.error = ex.DisplayString()
        Set result.success = 0
    }
    
    Return result.%ToJSON()
}

ClassMethod TestAssertionMacro() As %String
{
    Set result = {}
    
    Try {
        ; Create Manager and Context
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set tManager.Context = ##class(ExecuteMCP.TestRunner.Context).%New()
        
        ; Create test instance and inject Manager
        Set tTestInstance = ##class(ExecuteMCP.Test.SimpleTest).%New("")
        Set tTestInstance.Manager = tManager
        
        ; Test direct assertion
        Do tTestInstance.AssertEquals(1, 1, "Test direct assertion")
        
        Set result.success = 1
        Set result.message = "Assertion executed successfully"
    }
    Catch ex {
        Set result.error = ex.DisplayString()
        Set result.location = ex.Location
        Set result.code = ex.Code
        Set result.success = 0
    }
    
    Return result.%ToJSON()
}

ClassMethod TestManagerLogAssert() As %String
{
    Set result = {}
    
    Try {
        ; Create Manager with Context
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set tContext = ##class(ExecuteMCP.TestRunner.Context).%New()
        Set tManager.Context = tContext
        
        ; Test LogAssert directly
        Do result.steps.%Push("Testing LogAssert method")
        Do tManager.LogAssert(1, "test", "Testing LogAssert")
        Do result.steps.%Push("LogAssert called successfully")
        
        ; Get context results
        Set tResults = tContext.GetResults()
        Set result.contextResults = tResults
        
        Set result.success = 1
    }
    Catch ex {
        Set result.error = ex.DisplayString()
        Set result.success = 0
    }
    
    Return result.%ToJSON()
}

}
