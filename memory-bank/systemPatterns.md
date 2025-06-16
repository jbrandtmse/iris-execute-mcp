# System Patterns - IRIS Terminal MCP Server

## Overall Architecture

### Two-Tier Design Pattern
```
AI Agent (Claude/Cline)
    ↓ (MCP JSON-RPC)
Python MCP Server
    ↓ (IRIS Native API)
IRIS Instance
    ↓ (ObjectScript)
SessionMCP Classes
```

### Communication Flow
1. **AI Request**: Agent sends MCP tool call (JSON-RPC 2.0)
2. **Client Processing**: Python server validates parameters, opens IRIS connection
3. **IRIS Execution**: Native API calls ObjectScript methods in SessionMCP classes
4. **Command Processing**: IRIS executes commands with I/O redirection
5. **Response Assembly**: Output captured and returned via Native API
6. **MCP Response**: JSON-RPC response sent back to AI agent

## Core Architectural Patterns

### Session Management Pattern
**Based on %Atelier.v7.TerminalAgent:**
- Each MCP session maintains persistent IRIS context
- Session state includes: namespace, variables, device settings
- Sessions survive across multiple tool calls
- Cleanup mechanism for abandoned sessions

**Implementation:**
```objectscript
Class SessionMCP.Core.Session Extends %RegisteredObject
{
    Property SessionId As %String;
    Property Namespace As %String;
    Property Variables As array Of %String;
    Property CurrentDevice As %String;
    Property State As %String;
}
```

### I/O Redirection Pattern
**Adapted from TerminalAgent I/O capture:**
- Override default WRITE operations to capture output
- Redirect terminal output to buffer collection
- Handle special characters and ANSI escape sequences
- Preserve exact terminal formatting

**Key Methods:**
- `CaptureOutput()` - Enable output redirection
- `CollectBuffer()` - Gather captured text
- `RestoreIO()` - Return to normal I/O mode

### Command Execution Pattern
**Error-Safe Execution Wrapper:**
```objectscript
Method ExecuteCommand(pCommand As %String) As %Status
{
    Set tSC = $$$OK
    Try {
        Do ..CaptureOutput()
        XECUTE pCommand
        Set tOutput = ..CollectBuffer()
        Do ..RestoreIO()
        Return ..FormatResponse(tOutput, "")
    } Catch (ex) {
        Do ..RestoreIO()
        Return ..FormatResponse("", ex.DisplayString())
    }
}
```

### Native API Integration Pattern
**Connection Management:**
- Single connection per MCP session
- Connection pooling for multiple concurrent sessions
- Automatic reconnection on failure
- Credential caching and security

**Python Implementation:**
```python
import iris

class IRISConnector:
    def __init__(self, host, port, namespace, username, password):
        self.connection = iris.connect(host, port, namespace, username, password)
        
    def execute_command(self, session_id, command):
        return self.connection.invoke_classmethod(
            "SessionMCP.Core.Session", 
            "ExecuteCommand", 
            [session_id, command]
        )
```

## MCP Protocol Patterns

### Tool Definition Pattern
**Structured Tool Definitions:**
```python
@mcp.tool
async def execute_command(session_id: str, command: str) -> dict:
    """Execute an ObjectScript command in IRIS terminal session.
    
    Args:
        session_id: Unique identifier for IRIS session
        command: ObjectScript command to execute
        
    Returns:
        dict: Contains output, error, namespace, and execution status
    """
```

### Error Handling Pattern
**Comprehensive Error Categories:**
- **Connection Errors**: IRIS connectivity issues
- **Authentication Errors**: Invalid credentials or permissions
- **Syntax Errors**: Invalid ObjectScript commands
- **Runtime Errors**: Execution failures
- **Session Errors**: Invalid or expired sessions

### Response Format Pattern
**Standardized JSON Response:**
```json
{
    "output": "Command execution output text",
    "error": null,
    "namespace": "USER",
    "session_id": "abc123",
    "execution_time_ms": 45,
    "status": "success"
}
```

## Design Patterns from Reference Implementation

### From %Atelier.v7.TerminalAgent
**Debugger-Based Execution:**
- Uses %Debugger.System for child process management
- Implements sophisticated state tracking
- Handles interrupts and timeouts gracefully

**I/O Redirection Techniques:**
- Device redirection using ##class(%Device).ReDirectIO()
- Custom write methods (wstr, wchr, wnl)
- Terminal control sequence handling

### From %CSP.WebSocket
**Session Lifecycle Management:**
- OnPreServer() for initialization
- Server() for main processing loop
- OnPostServer() for cleanup

**Data Framing:**
- Structured message format
- Binary vs text data handling
- Timeout and error management

## Scalability Patterns

### Multi-Session Architecture
**Session Pool Management:**
- Hash-based session routing
- Session timeout and cleanup
- Resource limit enforcement
- Load balancing across IRIS instances

### Asynchronous Processing
**Non-Blocking Operations:**
- Async command execution
- Parallel session handling
- Event-driven I/O processing
- Background session maintenance

## Security Patterns

### Authentication Integration
**IRIS Native Security:**
- User credential validation
- Role-based access control
- Audit trail integration
- Session token management

### MCP Security Layer
**Additional Protection:**
- API key validation (optional)
- Rate limiting per session
- Command sanitization
- Resource access restrictions

## Extension Patterns

### Tool Modularity
**Expandable Architecture:**
- Base tool interface
- Plugin-style tool registration
- Configuration-driven tool enabling
- Dynamic tool discovery

### Future Tool Examples:
- `execute_sql` - SQL query execution
- `get_namespace_info` - Namespace exploration
- `manage_globals` - Global variable operations
- `monitor_system` - System performance metrics
- `backup_restore` - Backup and restore operations

## Performance Patterns

### Connection Optimization
- Connection pooling and reuse
- Lazy connection initialization
- Connection health monitoring
- Automatic failover handling

### Output Processing
- Streaming for large outputs
- Chunked response handling
- Memory-efficient buffer management
- Compression for text responses

## Monitoring and Observability

### Logging Patterns
- Request/response logging
- Performance metrics collection
- Error rate monitoring
- Session activity tracking

### Debugging Support
- Trace mode for development
- Command execution history
- Session state inspection
- Performance profiling
