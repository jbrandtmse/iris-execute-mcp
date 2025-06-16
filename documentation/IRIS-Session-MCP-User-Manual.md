# IRIS Session MCP Server - User Manual

## Overview

The IRIS Session MCP Server enables AI agents (like Claude Desktop and Cline) to execute ObjectScript commands in persistent IRIS sessions through the Model Context Protocol (MCP). This provides seamless integration between AI tools and InterSystems IRIS databases.

**🎉 Production Ready** - Single file implementation with proven IRIS connectivity and MCP protocol integration.

## Features

- **Persistent Sessions**: Maintain IRIS sessions across multiple AI interactions with GUID-based session management
- **ObjectScript Execution**: Execute any ObjectScript command within AI workflows with sub-millisecond response times
- **Session Management**: Create, validate, monitor, and cleanup sessions with 24-hour timeout
- **Security Compliance**: Proper IRIS privilege validation with `%Development:USE` security checks
- **Error Handling**: Comprehensive error reporting with session isolation and structured responses
- **Universal Compatibility**: Works with any MCP-compatible AI client through STDIO transport
- **Performance Optimized**: Synchronous IRIS calls eliminate timeout issues

---

## Installation Guide

### Prerequisites

1. **InterSystems IRIS Installation**
   - IRIS 2023.1 or later
   - Access to a namespace (HSCUSTOM or custom)
   - Compilation permissions for ObjectScript classes
   - `%Development:USE` privilege for XECUTE command execution

2. **Python Environment**
   - Python 3.8 or later
   - pip package manager
   - Virtual environment (recommended)

3. **AI Client**
   - Claude Desktop (Anthropic) or
   - Cline (VS Code extension) or
   - Any MCP-compatible client

### Step 1: Set Up Virtual Environment (Recommended)

1. **Navigate to your project directory**
   ```bash
   cd d:/iris-session-mcp
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS  
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Required packages:
   - `intersystems-irispython>=5.0.0` - IRIS Native API for Python
   - `mcp>=1.0.0` - Model Context Protocol SDK
   - `pydantic>=2.0.0` - Data validation

### Step 2: Install IRIS Components

1. **Compile the ObjectScript classes**
   ```objectscript
   Do $System.OBJ.CompilePackage("SessionMCP")
   ```

2. **Verify installation with unit testing**
   ```objectscript
   Do ##class(SessionMCP.Core.Tests.SessionTest).%RunTest()
   ```
   
   Expected output: All tests should pass with detailed results.

3. **Test manual functionality**
   ```objectscript
   Do ##class(SessionMCP.Core.Tests.ManualTest).RunAllTests()
   ```
   
   Expected output: `ALL TESTS PASSED! ✅`

### Step 3: Validate Python MCP Server

1. **Test the production MCP server**
   ```bash
   python validate_mvp.py
   ```
   
   Expected output: `🎉 ALL TESTS PASSED! The Python MCP client is ready for deployment.`

2. **Test direct IRIS connectivity**
   ```bash
   python test_full_workflow.py
   ```
   
   Expected output: Shows successful session creation and command execution.

### Step 4: Verify Complete Integration

1. **Test production server startup**
   ```bash
   python iris_session_mcp.py
   ```
   
   Look for:
   ```
   INFO:__main__:Starting IRIS Session MCP Server
   INFO:__main__:✅ IRIS connectivity test passed
   ```

2. **Verify security compliance**
   The server will automatically validate `%Development:USE` privileges during startup.

---

## MCP Client Configuration

### Claude Desktop

**Configuration File Location:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Add to claude_desktop_config.json:**
```json
{
  "mcpServers": {
    "iris-session-mcp": {
      "command": "D:/iris-session-mcp/venv/Scripts/python.exe",
      "args": ["D:/iris-session-mcp/iris_session_mcp.py"],
      "env": {
        "IRIS_HOSTNAME": "localhost",
        "IRIS_PORT": "1972", 
        "IRIS_NAMESPACE": "HSCUSTOM",
        "IRIS_USERNAME": "_SYSTEM",
        "IRIS_PASSWORD": "_SYSTEM"
      },
      "transportType": "stdio"
    }
  }
}
```

### Cline (VS Code Extension)

**MCP Settings Configuration:**
```json
{
  "iris-session-mcp": {
    "autoApprove": [
      "execute_command",
      "list_sessions"
    ],
    "disabled": false,
    "timeout": 60,
    "command": "D:/iris-session-mcp/venv/Scripts/python.exe",
    "args": [
      "D:/iris-session-mcp/iris_session_mcp.py"
    ],
    "env": {
      "IRIS_HOSTNAME": "localhost",
      "IRIS_PORT": "1972",
      "IRIS_NAMESPACE": "HSCUSTOM", 
      "IRIS_USERNAME": "_SYSTEM",
      "IRIS_PASSWORD": "_SYSTEM"
    },
    "transportType": "stdio"
  }
}
```

### Configuration Notes

**Important Configuration Details:**
- ✅ Use full absolute paths to Python executable and script
- ✅ Use virtual environment Python path for dependency isolation
- ✅ Set `transportType` to `"stdio"` for universal compatibility
- ✅ Include environment variables for IRIS connection
- ✅ Restart your MCP client after configuration changes

**Security Configuration:**
```json
"env": {
  "IRIS_HOSTNAME": "your-iris-server",
  "IRIS_PORT": "1972",
  "IRIS_NAMESPACE": "YOUR_NAMESPACE", 
  "IRIS_USERNAME": "your_secure_user",
  "IRIS_PASSWORD": "your_secure_password"
}
```

---

## Available MCP Tools

### execute_command

Executes ObjectScript commands in persistent IRIS sessions with automatic session management.

**Parameters:**
- `command` (string, required): ObjectScript command to execute
- `session_id` (string, optional): Specific session ID to use (auto-created if not provided)
- `namespace` (string, optional): IRIS namespace for new sessions (default: HSCUSTOM)
- `timeout` (integer, optional): Command timeout in seconds (default: 30)

**Response Format:**
```json
{
  "status": "success",
  "sessionId": "GUID-based-session-id", 
  "namespace": "HSCUSTOM",
  "executionTimeMs": 0,
  "output": "Command executed successfully"
}
```

**Usage Examples:**
```
Execute: WRITE "Hello World from IRIS!"
Execute: SET ^MyGlobal("test") = $HOROLOG  
Execute: Do ##class(MyPackage.MyClass).MyMethod()
Execute in SAMPLES namespace: WRITE $NAMESPACE
```

### list_sessions

Lists all active IRIS sessions with comprehensive session metadata.

**Parameters:**
- None required

**Response Format:**
```
📋 Active Sessions (X total)

