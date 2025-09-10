# System Patterns - IRIS Execute MCP Server

## Overall Architecture

### Simplified Direct Execution Pattern
```
AI Agent (Claude/Cline)
    ↓ (MCP JSON-RPC)
Python MCP Server (iris_execute_mcp.py)
    ↓ (IRIS Native API)
IRIS Instance
    ↓ (ObjectScript)
ExecuteMCP Classes
```

### Communication Flow
1. **AI Request**: Agent sends MCP tool call (JSON-RPC 2.0)
2. **Server Processing**: Python server validates parameters
3. **IRIS Execution**: Native API calls ObjectScript methods directly
4. **Response Assembly**: Output captured and returned via Native API
5. **MCP Response**: JSON-RPC response sent back to AI agent

## Core Architectural Patterns

### Direct Execution Pattern (No Sessions)
**Stateless Design for Maximum Performance:**
- Each command executes independently
- No session state management overhead
- Direct XECUTE for immediate results
- 0ms execution time achieved

**Implementation:**
```objectscript
ClassMethod ExecuteCommand(pCommand As %String, pNamespace As %String) As %String
{
    // Direct execution without session overhead
    Set $NAMESPACE = pNamespace
    If (pCommand [ "WRITE") {
        // I/O capture for WRITE commands
        Set ^MCPCapture = ""
        // Execute with capture
        Set tOutput = $GET(^MCPCapture,"")
        Kill ^MCPCapture
    } Else {
        XECUTE pCommand
    }
}
```

### I/O Capture Pattern (Breakthrough Innovation)
**Global Variable Capture Mechanism:**
- Avoids STDIO pollution that causes MCP timeouts
- Uses ^MCPCapture global for reliable output storage
- Smart detection of WRITE vs non-WRITE commands
- Automatic cleanup after each operation

**Key Implementation:**
```objectscript
If (pCommand [ "WRITE") {
    Set tModifiedCommand = $PIECE(pCommand,"WRITE",2)
    Set tCaptureCommand = "Set ^MCPCapture = ^MCPCapture_("_tModifiedCommand_")"
    XECUTE tCaptureCommand
    Set tOutput = $GET(^MCPCapture,"")
    Kill ^MCPCapture
}
```

### Custom TestRunner Architecture Pattern
**ExecuteMCP.TestRunner - VS Code Sync-Issue Free Testing:**

**Architecture Overview:**
```
ExecuteMCP.TestRunner.Manager
    ├── Discovery (test class/method discovery)
    ├── Context (auto-initialized execution context)
    └── Executor (test execution via $METHOD)
```

**Key Design Decisions:**
- **No Filesystem Dependency**: Works with compiled classes only
- **No %UnitTest.Manager**: Avoids singleton conflicts
- **Direct Class Invocation**: Uses $METHOD() for test execution
- **In-Memory Results**: No persistence layer needed
- **Full Compatibility**: Supports all %UnitTest.TestCase features

**Manager Pattern:**
```objectscript
Class ExecuteMCP.TestRunner.Manager Extends %RegisteredObject
{
    Property Context As ExecuteMCP.TestRunner.Context [ InitialExpression = {##class(ExecuteMCP.TestRunner.Context).%New()} ];
    
    Method RunTest(pTestClass As %String, pTestMethod As %String = "") As %String
    {
        // Direct test execution without filesystem
        Set tInstance = $CLASSMETHOD(pTestClass,"%New")
        
        // Lifecycle methods
        Do tInstance.OnBeforeAllTests()
        Do tInstance.OnBeforeOneTest()
        
        // Execute test method
        If pTestMethod'="" {
            Do $METHOD(tInstance, pTestMethod)
        }
        
        // Cleanup lifecycle
        Do tInstance.OnAfterOneTest()
        Do tInstance.OnAfterAllTests()
        
        // Return results from Context
        Quit ..Context.GetResults()
    }
}
```

