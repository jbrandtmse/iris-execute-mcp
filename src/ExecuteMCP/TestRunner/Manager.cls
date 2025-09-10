/// ExecuteMCP.TestRunner.Manager - Main orchestrator and test execution manager
/// Provides LogAssert interface for %UnitTest.TestCase compatibility
Class ExecuteMCP.TestRunner.Manager Extends %RegisteredObject
{

/// Test execution context (explicitly public for external access)
Property Context As ExecuteMCP.TestRunner.Context [ InitialExpression = {##class(ExecuteMCP.TestRunner.Context).%New()} ];

/// Main entry point - run tests for a single class
ClassMethod RunTests(pClassName As %String, pNamespace As %String = "HSCUSTOM") As %String
{
    Try {
        ; Switch to target namespace if needed
        Set tOrigNS = $NAMESPACE
        If $NAMESPACE '= pNamespace {
            Set $NAMESPACE = pNamespace
        }
        
        ; Create manager instance
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        
        ; Initialize context if not already initialized
        If '$ISOBJECT(tManager.Context) {
            Set tManager.Context = ##class(ExecuteMCP.TestRunner.Context).%New()
        }
        Set tManager.Context.StartTime = $ZTIMESTAMP
        
        ; Extract package from class name
        Set tPackage = $PIECE(pClassName, ".", 1, $LENGTH(pClassName, ".") - 1)
        
        ; Build test manifest for the specific class
        Set tTestManifestJSON = ##class(ExecuteMCP.TestRunner.Discovery).BuildTestManifest(tPackage)
        
        If tTestManifestJSON = "" {
            Return "{""error"":""No tests found for class "_pClassName_"""}"
        }
        
        ; Parse JSON back to object
        Set tTestManifest = {}.%FromJSON(tTestManifestJSON)
        
        ; Execute tests (filter by class name)
        Set tStatus = tManager.ExecuteTestManifest(tTestManifest, pClassName)
        
        If $$$ISERR(tStatus) {
            Return "{""error"":"""_$ZCONVERT($SYSTEM.Status.GetErrorText(tStatus), "O", "JS")_"""}"
        }
        
        ; Set end time
        Set tManager.Context.EndTime = $ZTIMESTAMP
        
        ; Get results
        Set tResults = tManager.Context.GetResults()
        
        ; Restore namespace
        If $NAMESPACE '= tOrigNS {
            Set $NAMESPACE = tOrigNS
        }
        
        Return tResults
    }
    Catch ex {
        ; Restore namespace on error
        If $DATA(tOrigNS) && ($NAMESPACE '= tOrigNS) {
            Set $NAMESPACE = tOrigNS
        }
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Run all tests in a package
ClassMethod RunPackageTests(pPackage As %String, pNamespace As %String = "HSCUSTOM") As %String
{
    Try {
        ; Switch to target namespace if needed
        Set tOrigNS = $NAMESPACE
        If $NAMESPACE '= pNamespace {
            Set $NAMESPACE = pNamespace
        }
        
        ; Create manager instance
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        
        ; Initialize context if not already initialized
        If '$ISOBJECT(tManager.Context) {
            Set tManager.Context = ##class(ExecuteMCP.TestRunner.Context).%New()
        }
        Set tManager.Context.StartTime = $ZTIMESTAMP
        
        ; Discover tests (returns JSON string)
        Set tTestManifestJSON = ##class(ExecuteMCP.TestRunner.Discovery).BuildTestManifest(pPackage)
        
        If tTestManifestJSON = "" {
            Return "{""error"":""No tests found in package "_pPackage_"""}"
        }
        
        ; Parse JSON back to object
        Set tTestManifest = {}.%FromJSON(tTestManifestJSON)
        
        ; Execute all tests in the package
        Set tStatus = tManager.ExecuteTestManifest(tTestManifest, "")
        
        If $$$ISERR(tStatus) {
            Return "{""error"":"""_$ZCONVERT($SYSTEM.Status.GetErrorText(tStatus), "O", "JS")_"""}"
        }
        
        ; Set end time
        Set tManager.Context.EndTime = $ZTIMESTAMP
        
        ; Get results
        Set tResults = tManager.Context.GetResults()
        
        ; Restore namespace
        If $NAMESPACE '= tOrigNS {
            Set $NAMESPACE = tOrigNS
        }
        
        Return tResults
    }
    Catch ex {
        ; Restore namespace on error
        If $DATA(tOrigNS) && ($NAMESPACE '= tOrigNS) {
            Set $NAMESPACE = tOrigNS
        }
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Validate the TestRunner is working correctly
ClassMethod ValidateTestRunner(pNamespace As %String = "HSCUSTOM") As %String
{
    Try {
        ; Switch to target namespace if needed
        Set tOrigNS = $NAMESPACE
        If $NAMESPACE '= pNamespace {
            Set $NAMESPACE = pNamespace
        }
        
        Set tResult = {}
        Set tResult.Success = 1
        Set tResult.ManagerReady = 1
        
        ; Test Discovery
        Try {
            Set tDiscoveryTest = ##class(ExecuteMCP.TestRunner.Discovery).ValidateDiscovery()
            Set tDiscoveryObj = {}.%FromJSON(tDiscoveryTest)
            Set tResult.DiscoveryWorking = tDiscoveryObj.success
            Set tResult.TestClassesFound = tDiscoveryObj.classesFound
        }
        Catch {
            Set tResult.DiscoveryWorking = 0
            Set tResult.TestClassesFound = 0
        }
        
        ; Check if we can execute tests
        Try {
            Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
            ; Context should auto-initialize now
            Set tResult.CanExecuteTests = $ISOBJECT(tManager.Context)
        }
        Catch {
            Set tResult.CanExecuteTests = 0
        }
        
        ; Restore namespace
        If $NAMESPACE '= tOrigNS {
            Set $NAMESPACE = tOrigNS
        }
        
        Return tResult.%ToJSON()
    }
    Catch ex {
        ; Restore namespace on error
        If $DATA(tOrigNS) && ($NAMESPACE '= tOrigNS) {
            Set $NAMESPACE = tOrigNS
        }
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Execute test manifest
Method ExecuteTestManifest(pManifest As %DynamicObject, pFilter As %String = "") As %Status
{
    Set tSC = $$$OK
    Try {
        ; Ensure Context is initialized
        If '$ISOBJECT(..Context) {
            Set ..Context = ##class(ExecuteMCP.TestRunner.Context).%New()
        }
        
        ; Iterate through classes in manifest
        Set tClassIter = pManifest.classes.%GetIterator()
        
        While tClassIter.%GetNext(.tKey, .tClassInfo) {
            ; Get class name from class info (fixed field name)
            Set tClassName = tClassInfo.className
            
            ; Check filter if provided
            If (pFilter '= "") && (tClassName '= pFilter) && (pFilter '[ tClassName) {
                Continue
            }
            
            ; Start class execution
            Set tSC = ..Context.StartClass(tClassName)
            If $$$ISERR(tSC) Continue
            
            ; Create test instance with proper initialization
            ; %UnitTest.TestCase expects an initvalue parameter
            Try {
                ; Pass empty string as initvalue to satisfy %UnitTest.TestCase constructor
                Set tTestInstance = $CLASSMETHOD(tClassName, "%New", "")
            }
            Catch {
                ; If that fails, try without parameter
                Try {
                    Set tTestInstance = $CLASSMETHOD(tClassName, "%New")
                }
                Catch exNew {
                    Do ..Context.AddMessage("Failed to create instance of "_tClassName_": "_exNew.DisplayString())
                    Do ..Context.EndClass()
                    Continue
                }
            }
            
            If '$ISOBJECT(tTestInstance) {
                Do ..Context.AddMessage("Failed to create instance of "_tClassName)
                Do ..Context.EndClass()
                Continue
            }
            
            ; Set Manager property for assertion support
            Try {
                Set tTestInstance.Manager = $THIS
            }
            Catch {
                ; Class might not have Manager property, continue anyway
            }
            
            ; Run OnBeforeAllTests if it exists
            Try {
                Do tTestInstance.OnBeforeAllTests()
            }
            Catch {
                ; Method might not exist, continue
            }
            
            ; Execute each test method
            Set tMethodIter = tClassInfo.methods.%GetIterator()
            
            While tMethodIter.%GetNext(.tMethodKey, .tMethodName) {
                ; Check method filter if provided
                If (pFilter '= "") && (pFilter [ "method:") {
                    Set tMethodFilter = $PIECE($PIECE(pFilter, "method:", 2), " ", 1)
                    If tMethodFilter '= tMethodName {
                        Continue
                    }
                }
                
                ; Start method execution
                Set tSC = ..Context.StartMethod(tMethodName)
                If $$$ISERR(tSC) Continue
                
                ; Run OnBeforeOneTest if it exists
                Try {
                    Do tTestInstance.OnBeforeOneTest(tMethodName)
                }
                Catch {
                    ; Method might not exist, continue
                }
                
                ; Execute test method
                Set tMethodStatus = $$$OK
                Try {
                    Set tMethodResult = $METHOD(tTestInstance, tMethodName)
                    ; Check if method returned a status
                    If $DATA(tMethodResult) && $SYSTEM.Status.IsError(tMethodResult) {
                        Set tMethodStatus = tMethodResult
                    }
                }
                Catch exMethod {
                    Set tMethodStatus = exMethod.AsStatus()
                    Do ..Context.AddMessage("Error in "_tMethodName_": "_exMethod.DisplayString())
                }
                
                ; Run OnAfterOneTest if it exists
                Try {
                    Do tTestInstance.OnAfterOneTest(tMethodName)
                }
                Catch {
                    ; Method might not exist, continue
                }
                
                ; End method execution
                Set tSC = ..Context.EndMethod(tMethodStatus)
            }
            
            ; Run OnAfterAllTests if it exists
            Try {
                Do tTestInstance.OnAfterAllTests()
            }
            Catch {
                ; Method might not exist, continue
            }
            
            ; End class execution
            Set tSC = ..Context.EndClass()
        }
    }
    Catch ex {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}

/// LogAssert interface for assertion macros - CRITICAL for compatibility
Method LogAssert(pSuccess As %Boolean, pAction As %String, pDescription As %String = "") As %Boolean
{
    ; Ensure Context is initialized
    If '$ISOBJECT(..Context) {
        Set ..Context = ##class(ExecuteMCP.TestRunner.Context).%New()
    }
    
    ; Add assertion to context
    Do ..Context.AddAssertion(pSuccess, pAction, pDescription)
    
    ; Return success value (important for macro behavior)
    Return pSuccess
}

/// LogMessage interface for test output
Method LogMessage(pMessage As %String) As %Boolean
{
    ; Ensure Context is initialized
    If '$ISOBJECT(..Context) {
        Set ..Context = ##class(ExecuteMCP.TestRunner.Context).%New()
    }
    
    ; Add message to context
    Do ..Context.AddMessage(pMessage)
    
    Return 1
}

/// Discover test packages (utility method)
ClassMethod DiscoverTestPackages(pNamespace As %String = "HSCUSTOM") As %String
{
    Try {
        ; Switch to target namespace if needed
        Set tOrigNS = $NAMESPACE
        If $NAMESPACE '= pNamespace {
            Set $NAMESPACE = pNamespace
        }
        
        ; Query for packages containing test classes
        Set tSQL = "SELECT DISTINCT $PIECE(Name, '.', 1, $LENGTH(Name, '.') - 1) AS Package "_
                  "FROM %Dictionary.CompiledClass "_
                  "WHERE Super [ '%UnitTest.TestCase' "_
                  "ORDER BY Package"
        
        Set tStatement = ##class(%SQL.Statement).%New()
        Set tSC = tStatement.%Prepare(tSQL)
        
        If $$$ISERR(tSC) {
            Throw ##class(%Exception.StatusException).CreateFromStatus(tSC)
        }
        
        Set tResultSet = tStatement.%Execute()
        Set tPackages = []
        
        While tResultSet.%Next() {
            Set tPackage = tResultSet.%Get("Package")
            If tPackage '= "" {
                Do tPackages.%Push(tPackage)
            }
        }
        
        ; Restore namespace
        If $NAMESPACE '= tOrigNS {
            Set $NAMESPACE = tOrigNS
        }
        
        Return "{""packages"":"_tPackages.%ToJSON()_"}"
    }
    Catch ex {
        ; Restore namespace on error
        If $DATA(tOrigNS) && ($NAMESPACE '= tOrigNS) {
            Set $NAMESPACE = tOrigNS
        }
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Quick test to verify Manager is working
ClassMethod TestManager() As %String
{
    Try {
        ; Test with ExecuteMCP.Test package
        Return ..RunPackageTests("ExecuteMCP.Test")
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

/// Run tests using the new Executor with test spec support
ClassMethod RunTestSpec(pSpec As %String, pNamespace As %String = "HSCUSTOM") As %String
{
    Try {
        ; CRITICAL FIX: Handle Native API parameter marshaling
        ; When called from Native API, parameters may arrive as object references
        ; Check if pSpec is an object reference (contains "@" character)
        If pSpec [ "@" {
            ; Parameter arrived as object reference (e.g., "5@%Net.Remote.Object")
            ; Cannot extract original string value from Native API object reference
            Return "{""error"":""Parameter marshaling error: Test spec arrived as object reference '"_pSpec_"'. This is a known Native API issue. Use execute_classmethod to call ExecuteMCP.TestRunner.Wrapper.RunTestDebug instead.""}"
        }
        
        ; Also check namespace parameter
        If pNamespace [ "@" {
            ; Namespace also corrupted, use default
            Set pNamespace = "HSCUSTOM"
        }
        
        ; Switch to target namespace if needed
        Set tOrigNS = $NAMESPACE
        If $NAMESPACE '= pNamespace {
            Set $NAMESPACE = pNamespace
        }
        
        ; Create manager and executor
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set tExecutor = ##class(ExecuteMCP.TestRunner.Executor).%New()
        Set tExecutor.Manager = tManager
        
        ; Initialize context if not already initialized
        If '$ISOBJECT(tManager.Context) {
            Set tManager.Context = ##class(ExecuteMCP.TestRunner.Context).%New()
        }
        Set tManager.Context.StartTime = $ZTIMESTAMP
        
        ; Execute using spec
        Set tStatus = tExecutor.ExecuteSpec(pSpec)
        
        If $$$ISERR(tStatus) {
            Return "{""error"":"""_$ZCONVERT($SYSTEM.Status.GetErrorText(tStatus), "O", "JS")_"""}"
        }
        
        ; Set end time
        Set tManager.Context.EndTime = $ZTIMESTAMP
        
        ; Get results
        Set tResults = tManager.Context.GetResults()
        
        ; Restore namespace
        If $NAMESPACE '= tOrigNS {
            Set $NAMESPACE = tOrigNS
        }
        
        Return tResults
    }
    Catch ex {
        ; Restore namespace on error
        If $DATA(tOrigNS) && ($NAMESPACE '= tOrigNS) {
            Set $NAMESPACE = tOrigNS
        }
        Return "{""error"":"""_$ZCONVERT(ex.DisplayString(), "O", "JS")_"""}"
    }
}

}
