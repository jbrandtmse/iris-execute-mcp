/// <h3>Unit Tests for SessionMCP.Core.Session</h3>
/// <p>Test basic session management functionality for MVP validation.</p>
Class SessionMCP.Core.Tests.SessionTest Extends %UnitTest.TestCase
{

/// <h3>Test Session Creation</h3>
/// <p>Verify that new sessions can be created with valid JSON response.</p>
Method TestSessionCreation()
{
    // Test basic session creation
    Set tResult = ##class(SessionMCP.Core.Session).CreateSession("USER")
    Set tData = {}.%FromJSON(tResult)
    
    // Verify success
    Do $$$AssertEquals(tData.status, "success", "Session creation should succeed")
    Do $$$AssertNotEquals(tData.sessionId, "", "Session ID should not be empty")
    Do $$$AssertEquals(tData.namespace, "USER", "Namespace should match")
    
    // Test with custom namespace
    Set tResult = ##class(SessionMCP.Core.Session).CreateSession("SAMPLES")
    Set tData = {}.%FromJSON(tResult)
    Do $$$AssertEquals(tData.status, "success", "Custom namespace session should succeed")
    Do $$$AssertEquals(tData.namespace, "SAMPLES", "Custom namespace should match")
}

/// <h3>Test Session Validation</h3>
/// <p>Verify session validation logic works correctly.</p>
Method TestSessionValidation()
{
    // Create a test session
    Set tResult = ##class(SessionMCP.Core.Session).CreateSession("USER")
    Set tData = {}.%FromJSON(tResult)
    Set tSessionId = tData.sessionId
    
    // Test valid session
    Set tValid = ##class(SessionMCP.Core.Session).ValidateSession(tSessionId)
    Do $$$AssertTrue(tValid, "Valid session should pass validation")
    
    // Test invalid session
    Set tValid = ##class(SessionMCP.Core.Session).ValidateSession("invalid-session-id")
    Do $$$AssertTrue('tValid, "Invalid session should fail validation")
    
    // Test empty session ID
    Set tValid = ##class(SessionMCP.Core.Session).ValidateSession("")
    Do $$$AssertTrue('tValid, "Empty session ID should fail validation")
}

/// <h3>Test Simple Command Execution</h3>
/// <p>Verify basic command execution functionality.</p>
Method TestCommandExecution()
{
    // Create a test session
    Set tResult = ##class(SessionMCP.Core.Session).CreateSession("USER")
    Set tData = {}.%FromJSON(tResult)
    Set tSessionId = tData.sessionId
    
    // Test simple command execution
    Set tResult = ##class(SessionMCP.Core.Session).ExecuteCommand(tSessionId, "SET tTest = 2+2")
    Set tData = {}.%FromJSON(tResult)
    
    // Verify success
    Do $$$AssertEquals(tData.status, "success", "Command execution should succeed")
    Do $$$AssertEquals(tData.sessionId, tSessionId, "Session ID should match")
    Do $$$AssertNotEquals(tData.executionTimeMs, "", "Execution time should be recorded")
    
    // Test command with invalid session
    Set tResult = ##class(SessionMCP.Core.Session).ExecuteCommand("invalid-session", "SET tTest = 1")
    Set tData = {}.%FromJSON(tResult)
    Do $$$AssertEquals(tData.status, "error", "Invalid session should return error")
}

/// <h3>Test Session Status Retrieval</h3>
/// <p>Verify session status information can be retrieved.</p>
Method TestSessionStatus()
{
    // Create a test session
    Set tResult = ##class(SessionMCP.Core.Session).CreateSession("USER", "testuser")
    Set tData = {}.%FromJSON(tResult)
    Set tSessionId = tData.sessionId
    
    // Get session status
    Set tResult = ##class(SessionMCP.Core.Session).GetSessionStatus(tSessionId)
    Set tData = {}.%FromJSON(tResult)
    
    // Verify status information
    Do $$$AssertEquals(tData.status, "success", "Status retrieval should succeed")
    Do $$$AssertEquals(tData.sessionId, tSessionId, "Session ID should match")
    Do $$$AssertEquals(tData.namespace, "USER", "Namespace should match")
    Do $$$AssertEquals(tData.user, "testuser", "User should match")
    Do $$$AssertNotEquals(tData.created, "", "Created timestamp should be present")
    
    // Test invalid session status
    Set tResult = ##class(SessionMCP.Core.Session).GetSessionStatus("invalid-session")
    Set tData = {}.%FromJSON(tResult)
    Do $$$AssertEquals(tData.status, "error", "Invalid session status should return error")
}

/// <h3>Test Session Destruction</h3>
/// <p>Verify sessions can be properly destroyed.</p>
Method TestSessionDestruction()
{
    // Create a test session
    Set tResult = ##class(SessionMCP.Core.Session).CreateSession("USER")
    Set tData = {}.%FromJSON(tResult)
    Set tSessionId = tData.sessionId
    
    // Verify session exists
    Set tValid = ##class(SessionMCP.Core.Session).ValidateSession(tSessionId)
    Do $$$AssertTrue(tValid, "Session should exist before destruction")
    
    // Destroy session
    Set tResult = ##class(SessionMCP.Core.Session).DestroySession(tSessionId)
    Set tData = {}.%FromJSON(tResult)
    Do $$$AssertEquals(tData.status, "success", "Session destruction should succeed")
    
    // Verify session no longer exists
    Set tValid = ##class(SessionMCP.Core.Session).ValidateSession(tSessionId)
    Do $$$AssertTrue('tValid, "Session should not exist after destruction")
    
    // Test destroying non-existent session
    Set tResult = ##class(SessionMCP.Core.Session).DestroySession("invalid-session")
    Set tData = {}.%FromJSON(tResult)
    Do $$$AssertEquals(tData.status, "error", "Destroying non-existent session should return error")
}

/// <h3>Test List Active Sessions</h3>
/// <p>Verify active session listing functionality.</p>
Method TestListActiveSessions()
{
    // Clean up any existing test sessions first
    Do ..CleanupTestSessions()
    
    // Create multiple test sessions
    Set tSession1 = ##class(SessionMCP.Core.Session).CreateSession("USER", "user1")
    Set tData1 = {}.%FromJSON(tSession1)
    Set tSessionId1 = tData1.sessionId
    
    Set tSession2 = ##class(SessionMCP.Core.Session).CreateSession("SAMPLES", "user2")
    Set tData2 = {}.%FromJSON(tSession2)
    Set tSessionId2 = tData2.sessionId
    
    // List active sessions
    Set tResult = ##class(SessionMCP.Core.Session).ListActiveSessions()
    Set tData = {}.%FromJSON(tResult)
    
    // Verify results
    Do $$$AssertEquals(tData.status, "success", "List sessions should succeed")
    Do $$$AssertTrue(tData.count >= 2, "Should have at least 2 active sessions")
    
    // Clean up test sessions
    Do ##class(SessionMCP.Core.Session).DestroySession(tSessionId1)
    Do ##class(SessionMCP.Core.Session).DestroySession(tSessionId2)
}

/// <h3>Test Error Handling</h3>
/// <p>Verify error handling for invalid commands.</p>
Method TestErrorHandling()
{
    // Create a test session
    Set tResult = ##class(SessionMCP.Core.Session).CreateSession("USER")
    Set tData = {}.%FromJSON(tResult)
    Set tSessionId = tData.sessionId
    
    // Test command with syntax error
    Set tResult = ##class(SessionMCP.Core.Session).ExecuteCommand(tSessionId, "INVALID SYNTAX HERE")
    Set tData = {}.%FromJSON(tResult)
    
    // Should return error but not crash
    Do $$$AssertEquals(tData.status, "error", "Invalid command should return error")
    Do $$$AssertNotEquals(tData.errorMessage, "", "Error message should be provided")
    
    // Verify session is still valid after error
    Set tValid = ##class(SessionMCP.Core.Session).ValidateSession(tSessionId)
    Do $$$AssertTrue(tValid, "Session should remain valid after command error")
    
    // Clean up
    Do ##class(SessionMCP.Core.Session).DestroySession(tSessionId)
}

/// <h3>Cleanup Test Sessions</h3>
/// <p>Utility method to clean up any leftover test sessions.</p>
Method CleanupTestSessions()
{
    // Get list of all sessions
    Set tResult = ##class(SessionMCP.Core.Session).ListActiveSessions()
    Set tData = {}.%FromJSON(tResult)
    
    If tData.status = "success" {
        Set tSessions = tData.sessions
        For tIndex = 0:1:(tSessions.%Size()-1) {
            Set tSession = tSessions.%Get(tIndex)
            Set tSessionId = tSession.sessionId
            
            // Only clean up test sessions (those with test users)
            Set tUser = $Get(tSession.user, "")
            If (tUser [ "test") || (tUser [ "user") {
                Do ##class(SessionMCP.Core.Session).DestroySession(tSessionId)
            }
        }
    }
}

/// <h3>Setup Method</h3>
/// <p>Called before each test method.</p>
Method OnBeforeAllTests() As %Status
{
    // Clean up any existing test data
    Do ..CleanupTestSessions()
    Quit $$$OK
}

/// <h3>Teardown Method</h3>
/// <p>Called after all tests complete.</p>
Method OnAfterAllTests() As %Status
{
    // Clean up test data
    Do ..CleanupTestSessions()
    Quit $$$OK
}

}
