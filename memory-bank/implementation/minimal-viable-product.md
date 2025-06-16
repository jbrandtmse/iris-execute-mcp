# Minimal Viable Product - IRIS Terminal MCP Server

## MVP Scope Definition

### Core MVP Features
**Single Tool Implementation:**
- `execute_command` MCP tool only
- Basic session management
- STDIO transport mode
- Essential error handling
- Native API connectivity

**Success Criteria:**
1. AI agent can execute simple ObjectScript commands
2. Session persists across multiple commands
3. Basic error handling and reporting
4. Output matches IRIS Terminal behavior
5. Setup time under 5 minutes

### MVP Exclusions
**Features Deferred to Phase 2:**
- Multiple tool types (execute_sql, get_namespace_info)
- HTTP transport mode
- Advanced session management
- Complex I/O redirection
- Production security features
- Performance optimization

## MVP Implementation Plan

### Phase 1A: IRIS Backend Core (Week 1)
**Deliverables:**
- SessionMCP.Core.Session class (basic implementation)
- SessionMCP.Transport.NativeConnector class
- SessionMCP.IO.OutputCapture class (simplified)
- Basic global storage structure

**Implementation Order:**
1. Create basic Session class with essential methods
2. Implement simple command execution with try/catch
3. Add basic I/O redirection using %Device
4. Create Native API ClassMethods for Python integration
5. Set up global storage for session state

### Phase 1B: Python MCP Client (Week 2)
**Deliverables:**
- Python MCP server with single execute_command tool
- IRIS Native API connection management
- JSON-RPC 2.0 protocol implementation
- STDIO transport layer
- Basic configuration management

**Implementation Order:**
1. Set up Python project structure and dependencies
2. Implement IRIS connection manager
3. Create execute_command tool with MCP decorators
4. Add JSON-RPC message handling
5. Implement STDIO transport

### Phase 1C: Integration and Testing (Week 3)
**Deliverables:**
- End-to-end integration testing
- Basic unit tests for core components
- Error handling validation
- Performance baseline
- MVP documentation

**Implementation Order:**
1. Test IRIS backend classes independently
2. Test Python client independently
3. End-to-end integration testing
4. Error scenario testing
5. Performance and load testing

## MVP Technical Specifications

### IRIS Backend MVP Classes

#### SessionMCP.Core.Session (MVP Version)
```objectscript
/// <h3>MVP IRIS Terminal Session for MCP</h3>
/// <p>Minimal implementation for MVP release.</p>
Class SessionMCP.Core.Session Extends %RegisteredObject
{
    Property SessionId As %String;
    Property Namespace As %String [ InitialExpression = "USER" ];
    Property Created As %TimeStamp;
    Property LastAccess As %TimeStamp;
    
    Parameter TIMEOUT = 30;
    Parameter MAXOUTPUT = 65536;  // 64KB limit for MVP
    
    /// <h3>Execute Command (MVP)</h3>
    /// <p>Simple command execution for MVP.</p>
    ClassMethod ExecuteCommand(pSessionId As %String, pCommand As %String) As %String
    {
        Set tSC = $$$OK
        Set tResult = {}
        
        Try {
            // Validate session
            If '..ValidateSession(pSessionId) {
                Set tResult.status = "error"
                Set tResult.errorMessage = "Invalid session ID"
                Quit
            }
            
            // Update last access
            Set ^SessionMCP.State(pSessionId, "lastAccess") = $HOROLOG
            
            // Simple command execution
            Set tOutput = ""
            Set $ZTrap = "ExecuteError"
            
            // Capture output (simplified)
            Do ##class(%Device).ReDirectIO($$$YES)
            XECUTE pCommand
            Do ##class(%Device).ReDirectIO($$$NO)
            
            // Get captured output (simplified - just return success for MVP)
            Set tResult.status = "success"
            Set tResult.output = "Command executed successfully"
            Set tResult.namespace = $NAMESPACE
            Set tResult.sessionId = pSessionId
            
        } Catch (ex) {
            Do ##class(%Device).ReDirectIO($$$NO)
            Set tResult.status = "error"
            Set tResult.errorMessage = ex.DisplayString()
        }
        
        Quit tResult.%ToJSON()
        
    ExecuteError:
        Do ##class(%Device).ReDirectIO($$$NO)
        Set tResult.status = "error"
        Set tResult.errorMessage = "Command execution error: "_$ZError
        Quit tResult.%ToJSON()
    }
    
    /// <h3>Create Session (MVP)</h3>
    /// <p>Simple session creation for MVP.</p>
    ClassMethod CreateSession(pNamespace As %String = "USER") As %String
    {
        Set tSessionId = $System.Util.CreateGUID()
        Set ^SessionMCP.State(tSessionId, "created") = $HOROLOG
        Set ^SessionMCP.State(tSessionId, "lastAccess") = $HOROLOG
        Set ^SessionMCP.State(tSessionId, "namespace") = pNamespace
        
        Set tResult = {}
        Set tResult.status = "success"
        Set tResult.sessionId = tSessionId
        Set tResult.namespace = pNamespace
        
        Quit tResult.%ToJSON()
    }
    
    /// <h3>Validate Session (MVP)</h3>
    /// <p>Simple session validation for MVP.</p>
    ClassMethod ValidateSession(pSessionId As %String) As %Boolean
    {
        If '$Data(^SessionMCP.State(pSessionId)) Quit 0
        
        // Check if expired (24 hour timeout for MVP)
        Set tCreated = $Get(^SessionMCP.State(pSessionId, "created"))
        If ($HOROLOG - tCreated) > 86400 Quit 0
        
        Quit 1
    }
}
```

