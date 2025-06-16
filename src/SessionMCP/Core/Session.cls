/// <h3>IRIS Terminal Session Manager for MCP</h3>
/// <p>Manages persistent terminal sessions with I/O redirection and state management.</p>
/// <p>Designed for Native API invocation from Python MCP clients.</p>
/// <p>MVP Implementation - Basic session management and command execution.</p>
Class SessionMCP.Core.Session Extends %RegisteredObject
{

/// <b>Command execution timeout in seconds</b>
Parameter DEFAULTTIMEOUT = 30;

/// <b>Maximum output size in bytes</b>
Parameter MAXOUTPUTSIZE = 65536;

/// <h3>Create New Session</h3>
/// <p>Class method for Native API invocation to create new session.</p>
/// <p>Returns JSON with session ID and namespace information.</p>
ClassMethod CreateSession(pNamespace As %String = "USER", pUserId As %String = "") As %String
{
    Set tSC = $$$OK
    Set tResult = {}
    
    Try {
        // Generate unique session ID
        Set tSessionId = $System.Util.CreateGUID()
        
        // Store session metadata in globals
        Set ^SessionMCP.State(tSessionId, "created") = $HOROLOG
        Set ^SessionMCP.State(tSessionId, "lastAccess") = $HOROLOG
        Set ^SessionMCP.State(tSessionId, "namespace") = pNamespace
        Set ^SessionMCP.State(tSessionId, "user") = pUserId
        Set ^SessionMCP.State(tSessionId, "status") = "ACTIVE"
        
        // Build success response
        Set tResult.status = "success"
        Set tResult.sessionId = tSessionId
        Set tResult.namespace = pNamespace
        Set tResult.created = $ZDateTime($HOROLOG, 3)
        
    } Catch (ex) {
        Set tResult.status = "error"
        Set tResult.errorMessage = ex.DisplayString()
    }
    
    Quit tResult.%ToJSON()
}

/// <h3>Execute Command</h3>
/// <p>Class method for Native API invocation to execute ObjectScript command.</p>
/// <p>Returns JSON with execution results and output.</p>
ClassMethod ExecuteCommand(pSessionId As %String, pCommand As %String, pTimeout As %Integer = 30) As %String
{
    Set tSC = $$$OK
    Set tResult = {}
    
    Try {
        // Validate session exists and is active
        If '..ValidateSession(pSessionId) {
            Set tResult.status = "error"
            Set tResult.errorMessage = "Invalid or expired session ID"
            Quit
        }
        
        // Update last access time
        Set ^SessionMCP.State(pSessionId, "lastAccess") = $HOROLOG
        
        // Get session namespace and switch if needed
        Set tOriginalNamespace = $NAMESPACE
        Set tSessionNamespace = $Get(^SessionMCP.State(pSessionId, "namespace"), "USER")
        If (tSessionNamespace '= $NAMESPACE) {
            Set $NAMESPACE = tSessionNamespace
        }
        
        // Execute command with timing
        Set tStartTime = $HOROLOG
        
        // Check security permissions before XECUTE
        If '$SYSTEM.Security.Check("%Development","USE") {
            Set tResult.status = "error"
            Set tResult.errorMessage = "Insufficient privileges for command execution (requires %Development:USE)"
            Quit
        }
        
        // Execute command with proper security
        XECUTE pCommand
        
        Set tEndTime = $HOROLOG
        Set tExecutionTime = $PIECE(tEndTime,",",2) - $PIECE(tStartTime,",",2)
        
        // Restore original namespace
        Set $NAMESPACE = tOriginalNamespace
        
        // Build success response
        Set tResult.status = "success"
        Set tResult.output = "Command executed successfully"
        Set tResult.sessionId = pSessionId
        Set tResult.namespace = tSessionNamespace
        Set tResult.executionTimeMs = (tExecutionTime * 1000)
        
    } Catch (ex) {
        // Restore namespace on error
        Set $NAMESPACE = tOriginalNamespace
        Set tResult.status = "error"
        Set tResult.errorMessage = ex.DisplayString()
    }
    
    Quit tResult.%ToJSON()
}

/// <h3>Get Session Status</h3>
/// <p>Class method for Native API invocation to get session information.</p>
/// <p>Returns JSON with session metadata and status.</p>
ClassMethod GetSessionStatus(pSessionId As %String) As %String
{
    Set tSC = $$$OK
    Set tResult = {}
    
    Try {
        If '..ValidateSession(pSessionId) {
            Set tResult.status = "error"
            Set tResult.errorMessage = "Session not found or expired"
            Quit
        }
        
        // Gather session information
        Set tResult.status = "success"
        Set tResult.sessionId = pSessionId
        Set tResult.namespace = $Get(^SessionMCP.State(pSessionId, "namespace"))
        Set tResult.user = $Get(^SessionMCP.State(pSessionId, "user"))
        Set tResult.created = $ZDateTime($Get(^SessionMCP.State(pSessionId, "created")), 3)
        Set tResult.lastAccess = $ZDateTime($Get(^SessionMCP.State(pSessionId, "lastAccess")), 3)
        Set tResult.sessionStatus = $Get(^SessionMCP.State(pSessionId, "status"))
        
    } Catch (ex) {
        Set tResult.status = "error"
        Set tResult.errorMessage = ex.DisplayString()
    }
    
    Quit tResult.%ToJSON()
}