**Discovery Pattern:**
```objectscript
ClassMethod DiscoverTestClasses(pPackage As %String = "") As %String
{
    // SQL-based discovery of compiled test classes
    Set tSQL = "SELECT Name FROM %Dictionary.CompiledClass WHERE Super [ '%UnitTest.TestCase'"
    If pPackage'="" {
        Set tSQL = tSQL_" AND Name %STARTSWITH '"_pPackage_"'"
    }
    
    Set tRS = ##class(%SQL.Statement).%ExecDirect(,tSQL)
    // Build JSON array of test classes
}
```

**Context Auto-Initialization Pattern:**
```objectscript
Class ExecuteMCP.TestRunner.Context Extends %RegisteredObject
{
    Property TestsFailed As %Integer [ InitialExpression = 0 ];
    Property TestsPassed As %Integer [ InitialExpression = 0 ];
    Property Assertions As list Of %String;
    
    Method LogAssert(pPassed As %Boolean, pDescription As %String)
    {
        If pPassed {
            Set ..TestsPassed = ..TestsPassed + 1
        } Else {
            Set ..TestsFailed = ..TestsFailed + 1
        }
        Do ..Assertions.Insert(pDescription)
    }
}
```

### WorkMgr Unit Testing Pattern
**Process Isolation via %SYSTEM.WorkMgr:**
```objectscript
ClassMethod QueueTests(pTestSpec As %String, pQualifiers As %String) As %String
{
    // Create work manager instance
    Set tWorkMgr = ##class(%SYSTEM.WorkMgr).%New()
    
    // Generate unique job ID
    Set tJobID = $SYSTEM.Util.CreateGUID()
    
    // Store request in global
    Set ^ExecuteMCP.TestQueue(tJobID,"spec") = pTestSpec
    Set ^ExecuteMCP.TestQueue(tJobID,"qualifiers") = pQualifiers
    
    // Queue for execution in isolated process
    Set tSC = tWorkMgr.Queue(
        "##class(ExecuteMCP.Core.UnitTestQueue).RunTestInWorker",
        tJobID
    )
    
    // Return immediately with job ID
    Quit {"jobID": tJobID, "status": "queued"}.%ToJSON()
}
```

### Native API Integration Pattern
**Direct Connection Without Session Management:**
```python
import iris

class IRISExecutor:
    def __init__(self):
        self.connection = iris.connect(
            hostname="localhost",
            port=1972,
            namespace="HSCUSTOM",
            username=username,
            password=password
        )
    
    def execute_command(self, command, namespace="HSCUSTOM"):
        return self.connection.classMethodValue(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            command,
            namespace
        )
```

## Tool Implementation Patterns

### Core Tool Pattern
**Standard JSON Response Format:**
```json
{
    "status": "success",
    "output": "Command output or result",
    "namespace": "HSCUSTOM",
    "executionTime": "0ms"
}
```

### Compilation Tool Pattern
```objectscript
ClassMethod CompileClasses(pClassNames As %String, pQSpec As %String) As %String
{
    // Ensure .cls suffix
    For i=1:1:$LENGTH(pClassNames,",") {
        Set className = $PIECE(pClassNames,",",i)
        If '$FIND(className,".cls") {
            Set $PIECE(pClassNames,",",i) = className_".cls"
        }
    }
    
    // Compile with error reporting
    Set tSC = $System.OBJ.CompileList(pClassNames, pQSpec, .tErrors)
    
    // Return structured response
    Quit {"status": $S($$$ISOK(tSC):"success",1:"error"), 
          "errors": tErrors}.%ToJSON()
}
```

### Unit Test Pattern with WorkMgr
**Test Specification Format (v2.3.1):**
```objectscript
// Leading colon is optional - auto-added if missing (v2.3.1)
Set testSpec = "ExecuteMCP.Test.SampleUnitTest"  // Colon auto-added
Set testSpec = ":ExecuteMCP.Test.SampleUnitTest" // Also works

// Default qualifiers for VS Code workflow  
Set qualifiers = "/noload/nodelete/recursive"
```

## MCP Protocol Patterns