### Python MCP Client MVP

#### Project Structure
```
iris-mcp-server/
├── src/
│   ├── __init__.py
│   ├── main.py              # MCP server entry point
│   ├── iris_connector.py    # IRIS connection management
│   ├── tools/
│   │   ├── __init__.py
│   │   └── execute_command.py
│   └── transport/
│       ├── __init__.py
│       └── stdio.py
├── requirements.txt
├── setup.py
├── config.yaml
└── README.md
```

#### Main MCP Server (main.py)
```python
#!/usr/bin/env python3
"""
IRIS Terminal MCP Server - MVP Implementation
Provides execute_command tool via STDIO transport.
"""

import asyncio
import json
import sys
from typing import Dict, Any

from iris_connector import IRISConnector
from tools.execute_command import ExecuteCommandTool
from transport.stdio import STDIOTransport

class IRISMCPServer:
    def __init__(self):
        self.connector = IRISConnector()
        self.tools = {
            'execute_command': ExecuteCommandTool(self.connector)
        }
        self.transport = STDIOTransport()
        
    async def start(self):
        """Start MCP server with STDIO transport."""
        await self.transport.start(self.handle_request)
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request."""
        try:
            if request.get('method') == 'tools/call':
                tool_name = request['params']['name']
                arguments = request['params']['arguments']
                
                if tool_name in self.tools:
                    result = await self.tools[tool_name].execute(**arguments)
                    return {
                        'jsonrpc': '2.0',
                        'id': request.get('id'),
                        'result': {'content': [{'type': 'text', 'text': json.dumps(result)}]}
                    }
                else:
                    return {
                        'jsonrpc': '2.0',
                        'id': request.get('id'),
                        'error': {'code': -32601, 'message': f'Tool not found: {tool_name}'}
                    }
            elif request.get('method') == 'tools/list':
                return {
                    'jsonrpc': '2.0',
                    'id': request.get('id'),
                    'result': {'tools': [
                        {
                            'name': 'execute_command',
                            'description': 'Execute ObjectScript command in IRIS session',
                            'inputSchema': {
                                'type': 'object',
                                'properties': {
                                    'command': {'type': 'string', 'description': 'ObjectScript command'},
                                    'session_id': {'type': 'string', 'description': 'Session ID (optional)'}
                                },
                                'required': ['command']
                            }
                        }
                    ]}
                }
        except Exception as e:
            return {
                'jsonrpc': '2.0',
                'id': request.get('id'),
                'error': {'code': -32603, 'message': str(e)}
            }

if __name__ == '__main__':
    server = IRISMCPServer()
    asyncio.run(server.start())
```

#### IRIS Connector (iris_connector.py)
```python
"""IRIS Native API connection management for MVP."""

import iris
import os
from typing import Optional

class IRISConnector:
    def __init__(self):
        self.connection: Optional[iris.IRISConnection] = None
        self.config = {
            'hostname': os.getenv('IRIS_HOSTNAME', 'localhost'),
            'port': int(os.getenv('IRIS_PORT', '1972')),
            'namespace': os.getenv('IRIS_NAMESPACE', 'USER'),
            'username': os.getenv('IRIS_USERNAME', '_SYSTEM'),
            'password': os.getenv('IRIS_PASSWORD', 'SYS')
        }
        
    def connect(self) -> iris.IRISConnection:
        """Establish connection to IRIS."""
        if not self.connection:
            self.connection = iris.connect(
                self.config['hostname'],
                self.config['port'],
                self.config['namespace'],
                self.config['username'],
                self.config['password']
            )
        return self.connection
        
    def execute_command(self, session_id: str, command: str) -> str:
        """Execute command via Native API."""
        connection = self.connect()
        return connection.invoke_classmethod(
            "SessionMCP.Core.Session",
            "ExecuteCommand",
            [session_id, command]
        )
        
    def create_session(self, namespace: str = "USER") -> str:
        """Create new session via Native API."""
        connection = self.connect()
        return connection.invoke_classmethod(
            "SessionMCP.Core.Session", 
            "CreateSession",
            [namespace]
        )
```

