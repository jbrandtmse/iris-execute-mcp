# Technical Context - IRIS Terminal MCP Server

## Technology Stack

### IRIS Backend Technologies
**ObjectScript Classes:**
- **Core Classes**: SessionMCP.Core.Session, SessionMCP.Core.Command
- **Transport Layer**: SessionMCP.Transport.NativeConnector
- **Security**: SessionMCP.Security.AuthHandler
- **Utilities**: SessionMCP.Core.Utils

**IRIS Native Capabilities:**
- Direct memory access via Native API
- Global variable manipulation
- SQL query execution
- System function access
- Device I/O control

### MCP Client Technologies
**Python Implementation:**
- **Primary Library**: `intersystems-iris` (Native API bindings)
- **MCP Framework**: Custom JSON-RPC 2.0 implementation or FastMCP
- **Async Support**: `asyncio` for concurrent session handling
- **Transport**: STDIO (initial) + HTTP (future)

**Key Dependencies:**
```python
# Minimal dependency list for easy setup
intersystems-iris>=3.2.0  # IRIS Native API
pydantic>=2.0.0          # Data validation
fastapi>=0.100.0         # HTTP transport (optional)
uvicorn>=0.23.0          # ASGI server (optional)
```

## IRIS Native API Integration

### Connection Architecture
**Direct IRIS Connectivity:**
```python
import iris

# Connection establishment
connection = iris.connect(
    hostname="localhost",
    port=1972,
    namespace="USER",
    username="username",
    password="password"
)

# Method invocation
result = connection.invoke_classmethod(
    "SessionMCP.Core.Session",
    "ExecuteCommand",
    ["session123", "WRITE 2+2"]
)
```

### Session State Management
**Persistent Context:**
- Sessions stored in IRIS globals: `^SessionMCP.State`
- Variable preservation across calls
- Namespace context maintenance
- Device state tracking

**Implementation Pattern:**
```objectscript
// Store session state
Set ^SessionMCP.State(pSessionId, "namespace") = $NAMESPACE
Set ^SessionMCP.State(pSessionId, "variables", varName) = value
Set ^SessionMCP.State(pSessionId, "lastAccess") = $HOROLOG
```

### Error Handling Integration
**IRIS Error Mapping:**
- `<UNDEFINED>` → "Variable not defined"
- `<SYNTAX>` → "Invalid ObjectScript syntax"
- `<PROTECT>` → "Access permission denied"
- `<MAXSTRING>` → "String length exceeded"

**Status Code Management:**
```objectscript
Method HandleError(pException As %Exception.AbstractException) As %String
{
    If pException.%IsA("%Exception.SystemException") {
        Set tError = pException.AsSystemError()
        // Clean up stack trace references
        Return ..FormatSystemError(tError)
    }
    Return pException.DisplayString()
}
```

## MCP Protocol Implementation

### JSON-RPC 2.0 Structure
**Request Format:**
```json
{
    "jsonrpc": "2.0",
    "id": "req-123",
    "method": "tools/call",
    "params": {
        "name": "execute_command",
        "arguments": {
            "session_id": "session-abc",
            "command": "WRITE $ZVERSION"
        }
    }
}
```

**Response Format:**
```json
{
    "jsonrpc": "2.0",
    "id": "req-123",
    "result": {
        "content": [
            {
                "type": "text",
                "text": "IRIS for Windows (x86-64) 2023.1 (Build 215)"
            }
        ]
    }
}
```

### Tool Definition Schema
**Type-Safe Tool Definitions:**
```python
from pydantic import BaseModel

class ExecuteCommandArgs(BaseModel):
    session_id: str
    command: str
    timeout: int = 30

class ExecuteCommandResult(BaseModel):
    output: str
    error: Optional[str] = None
    namespace: str
    execution_time_ms: int
    session_id: str
```

## Development Environment

### IRIS Setup Requirements
**Minimum IRIS Configuration:**
- IRIS for Windows/Linux/macOS 2022.1+
- Native API enabled (default)
- User account with %Development privilege
- SuperServer port accessible (default 1972)