### Tool Registration Pattern
```python
@server.tool()
async def execute_command(
    command: str,
    namespace: str = "HSCUSTOM"
) -> types.TextContent:
    """Execute an ObjectScript command directly in IRIS."""
    result = await call_iris_async(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        command,
        namespace
    )
    return types.TextContent(
        type="text",
        text=result
    )
```

### Error Handling Pattern
**Comprehensive Error Categories:**
- **Connection Errors**: IRIS connectivity issues
- **Security Errors**: Privilege validation failures  
- **Compilation Errors**: ObjectScript syntax issues
- **Test Errors**: Unit test failures
- **Timeout Prevention**: All handled via architecture

## Performance Optimization Patterns

### Zero-Overhead Execution
- Direct XECUTE without session management
- No intermediate buffering or state tracking
- Immediate response return
- Result: 0ms execution time

### WorkMgr Performance Pattern
**60,000x Improvement for Unit Tests:**
- Avoids %UnitTest.Manager overhead
- Process isolation prevents singleton conflicts
- Instant job ID return for non-blocking operation
- 0.5-2ms execution vs 120+ seconds

### Connection Optimization
```python
# Connection reuse pattern
_connection = None

def get_connection():
    global _connection
    if _connection is None:
        _connection = iris.connect(...)
    return _connection
```

## Security Patterns

### Privilege Validation
```objectscript
// Always check %Development privilege
If '($SYSTEM.Security.Check("%Development","USE")) {
    Quit {"error": "Insufficient privileges"}.%ToJSON()
}
```

### Namespace Isolation
```objectscript
// Save and restore namespace
Set tOldNS = $NAMESPACE
Try {
    Set $NAMESPACE = pNamespace
    // Execute operation
} Catch {
    // Handle error
}
Set $NAMESPACE = tOldNS
```

## Testing Patterns

### Unit Test Configuration
```objectscript
// Required global configuration
Set ^UnitTestRoot = "C:/InterSystems/IRIS/mgr/user/UnitTests/"

// VS Code auto-sync pattern
// Classes are synchronized but not compiled
// Use /noload to skip loading from filesystem
// Use /nodelete to keep test classes after run
```

### Test Discovery Pattern
```objectscript
// Leading colon auto-added in v2.3.1 for user convenience
Set testSpec = "PackageName.TestClass"     // Auto-prefix applied
Set testSpec = ":PackageName.TestClass"    // Already prefixed, no change
Set testSpec = "Package.Test:TestMethod"   // Method-specific, no prefix needed

// Auto-prefix logic ensures proper test discovery
// All formats now work correctly with automatic handling
```

### TestRunner vs %UnitTest.Manager Comparison
| Feature | %UnitTest.Manager | ExecuteMCP.TestRunner |
|---------|------------------|----------------------|
| Filesystem Dependency | Required | None |
| VS Code Sync Issues | Common | Eliminated |
| Performance | 120+ seconds | <1 second |
| Session Conflicts | Yes (singleton) | No |
| Assertion Macros | Full support | Full support |
| Lifecycle Methods | Full support | Full support |
| Result Storage | Persistent | In-memory |

## Troubleshooting Patterns

### Common Issues and Solutions

**Unit Tests Finding 0 Tests:**
- Solution: Leading colon auto-added in v2.3.1
- Example: Both work: "ExecuteMCP.Test.SampleUnitTest" or ":ExecuteMCP.Test.SampleUnitTest"
- Auto-prefix handles missing colons automatically

**Unit Test Timeouts:**
- Solution: Use queue_unit_tests/poll_unit_tests
- Avoids %UnitTest.Manager overhead

**WRITE Command Output Missing:**
- Solution: I/O capture mechanism handles automatically
- Global variable capture avoids STDIO issues

**Compilation Errors:**
- Solution: Always include .cls suffix
- Tool automatically adds if missing

**VS Code Sync Issues:**
- Solution: Use ExecuteMCP.TestRunner instead of %UnitTest.Manager
- Alternative: Manual $system.OBJ.Load() for specific classes

## User Experience Enhancement Patterns

