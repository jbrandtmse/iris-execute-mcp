/// *** DEPRECATED CLASS - DO NOT USE ***
/// This class is deprecated and will be removed in a future version.
/// Please use the execute_unit_tests MCP tool which uses the custom TestRunner
/// (ExecuteMCP.TestRunner) for better VS Code integration and reliability.
/// 
/// Legacy Unit Test Queue Implementation using WorkMgr Pattern
/// Originally provided async unit test execution with process isolation
/// but has been superseded by the custom TestRunner approach.
Class ExecuteMCP.Core.UnitTestQueue Extends %RegisteredObject [ Deprecated ]
{

/// Queue test execution using WorkMgr for process isolation
/// Returns JSON with job ID for polling
/// DEPRECATED: Use execute_unit_tests MCP tool instead
ClassMethod QueueTestExecution(pTestSpec As %String, pQualifiers As %String = "/recursive", pTestRoot As %String = "", pNamespace As %String = "HSCUSTOM") As %String [ Deprecated ]
{
    Set tSC = $$$OK
    Try {
        // Validate and initialize ^UnitTestRoot
        Set tSC = ..ValidateTestRoot(pTestRoot)
        If $$$ISERR(tSC) {
            Return ..FormatJSON("error", $SYSTEM.Status.GetErrorText(tSC))
        }
        
        // Generate unique job ID
        Set tJobID = $SYSTEM.Encryption.GenCryptToken()
        
        // Store request in global for worker access
        Set ^ExecuteMCP.TestQueue(tJobID, "request", "testSpec") = pTestSpec
        Set ^ExecuteMCP.TestQueue(tJobID, "request", "qualifiers") = pQualifiers
        Set ^ExecuteMCP.TestQueue(tJobID, "request", "namespace") = pNamespace
        Set ^ExecuteMCP.TestQueue(tJobID, "status") = "queued"
        Set ^ExecuteMCP.TestQueue(tJobID, "timestamp") = $ZDATETIME($HOROLOG, 3)
        
        // Create WorkMgr with single worker
        Set tWQM = $SYSTEM.WorkMgr.%New("", 1)
        
        // Queue execution to worker process
        Set tSC = tWQM.Queue("##class(ExecuteMCP.Core.UnitTestQueue).ExecuteInWorker", tJobID)
        If $$$ISERR(tSC) {
            Kill ^ExecuteMCP.TestQueue(tJobID)
            Return ..FormatJSON("error", $SYSTEM.Status.GetErrorText(tSC))
        }
        
        // Detach to allow async execution
        Do tWQM.Detach(.tToken)
        
        // Return job info
        Set tResult = {}
        Set tResult.jobID = tJobID
        Set tResult.status = "queued"
        Set tResult.token = tToken
        Return tResult.%ToJSON()
    }
    Catch ex {
        Return ..FormatJSON("error", ex.DisplayString())
    }
}

/// Execute tests in isolated worker process
/// DEPRECATED: Internal method for legacy WorkMgr pattern
ClassMethod ExecuteInWorker(pJobID As %String) As %Status [ Deprecated, Private ]
{
    Set tSC = $$$OK
    Try {
        // Update status
        Set ^ExecuteMCP.TestQueue(pJobID, "status") = "running"
        Set ^ExecuteMCP.TestQueue(pJobID, "startTime") = $ZDATETIME($HOROLOG, 3)
        
        // Retrieve request parameters
        Set tTestSpec = $GET(^ExecuteMCP.TestQueue(pJobID, "request", "testSpec"))
        Set tQualifiers = $GET(^ExecuteMCP.TestQueue(pJobID, "request", "qualifiers"))
        Set tNamespace = $GET(^ExecuteMCP.TestQueue(pJobID, "request", "namespace"), "HSCUSTOM")
        
        // Switch to target namespace if needed
        Set tOriginalNamespace = $NAMESPACE
        If (tNamespace '= $NAMESPACE) {
            Set $NAMESPACE = tNamespace
        }
        
        // Fix test spec format for VS Code workflow
        // The leading ":" indicates root test suite (classes already loaded)
        // DISABLED: Auto-prefix may interfere with discovery
        // If tTestSpec '[ ":" {
        //     Set tTestSpec = ":"_tTestSpec
        // }
        
        // Build smart qualifier defaults for VS Code workflow
        If tQualifiers = "" {
            // Default qualifiers optimized for VS Code workflow
            Set tQualifiers = "/noload/nodelete/recursive"
        } Else {
            // Ensure essential qualifiers are included
            If tQualifiers '[ "/noload" {
                Set tQualifiers = tQualifiers_"/noload"
            }
            If tQualifiers '[ "/nodelete" {
                Set tQualifiers = tQualifiers_"/nodelete"
            }
        }
        
        // Get the current highest result ID before running tests
        Set tBeforeID = $ORDER(^UnitTest.Result(""), -1)
        
        // Execute tests using Manager in isolated process
        Set tSC = ##class(%UnitTest.Manager).RunTest(tTestSpec, tQualifiers)
        
        // Get the new result ID (should be the one just created)
        Set tResultID = $ORDER(^UnitTest.Result(""), -1)
        
        // Only capture if a new result was created
        If (tResultID '= "") && (tResultID '= tBeforeID) {
            Do ..CaptureResults(pJobID, tResultID)
            Set ^ExecuteMCP.TestQueue(pJobID, "resultID") = tResultID
        } Else {
            // No new result created - tests might not have been found
            Set ^ExecuteMCP.TestQueue(pJobID, "debug", "noNewResult") = "No new test result created"
            Set ^ExecuteMCP.TestQueue(pJobID, "results", "passed") = 0
            Set ^ExecuteMCP.TestQueue(pJobID, "results", "failed") = 0
            Set ^ExecuteMCP.TestQueue(pJobID, "results", "errors") = 0
            Set ^ExecuteMCP.TestQueue(pJobID, "results", "skipped") = 0
        }
        
        // Restore original namespace
        Set $NAMESPACE = tOriginalNamespace
        
        // Update completion status
        Set ^ExecuteMCP.TestQueue(pJobID, "status") = $SELECT($$$ISOK(tSC): "completed", 1: "failed")
        Set ^ExecuteMCP.TestQueue(pJobID, "endTime") = $ZDATETIME($HOROLOG, 3)
    }
    Catch ex {
        Set ^ExecuteMCP.TestQueue(pJobID, "status") = "error"
        Set ^ExecuteMCP.TestQueue(pJobID, "error") = ex.DisplayString()
        // Try to restore namespace on error
        Try {
            Set $NAMESPACE = tOriginalNamespace
        } Catch {}
    }
    
    Quit tSC
}

