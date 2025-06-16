# Implementation Guide - IRIS Terminal MCP Server

## Quick Start Implementation Steps

### Step 1: IRIS Backend Setup (Day 1)
**Create Basic Session Management:**
```objectscript
// Create src/SessionMCP/Core/Session.cls
Class SessionMCP.Core.Session Extends %RegisteredObject
{
    /// Generate new session ID and store in globals
    ClassMethod CreateSession(pNamespace As %String = "USER") As %String
    {
        Set tSessionId = $System.Util.CreateGUID()
        Set ^SessionMCP.State(tSessionId, "created") = $HOROLOG
        Set ^SessionMCP.State(tSessionId, "namespace") = pNamespace
        
        Set tResult = {}
        Set tResult.status = "success"
        Set tResult.sessionId = tSessionId
        Set tResult.namespace = pNamespace
        Quit tResult.%ToJSON()
    }
    
    /// Execute command with basic I/O capture
    ClassMethod ExecuteCommand(pSessionId As %String, pCommand As %String) As %String
    {
        Set tResult = {}
        Try {
            If '..ValidateSession(pSessionId) {
                Set tResult.status = "error"
                Set tResult.errorMessage = "Invalid session"
                Quit
            }
            
            // Update access time
            Set ^SessionMCP.State(pSessionId, "lastAccess") = $HOROLOG
            
            // Execute with error trapping
            Set $ZTrap = "ExecuteError"
            XECUTE pCommand
            
            Set tResult.status = "success"
            Set tResult.output = "Command executed"
            Set tResult.sessionId = pSessionId
            
        } Catch (ex) {
            Set tResult.status = "error"
            Set tResult.errorMessage = ex.DisplayString()
        }
        Quit tResult.%ToJSON()
        
    ExecuteError:
        Set tResult.status = "error" 
        Set tResult.errorMessage = $ZError
        Quit tResult.%ToJSON()
    }
    
    ClassMethod ValidateSession(pSessionId As %String) As %Boolean
    {
        Quit $Data(^SessionMCP.State(pSessionId))
    }
}
```

### Step 2: Python MCP Client Setup (Day 2)
**Project Structure:**
```
iris-mcp-server/
├── main.py              # MCP server entry point
├── iris_connector.py    # IRIS connection manager
├── requirements.txt     # Dependencies
└── config.py           # Configuration
```

**main.py - Core MCP Server:**
```python
#!/usr/bin/env python3
import asyncio
import json
import sys
from iris_connector import IRISConnector

class IRISMCPServer:
    def __init__(self):
        self.connector = IRISConnector()
        
    async def start(self):
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                if not line:
                    break
                    
                request = json.loads(line.strip())
                response = await self.handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
                
            except Exception as e:
                error_response = {
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {'code': -32603, 'message': str(e)}
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
    
    async def handle_request(self, request):
        if request.get('method') == 'tools/list':
            return {
                'jsonrpc': '2.0',
                'id': request.get('id'),
                'result': {'tools': [{
                    'name': 'execute_command',
                    'description': 'Execute ObjectScript command',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'command': {'type': 'string'},
                            'session_id': {'type': 'string'}
                        },
                        'required': ['command']
                    }
                }]}
            }
        elif request.get('method') == 'tools/call':
            args = request['params']['arguments']
            result = await self.execute_command(args)
            return {
                'jsonrpc': '2.0',
                'id': request.get('id'),
                'result': {'content': [{'type': 'text', 'text': json.dumps(result)}]}
            }
    
    async def execute_command(self, args):
        command = args['command']
        session_id = args.get('session_id')
        
        if not session_id:
            session_response = self.connector.create_session()
            session_data = json.loads(session_response)
            session_id = session_data['sessionId']
        
        result = self.connector.execute_command(session_id, command)
        return json.loads(result)

if __name__ == '__main__':
    server = IRISMCPServer()
    asyncio.run(server.start())
```

**iris_connector.py - IRIS Interface:**
```python
import iris
import os

class IRISConnector:
    def __init__(self):
        self.connection = None
        self.config = {
            'hostname': os.getenv('IRIS_HOSTNAME', 'localhost'),
            'port': int(os.getenv('IRIS_PORT', '1972')),
            'namespace': os.getenv('IRIS_NAMESPACE', 'USER'),
            'username': os.getenv('IRIS_USERNAME', '_SYSTEM'),
            'password': os.getenv('IRIS_PASSWORD', 'SYS')
        }
    
    def connect(self):
        if not self.connection:
            self.connection = iris.connect(
                self.config['hostname'],
                self.config['port'],
                self.config['namespace'],
                self.config['username'],
                self.config['password']
            )
        return self.connection
    
    def create_session(self, namespace="USER"):
        connection = self.connect()
        return connection.invoke_classmethod(
            "SessionMCP.Core.Session",
            "CreateSession", 
            [namespace]
        )
    
    def execute_command(self, session_id, command):
        connection = self.connect()
        return connection.invoke_classmethod(
            "SessionMCP.Core.Session",
            "ExecuteCommand",
            [session_id, command]
        )
```

### Step 3: Integration Testing (Day 3)
**Test IRIS Backend:**
```objectscript
// Test in IRIS Terminal
Set tResult = ##class(SessionMCP.Core.Session).CreateSession("USER")
Write tResult, !

Set tData = {}.%FromJSON(tResult)
Set tSessionId = tData.sessionId

Set tResult = ##class(SessionMCP.Core.Session).ExecuteCommand(tSessionId, "WRITE 2+2")
Write tResult, !
```

