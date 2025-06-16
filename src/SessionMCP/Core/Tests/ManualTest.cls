/// <h3>Manual Testing Script for SessionMCP</h3>
/// <p>Simple test script to validate functionality without %UnitTest framework.</p>
Class SessionMCP.Core.Tests.ManualTest Extends %RegisteredObject
{

/// <h3>Run All Tests</h3>
/// <p>Execute all validation tests manually.</p>
ClassMethod RunAllTests() As %String
{
    Write !, "=== SessionMCP Manual Testing ==="
    Write !, "Starting tests...", !
    
    Set tResults = {}
    Set tResults.totalTests = 0
    Set tResults.passedTests = 0
    Set tResults.failedTests = 0
    Set tResults.details = []
    
    // Test 1: Session Creation
    Do ..TestSessionCreation(.tResults)
    
    // Test 2: Session Validation  
    Do ..TestSessionValidation(.tResults)
    
    // Test 3: Command Execution
    Do ..TestCommandExecution(.tResults)
    
    // Test 4: Session Status
    Do ..TestSessionStatus(.tResults)
    
    // Test 5: Session Destruction
    Do ..TestSessionDestruction(.tResults)
    
    // Test 6: List Sessions
    Do ..TestListSessions(.tResults)
    
    // Summary
    Write !, "=== Test Summary ==="
    Write !, "Total Tests: ", tResults.totalTests
    Write !, "Passed: ", tResults.passedTests
    Write !, "Failed: ", tResults.failedTests
    
    If tResults.failedTests = 0 {
        Write !, "ALL TESTS PASSED! ✅"
    } Else {
        Write !, "Some tests failed ❌"
    }
    
    Quit tResults.%ToJSON()
}

/// <h3>Test Session Creation</h3>
ClassMethod TestSessionCreation(ByRef pResults)
{
    Set pResults.totalTests = pResults.totalTests + 1
    Write !, "Test 1: Session Creation..."
    
    Try {
        Set tResult = ##class(SessionMCP.Core.Session).CreateSession("USER", "testuser")
        Set tData = {}.%FromJSON(tResult)
        
        If tData.status = "success" && (tData.sessionId '= "") {
            Write " PASSED ✅"
            Set pResults.passedTests = pResults.passedTests + 1
            Set ^test.session.created = tData.sessionId
        } Else {
            Write " FAILED ❌ - Invalid response: ", tResult
            Set pResults.failedTests = pResults.failedTests + 1
        }
        
    } Catch (ex) {
        Write " FAILED ❌ - Exception: ", ex.DisplayString()
        Set pResults.failedTests = pResults.failedTests + 1
    }
}

/// <h3>Test Session Validation</h3>
ClassMethod TestSessionValidation(ByRef pResults)
{
    Set pResults.totalTests = pResults.totalTests + 1
    Write !, "Test 2: Session Validation..."
    
    Try {
        Set tSessionId = $Get(^test.session.created)
        If tSessionId = "" {
            Write " SKIPPED - No session to validate"
            Quit
        }
        
        Set tValid = ##class(SessionMCP.Core.Session).ValidateSession(tSessionId)
        Set tInvalid = ##class(SessionMCP.Core.Session).ValidateSession("invalid-session")
        
        If tValid && 'tInvalid {
            Write " PASSED ✅"
            Set pResults.passedTests = pResults.passedTests + 1
        } Else {
            Write " FAILED ❌ - Valid: ", tValid, " Invalid: ", tInvalid
            Set pResults.failedTests = pResults.failedTests + 1
        }
        
    } Catch (ex) {
        Write " FAILED ❌ - Exception: ", ex.DisplayString()
        Set pResults.failedTests = pResults.failedTests + 1
    }
}

