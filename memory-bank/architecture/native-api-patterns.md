# Native API Patterns - IRIS Terminal MCP Server

## IRIS Native API Integration Architecture

### Connection Management Pattern
**Primary Connection Strategy:**
- Direct IRIS Native API connectivity via `intersystems-iris` Python package
- Single persistent connection per MCP session
- Connection pooling for multiple concurrent sessions
- Automatic reconnection with exponential backoff

**Connection Lifecycle:**
```python
import iris
from typing import Optional

class IRISConnectionManager:
    def __init__(self, hostname: str, port: int, namespace: str, 
                 username: str, password: str):
        self.config = {
            'hostname': hostname,
            'port': port, 
            'namespace': namespace,
            'username': username,
            'password': password
        }
        self.connection: Optional[iris.IRISConnection] = None
        
    def connect(self) -> iris.IRISConnection:
        if not self.connection or not self.is_connected():
            self.connection = iris.connect(
                self.config['hostname'],
                self.config['port'],
                self.config['namespace'],
                self.config['username'],
                self.config['password']
            )
        return self.connection
        
    def is_connected(self) -> bool:
        try:
            # Test connection with simple query
            self.connection.invoke_classmethod("%SYSTEM.Version", "GetVersion")
            return True
        except:
            return False
```

### Method Invocation Patterns
**ClassMethod Invocation for Session Operations:**
```python
# Execute command in IRIS session
result = connection.invoke_classmethod(
    "SessionMCP.Core.Session",
    "ExecuteCommand", 
    [session_id, command, timeout]
)

# Create new session
session_id = connection.invoke_classmethod(
    "SessionMCP.Core.Session",
    "CreateSession",
    [namespace, user_context]
)

# Get session status
status = connection.invoke_classmethod(
    "SessionMCP.Core.Session",
    "GetSessionStatus",
    [session_id]
)
```

**ObjectScript ClassMethod Pattern:**
```objectscript
/// Native API compatible method signature
ClassMethod ExecuteCommand(pSessionId As %String, pCommand As %String, 
                          pTimeout As %Integer = 30) As %String
{
    Set tSC = $$$OK
    Set tResult = ""
    
    Try {
        // Get or create session instance
        Set tSession = ..GetSessionInstance(pSessionId)
        If '$IsObject(tSession) {
            Set tResult = ..FormatError("SESSION_NOT_FOUND", "Invalid session ID")
            Quit
        }
        
        // Execute command with timeout
        Set tSC = tSession.ExecuteWithTimeout(pCommand, pTimeout)
        If $$$ISERR(tSC) {
            Set tResult = ..FormatError("EXECUTION_ERROR", $System.Status.GetErrorText(tSC))
            Quit
        }
        
        // Format successful response
        Set tResult = ..FormatSuccess(tSession.GetOutput(), tSession.GetNamespace())
        
    } Catch (ex) {
        Set tResult = ..FormatError("SYSTEM_ERROR", ex.DisplayString())
    }
    
    Quit tResult
}
```

## Session State Management

### Global Variable Patterns
**Session Storage Structure:**
```objectscript
// Session metadata
^SessionMCP.State(sessionId, "created") = $HOROLOG
^SessionMCP.State(sessionId, "lastAccess") = $HOROLOG
^SessionMCP.State(sessionId, "namespace") = currentNamespace
^SessionMCP.State(sessionId, "user") = username
^SessionMCP.State(sessionId, "status") = "ACTIVE"|"IDLE"|"EXPIRED"

// Session variables
^SessionMCP.State(sessionId, "variables", varName) = value

// Session output buffer
^SessionMCP.State(sessionId, "output", timestamp) = outputText

// Session configuration
^SessionMCP.State(sessionId, "config", "timeout") = 300
^SessionMCP.State(sessionId, "config", "maxOutput") = 1048576
```

**Session Access Patterns:**
```objectscript
/// Retrieve session instance with validation
ClassMethod GetSessionInstance(pSessionId As %String) As SessionMCP.Core.Session
{
    // Check if session exists and is valid
    If '$Data(^SessionMCP.State(pSessionId)) Quit ""
    
    Set tLastAccess = $Get(^SessionMCP.State(pSessionId, "lastAccess"))
    Set tTimeout = $Get(^SessionMCP.State(pSessionId, "config", "timeout"), 300)
    
    // Check if session has expired
    If ($HOROLOG - tLastAccess) > tTimeout {
        Do ..ExpireSession(pSessionId)
        Quit ""
    }
    
    // Update last access time
    Set ^SessionMCP.State(pSessionId, "lastAccess") = $HOROLOG
    
    // Return session instance
    Set tSession = ##class(SessionMCP.Core.Session).%New()
    Set tSession.SessionId = pSessionId
    Do tSession.LoadState()
    
    Quit tSession
}
```