/// Poll for test execution results
/// DEPRECATED: Use execute_unit_tests MCP tool instead
ClassMethod PollResults(pJobID As %String, pNamespace As %String = "HSCUSTOM") As %String [ Deprecated ]
{
    Try {
        // Check if job exists
        If '$DATA(^ExecuteMCP.TestQueue(pJobID)) {
            Return ..FormatJSON("error", "Job ID not found")
        }
        
        Set tStatus = $GET(^ExecuteMCP.TestQueue(pJobID, "status"), "unknown")
        
        // Return current status if still running
        If (tStatus = "queued") || (tStatus = "running") {
            Set tResult = {}
            Set tResult.jobID = pJobID
            Set tResult.testStatus = tStatus
            Set tStartTime = $GET(^ExecuteMCP.TestQueue(pJobID, "startTime"), "")
            If tStartTime '= "" {
                Set tResult.startTime = tStartTime
            }
            Return tResult.%ToJSON()
        }
        
        // Return complete results if finished
        If (tStatus = "completed") || (tStatus = "failed") {
            Set tResults = {}
            Set tResults.jobID = pJobID
            Set tResults.testStatus = tStatus
            Set tResults.startTime = $GET(^ExecuteMCP.TestQueue(pJobID, "startTime"))
            Set tResults.endTime = $GET(^ExecuteMCP.TestQueue(pJobID, "endTime"))
            Set tResults.resultID = $GET(^ExecuteMCP.TestQueue(pJobID, "resultID"))
            
            // Include test results
            If $DATA(^ExecuteMCP.TestQueue(pJobID, "results")) {
                Set tResults.totalTests = $GET(^ExecuteMCP.TestQueue(pJobID, "results", "totalTests"), 0)
                Set tResults.passed = $GET(^ExecuteMCP.TestQueue(pJobID, "results", "passed"), 0)
                Set tResults.failed = $GET(^ExecuteMCP.TestQueue(pJobID, "results", "failed"), 0)
                Set tResults.errors = $GET(^ExecuteMCP.TestQueue(pJobID, "results", "errors"), 0)
                Set tResults.skipped = $GET(^ExecuteMCP.TestQueue(pJobID, "results", "skipped"), 0)
                
                // Include test suite details
                If $DATA(^ExecuteMCP.TestQueue(pJobID, "results", "suites")) {
                    Set tSuites = []
                    Set tSuiteKey = ""
                    For {
                        Set tSuiteKey = $ORDER(^ExecuteMCP.TestQueue(pJobID, "results", "suites", tSuiteKey))
                        Quit:tSuiteKey=""
                        Set tSuiteInfo = $GET(^ExecuteMCP.TestQueue(pJobID, "results", "suites", tSuiteKey))
                        Do tSuites.%Push(tSuiteInfo)
                    }
                    If tSuites.%Size() > 0 {
                        Set tResults.suites = tSuites
                    }
                }
                
                // Include failed test details
                Set tFailures = []
                Set tKey = ""
                For {
                    Set tKey = $ORDER(^ExecuteMCP.TestQueue(pJobID, "results", "failures", tKey))
                    Quit:tKey=""
                    Set tFailureJSON = $GET(^ExecuteMCP.TestQueue(pJobID, "results", "failures", tKey))
                    If tFailureJSON '= "" {
                        // Parse and add failure
                        Set tFailure = {}.%FromJSON(tFailureJSON)
                        Do tFailures.%Push(tFailure)
                    }
                }
                If tFailures.%Size() > 0 {
                    Set tResults.failures = tFailures
                }
            }
            
            // Include debug info if present
            If $DATA(^ExecuteMCP.TestQueue(pJobID, "debug")) {
                Set tDebug = {}
                If $DATA(^ExecuteMCP.TestQueue(pJobID, "debug", "noResults")) {
                    Set tDebug.noResults = $GET(^ExecuteMCP.TestQueue(pJobID, "debug", "noResults"))
                }
                If $DATA(^ExecuteMCP.TestQueue(pJobID, "debug", "suiteCount")) {
                    Set tDebug.suiteCount = $GET(^ExecuteMCP.TestQueue(pJobID, "debug", "suiteCount"))
                }
                If $DATA(^ExecuteMCP.TestQueue(pJobID, "debug", "caseCount")) {
                    Set tDebug.caseCount = $GET(^ExecuteMCP.TestQueue(pJobID, "debug", "caseCount"))
                }
                Set tResults.debug = tDebug
            }
            
            // Clean up job data after retrieval
            Kill ^ExecuteMCP.TestQueue(pJobID)
            
            Return tResults.%ToJSON()
        }
        
        // Handle error status
        If tStatus = "error" {
            Set tError = $GET(^ExecuteMCP.TestQueue(pJobID, "error"), "Unknown error")
            Kill ^ExecuteMCP.TestQueue(pJobID)
            Return ..FormatJSON("error", tError)
        }
        
        // Unknown status
        Return ..FormatJSON("error", "Unknown job status: "_tStatus)
    }
    Catch ex {
        Return ..FormatJSON("error", ex.DisplayString())
    }
}