**Test Python Client:**
```bash
# Install dependencies
pip install intersystems-iris

# Set environment variables
export IRIS_HOSTNAME=localhost
export IRIS_PORT=1972
export IRIS_USERNAME=_SYSTEM
export IRIS_PASSWORD=SYS

# Test connection
python -c "import iris; print('IRIS connection OK')"

# Run MCP server
python main.py
```

## Key Implementation Patterns

### IRIS ObjectScript Patterns
**Status Handling:**
```objectscript
Method SomeMethod() As %Status
{
    Set tSC = $$$OK
    Try {
        // Implementation
    } Catch (ex) {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}
```

**Global Storage:**
```objectscript
// Session state
Set ^SessionMCP.State(sessionId, "property") = value
Set tValue = $Get(^SessionMCP.State(sessionId, "property"), defaultValue)

// Session cleanup
Kill ^SessionMCP.State(sessionId)
```

**Native API ClassMethods:**
```objectscript
/// Method signature must return %String for JSON
ClassMethod PublicMethod(pParam1 As %String, pParam2 As %Integer) As %String
{
    Set tResult = {}
    // Implementation
    Quit tResult.%ToJSON()
}
```

### Python MCP Patterns
**Async Request Handling:**
```python
async def handle_request(self, request):
    method = request.get('method')
    if method == 'tools/call':
        return await self.execute_tool(request['params'])
    elif method == 'tools/list':
        return self.list_tools()
```

**Error Response Format:**
```python
def error_response(self, request_id, code, message):
    return {
        'jsonrpc': '2.0',
        'id': request_id,
        'error': {'code': code, 'message': message}
    }
```

**IRIS Connection Management:**
```python
def ensure_connection(self):
    if not self.connection or not self.test_connection():
        self.connection = iris.connect(...)
    return self.connection
```

## Essential Configuration

### Environment Variables
```bash
# Required IRIS connection settings
export IRIS_HOSTNAME=localhost
export IRIS_PORT=1972
export IRIS_NAMESPACE=USER
export IRIS_USERNAME=_SYSTEM
export IRIS_PASSWORD=SYS

# Optional MCP settings
export MCP_ENABLED_TOOLS=execute_command
export MCP_SESSION_TIMEOUT=3600
export MCP_MAX_OUTPUT_SIZE=65536
```

### MCP Client Configuration
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

## Implementation Validation Checklist

### IRIS Backend Validation
- [ ] SessionMCP.Core.Session class compiles without errors
- [ ] CreateSession method returns valid JSON with sessionId
- [ ] ExecuteCommand method handles simple commands (e.g., "WRITE 2+2")
- [ ] ValidateSession method correctly identifies valid/invalid sessions
- [ ] Global storage ^SessionMCP.State functions correctly
- [ ] Error handling captures and returns meaningful error messages

### Python Client Validation
- [ ] iris package imports successfully
- [ ] Connection to IRIS establishes without errors
- [ ] invoke_classmethod calls work for CreateSession and ExecuteCommand
- [ ] JSON parsing of IRIS responses works correctly
- [ ] MCP protocol tools/list response follows specification
- [ ] MCP protocol tools/call response follows specification
- [ ] STDIO transport reads and writes JSON messages correctly

### End-to-End Validation
- [ ] MCP client can list available tools
- [ ] MCP client can execute simple ObjectScript commands
- [ ] Session persistence works across multiple commands
- [ ] Error scenarios return appropriate error responses
- [ ] No memory leaks or connection issues in extended testing

## Common Implementation Issues

### IRIS Backend Issues
**Compilation Errors:**
- Verify no underscore characters in parameter names
- Ensure all commands are properly indented
- Check macro syntax uses $$$ not $$

**Runtime Errors:**
- Validate JSON formatting in return values
- Check global storage permissions
- Verify namespace access permissions

### Python Client Issues
**Connection Problems:**
- Verify IRIS Native API is enabled
- Check firewall settings for port 1972
- Validate credentials and permissions

**Protocol Issues:**
- Ensure JSON-RPC 2.0 format compliance
- Validate tool input schema definitions
- Check response content format

## Next Implementation Steps

### Immediate (Week 1)
1. **Deploy Basic Classes**: Create SessionMCP.Core.Session in IRIS
2. **Test IRIS Backend**: Validate ClassMethods work via Terminal
3. **Create Python Client**: Implement basic MCP server structure
4. **Test Integration**: End-to-end command execution

### Short-term (Week 2-3)
1. **Enhance Error Handling**: Improve error categorization and messaging
2. **Add I/O Capture**: Implement basic output capture for WRITE commands
3. **Session Management**: Add session timeout and cleanup
4. **Documentation**: Create user setup guide

### Medium-term (Month 2)
1. **Additional Tools**: Implement execute_sql tool
2. **HTTP Transport**: Add FastAPI-based HTTP mode
3. **Production Features**: Add authentication and monitoring
4. **Testing Framework**: Comprehensive test suite

## Success Criteria Verification

### Functional Success
- AI agent executes "WRITE 2+2" and receives "4" in response
- Session persists across multiple command executions
- Error handling provides clear feedback for invalid commands

### Performance Success
- Command execution completes in <2 seconds
- Session creation completes in <1 second
- Memory usage remains stable over extended testing

### Operational Success
- Setup takes <5 minutes for new users
- Clear error messages guide troubleshooting
- Basic monitoring shows system health

This implementation guide provides the foundation to begin building the IRIS Terminal MCP Server. Focus on getting the MVP working first, then incrementally add features based on the expansion roadmap.
