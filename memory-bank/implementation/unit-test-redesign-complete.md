# Unit Test MCP Redesign - Complete Architecture Plan

## Executive Summary
Complete redesign of MCP unit test functionality to properly support %UnitTest.TestCase with assertion macros while avoiding Manager process conflicts. Uses %SYSTEM.WorkMgr async pattern proven successful in InterSystems Atelier implementation.

## Problem Analysis

### Root Cause
- **Manager Singleton Conflict**: %UnitTest.Manager maintains process-level state that conflicts with MCP's async execution model
- **Assertion Macro Dependency**: Test assertion macros ($$$AssertEquals, etc.) require active Manager instance
- **Timeout Issues**: Synchronous Manager.RunTest() takes 70-165 seconds, exceeding MCP timeout limits
- **Process Isolation Required**: Tests must run in isolated worker processes to avoid Manager conflicts

### Failed Approaches
1. **Direct Manager.RunTest()**: Causes MCP timeouts (70+ seconds)
2. **%RegisteredObject Extension**: Assertion macros fail without Manager context
3. **Manual TestCase Methods**: Bypasses Manager but loses assertion functionality
4. **Current UnitTestAsync**: Improper async implementation causing deadlocks

## Solution Architecture

### Core Pattern: WorkMgr Async Execution
Based on successful pattern in src/%Api/Atelier/v8.cls:

```objectscript
Class ExecuteMCP.Core.UnitTestQueue Extends %RegisteredObject
{
    /// Queue test execution using WorkMgr for process isolation
    ClassMethod QueueTestExecution(pTestSpec As %String, pQualifiers As %String = "/recursive", pTestRoot As %String = "") As %String
    {
        Set tSC = $$$OK
        Try {
            // Validate and initialize ^UnitTestRoot
            Set tSC = ..ValidateTestRoot(pTestRoot)
            If $$$ISERR(tSC) {
                Return $$$FormatJSON({
                    "status": "error",
                    "message": ($SYSTEM.Status.GetErrorText(tSC))
                })
            }
            
            // Generate unique job ID
            Set tJobID = $SYSTEM.Encryption.GenCryptToken()
            
            // Store request in global for worker access
            Set ^ExecuteMCP.TestQueue(tJobID, "request", "testSpec") = pTestSpec
            Set ^ExecuteMCP.TestQueue(tJobID, "request", "qualifiers") = pQualifiers
            Set ^ExecuteMCP.TestQueue(tJobID, "status") = "queued"
            Set ^ExecuteMCP.TestQueue(tJobID, "timestamp") = $ZDATETIME($HOROLOG, 3)
            
            // Create WorkMgr with single worker
            Set tWQM = $SYSTEM.WorkMgr.%New("", 1)
            
            // Queue execution to worker process
            Set tSC = tWQM.Queue("##class(ExecuteMCP.Core.UnitTestQueue).ExecuteInWorker", tJobID)
            If $$$ISERR(tSC) {
                Kill ^ExecuteMCP.TestQueue(tJobID)
                Return $$$FormatJSON({
                    "status": "error",
                    "message": ($SYSTEM.Status.GetErrorText(tSC))
                })
            }
            
            // Detach to allow async execution
            Do tWQM.Detach(.tToken)
            
            Return $$$FormatJSON({
                "jobID": (tJobID),
                "status": "queued",
                "token": (tToken)
            })
        }
        Catch ex {
            Return $$$FormatJSON({
                "status": "error",
                "message": (ex.DisplayString())
            })
        }
    }
    
    /// Execute tests in isolated worker process
    ClassMethod ExecuteInWorker(pJobID As %String) As %Status
    {
        Set tSC = $$$OK
        Try {
            // Update status
            Set ^ExecuteMCP.TestQueue(pJobID, "status") = "running"
            Set ^ExecuteMCP.TestQueue(pJobID, "startTime") = $ZDATETIME($HOROLOG, 3)
            
            // Retrieve request parameters
            Set tTestSpec = $GET(^ExecuteMCP.TestQueue(pJobID, "request", "testSpec"))
            Set tQualifiers = $GET(^ExecuteMCP.TestQueue(pJobID, "request", "qualifiers"))
            
            // Execute tests using Manager in isolated process
            Set tSC = ##class(%UnitTest.Manager).RunTest(tTestSpec, tQualifiers)
            
            // Capture results from ^UnitTest.Result
            Set tResultID = ##class(%UnitTest.Manager).LatestResultId()
            Do ..CaptureResults(pJobID, tResultID)
            
            // Update completion status
            Set ^ExecuteMCP.TestQueue(pJobID, "status") = $SELECT($$$ISOK(tSC): "completed", 1: "failed")
            Set ^ExecuteMCP.TestQueue(pJobID, "endTime") = $ZDATETIME($HOROLOG, 3)
            Set ^ExecuteMCP.TestQueue(pJobID, "resultID") = tResultID
        }
        Catch ex {
            Set ^ExecuteMCP.TestQueue(pJobID, "status") = "error"
            Set ^ExecuteMCP.TestQueue(pJobID, "error") = ex.DisplayString()
        }
        
        Quit tSC
    }
    
    /// Poll for test execution results
    ClassMethod PollResults(pJobID As %String) As %String
    {
        Try {
            // Check if job exists
            If '$DATA(^ExecuteMCP.TestQueue(pJobID)) {
                Return $$$FormatJSON({
                    "status": "error",
                    "message": "Job ID not found"
                })
            }
            
            Set tStatus = $GET(^ExecuteMCP.TestQueue(pJobID, "status"), "unknown")
            
            // Return current status if still running
            If (tStatus = "queued") || (tStatus = "running") {
                Return $$$FormatJSON({
                    "jobID": (pJobID),
                    "status": (tStatus),
                    "startTime": ($GET(^ExecuteMCP.TestQueue(pJobID, "startTime"), ""))
                })
            }
            
            // Return complete results if finished
            If (tStatus = "completed") || (tStatus = "failed") {
                Set tResults = {}
                Set tResults.jobID = pJobID
                Set tResults.status = tStatus
                Set tResults.startTime = $GET(^ExecuteMCP.TestQueue(pJobID, "startTime"))
                Set tResults.endTime = $GET(^ExecuteMCP.TestQueue(pJobID, "endTime"))
                Set tResults.resultID = $GET(^ExecuteMCP.TestQueue(pJobID, "resultID"))
                
                // Include test results
                If $DATA(^ExecuteMCP.TestQueue(pJobID, "results")) {
                    Set tResults.summary = {
                        "passed": ($GET(^ExecuteMCP.TestQueue(pJobID, "results", "passed"), 0)),
                        "failed": ($GET(^ExecuteMCP.TestQueue(pJobID, "results", "failed"), 0)),
                        "errors": ($GET(^ExecuteMCP.TestQueue(pJobID, "results", "errors"), 0)),
                        "skipped": ($GET(^ExecuteMCP.TestQueue(pJobID, "results", "skipped"), 0))
                    }
                    
                    // Include failed test details
                    Set tFailures = []
                    Set tKey = ""
                    For {
                        Set tKey = $ORDER(^ExecuteMCP.TestQueue(pJobID, "results", "failures", tKey))
                        Quit:tKey=""
                        Do tFailures.%Push($GET(^ExecuteMCP.TestQueue(pJobID, "results", "failures", tKey)))
                    }
                    If tFailures.%Size() > 0 {
                        Set tResults.failures = tFailures
                    }
                }
                
                // Clean up job data after retrieval
                Kill ^ExecuteMCP.TestQueue(pJobID)
                
                Return tResults.%ToJSON()
            }
            
            // Handle error status
            If tStatus = "error" {
                Set tError = $GET(^ExecuteMCP.TestQueue(pJobID, "error"), "Unknown error")
                Kill ^ExecuteMCP.TestQueue(pJobID)
                Return $$$FormatJSON({
                    "status": "error",
                    "message": (tError)
                })
            }
        }
        Catch ex {
            Return $$$FormatJSON({
                "status": "error",
                "message": (ex.DisplayString())
            })
        }
    }
    
    /// Validate and initialize ^UnitTestRoot
    ClassMethod ValidateTestRoot(pTestRoot As %String = "") As %Status
    {
        Set tSC = $$$OK
        Try {
            // Check if ^UnitTestRoot is configured
            If '$DATA(^UnitTestRoot) {
                If pTestRoot '= "" {
                    // Use provided test root
                    Set ^UnitTestRoot = pTestRoot
                } Else {
                    // Set intelligent default based on OS
                    If $SYSTEM.Version.GetOS() = "Windows" {
                        Set ^UnitTestRoot = "C:\InterSystems\UnitTests\"
                    } Else {
                        Set ^UnitTestRoot = "/opt/intersystems/unittest/"
                    }
                }
                
                // Create directory if it doesn't exist
                If '##class(%File).DirectoryExists(^UnitTestRoot) {
                    Set tSC = ##class(%File).CreateDirectoryChain(^UnitTestRoot)
                    If $$$ISERR(tSC) {
                        Return $$$ERROR($$$GeneralError, "Failed to create test root directory: "_^UnitTestRoot)
                    }
                }
            }
            
            // Validate directory exists
            If '##class(%File).DirectoryExists(^UnitTestRoot) {
                Return $$$ERROR($$$GeneralError, "Test root directory does not exist: "_^UnitTestRoot)
            }
        }
        Catch ex {
            Set tSC = ex.AsStatus()
        }
        
        Quit tSC
    }
    
    /// Capture test results from ^UnitTest.Result
    ClassMethod CaptureResults(pJobID As %String, pResultID As %Integer) As %Status [ Private ]
    {
        Set tSC = $$$OK
        Try {
            // Get result summary
            Set tResult = ##class(%UnitTest.Result.TestInstance).%OpenId(pResultID)
            If $ISOBJECT(tResult) {
                Set ^ExecuteMCP.TestQueue(pJobID, "results", "passed") = 0
                Set ^ExecuteMCP.TestQueue(pJobID, "results", "failed") = 0
                Set ^ExecuteMCP.TestQueue(pJobID, "results", "errors") = 0
                Set ^ExecuteMCP.TestQueue(pJobID, "results", "skipped") = 0
                
                // Iterate through test suites
                Set tSuiteIdx = ""
                For {
                    Set tSuiteIdx = $ORDER(^UnitTest.Result(pResultID, "TestSuite", tSuiteIdx))
                    Quit:tSuiteIdx=""
                    
                    // Process test cases in suite
                    Set tCaseIdx = ""
                    For {
                        Set tCaseIdx = $ORDER(^UnitTest.Result(pResultID, "TestSuite", tSuiteIdx, "TestCase", tCaseIdx))
                        Quit:tCaseIdx=""
                        
                        // Process test methods
                        Set tMethodIdx = ""
                        For {
                            Set tMethodIdx = $ORDER(^UnitTest.Result(pResultID, "TestSuite", tSuiteIdx, "TestCase", tCaseIdx, "TestMethod", tMethodIdx))
                            Quit:tMethodIdx=""
                            
                            Set tMethodResult = $GET(^UnitTest.Result(pResultID, "TestSuite", tSuiteIdx, "TestCase", tCaseIdx, "TestMethod", tMethodIdx))
                            
                            // Update counters based on result
                            If $LISTGET(tMethodResult, 1) = 1 {
                                Set ^ExecuteMCP.TestQueue(pJobID, "results", "passed") = $INCREMENT(^ExecuteMCP.TestQueue(pJobID, "results", "passed"))
                            } ElseIf $LISTGET(tMethodResult, 1) = 0 {
                                Set ^ExecuteMCP.TestQueue(pJobID, "results", "failed") = $INCREMENT(^ExecuteMCP.TestQueue(pJobID, "results", "failed"))
                                
                                // Capture failure details
                                Set tFailureKey = $INCREMENT(^ExecuteMCP.TestQueue(pJobID, "results", "failures"))
                                Set ^ExecuteMCP.TestQueue(pJobID, "results", "failures", tFailureKey) = {
                                    "suite": tSuiteIdx,
                                    "case": tCaseIdx,
                                    "method": tMethodIdx,
                                    "message": ($LISTGET(tMethodResult, 2, ""))
                                }.%ToJSON()
                            }
                        }
                    }
                }
            }
        }
        Catch ex {
            Set tSC = ex.AsStatus()
        }
        
        Quit tSC
    }
}
```