/// Validate ^UnitTestRoot exists (VS Code workflow - classes already loaded)
/// DEPRECATED: Internal method for legacy WorkMgr pattern
ClassMethod ValidateTestRoot(pTestRoot As %String = "") As %Status [ Deprecated, Private ]
{
    Set tSC = $$$OK
    Try {
        // For VS Code workflow, we just need ^UnitTestRoot to exist
        // The actual value doesn't matter since classes are already loaded
        If '$DATA(^UnitTestRoot) {
            If pTestRoot '= "" {
                // Use provided test root if given
                Set ^UnitTestRoot = pTestRoot
            } Else {
                // Set a default value for VS Code workflow
                Set ^UnitTestRoot = "C:\temp\"
            }
        }
        // That's it - no directory validation needed for VS Code workflow
    }
    Catch ex {
        Set tSC = ex.AsStatus()
    }
    
    Quit tSC
}

/// Capture test results from ^UnitTest.Result
/// DEPRECATED: Internal method for legacy WorkMgr pattern
ClassMethod CaptureResults(pJobID As %String, pResultID As %Integer) As %Status [ Deprecated, Private ]
{
    Set tSC = $$$OK
    Try {
        // Initialize counters
        Set tPassed = 0
        Set tFailed = 0
        Set tErrors = 0
        Set tSkipped = 0
        Set tTotalTests = 0
        Set tSuiteCount = 0
        Set tCaseCount = 0
        
        // The structure is: ^UnitTest.Result(ID, suiteName, caseName, methodName)
        // And the test status is in: ^UnitTest.Result(ID, suiteName, caseName, methodName, "Status")
        
        // Iterate through test suites
        Set tSuiteName = ""
        For {
            Set tSuiteName = $ORDER(^UnitTest.Result(pResultID, tSuiteName))
            Quit:tSuiteName=""
            
            // Skip non-suite nodes (like timestamps or metadata starting with $CHAR(0))
            Continue:$EXTRACT(tSuiteName,1,1)=$CHAR(0)
            
            Set tSuiteCount = tSuiteCount + 1
            Set tSuiteTestCount = 0
            Set tSuitePassed = 0
            Set tSuiteFailed = 0
            
            // Process test cases in suite
            Set tCaseName = ""
            For {
                Set tCaseName = $ORDER(^UnitTest.Result(pResultID, tSuiteName, tCaseName))
                Quit:tCaseName=""
                
                Set tCaseCount = tCaseCount + 1
                
                // Process test methods
                Set tMethodName = ""
                For {
                    Set tMethodName = $ORDER(^UnitTest.Result(pResultID, tSuiteName, tCaseName, tMethodName))
                    Quit:tMethodName=""
                    
                    // Skip metadata nodes
                    Continue:$EXTRACT(tMethodName,1,1)=$CHAR(0)
                    
                    // Check if this is actually a test method result
                    If $DATA(^UnitTest.Result(pResultID, tSuiteName, tCaseName, tMethodName)) {
                        Set tTotalTests = tTotalTests + 1
                        Set tSuiteTestCount = tSuiteTestCount + 1
                        
                        // Get the test status
                        Set tTestStatus = $GET(^UnitTest.Result(pResultID, tSuiteName, tCaseName, tMethodName, "Status"))
                        
                        // Check test status and categorize
                        If tTestStatus = 1 {
                            // Test passed
                            Set tPassed = tPassed + 1
                            Set tSuitePassed = tSuitePassed + 1
                        } ElseIf tTestStatus = 0 {
                            // Test failed
                            Set tFailed = tFailed + 1
                            Set tSuiteFailed = tSuiteFailed + 1
                            
                            // Capture failure details
                            Set tFailureCount = $INCREMENT(^ExecuteMCP.TestQueue(pJobID, "results", "failureCount"))
                            Set tFailure = {}
                            Set tFailure.suite = tSuiteName
                            Set tFailure.case = tCaseName
                            Set tFailure.method = tMethodName
                            Set tFailure.action = $GET(^UnitTest.Result(pResultID, tSuiteName, tCaseName, tMethodName, "Action"))
                            Set tFailure.description = $GET(^UnitTest.Result(pResultID, tSuiteName, tCaseName, tMethodName, "Description"))
                            Set ^ExecuteMCP.TestQueue(pJobID, "results", "failures", tFailureCount) = tFailure.%ToJSON()
                        } ElseIf tTestStatus = 2 {
                            // Test had an error
                            Set tErrors = tErrors + 1
                        } ElseIf tTestStatus = 3 {
                            // Test was skipped
                            Set tSkipped = tSkipped + 1
                        } Else {
                            // Unknown status - count as failed
                            Set tFailed = tFailed + 1
                            Set tSuiteFailed = tSuiteFailed + 1
                        }
                    }
                }
            }
            
            // Store suite summary
            If tSuiteTestCount > 0 {
                Set tSuiteInfo = tSuiteName_": "_tSuiteTestCount_" tests ("_tSuitePassed_" passed, "_tSuiteFailed_" failed)"
                Set ^ExecuteMCP.TestQueue(pJobID, "results", "suites", tSuiteCount) = tSuiteInfo
            }
        }
        
        // Store final results
        Set ^ExecuteMCP.TestQueue(pJobID, "results", "totalTests") = tTotalTests
        Set ^ExecuteMCP.TestQueue(pJobID, "results", "passed") = tPassed
        Set ^ExecuteMCP.TestQueue(pJobID, "results", "failed") = tFailed
        Set ^ExecuteMCP.TestQueue(pJobID, "results", "errors") = tErrors
        Set ^ExecuteMCP.TestQueue(pJobID, "results", "skipped") = tSkipped
        
        // Store debug info
        Set ^ExecuteMCP.TestQueue(pJobID, "debug", "suiteCount") = tSuiteCount
        Set ^ExecuteMCP.TestQueue(pJobID, "debug", "caseCount") = tCaseCount
        
        // If we found no results at all, log it
        If tTotalTests = 0 {
            Set ^ExecuteMCP.TestQueue(pJobID, "debug", "noResults") = "No test methods were discovered or executed"
            Set ^ExecuteMCP.TestQueue(pJobID, "debug", "resultID") = pResultID
        }
    }
    Catch ex {
        Set tSC = ex.AsStatus()
        Set ^ExecuteMCP.TestQueue(pJobID, "debug", "captureError") = ex.DisplayString()
    }
    
    Quit tSC
}

/// Helper method to format JSON error responses
/// DEPRECATED: Internal method for legacy WorkMgr pattern
ClassMethod FormatJSON(pStatus As %String, pMessage As %String) As %String [ Deprecated, Private ]
{
    Set tResult = {}
    Set tResult.status = pStatus
    Set tResult.message = pMessage
    Return tResult.%ToJSON()
}

}
