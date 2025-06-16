# SessionMCP Structure - IRIS Terminal MCP Server

## Directory Organization

### Proposed src/SessionMCP Structure
```
src/SessionMCP/
├── Core/
│   ├── Session.cls           # Main session management class
│   ├── Command.cls          # Command execution engine
│   ├── Utils.cls            # Utility functions
│   └── Tests/
│       ├── SessionTest.cls
│       └── CommandTest.cls
├── Transport/
│   ├── NativeConnector.cls  # Native API interface
│   ├── ResponseFormatter.cls # JSON response formatting
│   └── Tests/
│       └── ConnectorTest.cls
├── Security/
│   ├── AuthHandler.cls      # Authentication management
│   ├── Validator.cls        # Input validation
│   └── Tests/
│       └── SecurityTest.cls
└── IO/
    ├── OutputCapture.cls    # I/O redirection implementation
    ├── StreamHandler.cls    # Large output streaming
    └── Tests/
        └── IOTest.cls
```

### Class Hierarchy and Dependencies
```
SessionMCP.Core.Session
├── Extends: %RegisteredObject
├── Uses: SessionMCP.IO.OutputCapture
├── Uses: SessionMCP.Security.Validator
├── Uses: SessionMCP.Core.Command
└── Calls: SessionMCP.Transport.ResponseFormatter

SessionMCP.Core.Command
├── Extends: %RegisteredObject
├── Uses: SessionMCP.IO.OutputCapture
└── Uses: SessionMCP.Security.Validator

SessionMCP.Transport.NativeConnector
├── Extends: %RegisteredObject
├── ClassMethods for Native API
└── Uses: SessionMCP.Core.Session
```

## Core Classes Design

### SessionMCP.Core.Session
**Primary Session Management Class:**
```objectscript
/// <h3>IRIS Terminal Session Manager for MCP</h3>
/// <p>Manages persistent terminal sessions with I/O redirection and state management.</p>
/// <p>Designed for Native API invocation from Python MCP clients.</p>
Class SessionMCP.Core.Session Extends %RegisteredObject
{
    /// <b>Session identifier</b>
    Property SessionId As %String [ Required ];
    
    /// <b>Current namespace</b>
    Property Namespace As %String [ InitialExpression = "USER" ];
    
    /// <b>Session creation timestamp</b>
    Property Created As %TimeStamp [ InitialExpression = {$ZDateTime($HOROLOG, 3)} ];
    
    /// <b>Last access timestamp</b>
    Property LastAccess As %TimeStamp;
    
    /// <b>Session status</b>
    Property Status As %String [ InitialExpression = "ACTIVE" ];
    
    /// <b>Output capture instance</b>
    Property OutputCapture As SessionMCP.IO.OutputCapture;
    
    /// <b>Command execution timeout in seconds</b>
    Parameter DEFAULTTIMEOUT = 30;
    
    /// <b>Maximum output size in bytes</b>
    Parameter MAXOUTPUTSIZE = 1048576;
    
    /// <h3>Create New Session</h3>
    /// <p>Class method for Native API invocation to create new session.</p>
    ClassMethod CreateSession(pNamespace As %String = "USER", 
                             pUserId As %String = "") As %String;
    
    /// <h3>Execute Command</h3>
    /// <p>Class method for Native API invocation to execute ObjectScript command.</p>
    ClassMethod ExecuteCommand(pSessionId As %String, pCommand As %String, 
                              pTimeout As %Integer = 30) As %String;
    
    /// <h3>Get Session Status</h3>
    /// <p>Class method for Native API invocation to get session information.</p>
    ClassMethod GetSessionStatus(pSessionId As %String) As %String;
    
    /// <h3>Destroy Session</h3>
    /// <p>Class method for Native API invocation to clean up session.</p>
    ClassMethod DestroySession(pSessionId As %String) As %String;
    
    /// <h3>Execute Command Instance Method</h3>
    /// <p>Execute command in context of this session instance.</p>
    Method Execute(pCommand As %String, pTimeout As %Integer = 30) As %Status;
    
    /// <h3>Load Session State</h3>
    /// <p>Load session state from global storage.</p>
    Method LoadState() As %Status;
    
    /// <h3>Save Session State</h3>
    /// <p>Save session state to global storage.</p>
    Method SaveState() As %Status;
    
    /// <h3>Validate Session</h3>
    /// <p>Check if session is valid and not expired.</p>
    Method IsValid() As %Boolean;
}
```

