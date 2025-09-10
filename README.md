# IRIS Execute MCP Server

## Complete MCP Integration for InterSystems IRIS - 8 Development Tools! 🎉

The IRIS Execute MCP server provides **8 fully functional tools** for comprehensive IRIS development integration, including basic operations, compilation tools, and advanced unit testing capabilities with a custom VS Code-friendly TestRunner.

## Current Tool Status ✅

### Basic Tools (5):
- ✅ **execute_command**: Direct ObjectScript execution with **I/O CAPTURE** - Real output capture!
- ✅ **execute_classmethod**: Dynamic class method invocation with full parameter support
- ✅ **get_global**: Dynamic global retrieval with complex subscripts
- ✅ **set_global**: Dynamic global setting with verification  
- ✅ **get_system_info**: Real-time IRIS system information

### Compilation Tools (2):
- ✅ **compile_objectscript_class**: Compile one or more ObjectScript classes with error reporting
- ✅ **compile_objectscript_package**: Compile all classes in a package recursively

### Unit Testing Tool (1 - Experimental):
- ⚠️ **execute_unit_tests** (EXPERIMENTAL): Execute tests using custom ExecuteMCP.TestRunner (VS Code friendly!)

## Installation

### Prerequisites
- Python 3.8+
- InterSystems IRIS 2024.3 or later
- VS Code with Cline extension

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone https://github.com/jbrandtmse/iris-execute-mcp.git
cd iris-execute-mcp

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment
Create a `.env` file (copy from `.env.example`):
```env
IRIS_HOSTNAME=localhost
IRIS_PORT=1972
IRIS_NAMESPACE=HSCUSTOM
IRIS_USERNAME=_SYSTEM
IRIS_PASSWORD=_SYSTEM
```

### Step 3: Install IRIS Classes
1. Open IRIS Studio or VS Code with ObjectScript extension
2. Import classes from `src/ExecuteMCP/Core/` and `src/ExecuteMCP/TestRunner/` directories
3. Compile the ExecuteMCP package:
```objectscript
Do $System.OBJ.CompilePackage("ExecuteMCP")
```

## Cline MCP Configuration

### Step 1: Open Cline MCP Settings
1. Open VS Code with Cline extension
2. Open Settings (Ctrl + ,)
3. Search for "MCP" 
4. Find "Cline > MCP: Servers"
5. Click "Edit in settings.json"

### Step 2: Configuration (All 8 Tools)

Add this to your Cline MCP settings:

```json
{
  "iris-execute-mcp": {
    "autoApprove": [
      "execute_command",
      "execute_classmethod",
      "get_global",
      "set_global",
      "get_system_info",
      "compile_objectscript_class",
      "compile_objectscript_package",
      "execute_unit_tests"
    ],
    "disabled": false,
    "timeout": 60,
    "type": "stdio",
    "command": "C:/iris-execute-mcp/venv/Scripts/python.exe",
    "args": ["C:/iris-execute-mcp/iris_execute_mcp.py"],
    "env": {
      "IRIS_HOSTNAME": "localhost",
      "IRIS_PORT": "1972",
      "IRIS_NAMESPACE": "HSCUSTOM",
      "IRIS_USERNAME": "_SYSTEM",
      "IRIS_PASSWORD": "_SYSTEM"
    }
  }
}
```

### Key Configuration Details:
✅ **Server Name**: `iris-execute-mcp`  
✅ **Script Name**: `iris_execute_mcp.py` (consolidated server with all features)  
✅ **8 Tools**: 5 basic + 2 compilation + 1 unit testing tool  
✅ **Virtual Environment**: Uses isolated dependencies for reliability  
✅ **Environment Variables**: Proper IRIS connection configuration  
✅ **Auto-Approve**: All 8 tools approved for seamless AI workflows

### Step 3: Restart and Test
1. Save the settings.json file
2. Restart VS Code completely 
3. Open a new Cline chat
4. Test functionality:
   - "Show me IRIS system information"
   - "Execute: WRITE $ZV"
   - "Execute unit tests for ExecuteMCP.Test.SampleUnitTest"

## Verification

### Test Server Startup
```bash
# Navigate to project directory
cd C:/iris-execute-mcp

# Activate virtual environment
venv\Scripts\activate

# Test server startup
python iris_execute_mcp.py
```

