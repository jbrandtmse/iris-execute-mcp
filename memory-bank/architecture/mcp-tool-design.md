# MCP Tool Design - IRIS Terminal MCP Server

## Tool Architecture Overview

### MCP Tool Definition Pattern
**Single Tool MVP Approach:**
- Start with `execute_command` tool only
- Expand to multiple tools in phases
- Each tool as separate capability
- Shared connection infrastructure

**Tool Registration Structure:**
```python
@mcp.tool
async def execute_command(
    session_id: str,
    command: str, 
    timeout: int = 30
) -> dict:
    """Execute ObjectScript command in IRIS terminal session.
    
    Args:
        session_id: Unique session identifier (auto-generated if empty)
        command: ObjectScript command to execute
        timeout: Maximum execution time in seconds
        
    Returns:
        dict: Execution result with output, error, namespace, timing
    """
```

### Tool Implementation Framework
**Base Tool Interface:**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any
import iris

class IRISMCPTool(ABC):
    def __init__(self, connection_manager: IRISConnectionManager):
        self.connection_manager = connection_manager
        
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute tool with given parameters."""
        pass
        
    def format_response(self, success: bool, data: Any, 
                       error: str = None) -> Dict[str, Any]:
        """Standard response format for all tools."""
        return {
            'success': success,
            'data': data,
            'error': error,
            'timestamp': time.time()
        }
```

## Phase 1: Execute Command Tool

### Tool Specification
**execute_command Tool:**
```json
{
    "name": "execute_command",
    "description": "Execute ObjectScript command in IRIS terminal session",
    "inputSchema": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "Session ID (auto-generated if not provided)"
            },
            "command": {
                "type": "string", 
                "description": "ObjectScript command to execute"
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
                "default": 30,
                "minimum": 1,
                "maximum": 300
            }
        },
        "required": ["command"]
    }
}
```

### Implementation
**ExecuteCommand Tool Class:**
```python
class ExecuteCommandTool(IRISMCPTool):
    async def execute(self, command: str, session_id: str = None, 
                     timeout: int = 30) -> Dict[str, Any]:
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = self._generate_session_id()
            
            # Get IRIS connection
            connection = await self.connection_manager.get_connection(session_id)
            
            # Execute command via Native API
            result = connection.invoke_classmethod(
                "SessionMCP.Core.Session",
                "ExecuteCommand",
                [session_id, command, timeout]
            )
            
            # Parse JSON response from IRIS
            response_data = json.loads(result)
            
            return self.format_response(
                success=response_data.get('status') == 'success',
                data={
                    'output': response_data.get('output', ''),
                    'namespace': response_data.get('namespace', ''),
                    'session_id': session_id,
                    'execution_time_ms': response_data.get('executionTimeMs', 0)
                },
                error=response_data.get('errorMessage')
            )
            
        except Exception as e:
            return self.format_response(
                success=False,
                data=None,
                error=f"Tool execution failed: {str(e)}"
            )
```

## Phase 2: Additional Tools

### execute_sql Tool
**SQL Query Execution:**
```python
@mcp.tool
async def execute_sql(
    query: str,
    session_id: str = None,
    parameters: List[str] = None
) -> dict:
    """Execute SQL query in IRIS session.
    
    Args:
        query: SQL query to execute
        session_id: Session identifier
        parameters: Query parameters for prepared statements
        
    Returns:
        dict: Query results with column metadata
    """
```

### get_namespace_info Tool
**Namespace Exploration:**
```python
@mcp.tool
async def get_namespace_info(
    namespace: str = None,
    include_globals: bool = False,
    include_routines: bool = False
) -> dict:
    """Get information about IRIS namespace.
    
    Args:
        namespace: Target namespace (current if not specified)
        include_globals: Include global variable information
        include_routines: Include routine/class information
        
    Returns:
        dict: Namespace structure and metadata
    """
```

### manage_session Tool
**Session Lifecycle Management:**
```python
@mcp.tool
async def manage_session(
    action: str,
    session_id: str = None,
    **kwargs
) -> dict:
    """Manage IRIS session lifecycle.
    
    Args:
        action: create|destroy|list|status
        session_id: Target session ID
        **kwargs: Action-specific parameters
        
    Returns:
        dict: Session management result
    """
```

## Error Handling Patterns

### Tool-Level Error Handling
**Standardized Error Response:**
```python
class MCPToolError(Exception):
    def __init__(self, code: str, message: str, details: Dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

def handle_tool_error(func):
    """Decorator for consistent error handling."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except iris.IRISError as e:
            return {
                'success': False,
                'error': {
                    'code': 'IRIS_ERROR',
                    'message': str(e),
                    'type': 'connection'
                }
            }
        except MCPToolError as e:
            return {
                'success': False,
                'error': {
                    'code': e.code,
                    'message': e.message,
                    'details': e.details
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'code': 'UNEXPECTED_ERROR',
                    'message': str(e),
                    'type': 'system'
                }
            }
    return wrapper