#### Execute Command Tool (tools/execute_command.py)
```python
"""Execute command tool implementation."""

import json
from typing import Dict, Any

class ExecuteCommandTool:
    def __init__(self, connector):
        self.connector = connector
        
    async def execute(self, command: str, session_id: str = None) -> Dict[str, Any]:
        """Execute ObjectScript command."""
        try:
            # Create session if not provided
            if not session_id:
                session_response = self.connector.create_session()
                session_data = json.loads(session_response)
                if session_data['status'] != 'success':
                    return {'success': False, 'error': 'Failed to create session'}
                session_id = session_data['sessionId']
            
            # Execute command
            result = self.connector.execute_command(session_id, command)
            result_data = json.loads(result)
            
            return {
                'success': result_data['status'] == 'success',
                'output': result_data.get('output', ''),
                'error': result_data.get('errorMessage'),
                'session_id': session_id,
                'namespace': result_data.get('namespace', '')
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
```

## MVP Testing Strategy

### Unit Tests
**IRIS Backend Tests:**
```objectscript
Class SessionMCP.Tests.MVPTest Extends %UnitTest.TestCase
{
    Method TestSessionCreation()
    {
        Set tResult = ##class(SessionMCP.Core.Session).CreateSession("USER")
        Set tData = {}.%FromJSON(tResult)
        Do $$$AssertEquals(tData.status, "success")
        Do $$$AssertNotEquals(tData.sessionId, "")
    }
    
    Method TestCommandExecution()
    {
        // Create session
        Set tSessionResult = ##class(SessionMCP.Core.Session).CreateSession("USER")
        Set tSessionData = {}.%FromJSON(tSessionResult)
        Set tSessionId = tSessionData.sessionId
        
        // Execute simple command
        Set tResult = ##class(SessionMCP.Core.Session).ExecuteCommand(tSessionId, "WRITE 2+2")
        Set tData = {}.%FromJSON(tResult)
        Do $$$AssertEquals(tData.status, "success")
    }
}
```

**Python Tests:**
```python
import unittest
from unittest.mock import Mock, patch
from tools.execute_command import ExecuteCommandTool

class TestExecuteCommand(unittest.TestCase):
    def setUp(self):
        self.mock_connector = Mock()
        self.tool = ExecuteCommandTool(self.mock_connector)
        
    async def test_execute_with_session(self):
        self.mock_connector.execute_command.return_value = '{"status":"success","output":"4"}'
        
        result = await self.tool.execute("WRITE 2+2", "test-session")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['output'], "4")
```

### Integration Tests
**End-to-End Test:**
1. Start Python MCP server
2. Send MCP request via STDIO
3. Verify IRIS command execution
4. Validate response format
5. Test error handling scenarios

## MVP Deployment

### Requirements
**System Requirements:**
- IRIS 2022.1+ with Native API enabled
- Python 3.8+ with intersystems-iris package
- Environment variables for IRIS connection

**Installation Steps:**
1. Install Python dependencies: `pip install intersystems-iris`
2. Deploy IRIS classes to src/SessionMCP
3. Configure environment variables
4. Test connectivity: `python -c "import iris; print('OK')"`
5. Run MCP server: `python main.py`

### Configuration
**Environment Variables:**
```bash
export IRIS_HOSTNAME=localhost
export IRIS_PORT=1972
export IRIS_NAMESPACE=USER
export IRIS_USERNAME=_SYSTEM
export IRIS_PASSWORD=SYS
```

**MCP Client Configuration:**
```json
{
  "mcpServers": {
    "iris-terminal": {
      "command": "python",
      "args": ["/path/to/iris-mcp-server/main.py"],
      "env": {
        "IRIS_HOSTNAME": "localhost",
        "IRIS_PORT": "1972"
      }
    }
  }
}
```

## MVP Success Metrics

### Functional Metrics
- [ ] Command execution success rate > 95%
- [ ] Session creation time < 1 second
- [ ] Basic error handling working
- [ ] Output capture functional (even if simplified)

### Performance Metrics
- [ ] Command response time < 2 seconds
- [ ] Memory usage stable over 100 commands
- [ ] No memory leaks in 1-hour test

### User Experience Metrics
- [ ] Setup time < 5 minutes
- [ ] Clear error messages
- [ ] Basic functionality documentation
- [ ] Working example commands

## MVP Limitations and Known Issues

### Known Limitations
1. **Simplified I/O Capture**: Output capture is basic, may not handle all terminal formatting
2. **Single Tool**: Only execute_command available
3. **Basic Error Handling**: Limited error categorization and recovery
4. **No Advanced Security**: Basic session validation only
5. **STDIO Only**: No HTTP transport mode

### Acceptable MVP Issues
- Output formatting may not match Terminal exactly
- Limited command timeout handling
- Basic session cleanup only
- No advanced debugging features
- Minimal logging and monitoring

### Post-MVP Improvements
- Enhanced I/O redirection based on TerminalAgent patterns
- Multiple tool types (execute_sql, get_namespace_info)
- HTTP transport mode
- Advanced error handling and recovery
- Production security features
- Performance optimization and caching
