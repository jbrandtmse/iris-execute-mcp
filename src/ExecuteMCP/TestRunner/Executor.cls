/// ExecuteMCP.TestRunner.Executor - Executes test methods with lifecycle support
/// Handles test method invocation and assertion macro compatibility
Class ExecuteMCP.TestRunner.Executor Extends %RegisteredObject
{

/// Reference to the Manager instance for LogAssert/LogMessage calls
Property Manager As ExecuteMCP.TestRunner.Manager;

/// Execute a single test method
Method ExecuteTestMethod(pTestClass As %String, pMethodName As %String) As %Status
{
    Set tSC = $$$OK
    Try {
        ; Validate inputs
        If (pTestClass = "") || (pMethodName = "") {
            Set tSC = $$$ERROR($$$GeneralError, "Test class and method required")
            Quit
        }
        
        ; Check if class exists
        If '##class(%Dictionary.CompiledClass).%ExistsId(pTestClass) {
            Set tSC = $$$ERROR($$$GeneralError, "Test class "_pTestClass_" not found")
            Quit
        }
        
        ; CRITICAL: Set Manager in global BEFORE creating test instance
        ; This allows our custom TestCase base class to pick it up in %OnNew
        Set ^||TestRunnerManager = ..Manager
        
        ; Create instance of test class using XECUTE for dynamic instantiation
        ; This avoids $CLASSMETHOD issues with %New
        Set tTestInstance = ""
        Set tCreateCmd = "Set tTestInstance = ##class("_pTestClass_").%New("""")"
        XECUTE tCreateCmd
        
        If '$ISOBJECT(tTestInstance) {
            Set tSC = $$$ERROR($$$GeneralError, "Failed to create instance of "_pTestClass)
            Quit
        }
        
        ; Start method in context - FIXED: Capture status properly
        Set tSC = ..Manager.Context.StartMethod(pMethodName)
        If $$$ISERR(tSC) {
            Quit
        }
        
        ; Call OnBeforeAllTests if it exists and this is the first test
        If ..Manager.Context.IsFirstTest() {
            If ##class(%Dictionary.CompiledMethod).%ExistsId(pTestClass_"||OnBeforeAllTests") {
                Try {
                    Do $METHOD(tTestInstance, "OnBeforeAllTests")
                } Catch ex {
                    ; Log but don't fail the test
                    Set tSC2 = ..Manager.Context.AddMessage("OnBeforeAllTests error: "_ex.DisplayString())
                }
            }
        }
        
        ; Call OnBeforeOneTest if it exists
        If ##class(%Dictionary.CompiledMethod).%ExistsId(pTestClass_"||OnBeforeOneTest") {
            Try {
                Do $METHOD(tTestInstance, "OnBeforeOneTest", pMethodName)
            } Catch ex {
                ; Log but don't fail the test
                Set tSC2 = ..Manager.Context.AddMessage("OnBeforeOneTest error: "_ex.DisplayString())
            }
        }
        
        ; Execute the test method
        Set tMethodStatus = $$$OK
        Try {
            Do $METHOD(tTestInstance, pMethodName)
        } Catch ex {
            Set tMethodStatus = ex.AsStatus()
            Set tSC2 = ..Manager.Context.AddMessage("Test method error: "_ex.DisplayString())
        }
        
        ; Call OnAfterOneTest if it exists
        If ##class(%Dictionary.CompiledMethod).%ExistsId(pTestClass_"||OnAfterOneTest") {
            Try {
                Do $METHOD(tTestInstance, "OnAfterOneTest", pMethodName)
            } Catch ex {
                ; Log but don't fail the test
                Set tSC2 = ..Manager.Context.AddMessage("OnAfterOneTest error: "_ex.DisplayString())
            }
        }
        
        ; End method in context - FIXED: Capture status properly
        Set tSC = ..Manager.Context.EndMethod(tMethodStatus)
        
        ; Clean up any global variables
        Kill ^||TestRunnerManager
        
    }
    Catch ex {
        Set tSC = ex.AsStatus()
        ; Ensure cleanup even on error
        Kill ^||TestRunnerManager
    }
    Quit tSC
}

/// Execute all test methods in a class
Method ExecuteTestClass(pTestClass As %String) As %Status
{
    Set tSC = $$$OK
    Try {
        ; Start class in context - FIXED: Capture status properly
        Set tSC = ..Manager.Context.StartClass(pTestClass)
        If $$$ISERR(tSC) {
            Quit
        }
        
        ; Get test methods using Discovery (returns JSON string)
        Set tMethodsJSON = ##class(ExecuteMCP.TestRunner.Discovery).DiscoverTestMethods(pTestClass)
        
        ; Parse JSON string to array
        Set tMethods = [].%FromJSON(tMethodsJSON)
        
        If '$ISOBJECT(tMethods) || (tMethods.%Size() = 0) {
            Set tSC = $$$ERROR($$$GeneralError, "No test methods found for "_pTestClass)
            Quit
        }
        
        ; Execute each test method
        Set tIterator = tMethods.%GetIterator()
        While tIterator.%GetNext(.tKey, .tMethodName) {
            Set tSC = ..ExecuteTestMethod(pTestClass, tMethodName)
            If $$$ISERR(tSC) {
                ; Log error but continue with other tests
                Set tSC2 = ..Manager.Context.AddMessage("Failed to execute "_tMethodName_": "_$SYSTEM.Status.GetErrorText(tSC))
            }
        }
        
        ; Check if we need to call OnAfterAllTests
        ; This is a simplified check - in production would track properly
        Set tTestInstance = ""
        Set tCreateCmd = "Set tTestInstance = ##class("_pTestClass_").%New("""")"
        XECUTE tCreateCmd
        
        If $ISOBJECT(tTestInstance) {
            If ##class(%Dictionary.CompiledMethod).%ExistsId(pTestClass_"||OnAfterAllTests") {
                Try {
                    Do $METHOD(tTestInstance, "OnAfterAllTests")
                } Catch ex {
                    Set tSC2 = ..Manager.Context.AddMessage("OnAfterAllTests error: "_ex.DisplayString())
                }
            }
        }
        
        ; End class in context - FIXED: Capture status properly
        Set tSC = ..Manager.Context.EndClass()
        
    }
    Catch ex {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}