## Python MCP Integration

### Updated iris_execute_mcp.py Tools

```python
@server.tool()
async def queue_unit_tests(
    test_spec: str,
    qualifiers: str = "/recursive",
    test_root_path: str = "",
    namespace: str = "HSCUSTOM"
) -> str:
    """
    Queue unit test execution using async WorkMgr pattern.
    Returns immediately with job ID for polling.
    """
    try:
        result_json = call_iris_sync(
            class_name="ExecuteMCP.Core.UnitTestQueue",
            method_name="QueueTestExecution",
            args=[test_spec, qualifiers, test_root_path],
            namespace=namespace
        )
        return result_json
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

@server.tool()
async def poll_unit_tests(
    job_id: str,
    namespace: str = "HSCUSTOM"
) -> str:
    """
    Poll for unit test results. Returns status if running,
    or complete results if finished.
    """
    try:
        result_json = call_iris_sync(
            class_name="ExecuteMCP.Core.UnitTestQueue",
            method_name="PollResults",
            args=[job_id],
            namespace=namespace
        )
        return result_json
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })
```

## Implementation Steps

### Phase 1: Clean Up
1. Remove ExecuteMCP.Core.UnitTest class (broken synchronous implementation)
2. Remove ExecuteMCP.Core.UnitTestAsync class (incorrect async attempt)
3. Remove old unit test Python tools from iris_execute_mcp.py
4. Clean up test scripts