Session ID: A1B2C3D4-E5F6-7890-ABCD-123456789ABC
  Namespace: HSCUSTOM
  Created: 2025-06-16 00:45:01
  Last Access: 2025-06-16 00:45:01  
  Status: ACTIVE
```

**Usage Examples:**
```
"How many IRIS sessions are currently active?"
"Show me all active sessions"
"List current session details"
```

---

## Usage Examples

### Hello World Integration Test

**User Request:**
```
Execute this ObjectScript command: WRITE "Hello World from IRIS via MCP!"
```

**Expected Response:**
```
✅ Command executed successfully
Session: [GUID-SESSION-ID]
Namespace: HSCUSTOM
Execution time: 0ms

Output:
Command executed successfully
```

### Session Persistence Workflow

**User Request:**
```
1. Set a global: SET ^MyTest = "Hello"
2. Read it back: WRITE ^MyTest
3. Check the session details
```

The AI will execute all commands in the same persistent session, maintaining context throughout.

### Multi-Namespace Operations

**User Request:**
```
Create a session in the SAMPLES namespace and explore the available classes
```

**AI Usage:**
```
execute_command("WRITE $NAMESPACE", namespace="SAMPLES")
execute_command("Do $SYSTEM.OBJ.ShowPackages()")
```

### Session Management

**User Request:**
```
Show me all active IRIS sessions and their details
```

**AI Usage:**
```
list_sessions()
```

---

## Architecture and Performance

### Production Implementation

**Single File Architecture:**
- ✅ **Production File**: `iris_session_mcp.py` - Consolidated implementation
- ✅ **Real IRIS Connectivity**: Via `intersystems-irispython` Native API
- ✅ **Synchronous IRIS Calls**: `call_iris_sync()` function eliminates timeout issues
- ✅ **Security Validation**: Proper `%Development:USE` privilege checking
- ✅ **Session Management**: GUID-based sessions with persistent global storage
- ✅ **MCP Protocol**: Full STDIO transport compliance

**Performance Metrics:**
- ✅ **Command Execution**: 0ms for simple commands, sub-second for complex operations
- ✅ **Session Creation**: <1 second with GUID generation
- ✅ **MCP Response Time**: Immediate (no timeout issues)
- ✅ **Memory Usage**: Minimal footprint with efficient implementation

**Quality Assurance:**
- ✅ **Security Compliance**: IRIS privilege validation enforced
- ✅ **Error Handling**: Comprehensive structured error responses
- ✅ **Session Isolation**: Individual session state management
- ✅ **Resource Cleanup**: 24-hour session timeout with automatic cleanup

---

## Troubleshooting

### Common Issues

**1. "Not connected" MCP Error**
- Verify virtual environment is activated: `venv\Scripts\activate`
- Check Python path in MCP configuration points to virtual environment
- Ensure `iris_session_mcp.py` runs without errors manually
- Restart MCP client after configuration changes

**2. "Cannot connect to IRIS"** 
- Verify IRIS is running on specified hostname:port
- Check username/password credentials in environment variables
- Ensure network connectivity and firewall settings
- Test connection: `python test_full_workflow.py`

**3. "Class SessionMCP.Core.Session not found"**
- Compile classes: `Do $System.OBJ.CompilePackage("SessionMCP")`
- Verify you're in the correct IRIS namespace
- Check compilation permissions and privileges

**4. "Security violation" or XECUTE Permission Errors**
- Verify user has `%Development:USE` privilege
- Check: `Write $SYSTEM.Security.Check("%Development","USE")`
- Grant privilege: `Do $SYSTEM.Security.Grant(Username,"%Development","USE")`

**5. "Timeout" Issues**
- The production implementation uses synchronous calls to eliminate timeouts
- If timeouts occur, check IRIS server performance and connectivity
- Verify virtual environment has latest `intersystems-irispython` package

### Debug and Validation

**Test Production Server:**
```bash
# Activate virtual environment
venv\Scripts\activate