### Connection Pooling Implementation
**Pool Management:**
```python
import asyncio
import queue
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

class IRISConnectionPool:
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.available_connections = queue.Queue(maxsize=max_connections)
        self.active_connections: Dict[str, iris.IRISConnection] = {}
        self.connection_config = None
        
    async def get_connection(self, session_id: str) -> iris.IRISConnection:
        # Try to reuse existing connection for session
        if session_id in self.active_connections:
            connection = self.active_connections[session_id]
            if self._test_connection(connection):
                return connection
            else:
                # Remove dead connection
                del self.active_connections[session_id]
        
        # Get connection from pool or create new
        try:
            connection = self.available_connections.get_nowait()
        except queue.Empty:
            if len(self.active_connections) < self.max_connections:
                connection = self._create_connection()
            else:
                # Wait for available connection
                connection = await self._wait_for_connection()
        
        self.active_connections[session_id] = connection
        return connection
    
    def release_connection(self, session_id: str):
        if session_id in self.active_connections:
            connection = self.active_connections.pop(session_id)
            if self._test_connection(connection):
                self.available_connections.put(connection)
            # Dead connections are simply discarded
```

## Error Handling and Recovery

### Connection Error Recovery
**Automatic Reconnection:**
```python
import time
import logging
from typing import Callable, Any

class ConnectionRecovery:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        
    def with_retry(self, operation: Callable, *args, **kwargs) -> Any:
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except iris.IRISError as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                    logging.warning(f"Connection attempt {attempt + 1} failed, retrying in {delay}s")
                    time.sleep(delay)
                else:
                    logging.error(f"All {self.max_retries + 1} connection attempts failed")
                    
        raise last_exception
```

### IRIS Error Code Mapping
**System Error Translation:**
```objectscript
/// Map IRIS system errors to user-friendly messages
ClassMethod TranslateSystemError(pErrorCode As %String) As %String
{
    Set tMessage = ""
    
    If pErrorCode [ "<UNDEFINED>" {
        Set tMessage = "Variable or routine not defined"
    } ElseIf pErrorCode [ "<SYNTAX>" {
        Set tMessage = "Invalid ObjectScript syntax"
    } ElseIf pErrorCode [ "<PROTECT>" {
        Set tMessage = "Access permission denied"
    } ElseIf pErrorCode [ "<MAXSTRING>" {
        Set tMessage = "String length limit exceeded"
    } ElseIf pErrorCode [ "<STORE>" {
        Set tMessage = "Insufficient storage space"
    } ElseIf pErrorCode [ "<INTERRUPT>" {
        Set tMessage = "Operation interrupted by user"
    } Else {
        Set tMessage = "System error: "_pErrorCode
    }
    
    Quit tMessage
}
```

## Data Transfer Patterns

### Large Output Handling
**Streaming Response Pattern:**
```objectscript
/// Handle large output with streaming
ClassMethod ExecuteCommandStream(pSessionId As %String, pCommand As %String) As %Stream.Object
{
    Set tStream = ##class(%Stream.TmpCharacter).%New()
    Set tSession = ..GetSessionInstance(pSessionId)
    
    If '$IsObject(tSession) {
        Do tStream.WriteLine(..FormatError("SESSION_NOT_FOUND", "Invalid session ID"))
        Quit tStream
    }
    
    Try {
        // Execute command with streaming output
        Set tSC = tSession.ExecuteWithStream(pCommand, tStream)
        If $$$ISERR(tSC) {
            Do tStream.WriteLine(..FormatError("EXECUTION_ERROR", $System.Status.GetErrorText(tSC)))
        }
    } Catch (ex) {
        Do tStream.WriteLine(..FormatError("SYSTEM_ERROR", ex.DisplayString()))
    }
    
    Quit tStream
}
```

**Python Streaming Client:**
```python
def execute_command_stream(connection: iris.IRISConnection, 
                          session_id: str, command: str) -> Iterator[str]:
    """Execute command and yield output in chunks."""
    try:
        stream = connection.invoke_classmethod(
            "SessionMCP.Core.Session",
            "ExecuteCommandStream",
            [session_id, command]
        )
        
        # Read stream in chunks
        while True:
            chunk = stream.read(8192)  # 8KB chunks
            if not chunk:
                break
            yield chunk
            
    except iris.IRISError as e:
        yield f"Error: {str(e)}"
```