### SessionMCP.Core.Command
**Command Execution Engine:**
```objectscript
/// <h3>ObjectScript Command Execution Engine</h3>
/// <p>Handles safe execution of ObjectScript commands with I/O capture.</p>
Class SessionMCP.Core.Command Extends %RegisteredObject
{
    /// <b>Command text</b>
    Property CommandText As %String [ Required ];
    
    /// <b>Execution timeout</b>
    Property Timeout As %Integer [ InitialExpression = 30 ];
    
    /// <b>Execution start time</b>
    Property StartTime As %TimeStamp;
    
    /// <b>Execution end time</b>
    Property EndTime As %TimeStamp;
    
    /// <b>Output capture instance</b>
    Property OutputCapture As SessionMCP.IO.OutputCapture;
    
    /// <h3>Execute Command</h3>
    /// <p>Execute the command with timeout and output capture.</p>
    Method Execute() As %Status;
    
    /// <h3>Validate Command</h3>
    /// <p>Check command for safety and syntax.</p>
    Method Validate() As %Status;
    
    /// <h3>Get Execution Time</h3>
    /// <p>Calculate execution duration in milliseconds.</p>
    Method GetExecutionTimeMs() As %Integer;
    
    /// <h3>Get Output</h3>
    /// <p>Retrieve captured output from execution.</p>
    Method GetOutput() As %String;
}
```

### SessionMCP.IO.OutputCapture
**I/O Redirection Implementation:**
```objectscript
/// <h3>Output Capture for Terminal Emulation</h3>
/// <p>Captures WRITE output and device I/O for terminal session emulation.</p>
/// <p>Adapted from %Atelier.v7.TerminalAgent patterns.</p>
Class SessionMCP.IO.OutputCapture Extends %RegisteredObject
{
    /// <b>Output buffer</b>
    Property Buffer As %String;
    
    /// <b>Capture active flag</b>
    Property Active As %Boolean [ InitialExpression = 0 ];
    
    /// <b>Original device</b>
    Property OriginalDevice As %String;
    
    /// <b>Buffer size limit</b>
    Parameter BUFFERSIZELIMIT = 1048576;
    
    /// <h3>Start Output Capture</h3>
    /// <p>Enable I/O redirection to capture output.</p>
    Method StartCapture() As %Status;
    
    /// <h3>Stop Output Capture</h3>
    /// <p>Disable I/O redirection and restore normal output.</p>
    Method StopCapture() As %Status;
    
    /// <h3>Get Captured Output</h3>
    /// <p>Retrieve and clear captured output buffer.</p>
    Method GetOutput() As %String;
    
    /// <h3>Clear Buffer</h3>
    /// <p>Reset output buffer.</p>
    Method ClearBuffer() As %Status;
    
    /// <h3>Write to Buffer</h3>
    /// <p>Append text to output buffer (internal use).</p>
    Method WriteToBuffer(pText As %String) As %Status;
}
```

### SessionMCP.Transport.NativeConnector
**Native API Interface Layer:**
```objectscript
/// <h3>Native API Connector for MCP Integration</h3>
/// <p>Provides ClassMethods for Python Native API invocation.</p>
/// <p>Handles connection management and response formatting.</p>
Class SessionMCP.Transport.NativeConnector Extends %RegisteredObject
{
    /// <h3>Execute Terminal Command</h3>
    /// <p>Main entry point for command execution via Native API.</p>
    ClassMethod ExecuteTerminalCommand(pSessionId As %String, pCommand As %String, 
                                      pTimeout As %Integer = 30) As %String;
    
    /// <h3>Create Terminal Session</h3>
    /// <p>Create new terminal session via Native API.</p>
    ClassMethod CreateTerminalSession(pNamespace As %String = "USER", 
                                     pUserId As %String = "") As %String;
    
    /// <h3>Get Session Information</h3>
    /// <p>Retrieve session status and metadata via Native API.</p>
    ClassMethod GetSessionInfo(pSessionId As %String) As %String;
    
    /// <h3>Cleanup Session</h3>
    /// <p>Destroy session and clean up resources via Native API.</p>
    ClassMethod CleanupSession(pSessionId As %String) As %String;
    
    /// <h3>Health Check</h3>
    /// <p>Verify system health for monitoring.</p>
    ClassMethod HealthCheck() As %String;
    
    /// <h3>List Active Sessions</h3>
    /// <p>Get list of all active sessions.</p>
    ClassMethod ListActiveSessions() As %String;
}
```

## Global Variable Structure