/// <h3>Destroy Session</h3>
/// <p>Class method for Native API invocation to clean up session.</p>
/// <p>Removes session state from global storage.</p>
ClassMethod DestroySession(pSessionId As %String) As %String
{
    Set tSC = $$$OK
    Set tResult = {}
    
    Try {
        If '$Data(^SessionMCP.State(pSessionId)) {
            Set tResult.status = "error"
            Set tResult.errorMessage = "Session not found"
            Quit
        }
        
        // Clean up session state
        Kill ^SessionMCP.State(pSessionId)
        
        Set tResult.status = "success"
        Set tResult.message = "Session destroyed successfully"
        Set tResult.sessionId = pSessionId
        
    } Catch (ex) {
        Set tResult.status = "error"
        Set tResult.errorMessage = ex.DisplayString()
    }
    
    Quit tResult.%ToJSON()
}

/// <h3>Validate Session</h3>
/// <p>Check if session is valid and not expired.</p>
/// <p>Returns 1 if valid, 0 if invalid or expired.</p>
ClassMethod ValidateSession(pSessionId As %String) As %Boolean
{
    // Check if session exists
    If '$Data(^SessionMCP.State(pSessionId)) Quit 0
    
    // Check if session is expired (24 hour timeout for MVP)
    Set tCreated = $Get(^SessionMCP.State(pSessionId, "created"))
    If tCreated = "" Quit 0
    
    Set tCurrentTime = $HOROLOG
    Set tTimeDiff = $PIECE(tCurrentTime,",",1) - $PIECE(tCreated,",",1)
    
    // 24 hour timeout (1 day in $HOROLOG days)
    If tTimeDiff > 1 {
        // Mark session as expired
        Set ^SessionMCP.State(pSessionId, "status") = "EXPIRED"
        Quit 0
    }
    
    Quit 1
}

/// <h3>List Active Sessions</h3>
/// <p>Class method to get list of all active sessions.</p>
/// <p>Returns JSON array of session information.</p>
ClassMethod ListActiveSessions() As %String
{
    Set tSC = $$$OK
    Set tResult = {}
    Set tSessions = []
    
    Try {
        Set tSessionId = ""
        For {
            Set tSessionId = $Order(^SessionMCP.State(tSessionId))
            If tSessionId = "" Quit
            
            // Check if session is still valid
            If ..ValidateSession(tSessionId) {
                Set tSessionInfo = {}
                Set tSessionInfo.sessionId = tSessionId
                Set tSessionInfo.namespace = $Get(^SessionMCP.State(tSessionId, "namespace"))
                Set tSessionInfo.user = $Get(^SessionMCP.State(tSessionId, "user"))
                Set tSessionInfo.created = $ZDateTime($Get(^SessionMCP.State(tSessionId, "created")), 3)
                Set tSessionInfo.lastAccess = $ZDateTime($Get(^SessionMCP.State(tSessionId, "lastAccess")), 3)
                Set tSessionInfo.status = $Get(^SessionMCP.State(tSessionId, "status"))
                
                Do tSessions.%Push(tSessionInfo)
            }
        }
        
        Set tResult.status = "success"
        Set tResult.sessions = tSessions
        Set tResult.count = tSessions.%Size()
        
    } Catch (ex) {
        Set tResult.status = "error"
        Set tResult.errorMessage = ex.DisplayString()
    }
    
    Quit tResult.%ToJSON()
}

/// <h3>Cleanup Expired Sessions</h3>
/// <p>Background maintenance method to clean up expired sessions.</p>
/// <p>Should be called periodically by system maintenance.</p>
ClassMethod CleanupExpiredSessions() As %String
{
    Set tSC = $$$OK
    Set tResult = {}
    Set tCleanedCount = 0
    
    Try {
        Set tCutoffTime = $HOROLOG - 1  // 1 day ago
        Set tSessionId = ""
        
        For {
            Set tSessionId = $Order(^SessionMCP.State(tSessionId))
            If tSessionId = "" Quit
            
            Set tCreated = $Get(^SessionMCP.State(tSessionId, "created"))
            If (tCreated '= "") && ($PIECE(tCreated,",",1) < $PIECE(tCutoffTime,",",1)) {
                Kill ^SessionMCP.State(tSessionId)
                Set tCleanedCount = tCleanedCount + 1
            }
        }
        
        Set tResult.status = "success"
        Set tResult.message = "Cleanup completed"
        Set tResult.sessionsRemoved = tCleanedCount
        
    } Catch (ex) {
        Set tResult.status = "error"
        Set tResult.errorMessage = ex.DisplayString()
    }
    
    Quit tResult.%ToJSON()
}

}