/// Execute multiple test classes
Method ExecuteTestClasses(pTestClasses As %DynamicArray) As %Status
{
    Set tSC = $$$OK
    Try {
        If '$ISOBJECT(pTestClasses) {
            Set tSC = $$$ERROR($$$GeneralError, "Invalid test class list")
            Quit
        }
        
        ; Mark start time
        Set ..Manager.Context.StartTime = $ZTIMESTAMP
        
        ; Execute each test class
        Set tIterator = pTestClasses.%GetIterator()
        While tIterator.%GetNext(.tKey, .tClassName) {
            Set tSC = ..ExecuteTestClass(tClassName)
            If $$$ISERR(tSC) {
                ; Log error but continue with other classes
                Set tSC2 = ..Manager.Context.AddMessage("Failed to execute class "_tClassName_": "_$SYSTEM.Status.GetErrorText(tSC))
            }
        }
        
        ; Mark end time
        Set ..Manager.Context.EndTime = $ZTIMESTAMP
        
    }
    Catch ex {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}

/// Execute tests matching a specification (like ":ExecuteMCP.Test.SimpleTest")
Method ExecuteSpec(pSpec As %String) As %Status
{
    Set tSC = $$$OK
    Try {
        ; Remove leading colon if present
        If $EXTRACT(pSpec, 1) = ":" {
            Set pSpec = $EXTRACT(pSpec, 2, *)
        }
        
        ; Check if spec includes a method (Class:Method format)
        If pSpec [ ":" {
            Set tClass = $PIECE(pSpec, ":", 1)
            Set tMethod = $PIECE(pSpec, ":", 2)
            
            ; Execute single method
            Set tSC = ..Manager.Context.StartClass(tClass)
            If $$$ISERR(tSC) {
                Quit
            }
            Set tSC = ..ExecuteTestMethod(tClass, tMethod)
            Set tSC2 = ..Manager.Context.EndClass()
        }
        Else {
            ; Check if it's a single class or a package
            If ##class(%Dictionary.CompiledClass).%ExistsId(pSpec) {
                ; Single class
                Set tSC = ..ExecuteTestClass(pSpec)
            }
            Else {
                ; Assume it's a package - discover all classes (returns JSON string)
                Set tClassesJSON = ##class(ExecuteMCP.TestRunner.Discovery).DiscoverTestClasses(pSpec)
                
                ; Parse JSON string to array
                Set tClasses = [].%FromJSON(tClassesJSON)
                
                If '$ISOBJECT(tClasses) || (tClasses.%Size() = 0) {
                    Set tSC = $$$ERROR($$$GeneralError, "No test classes found for spec: "_pSpec)
                    Quit
                }
                
                Set tSC = ..ExecuteTestClasses(tClasses)
            }
        }
    }
    Catch ex {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}

}
