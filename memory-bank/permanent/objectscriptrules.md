# ObjectScript Development Rules - IRIS Terminal MCP Server

## Core Development Standards

### Class and Method Naming
**Class Parameter Rules:**
- NEVER use underscore ('_') characters in parameter names
- Use camelCase: `MyParameter`, `SessionTimeout`, `MaxConnections`
- Use ALL CAPS for constants: `TIMEOUT`, `MAXLENGTH`, `VERSION`
- Access parameters with # character: `..#PARAMETERNAME`

**Variable Naming Conventions:**
- **Parameters**: "p" prefix (e.g., `pSessionId`, `pCommand`, `pTimeout`)
- **Local variables**: "t" prefix (e.g., `tResult`, `tIndex`, `tConnection`)
- **Class properties**: Capitalized, no prefix (e.g., `SessionId`, `OutputBuffer`)

**Method Naming:**
- PascalCase for public methods: `ExecuteCommand()`, `CreateSession()`
- camelCase for private methods: `captureOutput()`, `validateInput()`

### Status Handling Pattern
**Standard Method Structure:**
```objectscript
Method ExecuteCommand(pSessionId As %String, pCommand As %String) As %Status
{
    Set tSC = $$$OK
    Try {
        // Method implementation
        Do ..SomeOperation()
        Set tResult = ..ProcessCommand(pCommand)
    } Catch (ex) {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}
```

**Key Requirements:**
- First line: `Set tSC = $$$OK`
- Last line: `Quit tSC`
- Use try/catch for error trapping
- Return %Status from methods that produce no return value

### Macro Syntax Rules
**CRITICAL: Use Triple Dollar Signs ($$$)**
```objectscript
// CORRECT - Use $$$
Set tSC = $$$OK
If $$$ISERR(tSC) Quit tSC
Set tResult = $$$ERROR($$$GeneralError, "Message")

// INCORRECT - Never use $$
Set tSC = $$OK              // WRONG
If $$ISERR(tSC) Quit tSC    // WRONG
```

**Macro Fix Strategy:**
- When encountering multiple $$ syntax errors, use `write_to_file` for full replacement
- NEVER use `replace_in_file` for $ vs $$ macro syntax fixes
- Single file replacement prevents cascading errors

### Indentation and Formatting
**Command Indentation:**
- ALWAYS indent ObjectScript commands within methods by at least 1 space or tab
- Maintain consistent spacing throughout method body
- Avoid zero-indentation for commands (causes compile errors)

**Example:**
```objectscript
Method ValidExample() As %Status
{
    Set tSC = $$$OK           // Properly indented
    Try {
        Set tValue = 1        // Properly indented
        Write "Hello"         // Properly indented
    } Catch (ex) {
        Set tSC = ex.AsStatus() // Properly indented
    }
    Quit tSC
}
```

### Documentation Standards
**Class Documentation:**
```objectscript
/// <h3>SessionMCP Core Session Manager</h3>
/// <p>Manages IRIS terminal sessions for MCP server integration.</p>
/// <p>Provides command execution, I/O redirection, and state management.</p>
/// 
/// <h4>Key Features:</h4>
/// <ul>
/// <li>Session persistence across multiple commands</li>
/// <li>I/O redirection and output capture</li>
/// <li>Error handling and status reporting</li>
/// </ul>
Class SessionMCP.Core.Session Extends %RegisteredObject
```

**Method Documentation:**
```objectscript
/// <h3>Execute ObjectScript Command</h3>
/// <p>Executes an ObjectScript command in the context of this session.</p>
/// 
/// <h4>Parameters:</h4>
/// <ul>
/// <li><b>pCommand</b> - ObjectScript command to execute</li>
/// <li><b>pTimeout</b> - Maximum execution time in seconds</li>
/// </ul>
/// 
/// <h4>Returns:</h4>
/// <p>%Status indicating success or failure</p>
Method ExecuteCommand(pCommand As %String, pTimeout As %Integer = 30) As %Status
```

### Error Handling Patterns
**Exception Handling:**
```objectscript
Try {
    // Risky operation
    Set tResult = ..ProcessData(pInput)
} Catch (ex) {
    // Log error details
    Do ..LogError("ProcessData failed", ex)
    Set tSC = ex.AsStatus()
}
```

**Status Code Checking:**
```objectscript
Set tSC = ..SomeOperation()
If $$$ISERR(tSC) {
    Do ..LogStatus("Operation failed", tSC)
    Quit tSC
}
```