Expected output:
```
INFO - Starting IRIS Execute FastMCP Server
INFO - IRIS Available: True
INFO - ✅ IRIS connectivity test passed
INFO - 🚀 FastMCP server ready for connections
```

### Test Tools Directly
```bash
# Test all functionality
python test_execute_final.py

# Test FastMCP integration
python test_fastmcp.py

# Validate MVP implementation
python validate_mvp.py

# Test unit test implementation
python test_unittest_final_validation.py
```

## Tool Documentation

### Basic Tools

#### execute_command
Execute ObjectScript commands with I/O capture:
```python
# Examples:
"Execute: WRITE $ZV"
→ Returns actual IRIS version string

"Execute: SET ^MyGlobal = 123"
→ Returns "Command executed successfully"
```

#### execute_classmethod
Dynamically invoke ObjectScript class methods:
```python
# Examples:
"Call GetVersion on %SYSTEM.Version"
→ Returns IRIS version details

"Call ABS on %SYSTEM.SQL.Functions with parameter -456"
→ Returns 456
```

#### get_global / set_global
Manage IRIS globals dynamically:
```python
# Set a global
"Set global ^MyApp('Config','Version') to '1.0.0'"

# Get a global
"Get the value of ^MyApp('Config','Version')"
```

#### get_system_info
Retrieve IRIS system information:
```python
"What version of IRIS is running?"
→ Returns version, namespace, timestamp
```

### Compilation Tools

#### compile_objectscript_class
Compile one or more ObjectScript classes with comprehensive error reporting.

**IMPORTANT**: Class names MUST include the .cls suffix for proper compilation.

```python
# Compile single class (note the .cls suffix)
"Compile ObjectScript class MyPackage.MyClass.cls"
→ Returns compilation status and any errors

# Compile multiple classes (all with .cls suffix)
"Compile classes MyPackage.Class1.cls, MyPackage.Class2.cls"
→ Returns status for each class

# Custom compilation flags
"Compile MyPackage.MyClass.cls with flags 'bckry'"
→ b=rebuild, c=compile, k=keep source, r=recursive, y=display info

# Note: If .cls suffix is omitted, it will be automatically added
"Compile MyPackage.MyClass" → Internally becomes "MyPackage.MyClass.cls"
```

#### compile_objectscript_package
Compile all classes in a package recursively:
```python
# Compile entire package
"Compile ObjectScript package MyPackage"
→ Compiles all classes in package and sub-packages

# With custom flags
"Compile package MyPackage with flags 'bc'"
→ Basic compile without recursion
```

### Unit Testing Tool (Experimental)

#### execute_unit_tests (EXPERIMENTAL)
Execute tests using the custom ExecuteMCP.TestRunner instead of %UnitTest.Manager.

**⚠️ Note: This tool is experimental and under active development.**

This tool provides a VS Code-friendly alternative to the standard %UnitTest.Manager, eliminating file path dependencies and VS Code sync issues. The custom TestRunner executes tests directly from compiled classes without filesystem interaction.

```python
# Run all tests in a package
"Execute unit tests for ExecuteMCP.Test"
→ Executes all test classes in the package

# Run tests in a specific class
"Execute unit tests for ExecuteMCP.Test.SimpleTest"
→ Executes all test methods in the class

# Run a specific test method
"Execute unit tests for ExecuteMCP.Test.SimpleTest:TestAddition"
→ Executes only the specified test method

# Response includes:
# - Summary with pass/fail counts
# - Individual test results
# - Execution times
# - Full assertion details
```

**Advantages over %UnitTest.Manager:**
- ✅ No filesystem dependencies (works with VS Code auto-sync)
- ✅ No ^UnitTestRoot configuration required
- ✅ Executes from compiled classes directly
- ✅ Full support for %UnitTest.TestCase and assertion macros
- ✅ Clean JSON response format
- ✅ Process isolation without WorkMgr complexity

## Architecture

### Technology Stack
- **Python MCP Server**: FastMCP framework with STDIO transport
- **IRIS Backend**: ExecuteMCP.Core.Command, ExecuteMCP.Core.Compile, and ExecuteMCP.TestRunner classes
- **Custom TestRunner**: ExecuteMCP.TestRunner.Manager for VS Code-friendly test execution
- **I/O Capture**: Global variable mechanism avoiding STDIO conflicts
- **Compilation Engine**: $System.OBJ methods with comprehensive error handling