```

### Input Validation
**Parameter Validation:**
```python
from pydantic import BaseModel, validator

class ExecuteCommandRequest(BaseModel):
    command: str
    session_id: str = None
    timeout: int = 30
    
    @validator('command')
    def command_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Command cannot be empty')
        return v.strip()
    
    @validator('timeout')
    def timeout_range(cls, v):
        if not 1 <= v <= 300:
            raise ValueError('Timeout must be between 1 and 300 seconds')
        return v
```

## Tool Registration and Discovery

### Dynamic Tool Loading
**Tool Registry:**
```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}
        
    def register_tool(self, name: str, tool_class: type):
        """Register tool class with registry."""
        self.tools[name] = tool_class
        
    def get_tool_definitions(self) -> List[Dict]:
        """Get MCP tool definitions for all registered tools."""
        definitions = []
        for name, tool_class in self.tools.items():
            definitions.append({
                'name': name,
                'description': tool_class.__doc__,
                'inputSchema': tool_class.get_input_schema()
            })
        return definitions
```

### Tool Configuration
**Environment-Based Configuration:**
```python
# Tool enabling/disabling via environment
ENABLED_TOOLS = os.getenv('MCP_ENABLED_TOOLS', 'execute_command').split(',')

# Security levels for tools
TOOL_SECURITY_LEVELS = {
    'execute_command': 'basic',
    'execute_sql': 'standard', 
    'manage_session': 'advanced',
    'system_admin': 'restricted'
}
```

## Performance and Scalability

### Async Tool Execution
**Concurrent Tool Processing:**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncToolExecutor:
    def __init__(self, max_workers: int = 5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    async def execute_tool(self, tool: IRISMCPTool, **kwargs):
        """Execute tool in thread pool to avoid blocking."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            lambda: tool.execute(**kwargs)
        )
```

### Tool Caching
**Response Caching for Read-Only Operations:**
```python
from functools import lru_cache
import hashlib

class CachingToolWrapper:
    def __init__(self, tool: IRISMCPTool, cache_size: int = 128):
        self.tool = tool
        self.cache_size = cache_size
        
    @lru_cache(maxsize=128)
    def _cached_execute(self, cache_key: str, **kwargs):
        """Execute with caching for idempotent operations."""
        return self.tool.execute(**kwargs)
        
    def should_cache(self, tool_name: str, **kwargs) -> bool:
        """Determine if operation should be cached."""
        read_only_tools = ['get_namespace_info', 'get_session_status']
        return tool_name in read_only_tools
```

## Security Integration

### Tool-Level Authorization
**Permission Checking:**
```python
class ToolSecurityManager:
    def __init__(self):
        self.permissions = {}
        
    def check_permission(self, user: str, tool_name: str) -> bool:
        """Check if user can execute specific tool."""
        required_level = TOOL_SECURITY_LEVELS.get(tool_name, 'basic')
        user_level = self.get_user_security_level(user)
        return self._compare_levels(user_level, required_level)
        
    def audit_tool_execution(self, user: str, tool_name: str, 
                           success: bool, execution_time: float):
        """Log tool execution for audit trail."""
        pass