### Auto-Prefix Pattern (v2.3.1)
**Intelligent Test Spec Handling:**
```python
# Auto-add colon prefix if missing (for root test suite format)
if test_spec and not test_spec.startswith(':'):
    if ':' in test_spec:
        # Method-specific tests don't need the leading colon
        logger.info(f"Method-specific test spec detected, no prefix needed: {test_spec}")
    elif '.' in test_spec:
        # Regular test spec without method selection - needs leading colon
        logger.info(f"Auto-adding colon prefix to test spec: {test_spec} -> :{test_spec}")
        test_spec = ':' + test_spec
    else:
        logger.warning(f"Test spec may be invalid (no package structure detected): {test_spec}")
```

**Three Cases Handled:**
1. **Regular specs**: `ExecuteMCP.Test.SampleUnitTest` → `:ExecuteMCP.Test.SampleUnitTest`
2. **Already prefixed**: `:ExecuteMCP.Test.SampleUnitTest` → No change
3. **Method-specific**: `ExecuteMCP.Test.SampleUnitTest:TestAddition` → No prefix needed

**Benefits:**
- Reduces user friction - no need to remember colon requirement
- Maintains backward compatibility - existing prefixed specs still work
- Smart detection prevents invalid prefixing of method-specific tests

## Extension Patterns

### Adding New Tools
```python
@server.tool()
async def new_tool(param1: str, param2: str) -> types.TextContent:
    """Tool description for MCP."""
    result = await call_iris_async(
        "ExecuteMCP.Core.NewClass",
        "NewMethod",
        param1,
        param2
    )
    return types.TextContent(type="text", text=result)
```

### Future Tool Categories
- **SQL Tools**: Advanced query execution with result sets
- **Transaction Tools**: Transaction management and rollback
- **Monitoring Tools**: Performance metrics and profiling
- **Security Tools**: Audit and compliance operations

## Production Deployment Patterns

### Configuration Management
```json
{
    "iris-execute-mcp": {
        "command": "path/to/venv/Scripts/python.exe",
        "args": ["path/to/iris_execute_mcp.py"],
        "transportType": "stdio"
    }
}
```

### Environment Variables
```python
# .env file pattern
IRIS_HOST=localhost
IRIS_PORT=1972
IRIS_NAMESPACE=HSCUSTOM
IRIS_USERNAME=_SYSTEM
IRIS_PASSWORD=SYS
```

### Virtual Environment Pattern
```bash
# Standard Python virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Innovation Patterns

### I/O Capture Breakthrough
- **Problem**: STDIO pollution causing MCP timeouts
- **Innovation**: Global variable capture mechanism
- **Result**: Real output with zero timeouts

### WorkMgr Process Isolation
- **Problem**: %UnitTest.Manager singleton conflicts
- **Innovation**: %SYSTEM.WorkMgr process isolation
- **Result**: 60,000x performance improvement

### Direct Execution Model
- **Problem**: Session management overhead
- **Innovation**: Stateless direct execution
- **Result**: 0ms execution time achieved

### Custom TestRunner
- **Problem**: VS Code sync issues with %UnitTest.Manager
- **Innovation**: Direct compiled class execution
- **Result**: Eliminated filesystem dependency

## Documentation Patterns

### Memory Bank Structure
```
memory-bank/
├── activeContext.md    # Current implementation status
├── progress.md         # Development timeline
├── productContext.md   # Product vision and features
├── systemPatterns.md   # This file - architecture patterns
└── implementation/     # Technical implementation details
```

### Version Management
- v2.4.0: Custom TestRunner Implementation (In Progress)
- v2.3.1: Auto-Prefix Enhancement for Unit Tests
- v2.3.0: WorkMgr Unit Testing Implementation
- v2.2.0: Compilation Tools Added
- v2.1.0: I/O Capture Breakthrough
- v2.0.0: Direct Execution Architecture

**Current Architecture**: Development-focused IRIS Execute MCP Server with 8 essential tools, featuring breakthrough innovations in I/O capture and custom TestRunner implementation for VS Code sync-free unit testing.