# Test server startup
python iris_session_mcp.py
# Look for: "✅ IRIS connectivity test passed"

# Test direct connectivity
python test_full_workflow.py
# Should show successful session creation and command execution
```

**Test IRIS Components:**
```objectscript
// Run comprehensive tests
Do ##class(SessionMCP.Core.Tests.SessionTest).%RunTest()

// Test manual workflows  
Do ##class(SessionMCP.Core.Tests.ManualTest).RunAllTests()

// Check security privileges
Write $SYSTEM.Security.Check("%Development","USE")
// Should return 1
```

**Validate Complete Integration:**
1. Start MCP client (Claude Desktop or Cline)
2. Test basic command: `Execute: WRITE "Hello World!"`
3. Verify session persistence: `List active sessions`
4. Check session cleanup: `Execute: Do ##class(SessionMCP.Core.Session).CleanupExpiredSessions()`

---

## Advanced Configuration

### Custom IRIS Environment

**Multiple IRIS Instances:**
```json
{
  "mcpServers": {
    "iris-prod": {
      "command": "D:/iris-session-mcp/venv/Scripts/python.exe",
      "args": ["D:/iris-session-mcp/iris_session_mcp.py"],
      "env": {
        "IRIS_HOSTNAME": "prod-iris-server",
        "IRIS_NAMESPACE": "PRODUCTION"
      }
    },
    "iris-dev": {
      "command": "D:/iris-session-mcp/venv/Scripts/python.exe", 
      "args": ["D:/iris-session-mcp/iris_session_mcp.py"],
      "env": {
        "IRIS_HOSTNAME": "dev-iris-server",
        "IRIS_NAMESPACE": "DEVELOPMENT"
      }
    }
  }
}
```

**Custom Session Timeout:**
Modify `SessionMCP.Core.Session` class for custom timeout values:
```objectscript
// Change 24-hour default to custom timeout
Set tExpirationDays = 7  // 7 days instead of 1
```

**Enhanced Security Configuration:**
```json
"env": {
  "IRIS_HOSTNAME": "secure-iris.company.com",
  "IRIS_PORT": "1972",
  "IRIS_NAMESPACE": "SECURE_NAMESPACE",
  "IRIS_USERNAME": "mcp_service_user", 
  "IRIS_PASSWORD": "secure_password_here",
  "IRIS_CONNECTION_TIMEOUT": "30"
}
```

### Performance Tuning

**Optimize for High Volume:**
- Use dedicated IRIS namespace for MCP sessions
- Configure session cleanup frequency based on usage
- Monitor IRIS global storage usage (`^SessionMCP.State`)
- Implement custom logging for session analytics

