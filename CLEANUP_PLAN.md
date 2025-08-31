# IRIS Execute MCP - Cleanup Plan

## Current Status
- **Production Server**: `iris_execute_fastmcp.py` (ALL 5 TOOLS WORKING)
- **IRIS Backend**: `src/ExecuteMCP/Core/Command.cls`
- **Configuration**: Currently points to D:/iris-session-mcp but is disabled

## File Categories

### 🟢 KEEP - Production Files
- `iris_execute_fastmcp.py` - Production FastMCP server with I/O capture breakthrough
- `setup.py` - Package setup
- `requirements.txt` - Dependencies  
- `.env.example` - Environment configuration example
- `CLINE_MCP_CONFIGURATION.md` - Configuration documentation

### 🔴 DELETE - Deprecated Server Files
- `iris_execute_mcp.py` - Old version without FastMCP
- `iris_session_mcp.py` - Deprecated session-based approach
- `iris_session_mcp_debug.py` - Debug version of deprecated approach

### 🟡 DELETE - Development/Debug Test Files
These test files were created during development and debugging:
- `test_basic_http.py` - HTTP testing (not used)
- `test_classmethod_fix.py` - ClassMethod debugging
- `test_complex_command.py` - Complex command testing
- `test_direct_execution.py` - Direct execution testing
- `test_execute_classmethod_debug.py` - ClassMethod debugging
- `test_execute_classmethod_simple.py` - ClassMethod simple tests
- `test_execute_classmethod.py` - ClassMethod testing
- `test_execute_command_debug.py` - Command debugging
- `test_execute_mcp.py` - MCP execution testing
- `test_full_workflow.py` - Workflow testing
- `test_global_methods.py` - Global methods testing
- `test_hello_world.py` - Basic hello world test
- `test_iris_class.py` - IRIS class testing
- `test_mcp_direct.py` - Direct MCP testing
- `test_mcp_globals.py` - Global MCP testing
- `test_mcp_simple.py` - Simple MCP testing
- `test_minimal_mcp.py` - Minimal MCP testing
- `test_security_fix.py` - Security testing
- `test_simple.py` - Simple testing
- `test_timeout_fix.py` - Timeout fix testing

### 🟢 KEEP - Validation Test Files
Keep these for production validation:
- `test_execute_classmethod_verify.py` - ClassMethod verification (referenced in docs)
- `test_execute_final.py` - Comprehensive production test (referenced in docs)
- `test_fastmcp.py` - FastMCP production test (referenced in docs)
- `validate_mvp.py` - MVP validation script

## Cleanup Actions

1. **Delete deprecated server files** (3 files)
2. **Delete development test files** (20 files)
3. **Keep production and validation files** (9 files + directories)
4. **Update documentation** if needed

## After Cleanup Structure
```
iris-execute-mcp/
├── iris_execute_fastmcp.py          # Production server
├── test_execute_classmethod_verify.py # Validation test
├── test_execute_final.py            # Comprehensive test
├── test_fastmcp.py                  # FastMCP test
├── validate_mvp.py                  # MVP validation
├── setup.py                         # Package setup
├── requirements.txt                 # Dependencies
├── .env.example                     # Config example
├── CLINE_MCP_CONFIGURATION.md      # Configuration docs
├── CLEANUP_PLAN.md                 # This file
├── src/                            # IRIS classes
├── memory-bank/                    # Documentation
└── documentation/                  # User manuals
```

## Cleanup Benefits
- Reduces 32 Python files to 9 essential files
- Eliminates confusion about which server to use
- Keeps only production and essential validation tests
- Maintains working configuration and documentation
