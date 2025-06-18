# Cline MCP Configuration Fix

## Problem Identified
```
C:\Python312\python.exe: can't open file 'D:\\\iris-session-mcp\\\iris_session_mcp_with_output.py': [Errno 2] No such file or directory
```

## Issues:
1. ❌ Wrong filename: `iris_session_mcp_with_output.py` 
2. ❌ Wrong Python path: `C:\Python312\python.exe`

## Correct Cline Configuration

### Step 1: Open Cline MCP Settings
1. Open VS Code with Cline extension
2. Open Settings (Ctrl + ,)
3. Search for "MCP" 
4. Find "Cline > MCP: Servers"
5. Click "Edit in settings.json"

### Step 2: Replace with Correct Configuration

```json
{
  "cline.mcp.servers": {
    "iris-session-mcp": {
      "autoApprove": ["execute_command", "list_sessions"],
      "disabled": false,
      "timeout": 60,
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

### Key Corrections:
✅ **Correct Python Path**: `D:/iris-session-mcp/venv/Scripts/python.exe`
✅ **Correct Script Name**: `iris_session_mcp.py` (not `iris_session_mcp_with_output.py`)
✅ **Virtual Environment**: Uses isolated dependencies
✅ **Environment Variables**: Proper IRIS connection configuration

### Step 3: Restart and Test
1. Save the settings.json file
2. Restart VS Code completely 
3. Open a new Cline chat
4. Try: "Execute this IRIS command: WRITE 'Hello World!'"

## Verification Commands

Test the configuration manually:
```bash
# Navigate to project directory
cd D:/iris-session-mcp

# Activate virtual environment
venv\Scripts\activate

# Test server startup
python iris_session_mcp.py
```

Expected output:
```
INFO:__main__:Starting IRIS Session MCP Server
INFO:__main__:IRIS Configuration: localhost:1972/HSCUSTOM (user: _SYSTEM)
INFO:__main__:✅ IRIS connectivity test passed: IRIS for Windows...
INFO:__main__:STDIO server initialized
```

## Alternative: Direct MCP Settings UI

If using Cline's MCP Settings UI:
- **Server Name**: iris-session-mcp
- **Command**: D:/iris-session-mcp/venv/Scripts/python.exe
- **Args**: ["D:/iris-session-mcp/iris_session_mcp.py"]
- **Transport**: stdio
- **Environment Variables**:
  - IRIS_HOSTNAME=localhost
  - IRIS_PORT=1972
  - IRIS_NAMESPACE=HSCUSTOM
  - IRIS_USERNAME=_SYSTEM
  - IRIS_PASSWORD=_SYSTEM

## Troubleshooting

**If you still get connection errors:**
1. Verify file paths are correct (use forward slashes or escaped backslashes)
2. Ensure virtual environment has required packages: `pip list | findstr iris`
3. Test IRIS connectivity: `python test_full_workflow.py`
4. Check IRIS is running and accessible
