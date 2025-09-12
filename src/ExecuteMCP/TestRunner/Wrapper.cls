/// ExecuteMCP.TestRunner.Wrapper - MCP-safe wrapper for TestRunner
/// Works around Native API parameter marshaling issues
Class ExecuteMCP.TestRunner.Wrapper Extends %RegisteredObject
{

/// Run tests using spec passed via global to avoid Native API parameter issues
ClassMethod RunTestFromGlobal() As %String
{
    Try {
        ; Get test spec from global (set by MCP server)
        Set tSpec = $GET(^ExecuteMCP.TestSpec, "")
        Set tNamespace = $GET(^ExecuteMCP.TestNamespace, "HSCUSTOM")
        
        ; Clear the globals after reading
        Kill ^ExecuteMCP.TestSpec
        Kill ^ExecuteMCP.TestNamespace
        
        If tSpec = "" {
            Return "{""error"":""No test spec provided in ^ExecuteMCP.TestSpec""}"
        }
        
        ; Log the spec we're about to run
        Set ^ExecuteMCP.TestDebug = "Running spec: "_tSpec_" in namespace: "_tNamespace
        
        ; Call the TestRunner directly with string parameters
        Return ##class(ExecuteMCP.TestRunner.Manager).RunTestSpec(tSpec, tNamespace)
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Debug method with hardcoded test spec to bypass parameter issues
ClassMethod RunTestDebug() As %String
{
    Try {
        ; Hardcoded test spec to bypass Native API parameter issues
        Set tSpec = "ExecuteMCP.Test.SimpleTest:TestCalculations"
        
        ; Call the TestRunner directly with string parameters
        Return ##class(ExecuteMCP.TestRunner.Manager).RunTestSpec(tSpec, "HSCUSTOM")
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Run any test spec by encoding it in the method name
/// Call methods like RunTestSimpleTest or RunTestSimpleTestColonTestCalculations
ClassMethod RunTest(pEncodedSpec As %String = "") As %String
{
    Try {
        ; Decode the test spec from the encoded parameter
        ; Replace "Colon" with ":" and "Dot" with "."
        Set tSpec = pEncodedSpec
        Set tSpec = $REPLACE(tSpec, "Colon", ":")
        Set tSpec = $REPLACE(tSpec, "Dot", ".")
        
        If tSpec = "" {
            ; Default to SimpleTest if no spec provided
            Set tSpec = "ExecuteMCP.Test.SimpleTest"
        }
        
        ; Call the TestRunner directly with string parameters
        Return ##class(ExecuteMCP.TestRunner.Manager).RunTestSpec(tSpec, "HSCUSTOM")
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Run tests for ExecuteMCP.Test.SimpleTest
ClassMethod RunSimpleTest() As %String
{
    Try {
        Return ##class(ExecuteMCP.TestRunner.Manager).RunTestSpec("ExecuteMCP.Test.SimpleTest", "HSCUSTOM")
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Run tests for ExecuteMCP.Test.ErrorTest
ClassMethod RunErrorTest() As %String
{
    Try {
        Return ##class(ExecuteMCP.TestRunner.Manager).RunTestSpec("ExecuteMCP.Test.ErrorTest", "HSCUSTOM")
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Run all tests in ExecuteMCP.Test package
ClassMethod RunAllTests() As %String
{
    Try {
        Return ##class(ExecuteMCP.TestRunner.Manager).RunTestSpec("ExecuteMCP.Test", "HSCUSTOM")
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Provide instructions for using TestRunner through MCP
ClassMethod GetUsageInstructions() As %String
{
    Set tInstructions = {}
    Set tInstructions.problem = "Native API parameter marshaling converts strings to object references"
    Set tInstructions.solution = "Use execute_classmethod to call Wrapper methods or set globals"
    
    Set tInstructions.availableMethods = []
    Do tInstructions.availableMethods.%Push("RunTestFromGlobal - Reads spec from ^ExecuteMCP.TestSpec global")
    Do tInstructions.availableMethods.%Push("RunTestDebug - Runs ExecuteMCP.Test.SimpleTest:TestCalculations")
    Do tInstructions.availableMethods.%Push("RunSimpleTest - Runs all tests in ExecuteMCP.Test.SimpleTest")
    Do tInstructions.availableMethods.%Push("RunErrorTest - Runs all tests in ExecuteMCP.Test.ErrorTest")
    Do tInstructions.availableMethods.%Push("RunAllTests - Runs all tests in ExecuteMCP.Test package")
    Do tInstructions.availableMethods.%Push("RunTest - Accepts encoded spec (replace : with Colon, . with Dot)")
    
    Set tInstructions.example = {}
    Set tInstructions.example.tool = "execute_classmethod"
    Set tInstructions.example.className = "ExecuteMCP.TestRunner.Wrapper"
    Set tInstructions.example.methodName = "RunSimpleTest"
    Set tInstructions.example.namespace = "HSCUSTOM"
    
    Set tInstructions.globalApproach = {}
    Set tInstructions.globalApproach.step1 = "Set ^ExecuteMCP.TestSpec = ""ExecuteMCP.Test.SimpleTest"""
    Set tInstructions.globalApproach.step2 = "Call RunTestFromGlobal()"
    
    Return tInstructions.%ToJSON()
}

/// Diagnostic method to test Discovery component
ClassMethod DiagnoseDiscovery() As %String
{
    Try {
        Set tResult = {}
        Set tResult.step = "Discovery Diagnosis"
        
        ; Test 1: Check if Discovery class exists
        Set tResult.discoveryExists = ##class(%Dictionary.CompiledClass).%ExistsId("ExecuteMCP.TestRunner.Discovery")
        
        ; Test 2: Try to discover test classes (should return JSON)
        Try {
            Set tClassesJSON = ##class(ExecuteMCP.TestRunner.Discovery).DiscoverTestClasses("ExecuteMCP.Test")
            Set tResult.discoverClassesSuccess = 1
            Set tResult.classesFound = tClassesJSON
        }
        Catch ex {
            Set tResult.discoverClassesSuccess = 0
            Set tResult.discoverError = ex.DisplayString()
        }
        
        ; Test 3: Try to discover test methods for SimpleTest
        Try {
            Set tMethodsJSON = ##class(ExecuteMCP.TestRunner.Discovery).DiscoverTestMethods("ExecuteMCP.Test.SimpleTest")
            Set tResult.discoverMethodsSuccess = 1
            Set tResult.methodsFound = tMethodsJSON
        }
        Catch ex {
            Set tResult.discoverMethodsSuccess = 0
            Set tResult.methodError = ex.DisplayString()
        }
        
        Return tResult.%ToJSON()
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Diagnostic method to test Context component
ClassMethod DiagnoseContext() As %String
{
    Try {
        Set tResult = {}
        Set tResult.step = "Context Diagnosis"
        
        ; Test 1: Create Context
        Try {
            Set tContext = ##class(ExecuteMCP.TestRunner.Context).%New()
            Set tResult.contextCreated = $ISOBJECT(tContext)
            
            ; Test 2: Add test data
            Do tContext.StartClass("TestClass")
            Do tContext.StartMethod("TestMethod")
            Do tContext.AddAssertion(1, "Test assertion", "Test passed")
            Do tContext.EndMethod($$$OK)
            Do tContext.EndClass()
            
            ; Test 3: Get results
            Set tResults = tContext.GetResults()
            Set tResult.resultsGenerated = (tResults '= "")
            Set tResult.results = tResults
        }
        Catch ex {
            Set tResult.contextError = ex.DisplayString()
        }
        
        Return tResult.%ToJSON()
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Diagnostic method to test Manager component
ClassMethod DiagnoseManager() As %String
{
    Try {
        Set tResult = {}
        Set tResult.step = "Manager Diagnosis"
        
        ; Test 1: Create Manager
        Try {
            Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
            Set tResult.managerCreated = $ISOBJECT(tManager)
            Set tResult.contextCreated = $ISOBJECT(tManager.Context)
        }
        Catch ex {
            Set tResult.managerError = ex.DisplayString()
        }
        
        ; Test 2: Validate TestRunner
        Try {
            Set tValidation = ##class(ExecuteMCP.TestRunner.Manager).ValidateTestRunner()
            Set tResult.validation = tValidation
        }
        Catch ex {
            Set tResult.validationError = ex.DisplayString()
        }
        
        Return tResult.%ToJSON()
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Full diagnostic to isolate timeout issue
ClassMethod FullDiagnosis() As %String
{
    Try {
        Set tResult = {}
        Set tResult.timestamp = $ZDATETIME($NOW(), 3)
        
        ; Test each component
        Set tResult.discovery = {}.%FromJSON(..DiagnoseDiscovery())
        Set tResult.context = {}.%FromJSON(..DiagnoseContext())
        Set tResult.manager = {}.%FromJSON(..DiagnoseManager())
        
        ; Overall status
        Set tResult.overallStatus = "Complete"
        
        Return tResult.%ToJSON()
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Simple test that bypasses the Manager property issue
ClassMethod TestManagerCreation() As %String
{
    Try {
        Set tResult = {}
        
        ; Step 1: Create TestRunner Manager
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set tResult.managerCreated = $ISOBJECT(tManager)
        
        ; Step 2: Create Executor and set Manager
        Set tExecutor = ##class(ExecuteMCP.TestRunner.Executor).%New()
        Set tExecutor.Manager = tManager
        Set tResult.executorCreated = $ISOBJECT(tExecutor)
        
        ; Step 3: Check if we can create test instance
        Set tTest = ##class(ExecuteMCP.Test.SimpleTest).%New("")
        Set tResult.testInstanceCreated = $ISOBJECT(tTest)
        
        ; Step 4: Try minimal execution without setting Manager on test
        Set tResult.testStep = "About to call ExecuteSpec"
        
        ; Don't actually execute - just verify we can get this far
        Set tResult.success = 1
        
        Return tResult.%ToJSON()
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Test if we can bypass the Manager property issue by using reflection
ClassMethod TestReflectionApproach() As %String
{
    Try {
        Set tResult = {}
        
        ; Create test instance and %UnitTest.Manager
        Set tTest = ##class(ExecuteMCP.Test.SimpleTest).%New("")
        Set tUnitMgr = ##class(%UnitTest.Manager).%New()
        
        ; Try to use $PROPERTY to set it
        Try {
            Set $PROPERTY(tTest, "Manager") = tUnitMgr
            Set tResult.propertySetSuccess = 1
        }
        Catch ex {
            Set tResult.propertySetError = ex.DisplayString()
            ; Try alternative approach using %Set
            Try {
                Do tTest.%Set("Manager", tUnitMgr)
                Set tResult.setMethodSuccess = 1
            }
            Catch ex2 {
                Set tResult.setMethodError = ex2.DisplayString()
            }
        }
        
        Return tResult.%ToJSON()
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Simplified test runner that avoids Manager property issues
ClassMethod RunSimpleTestDirect() As %String
{
    Try {
        Set tResult = {}
        Set tResult.test = "Direct execution bypassing Manager property"
        
        ; Create our TestRunner components
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set tExecutor = ##class(ExecuteMCP.TestRunner.Executor).%New()
        Set tExecutor.Manager = tManager
        
        ; Try to execute without the problematic Manager injection
        ; We'll modify the approach to not require setting Manager on test instance
        
        ; Start the test class
        Do tManager.Context.StartClass("ExecuteMCP.Test.SimpleTest")
        
        ; Get test methods
        Set tMethodsJSON = ##class(ExecuteMCP.TestRunner.Discovery).DiscoverTestMethods("ExecuteMCP.Test.SimpleTest")
        Set tMethods = [].%FromJSON(tMethodsJSON)
        
        ; Just record that we found the methods
        Set tResult.methodsFound = tMethods.%Size()
        Set tResult.methods = tMethodsJSON
        
        ; End the test class
        Do tManager.Context.EndClass()
        
        ; Get results
        Set tResult.results = tManager.Context.GetResults()
        
        Return tResult.%ToJSON()
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Test instance creation of ExecuteMCP.Test.SimpleTest with proper Manager setup
ClassMethod TestInstanceCreation() As %String
{
    Set result = "{""status"":""starting""}"
    Try {
        // Create a Manager instance
        Set manager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set result = result _ ",""managerCreated"":true"
        
        // Store Manager in both global types for testing
        Set ^||TestRunnerManager = manager
        Set ^TestRunnerManager = manager
        Set result = result _ ",""managerStored"":true"
        
        // Try to create test instance with empty initvalue parameter
        Set testInstance = ##class(ExecuteMCP.Test.SimpleTest).%New("")
        
        If $ISOBJECT(testInstance) {
            Set result = result _ ",""instanceCreated"":true"
            
            // Check if Manager property is set
            If $ISOBJECT(testInstance.Manager) {
                Set result = result _ ",""managerPropertySet"":true"
            } Else {
                Set result = result _ ",""managerPropertySet"":false"
            }
        } Else {
            Set result = result _ ",""instanceCreated"":false,""error"":""Failed to create instance"""
        }
        
        Set result = result _ ",""success"":true}"
    }
    Catch ex {
        Set result = result _ ",""exception"":"""_ex.DisplayString()_""",""success"":false}"
    }
    
    // Cleanup
    Kill ^||TestRunnerManager
    Kill ^TestRunnerManager
    
    Quit result
}

/// Test Manager creation independently
ClassMethod TestManagerCreation() As %String
{
    Set result = "{""status"":""starting""}"
    Try {
        // Create Manager
        Set manager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        
        If $ISOBJECT(manager) {
            Set result = result _ ",""managerCreated"":true"
            
            // Test basic Manager properties
            Set className = $CLASSNAME(manager)
            Set result = result _ ",""className"":"""_className_""""
            
            // Try to access Manager properties/methods
            Set manager.CurrentTest = "TestMethod"
            Set result = result _ ",""propertySet"":true"
        } Else {
            Set result = result _ ",""managerCreated"":false"
        }
        
        Set result = result _ ",""success"":true}"
    }
    Catch ex {
        Set result = result _ ",""exception"":"""_ex.DisplayString()_""",""success"":false}"
    }
    
    Quit result
}

}
