# Cline MCP Configuration for IRIS Execute MCP

## Updated Configuration for Simplified Architecture

The IRIS Execute MCP server has been refactored to focus on direct command execution without session management complexity.

## Correct Cline Configuration

### Step 1: Open Cline MCP Settings
1. Open VS Code with Cline extension
2. Open Settings (Ctrl + ,)
3. Search for "MCP" 
4. Find "Cline > MCP: Servers"
5. Click "Edit in settings.json"

### Step 2: Replace with Updated Configuration

```json
{
  "cline.mcp.servers": {
    "iris-execute-mcp": {
      "autoApprove": ["execute_command"],
      "disabled": false,
      "timeout": 60,
      "command": "D:/iris-session-mcp/venv/Scripts/python.exe",
      "args": ["D:/iris-session-mcp/iris_execute_mcp.py"],
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

### Key Updates:
✅ **Server Name**: `iris-execute-mcp` (reflects new simplified focus)
✅ **Script Name**: `iris_execute_mcp.py` (new simplified server)
✅ **Single Tool**: Only `execute_command` (session management removed)
✅ **Virtual Environment**: Uses isolated dependencies
✅ **Environment Variables**: Proper IRIS connection configuration

### Step 3: Restart and Test
1. Save the settings.json file
2. Restart VS Code completely 
3. Open a new Cline chat
4. Try: "Execute this IRIS command: WRITE 'Hello World!'"

## New Architecture Benefits

### Simplified Tool Set
- ✅ **execute_command**: Direct ObjectScript execution
- ❌ **Removed**: list_sessions, diagnose_timeout (session complexity eliminated)

### Enhanced Reliability
- ✅ **No Session Management**: Eliminates timeout issues
- ✅ **Direct Execution**: Uses proven `ExecuteMCP.Core.Command` class
- ✅ **Faster Response**: No global storage operations
- ✅ **Security Compliant**: Maintains IRIS privilege validation

## Verification Commands

Test the configuration manually:
```bash
# Navigate to project directory
cd D:/iris-session-mcp

# Activate virtual environment
venv\Scripts\activate

# Test new server startup
python iris_execute_mcp.py
```

Expected output:
```
INFO:__main__:Starting IRIS Execute MCP Server
INFO:__main__:IRIS Configuration: localhost:1972/HSCUSTOM (user: _SYSTEM)
INFO:__main__:✅ IRIS connectivity test passed
INFO:__main__:STDIO server initialized
```

## Alternative: Direct MCP Settings UI

If using Cline's MCP Settings UI:
- **Server Name**: iris-execute-mcp
- **Command**: D:/iris-session-mcp/venv/Scripts/python.exe
- **Args**: ["D:/iris-session-mcp/iris_execute_mcp.py"]
- **Transport**: stdio
- **Auto-approve**: ["execute_command"]
- **Environment Variables**:
  - IRIS_HOSTNAME=localhost
  - IRIS_PORT=1972
  - IRIS_NAMESPACE=HSCUSTOM
  - IRIS_USERNAME=_SYSTEM
  - IRIS_PASSWORD=_SYSTEM

## Migration Notes

### What Changed
- **Architecture**: Session-based → Direct execution
- **IRIS Classes**: SessionMCP.Core.Session → ExecuteMCP.Core.Command
- **Python Server**: iris_session_mcp.py → iris_execute_mcp.py
- **Tool Count**: 4 tools → 1 focused tool

### What Stayed the Same
- **IRIS Connectivity**: Same reliable Native API pattern
- **Security**: Same privilege validation
- **Environment Setup**: Same virtual environment and dependencies
- **Performance**: Same sub-second execution times

## Troubleshooting

**If you get connection errors:**
1. Verify file paths point to new `iris_execute_mcp.py`
2. Ensure virtual environment has required packages: `pip list | findstr iris`
3. Test IRIS connectivity: `python test_direct_execution.py`
4. Check IRIS is running and accessible
5. Verify new ExecuteMCP.Core.Command class is compiled in IRIS