**Required IRIS Packages:**
- No additional packages required (uses built-in classes)
- Optional: %SYS.Python for future Python embedding

### Python Development Environment
**Setup Commands:**
```bash
# Create virtual environment
python -m venv iris-mcp-env
source iris-mcp-env/bin/activate  # Linux/macOS
# iris-mcp-env\Scripts\activate   # Windows

# Install dependencies
pip install intersystems-iris pydantic

# Verify IRIS connectivity
python -c "import iris; print('IRIS Native API available')"
```

**Configuration Management:**
```python
# Environment variables for connection
import os

IRIS_CONFIG = {
    'hostname': os.getenv('IRIS_HOSTNAME', 'localhost'),
    'port': int(os.getenv('IRIS_PORT', '1972')),
    'namespace': os.getenv('IRIS_NAMESPACE', 'USER'),
    'username': os.getenv('IRIS_USERNAME', '_SYSTEM'),
    'password': os.getenv('IRIS_PASSWORD', 'SYS')
}
```

## Security Implementation

### Authentication Flow
**IRIS Native Authentication:**
1. Credentials provided via environment variables
2. Native API handles IRIS authentication
3. Session inherits user privileges and roles
4. All commands execute under authenticated user context

**Security Layers:**
```python
class SecurityManager:
    def validate_user(self, username: str, password: str) -> bool:
        try:
            test_conn = iris.connect(
                self.hostname, self.port, self.namespace,
                username, password
            )
            test_conn.close()
            return True
        except iris.IRISError:
            return False
```

### Command Sanitization
**Input Validation:**
- Maximum command length limits
- Forbidden command patterns (system-level operations)
- SQL injection prevention for dynamic SQL
- Global variable access restrictions

## Performance Considerations

### Connection Optimization
**Connection Pooling:**
```python
from concurrent.futures import ThreadPoolExecutor
import threading

class ConnectionPool:
    def __init__(self, max_connections=10):
        self.pool = Queue(maxsize=max_connections)
        self.lock = threading.Lock()
        
    def get_connection(self):
        try:
            return self.pool.get_nowait()
        except Empty:
            return self.create_connection()
```

### Memory Management
**Large Output Handling:**
- Stream processing for outputs > 1MB
- Chunked response delivery
- Memory-mapped file handling for very large results
- Automatic cleanup of temporary objects

### Caching Strategy
**Session Cache:**
- In-memory session metadata cache
- LRU eviction for inactive sessions
- Periodic cache validation against IRIS state

## Monitoring and Observability

### Logging Framework
**Structured Logging:**
```python
import logging
import json

class IRISMCPLogger:
    def __init__(self):
        self.logger = logging.getLogger('iris-mcp')
        
    def log_command(self, session_id: str, command: str, 
                   execution_time: float, success: bool):
        self.logger.info(json.dumps({
            'event': 'command_executed',
            'session_id': session_id,
            'command_hash': hashlib.md5(command.encode()).hexdigest(),
            'execution_time_ms': int(execution_time * 1000),
            'success': success
        }))
```

### Metrics Collection
**Key Performance Indicators:**
- Command execution latency (p50, p95, p99)
- Session creation/destruction rates
- Error rates by error type
- Connection pool utilization
- Memory usage patterns

### Health Checks
**System Health Monitoring:**
```python
async def health_check():
    return {
        'iris_connectivity': await test_iris_connection(),
        'session_count': len(active_sessions),
        'memory_usage_mb': get_memory_usage(),
        'uptime_seconds': time.time() - start_time
    }
```

## Development Tools

### Testing Framework
**Unit Testing:**
```python
import pytest
from unittest.mock import Mock, patch

class TestSessionMCP:
    @patch('iris.connect')
    def test_execute_command_success(self, mock_connect):
        # Test implementation
        pass
```

### Debugging Tools
**Development Utilities:**
- IRIS session state inspection tools
- Command execution tracing
- Performance profiling utilities
- Connection state monitoring

### Code Quality Tools
**Static Analysis:**
- `mypy` for Python type checking
- `black` for code formatting
- `flake8` for linting
- `pytest` for test coverage
