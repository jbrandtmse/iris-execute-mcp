# Implementation Plan: Compilation Tools for IRIS Execute MCP Server

## Overview
Add two new tools to the IRIS Execute MCP Server for compiling ObjectScript classes and packages:
1. **compile_objectscript_class** - Compile individual or multiple classes
2. **compile_objectscript_package** - Compile all classes in a package

## Technical Research Summary

### Core IRIS Compilation Methods

#### 1. $System.OBJ.CompileList
For compiling individual or multiple classes:
```objectscript
ClassMethod CompileList(
    ByRef list As %String = "",     // List of items to compile
    qspec As %String = "",           // Compilation flags/qualifiers
    ByRef errorlog As %String,       // Output: Error information array
    ByRef updatedlist As %String     // Output: List of updated items
) As %Status
```

Key points:
- List format: "Class1.cls,Class2.cls,Routine.mac"
- Each item must include type suffix (.cls for classes)
- Returns %Status indicating success/failure
- errorlog is populated with detailed error information

#### 2. $System.OBJ.CompilePackage
For compiling entire packages:
```objectscript
ClassMethod CompilePackage(
    package As %String = "",      // Package name
    qspec As %String = "",        // Compilation flags/qualifiers
    ByRef errorlog As %String     // Output: Error information array
) As %Status
```

Key points:
- Compiles all classes within specified package
- Automatically handles dependencies
- Returns %Status with comprehensive error reporting

### Error Handling Architecture

#### %Status Processing
```objectscript
// Check if error occurred
If $$$ISERR(tSC) {
    // Decompose status into error array
    Do $SYSTEM.Status.DecomposeStatus(tSC, .errorlist)
    // Process each error
    For i=1:1:errorlist {
        // errorlist(i) contains error message
        // errorlist(i,"code") contains error code
        // errorlist(i,"namespace") contains namespace
        // errorlist(i,"caller") contains calling context
    }
}
```

#### Errorlog Array Structure
```
errorlog = 2  // Number of errors
errorlog(1) = "Primary error message"
errorlog(1,"code") = 5001
errorlog(1,"domain") = "%ObjectErrors"
errorlog(1,"namespace") = "USER"
errorlog(1,"caller") = "CompileList+123^%SYSTEM.OBJ"
errorlog(1,"param") = 1
errorlog(1,"param",1) = "ClassName.cls"
errorlog(2) = "Secondary error message"
// ... continues for each error
```

### Compilation Flags (qspec)
Common compilation flags:
- **"ck"** - Compile and keep intermediate code
- **"/display=all"** - Show all compilation messages
- **"/checkuptodate=expandedonly"** - Check dependencies
- **"b"** - Build (compile) dependent classes
- **"d"** - Display compilation progress
- **"e"** - Delete existing error log before compiling
- **"u"** - Update only (skip if up-to-date)

## Implementation Architecture

### Tool 1: compile_objectscript_class

#### ObjectScript Backend (ExecuteMCP.Core.Compile.cls)
```objectscript
ClassMethod CompileClasses(
    pClassList As %String,          // Comma-separated list of classes
    pQSpec As %String = "bckry",    // Compilation flags (default: bckry)
    pNamespace As %String            // Target namespace
) As %String
{
    // 1. Switch to target namespace
    // 2. Build properly formatted list with .cls suffixes
    // 3. Call $System.OBJ.CompileList
    // 4. Process errorlog array
    // 5. Return JSON with results and errors
}
```

#### Python MCP Tool
```python
@mcp.tool()
def compile_objectscript_class(
    class_names: str,                # Single class or comma-separated list
    qspec: str = "bckry",            # Compilation flags (optional)
    namespace: str = "HSCUSTOM"      # Target namespace
) -> str:
    """
    Compile one or more ObjectScript classes.
    
    Args:
        class_names: Class name(s) to compile (e.g., "MyClass" or "Class1,Class2")
        qspec: Compilation flags (default: "bckry")
               b = Rebuild dependencies
               c = Compile
               k = Keep generated source
               r = Recursive compile  
               y = Display compilation information
        namespace: Target namespace (default: HSCUSTOM)
    
    Returns:
        JSON with compilation status and any errors
    """
```

### Tool 2: compile_objectscript_package

#### ObjectScript Backend (ExecuteMCP.Core.Compile.cls)
```objectscript
ClassMethod CompilePackage(
    pPackageName As %String,         // Package name
    pQSpec As %String = "bckry",     // Compilation flags (default: bckry)
    pNamespace As %String             // Target namespace
) As %String
{
    // 1. Switch to target namespace
    // 2. Call $System.OBJ.CompilePackage
    // 3. Process errorlog array
    // 4. Return JSON with results and errors
}
```