### Key Innovations
1. **I/O Capture Breakthrough**: Real output from WRITE commands via ^MCPCapture
2. **Dynamic Method Invocation**: Call any ObjectScript class method by name
3. **Custom TestRunner**: VS Code-friendly alternative to %UnitTest.Manager
4. **Zero Timeout Architecture**: All operations complete in <100ms

### Performance Metrics
- ✅ **Command Execution**: 0ms with I/O capture
- ✅ **Method Invocation**: <10ms for complex calls
- ✅ **Global Operations**: Sub-millisecond response
- ✅ **Unit Test Execution**: Direct execution with structured results
- ✅ **System Info**: <50ms full details

## Troubleshooting

### MCP Connection Issues
If you see "MCP error -32000: Connection closed":
1. Restart VS Code completely
2. Or disable/enable Cline extension
3. Check server is running: `python iris_execute_mcp.py`

### Tool Not Working
1. Verify IRIS classes are compiled:
   ```objectscript
   Do $System.OBJ.CompilePackage("ExecuteMCP")
   ```
2. Check security privileges:
   ```objectscript
   Write $SYSTEM.Security.Check("%Development","USE")
   ```
3. Test backend directly in IRIS terminal

### Path Issues
- Use absolute paths in configuration
- Verify virtual environment activation
- Check Python path points to venv Python

### Unit Test Issues

#### Test Discovery Problems
- **Symptom**: Tests run but report "0 tests found"
- **Cause**: Test classes not compiled in IRIS
- **Solution**: 
  ```objectscript
  // Compile test classes (VS Code syncs but doesn't compile)
  Do $System.OBJ.CompilePackage("ExecuteMCP.Test")
  ```

#### Test Spec Format
- **Supported Formats**:
  - `ExecuteMCP.Test` - Run all tests in package
  - `ExecuteMCP.Test.SampleUnitTest` - Run all tests in class
  - `ExecuteMCP.Test.SampleUnitTest:TestMethod` - Run specific method

## Advanced Usage

### Combined Workflows
```python
# Complete test workflow with compilation
1. "Compile ObjectScript package ExecuteMCP.Test"
2. "Execute unit tests for ExecuteMCP.Test.SampleUnitTest"
3. "Get global ^TestRunnerResults to see detailed results"
```

### Understanding Test Results
The custom TestRunner stores results in process-local globals during execution and returns structured JSON:
```json
{
  "status": "success",
  "summary": {
    "passed": 5,
    "failed": 1,
    "errors": 0,
    "skipped": 0,
    "total": 6
  },
  "tests": [
    {
      "class": "ExecuteMCP.Test.SimpleTest",
      "method": "TestAddition",
      "status": "passed",
      "duration": 0.001
    }
  ],
  "executionTime": 0.125
}
```

## Contributing
Contributions welcome! Please ensure:
- All tests pass
- Code follows ObjectScript conventions
- MCP tools have proper documentation
- Changes are tested with Cline

## License
MIT License - See LICENSE file for details

## Version History
- **v3.0.0** (September 9, 2025): Refactored to 8 development tools, removed deprecated WorkMgr async pattern
- **v2.4.0** (September 9, 2025): Added custom TestRunner MCP tool (10 tools total)
- **v2.3.1** (September 7, 2025): Added auto-prefix feature for unit test specifications
- **v2.3.0** (September 7, 2025): Fixed unit testing with WorkMgr pattern (9 tools total)
- **v2.2.0** (September 3, 2025): Added 2 compilation tools
- **v2.1.0** (August 30, 2025): Consolidated server with unit testing
- **v2.0.0**: Added unit testing capabilities
- **v1.0.0**: Initial 5 basic tools

## Support
- GitHub Issues: https://github.com/jbrandtmse/iris-execute-mcp/issues
- Documentation: See `/documentation` directory
- Memory Bank: See `/memory-bank` for project context

---
**Status**: ✅ **Development Tool** - All 8 tools operational for IRIS development  
**Last Updated**: September 9, 2025