**Session Management Commands:**
```objectscript
// Manual cleanup
Do ##class(SessionMCP.Core.Session).CleanupExpiredSessions()

// List all sessions
Do ##class(SessionMCP.Core.Session).ListActiveSessions()

// Session statistics
Write "Active Sessions: "_$Data(^SessionMCP.State)
```

---

## Security Considerations

### IRIS Security Best Practices

**User Account Configuration:**
- Create dedicated MCP service user account
- Grant minimal required privileges (`%Development:USE`)
- Restrict namespace access as needed
- Monitor session activity and command history

**Command Validation:**
- The server executes any valid ObjectScript command
- Implement additional validation for production environments
- Consider read-only access for sensitive data operations
- Log all executed commands for audit trails

**Network Security:**
- MCP communication uses STDIO (no network exposure)
- IRIS connection follows standard IRIS security protocols
- Use secure authentication and encrypted connections
- Consider VPN for remote IRIS access

### Production Deployment

**Environment Variables Security:**
```bash
# Use environment-specific configuration
export IRIS_HOSTNAME="prod-server.internal"
export IRIS_USERNAME="prod_mcp_user"
export IRIS_PASSWORD="$(cat /secure/iris_password)"
```

**Access Control:**
- Limit MCP server access to authorized AI agents only
- Implement session monitoring and alerting
- Regular security audits of granted privileges
- Monitor and rotate credentials periodically

---

## Support and Maintenance

### Regular Maintenance Tasks

**Session Cleanup:**
```objectscript
// Weekly cleanup of expired sessions
Do ##class(SessionMCP.Core.Session).CleanupExpiredSessions()

// Monitor session usage
Do ##class(SessionMCP.Core.Session).ListActiveSessions()
```

**Health Monitoring:**
```bash
# Test connectivity
python test_full_workflow.py

# Validate MCP server
python validate_mvp.py

# Check virtual environment
venv\Scripts\python.exe --version
pip list | findstr intersystems
```

**Updates and Upgrades:**
1. **Update Python Dependencies:**
   ```bash
   pip install --upgrade intersystems-irispython mcp pydantic
   ```

2. **Update IRIS Classes:**
   ```objectscript
   Do $System.OBJ.CompilePackage("SessionMCP")
   Do ##class(SessionMCP.Core.Tests.SessionTest).%RunTest()
   ```

3. **Validate After Updates:**
   ```bash
   python validate_mvp.py
   ```

### Documentation and Resources

**Project Documentation:**
- Technical architecture: `memory-bank/architecture/`
- Implementation details: `memory-bank/implementation/`
- Project progress: `memory-bank/progress.md`
- Active context: `memory-bank/activeContext.md`

**Support Resources:**
- User manual: `documentation/IRIS-Session-MCP-User-Manual.md`
- Project intelligence: `.clinerules` file contains learned patterns
- Validation scripts: `validate_mvp.py`, `test_full_workflow.py`

---

## Conclusion

The IRIS Session MCP Server provides seamless integration between AI agents and InterSystems IRIS, enabling powerful ObjectScript automation within AI workflows. With the consolidated production implementation, it offers:

**✅ Production Excellence:**
- Single file architecture (`iris_session_mcp.py`) for simplified deployment
- Sub-millisecond command execution with security compliance
- Comprehensive error handling and session management
- Virtual environment isolation for dependency management

**✅ Security and Reliability:**
- IRIS privilege validation enforced
- Session isolation and timeout management
- Structured error responses for robust AI agent integration
- Production-ready configuration patterns

**✅ Developer Experience:**
- Complete documentation and validation tools
- Comprehensive testing framework with unit tests
- Clear troubleshooting guides and configuration examples
- Memory Bank knowledge capture for future development

**✅ AI Agent Integration:**
- Universal MCP client compatibility (Claude, Cline, etc.)
- STDIO transport for maximum compatibility
- Auto-approved tools for seamless AI workflows
- Session persistence enabling complex multi-step operations

**Ready for Production Use**: The IRIS Session MCP Server is fully consolidated, tested, and ready for deployment in production AI agent workflows with confidence in its reliability, performance, and maintainability.

For technical questions, advanced configurations, or development guidance, refer to the comprehensive project documentation in the `memory-bank/` directory.

**Version**: Production Consolidated (June 16, 2025)  
**Status**: ✅ Ready for Production Deployment