**Custom Error Creation:**
```objectscript
Set tSC = $$$ERROR($$$GeneralError, "Invalid session ID: "_pSessionId)
```

## SessionMCP-Specific Rules

### Session Management Pattern
**Global Variable Usage:**
```objectscript
// Store session state
Set ^SessionMCP.State(pSessionId, "namespace") = $NAMESPACE
Set ^SessionMCP.State(pSessionId, "created") = $HOROLOG
Set ^SessionMCP.State(pSessionId, "lastAccess") = $HOROLOG

// Retrieve session state
Set tNamespace = $Get(^SessionMCP.State(pSessionId, "namespace"), "USER")
```

### I/O Redirection Pattern
**Output Capture Implementation:**
```objectscript
Method CaptureOutput() As %Status
{
    Set tSC = $$$OK
    Try {
        // Enable I/O redirection
        Do ##class(%Device).ReDirectIO($$$YES)
        Set ..OutputCapture = 1
    } Catch (ex) {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}

Method RestoreIO() As %Status
{
    Set tSC = $$$OK
    Try {
        // Disable I/O redirection
        Do ##class(%Device).ReDirectIO($$$NO)
        Set ..OutputCapture = 0
    } Catch (ex) {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}
```

### Native API Integration
**Method Signature for Native API Calls:**
```objectscript
/// ClassMethod for Native API invocation
ClassMethod ExecuteCommand(pSessionId As %String, pCommand As %String) As %String
{
    Set tSession = ..GetSession(pSessionId)
    If '$IsObject(tSession) {
        Return ..FormatError("Invalid session ID")
    }
    
    Set tSC = tSession.Execute(pCommand)
    If $$$ISERR(tSC) {
        Return ..FormatError($System.Status.GetErrorText(tSC))
    }
    
    Return tSession.GetOutput()
}
```

### Security Patterns
**Input Validation:**
```objectscript
Method ValidateCommand(pCommand As %String) As %Status
{
    Set tSC = $$$OK
    
    // Check command length
    If $Length(pCommand) > ..#MAXCOMMANDLENGTH {
        Set tSC = $$$ERROR($$$GeneralError, "Command too long")
        Quit tSC
    }
    
    // Check for forbidden patterns
    If ..ContainsForbiddenPattern(pCommand) {
        Set tSC = $$$ERROR($$$GeneralError, "Forbidden command pattern")
        Quit tSC
    }
    
    Quit tSC
}
```

## File Editing Best Practices

### When to Use write_to_file vs replace_in_file
**Use write_to_file for:**
- Multiple $ vs $$ macro syntax corrections
- Extensive indentation fixes
- Major structural changes
- New file creation

**Use replace_in_file for:**
- Single line changes
- Small targeted modifications
- Adding individual methods or properties

### Editing Workflow
**Before Editing:**
1. Read entire file to understand structure
2. Identify all necessary changes
3. Determine if changes affect indentation/formatting
4. Choose appropriate editing tool

**Quality Checks:**
1. Verify all commands are properly indented
2. Check all macro syntax uses $$$
3. Validate method signatures and documentation
4. Ensure consistent naming conventions

## Debugging and Troubleshooting

### Common Compilation Errors
**Indentation Errors:**
- **Symptom**: Commands not properly indented
- **Fix**: Ensure all commands within methods have proper indentation

**Macro Syntax Errors:**
- **Symptom**: Multiple $$ references causing compilation failures
- **Fix**: Use write_to_file to replace entire file with corrected $$$ syntax

**Parameter Name Errors:**
- **Symptom**: Underscore characters in parameter names
- **Fix**: Rename parameters to use camelCase

### Performance Considerations
**Global Variable Access:**
- Use subscript patterns for efficient access
- Implement cleanup mechanisms for abandoned sessions
- Consider memory usage for large session counts

**Method Optimization:**
- Minimize Try/Catch overhead in critical paths
- Use local variables for frequently accessed values
- Implement caching for expensive operations

## Version Control and Maintenance

### Code Review Checklist
- [ ] All parameter names use camelCase (no underscores)
- [ ] All macro references use $$$ syntax
- [ ] All commands properly indented
- [ ] Documentation includes HTML markup
- [ ] Error handling follows status pattern
- [ ] Method signatures compatible with Native API

### Maintenance Procedures
**Regular Code Audits:**
- Scan for deprecated patterns
- Verify macro syntax consistency
- Check documentation completeness
- Validate error handling coverage

**Refactoring Guidelines:**
- Maintain backward compatibility with Native API
- Preserve existing session state structures
- Update documentation with changes
- Test all affected functionality