### Phase 2: Implement Core
1. Create ExecuteMCP.Core.UnitTestQueue class with WorkMgr pattern
2. Implement ValidateTestRoot for proper ^UnitTestRoot handling
3. Add QueueTestExecution method with process isolation
4. Implement ExecuteInWorker for Manager execution
5. Create PollResults for non-blocking result retrieval
6. Add CaptureResults to extract test outcomes

### Phase 3: Python Integration
1. Update iris_execute_mcp.py with queue_unit_tests tool
2. Add poll_unit_tests tool for result retrieval
3. Remove old synchronous unit test tools
4. Update tool documentation

### Phase 4: Testing
1. Test with ExecuteMCP.Test.SampleUnitTest
2. Verify assertion macros work correctly
3. Confirm no timeout issues
4. Validate result capture accuracy
5. Test ^UnitTestRoot initialization logic

## Key Design Decisions

### 1. WorkMgr Process Isolation
- **Rationale**: Avoids Manager singleton conflicts
- **Pattern**: Proven successful in Atelier implementation
- **Benefits**: Clean process state for each test run

### 2. Global Storage for Job State
- **Location**: ^ExecuteMCP.TestQueue
- **Structure**: Hierarchical with job ID as primary key
- **Cleanup**: Automatic after result retrieval

### 3. ^UnitTestRoot Validation
- **Smart Defaults**: OS-specific default directories
- **Auto-Creation**: Creates directory if missing
- **Override Option**: Accepts custom path parameter

### 4. Queue/Poll Pattern
- **Queue**: Returns immediately with job ID
- **Poll**: Non-blocking status checks
- **Completion**: Returns full results and cleans up

## Expected Outcomes

### Performance
- **Queue Response**: < 100ms
- **Poll Response**: < 50ms
- **Test Execution**: Normal Manager timing (no MCP timeout)

### Reliability
- **Process Isolation**: No Manager conflicts
- **Assertion Support**: Full macro functionality
- **Error Recovery**: Comprehensive error handling

### Compatibility
- **%UnitTest.TestCase**: Full support
- **Manager Features**: All features available
- **Result Portal**: Compatible with web UI

## Migration Path

### For Existing Tests
1. No changes needed to test classes
2. Continue extending %UnitTest.TestCase
3. All assertion macros work as expected

### For MCP Usage
1. Replace run_unit_tests with queue_unit_tests
2. Add polling loop for results
3. Handle async job lifecycle

## Success Criteria

1. ✅ Tests execute without MCP timeouts
2. ✅ Assertion macros function correctly
3. ✅ Results captured accurately
4. ✅ ^UnitTestRoot properly managed
5. ✅ Process isolation prevents conflicts
6. ✅ Compatible with existing test classes

## References

- src/%Api/Atelier/v8.cls - WorkMgr async pattern
- src/%UnitTest/Manager.cls - Framework requirements
- Research: ^UnitTestRoot configuration requirements
- Analysis: Manager singleton process conflicts