/// <h3>Test Command Execution</h3>
ClassMethod TestCommandExecution(ByRef pResults)
{
    Set pResults.totalTests = pResults.totalTests + 1
    Write !, "Test 3: Command Execution..."
    
    Try {
        Set tSessionId = $Get(^test.session.created)
        If tSessionId = "" {
            Write " SKIPPED - No session for command execution"
            Quit
        }
        
        Set tResult = ##class(SessionMCP.Core.Session).ExecuteCommand(tSessionId, "SET tTestVar = 42")
        Set tData = {}.%FromJSON(tResult)
        
        If tData.status = "success" {
            Write " PASSED ✅"
            Set pResults.passedTests = pResults.passedTests + 1
        } Else {
            Write " FAILED ❌ - ", tData.errorMessage
            Set pResults.failedTests = pResults.failedTests + 1
        }
        
    } Catch (ex) {
        Write " FAILED ❌ - Exception: ", ex.DisplayString()
        Set pResults.failedTests = pResults.failedTests + 1
    }
}

/// <h3>Test Session Status</h3>
ClassMethod TestSessionStatus(ByRef pResults)
{
    Set pResults.totalTests = pResults.totalTests + 1
    Write !, "Test 4: Session Status..."
    
    Try {
        Set tSessionId = $Get(^test.session.created)
        If tSessionId = "" {
            Write " SKIPPED - No session for status check"
            Quit
        }
        
        Set tResult = ##class(SessionMCP.Core.Session).GetSessionStatus(tSessionId)
        Set tData = {}.%FromJSON(tResult)
        
        If tData.status = "success" && (tData.sessionId = tSessionId) {
            Write " PASSED ✅"
            Set pResults.passedTests = pResults.passedTests + 1
        } Else {
            Write " FAILED ❌ - Invalid status response"
            Set pResults.failedTests = pResults.failedTests + 1
        }
        
    } Catch (ex) {
        Write " FAILED ❌ - Exception: ", ex.DisplayString()
        Set pResults.failedTests = pResults.failedTests + 1
    }
}

/// <h3>Test Session Destruction</h3>
ClassMethod TestSessionDestruction(ByRef pResults)
{
    Set pResults.totalTests = pResults.totalTests + 1
    Write !, "Test 5: Session Destruction..."
    
    Try {
        Set tSessionId = $Get(^test.session.created)
        If tSessionId = "" {
            Write " SKIPPED - No session to destroy"
            Quit
        }
        
        Set tResult = ##class(SessionMCP.Core.Session).DestroySession(tSessionId)
        Set tData = {}.%FromJSON(tResult)
        
        If tData.status = "success" {
            // Verify session no longer exists
            Set tValid = ##class(SessionMCP.Core.Session).ValidateSession(tSessionId)
            If 'tValid {
                Write " PASSED ✅"
                Set pResults.passedTests = pResults.passedTests + 1
                Kill ^test.session.created
            } Else {
                Write " FAILED ❌ - Session still exists after destruction"
                Set pResults.failedTests = pResults.failedTests + 1
            }
        } Else {
            Write " FAILED ❌ - ", tData.errorMessage
            Set pResults.failedTests = pResults.failedTests + 1
        }
        
    } Catch (ex) {
        Write " FAILED ❌ - Exception: ", ex.DisplayString()
        Set pResults.failedTests = pResults.failedTests + 1
    }
}

/// <h3>Test List Sessions</h3>
ClassMethod TestListSessions(ByRef pResults)
{
    Set pResults.totalTests = pResults.totalTests + 1
    Write !, "Test 6: List Active Sessions..."
    
    Try {
        Set tResult = ##class(SessionMCP.Core.Session).ListActiveSessions()
        Set tData = {}.%FromJSON(tResult)
        
        If tData.status = "success" && $IsObject(tData.sessions) {
            Write " PASSED ✅"
            Set pResults.passedTests = pResults.passedTests + 1
        } Else {
            Write " FAILED ❌ - Invalid list response"
            Set pResults.failedTests = pResults.failedTests + 1
        }
        
    } Catch (ex) {
        Write " FAILED ❌ - Exception: ", ex.DisplayString()
        Set pResults.failedTests = pResults.failedTests + 1
    }
}

/// <h3>Cleanup</h3>
ClassMethod Cleanup()
{
    Write !, "Cleaning up test data..."
    Kill ^test.session.created
    Write " Done ✅"
}

}