### Session State Storage
**Global Organization:**
```objectscript
// Session metadata
^SessionMCP.State(sessionId) = {JSON metadata}
^SessionMCP.State(sessionId, "created") = $HOROLOG
^SessionMCP.State(sessionId, "lastAccess") = $HOROLOG
^SessionMCP.State(sessionId, "namespace") = namespace
^SessionMCP.State(sessionId, "user") = userId
^SessionMCP.State(sessionId, "status") = "ACTIVE"|"IDLE"|"EXPIRED"

// Session variables and state
^SessionMCP.State(sessionId, "variables", varName) = value
^SessionMCP.State(sessionId, "device") = currentDevice
^SessionMCP.State(sessionId, "io", "state") = ioState

// Session configuration
^SessionMCP.Config(sessionId, "timeout") = timeoutSeconds
^SessionMCP.Config(sessionId, "maxOutput") = maxBytes
^SessionMCP.Config(sessionId, "security") = securityLevel

// Output history (for debugging/audit)
^SessionMCP.History(sessionId, timestamp, "command") = command
^SessionMCP.History(sessionId, timestamp, "output") = output
^SessionMCP.History(sessionId, timestamp, "error") = error

// Cache for performance
^SessionMCP.Cache("namespace", namespace) = {namespaceInfo}
^SessionMCP.Cache("user", userId) = {userInfo}

// System metrics
^SessionMCP.Metrics("sessions", "active") = count
^SessionMCP.Metrics("commands", "executed") = count
^SessionMCP.Metrics("errors", errorType) = count
```

### Cleanup and Maintenance
**Session Lifecycle Management:**
```objectscript
/// Background task to clean up expired sessions
ClassMethod CleanupExpiredSessions() As %Status
{
    Set tSC = $$$OK
    Set tCutoff = $HOROLOG - 86400  // 24 hours ago
    
    Set tSessionId = ""
    For {
        Set tSessionId = $Order(^SessionMCP.State(tSessionId))
        If tSessionId = "" Quit
        
        Set tLastAccess = $Get(^SessionMCP.State(tSessionId, "lastAccess"))
        If tLastAccess < tCutoff {
            Do ..ExpireSession(tSessionId)
        }
    }
    
    Quit tSC
}
```

## Package Management

### Installation Structure
**Package Definition:**
```objectscript
/// Package installer for SessionMCP
Class SessionMCP.Installer Extends %RegisteredObject
{
    /// <h3>Install SessionMCP Package</h3>
    /// <p>Install all classes and set up globals.</p>
    ClassMethod Install() As %Status;
    
    /// <h3>Uninstall SessionMCP Package</h3>
    /// <p>Remove classes and clean up globals.</p>
    ClassMethod Uninstall() As %Status;
    
    /// <h3>Verify Installation</h3>
    /// <p>Check that all components are properly installed.</p>
    ClassMethod Verify() As %Status;
    
    /// <h3>Setup Demo Data</h3>
    /// <p>Create sample sessions for testing.</p>
    ClassMethod SetupDemo() As %Status;
}
```

### Dependencies and Requirements
**System Requirements:**
- IRIS 2022.1 or later
- %Development privilege for installation
- Native API enabled (default configuration)
- Sufficient global storage for session state

**Optional Components:**
- %SYS.Python for future Python embedding
- Custom security domains for advanced authentication
- Monitoring hooks for production deployment

## Testing Framework

### Unit Test Structure
**Test Organization:**
```
src/SessionMCP/Core/Tests/
├── SessionTest.cls
├── CommandTest.cls
└── TestUtils.cls

src/SessionMCP/Transport/Tests/
├── ConnectorTest.cls
└── ResponseTest.cls

src/SessionMCP/IO/Tests/
├── OutputCaptureTest.cls
└── StreamTest.cls
```

### Test Data Management
**Test Session Creation:**
```objectscript
/// Test utility for creating test sessions
Class SessionMCP.Core.Tests.TestUtils Extends %UnitTest.TestCase
{
    /// Create test session with known state
    ClassMethod CreateTestSession(pSessionId As %String = "") As %String;
    
    /// Clean up test sessions
    ClassMethod CleanupTestSessions() As %Status;
    
    /// Verify test environment
    ClassMethod VerifyTestEnvironment() As %Boolean;
}
```

## Performance Considerations

### Memory Management
**Session State Optimization:**
- Use sparse global subscripts for efficiency
- Implement session state compression for large outputs
- Cache frequently accessed metadata
- Implement LRU eviction for session cache

### Scalability Patterns
**Multi-Session Support:**
- Session affinity with connection pooling
- Background cleanup processes
- Resource limit enforcement
- Performance monitoring hooks

### Index Strategies
**Global Access Optimization:**
```objectscript
// Efficient session lookup by user
^SessionMCP.Index("user", userId, sessionId) = ""

// Efficient session lookup by namespace  
^SessionMCP.Index("namespace", namespace, sessionId) = ""

// Efficient session lookup by status
^SessionMCP.Index("status", status, sessionId) = ""

// Time-based cleanup index
^SessionMCP.Index("cleanup", $HOROLOG, sessionId) = ""