#### Python MCP Tool
```python
@mcp.tool()
def compile_objectscript_package(
    package_name: str,               # Package name to compile
    qspec: str = "bckry",            # Compilation flags (optional)
    namespace: str = "HSCUSTOM"      # Target namespace
) -> str:
    """
    Compile all classes in an ObjectScript package.
    
    Args:
        package_name: Package name (e.g., "ExecuteMCP.Core")
        qspec: Compilation flags (default: "bckry")
               b = Rebuild dependencies
               c = Compile
               k = Keep generated source
               r = Recursive compile
               y = Display compilation information
        namespace: Target namespace (default: HSCUSTOM)
    
    Returns:
        JSON with compilation status and any errors
    """
```

## JSON Response Format

### Success Response
```json
{
    "status": "success",
    "compiledItems": ["Class1.cls", "Class2.cls"],
    "compiledCount": 2,
    "namespace": "HSCUSTOM",
    "qspec": "ck",
    "executionTime": 245,
    "warnings": []
}
```

### Error Response
```json
{
    "status": "error",
    "compiledItems": ["Class1.cls"],
    "failedItems": ["Class2.cls"],
    "compiledCount": 1,
    "errorCount": 1,
    "namespace": "HSCUSTOM",
    "errors": [
        {
            "message": "Syntax error in method TestMethod",
            "class": "Class2.cls",
            "code": 5002,
            "line": 45,
            "offset": 12
        }
    ],
    "executionTime": 189
}
```

### Partial Success Response
```json
{
    "status": "partial",
    "compiledItems": ["Class1.cls", "Class3.cls"],
    "failedItems": ["Class2.cls"],
    "compiledCount": 2,
    "errorCount": 1,
    "namespace": "HSCUSTOM",
    "errors": [
        {
            "message": "Property type not found",
            "class": "Class2.cls",
            "code": 5001
        }
    ],
    "warnings": [
        {
            "message": "Deprecated method usage",
            "class": "Class3.cls"
        }
    ],
    "executionTime": 312
}
```

## Implementation Steps

### Phase 1: Backend Implementation
1. Create `src/ExecuteMCP/Core/Compile.cls` class
2. Implement `CompileClasses` method
   - Parse class list and add .cls suffixes
   - Call $System.OBJ.CompileList
   - Process errorlog array
   - Format JSON response
3. Implement `CompilePackage` method
   - Call $System.OBJ.CompilePackage
   - Process errorlog array
   - Format JSON response
4. Add helper method `ProcessErrorLog` for consistent error formatting

### Phase 2: MCP Integration
1. Update `iris_execute_mcp.py`
   - Add `compile_objectscript_class` tool
   - Add `compile_objectscript_package` tool
   - Use existing call_iris_sync pattern
2. Update tool count in documentation (13 → 15 tools)

### Phase 3: Testing
1. Create test classes with various scenarios:
   - Valid class compilation
   - Class with syntax errors
   - Class with missing dependencies
   - Package compilation
2. Test error reporting accuracy
3. Verify qspec flag behavior
4. Test namespace switching

## Error Scenarios to Handle

1. **Syntax Errors**: Missing semicolons, invalid method signatures
2. **Dependency Errors**: Referenced classes don't exist
3. **Permission Errors**: Insufficient privileges to compile
4. **Namespace Errors**: Invalid namespace specified
5. **Class Not Found**: Specified class doesn't exist
6. **Package Not Found**: Specified package doesn't exist
7. **Compilation Timeout**: Very large packages

## Testing Strategy

### Unit Tests
```objectscript
// Test valid compilation
Set tSC = ##class(ExecuteMCP.Core.Compile).CompileClasses("ExecuteMCP.Test.ValidClass", "ck", "HSCUSTOM")

// Test error handling
Set tSC = ##class(ExecuteMCP.Core.Compile).CompileClasses("ExecuteMCP.Test.InvalidClass", "ck", "HSCUSTOM")

// Test package compilation
Set tSC = ##class(ExecuteMCP.Core.Compile).CompilePackage("ExecuteMCP.Test", "ck", "HSCUSTOM")
```

### Integration Tests
```python
# Test single class compilation
result = compile_objectscript_class("MyClass", "ck", "HSCUSTOM")

# Test multiple classes
result = compile_objectscript_class("Class1,Class2,Class3", "ck", "HSCUSTOM")

# Test package compilation
result = compile_objectscript_package("MyPackage", "ckb", "HSCUSTOM")
```

## Success Criteria
1. ✅ Both tools successfully compile valid classes/packages
2. ✅ Comprehensive error reporting for compilation failures
3. ✅ Proper handling of multiple classes in single call
4. ✅ Accurate error location reporting (line/offset when available)
5. ✅ Support for common compilation flags
6. ✅ Clean JSON response format for all scenarios
7. ✅ Integration with existing MCP server architecture

## Implementation Confidence: 100%
Based on comprehensive research, I have complete understanding of:
- $System.OBJ.CompileList and CompilePackage methods
- %Status error handling patterns
- Errorlog array structure and processing
- Compilation flag system (qspec)
- Error decomposition and reporting
- Integration with existing ExecuteMCP architecture

Ready to proceed with implementation.
