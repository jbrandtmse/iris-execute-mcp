# IRIS Execute MCP Server

A Model Context Protocol (MCP) server that enables AI agents to execute ObjectScript commands and manage unit tests in InterSystems IRIS environments. This server provides direct integration between AI tools like Claude/Cline and IRIS systems through standardized MCP protocol.

## Features

### Core Execution Tools
- **execute_command**: Execute ObjectScript commands with real output capture
- **execute_classmethod**: Dynamic ObjectScript class method invocation with parameter support
- **get_global**: Retrieve IRIS global variable values with complex subscripts
- **set_global**: Set IRIS global variable values with verification
- **get_system_info**: IRIS system connectivity and version information

### Unit Testing Tools
- **list_unit_tests**: Discover available unit test classes and methods
- **run_unit_tests**: Execute unit tests using standard %UnitTest.Manager
- **get_unit_test_results**: Retrieve detailed test execution results

### Async Unit Testing Tools
- **queue_unit_tests**: Queue unit test execution for immediate return (eliminates timeouts)
- **poll_unit_tests**: Poll for async test results with sub-second performance
- **get_job_status**: Monitor job status without retrieving results
- **cancel_job**: Cancel running jobs and cleanup resources
- **list_active_jobs**: List all active async test jobs

## Key Benefits

- **Timeout Elimination**: Async unit testing eliminates 120+ second timeout issues
- **Real Output Capture**: WRITE commands return actual output instead of generic messages
- **Performance Improvement**: Sub-second unit test execution vs traditional Manager overhead
- **Dual Test Support**: Works with both %UnitTest.TestCase and custom test classes
- **Complete IRIS Integration**: Full ObjectScript command execution and global manipulation

## Prerequisites

- InterSystems IRIS 2024.1 or later
- Python 3.8 or later
- intersystems-irispython package
- fastmcp package

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/jbrandtmse/iris-session-mcp.git
cd iris-session-mcp
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux  
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure IRIS Classes
Ensure the ExecuteMCP classes are compiled in your IRIS instance:
```objectscript
Do $System.OBJ.CompilePackage("ExecuteMCP")
```

## Configuration

### Environment Variables
Set these environment variables or include them in your MCP configuration:

```bash
IRIS_HOSTNAME=localhost
IRIS_PORT=1972
IRIS_NAMESPACE=HSCUSTOM
IRIS_USERNAME=_SYSTEM
IRIS_PASSWORD=_SYSTEM
```

### MCP Server Configuration

#### For Cline (VS Code Extension)
Add to your Cline MCP settings (File → Preferences → Settings → Search "MCP" → Edit in settings.json):

```json
{
  "cline.mcp.servers": {
    "iris-execute-mcp": {
      "autoApprove": [
        "execute_command",
        "execute_classmethod", 
        "get_global",
        "set_global",
        "get_system_info",
        "list_unit_tests",
        "run_unit_tests", 
        "get_unit_test_results",
        "queue_unit_tests",
        "poll_unit_tests",
        "get_job_status",
        "cancel_job",
        "list_active_jobs"
      ],
      "disabled": false,
      "timeout": 120,
      "type": "stdio",
      "command": "/path/to/your/venv/Scripts/python.exe",
      "args": ["/path/to/iris_execute_mcp.py"],
      "env": {
        "IRIS_HOSTNAME": "localhost",
        "IRIS_PORT": "1972",
        "IRIS_NAMESPACE": "HSCUSTOM", 
        "IRIS_USERNAME": "_SYSTEM",
        "IRIS_PASSWORD": "_SYSTEM"
      }
    }
  }
}
```

#### For Other MCP Clients
Standard MCP configuration:
```json
{
  "servers": {
    "iris-execute-mcp": {
      "command": "/path/to/your/venv/Scripts/python.exe",
      "args": ["/path/to/iris_execute_mcp.py"],
      "env": {
        "IRIS_HOSTNAME": "localhost",
        "IRIS_PORT": "1972",
        "IRIS_NAMESPACE": "HSCUSTOM",
        "IRIS_USERNAME": "_SYSTEM", 
        "IRIS_PASSWORD": "_SYSTEM"
      }
    }
  }
}
```

## Usage Examples

### Basic ObjectScript Execution
```
Execute this command: WRITE $ZV
```
Returns actual IRIS version string.

### Global Variable Operations
```
Set global ^MyApp("config","version") to "1.0.0"
Get the value of ^MyApp("config","version") 
```

### Dynamic Method Invocation
```
Call the GetVersion method on class %SYSTEM.Version
Use %SYSTEM.SQL.Functions to calculate the absolute value of -456
```

### Async Unit Testing
```
Queue unit tests for ExecuteMCP.Test.SampleUnitTest
Poll for the test results
List all active test jobs
```

## Testing

### Run Basic Tests
```bash
# Test IRIS connectivity
python test_simple.py

# Test all basic functionality
python test_execute_final.py

# Test async unit testing specifically
python test_fastmcp.py
```

### Validate Installation
```bash
# Start server manually to verify
python iris_execute_mcp.py

# Should output:
# INFO:__main__:Starting IRIS Execute FastMCP Server
# INFO:__main__:✅ IRIS connectivity test passed
# INFO:__main__:🚀 FastMCP server ready for connections
```

## Troubleshooting

### Connection Issues
1. Verify IRIS is running and accessible
2. Check credentials and connection parameters
3. Ensure intersystems-irispython is properly installed
4. Test IRIS connectivity: `python test_simple.py`

### MCP Integration Issues  
1. Restart VS Code completely after configuration changes
2. Check file paths use absolute paths
3. Verify virtual environment activation
4. Check MCP server logs for errors

### Unit Testing Issues
1. Ensure ExecuteMCP classes are compiled in IRIS
2. Verify test classes exist in specified namespace
3. Use async tools (queue_unit_tests/poll_unit_tests) for best performance
4. Check IRIS security permissions for test execution

## Architecture

### Components
- **iris_execute_mcp.py**: Main MCP server using FastMCP framework
- **src/ExecuteMCP/Core/Command.cls**: IRIS backend for command execution
- **src/ExecuteMCP/Core/UnitTestAsync.cls**: IRIS backend for async unit testing
- **src/ExecuteMCP/Test/**: Sample unit test classes

### Design Patterns
- **Direct Execution**: Commands execute immediately without session management
- **I/O Capture**: Real output capture using global variable patterns
- **Async Work Queue**: Background job execution for timeout elimination
- **Security Validation**: IRIS privilege checking for all operations

## Development

### Adding New Tools
1. Add @mcp.tool() decorated function to iris_execute_mcp.py
2. Implement backend logic in appropriate ExecuteMCP.Core class
3. Update configuration to include new tool in autoApprove list
4. Add tests in test_*.py files

### Contributing
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality  
4. Submit pull request with clear description

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create GitHub issue for bugs or feature requests
- Check existing documentation in documentation/ folder
- Review test files for usage examples