### JSON Response Format
**Standardized Response Structure:**
```objectscript
/// Format successful command response
ClassMethod FormatSuccess(pOutput As %String, pNamespace As %String, 
                         pExecutionTime As %Numeric = 0) As %String
{
    Set tResponse = {}
    Set tResponse.status = "success"
    Set tResponse.output = pOutput
    Set tResponse.namespace = pNamespace
    Set tResponse.executionTimeMs = pExecutionTime
    Set tResponse.timestamp = $ZDateTime($HOROLOG, 3)
    
    Quit tResponse.%ToJSON()
}

/// Format error response
ClassMethod FormatError(pErrorCode As %String, pErrorMessage As %String) As %String
{
    Set tResponse = {}
    Set tResponse.status = "error"
    Set tResponse.errorCode = pErrorCode
    Set tResponse.errorMessage = pErrorMessage
    Set tResponse.timestamp = $ZDateTime($HOROLOG, 3)
    
    Quit tResponse.%ToJSON()
}
```

## Performance Optimization

### Connection Reuse Strategy
**Session Affinity Pattern:**
```python
class SessionAffinityManager:
    def __init__(self):
        self.session_connections: Dict[str, iris.IRISConnection] = {}
        
    def get_connection_for_session(self, session_id: str) -> iris.IRISConnection:
        """Get dedicated connection for session to maintain state."""
        if session_id not in self.session_connections:
            self.session_connections[session_id] = self._create_connection()
        return self.session_connections[session_id]
        
    def cleanup_session(self, session_id: str):
        """Clean up resources when session ends."""
        if session_id in self.session_connections:
            connection = self.session_connections.pop(session_id)
            connection.close()
```

### Caching Patterns
**Metadata Caching:**
```objectscript
/// Cache namespace information for performance
ClassMethod GetNamespaceInfo(pNamespace As %String) As %String
{
    // Check cache first
    Set tCacheKey = "NAMESPACE_INFO_"_pNamespace
    Set tCached = $Get(^SessionMCP.Cache(tCacheKey))
    
    If tCached '= "" {
        // Check if cache is still valid (5 minutes)
        Set tCacheTime = $Get(^SessionMCP.Cache(tCacheKey, "timestamp"))
        If ($HOROLOG - tCacheTime) < 300 {
            Quit tCached
        }
    }
    
    // Generate fresh data
    Set tInfo = ..BuildNamespaceInfo(pNamespace)
    
    // Cache result
    Set ^SessionMCP.Cache(tCacheKey) = tInfo
    Set ^SessionMCP.Cache(tCacheKey, "timestamp") = $HOROLOG
    
    Quit tInfo
}
```

## Security and Authentication

### Authentication Flow
**Credential Validation:**
```objectscript
/// Validate user credentials and create authenticated session
ClassMethod CreateAuthenticatedSession(pUsername As %String, pPassword As %String, 
                                      pNamespace As %String) As %String
{
    Set tSC = $$$OK
    Set tResult = ""
    
    Try {
        // Validate credentials by attempting connection
        Set tValidated = $SYSTEM.Security.Login(pUsername, pPassword)
        If 'tValidated {
            Set tResult = ..FormatError("AUTH_FAILED", "Invalid credentials")
            Quit
        }
        
        // Create session with authenticated user context
        Set tSessionId = ..GenerateSessionId()
        Set ^SessionMCP.State(tSessionId, "user") = pUsername
        Set ^SessionMCP.State(tSessionId, "namespace") = pNamespace
        Set ^SessionMCP.State(tSessionId, "created") = $HOROLOG
        Set ^SessionMCP.State(tSessionId, "authenticated") = 1
        
        Set tResult = ..FormatSuccess("", pNamespace)
        Set $PIECE(tResult, """sessionId"":", 2) = """"_tSessionId_""""
        
    } Catch (ex) {
        Set tResult = ..FormatError("SYSTEM_ERROR", ex.DisplayString())
    }
    
    Quit tResult
}
```

### Access Control
**Command Authorization:**
```objectscript
/// Check if user can execute specific command
Method AuthorizeCommand(pCommand As %String) As %Boolean
{
    Set tUserId = $Get(^SessionMCP.State(..SessionId, "user"))
    
    // System administrators can execute any command
    If $SYSTEM.Security.Check("%ALL", "USE", tUserId) {
        Quit 1
    }
    
    // Check for dangerous operations
    If ..ContainsDangerousPattern(pCommand) {
        If '$SYSTEM.Security.Check("%Development", "USE", tUserId) {
            Quit 0
        }
    }
    
    Quit 1
}
