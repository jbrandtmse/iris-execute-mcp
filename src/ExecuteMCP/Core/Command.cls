/// <h3>IRIS Command Executor for MCP</h3>
/// <p>Direct ObjectScript command execution without session management.</p>
/// <p>Designed for Native API invocation from Python MCP clients.</p>
/// <p>Simplified architecture - focuses on reliable direct execution.</p>
/// 
Class ExecuteMCP.Core.Command Extends %RegisteredObject
{

/// <b>Command execution timeout in seconds</b>
Parameter DEFAULTTIMEOUT = 30;

/// <b>Maximum output size in bytes</b>
Parameter MAXOUTPUTSIZE = 65536;

/// <h3>Execute Command</h3>
/// <p>Class method for Native API invocation to execute ObjectScript command directly.</p>
/// <p>No session management - immediate execution with security validation.</p>
/// <p>Returns JSON with execution results and timing information.</p>
ClassMethod ExecuteCommand(pCommand As %String, pNamespace As %String = "HSCUSTOM") As %String
{
    Set tSC = $$$OK
    Set tResult = {}
    Set tOriginalNamespace = $NAMESPACE
    
    Try {
        // Switch namespace if needed
        If (pNamespace '= $NAMESPACE) {
            Set $NAMESPACE = pNamespace
        }
        
        // Check security permissions before execution
        If '$SYSTEM.Security.Check("%Development","USE") {
            Set tResult.status = "error"
            Set tResult.errorMessage = "Insufficient privileges for command execution (requires %Development:USE)"
            Quit
        }
        
        // Execute command with timing
        Set tStartTime = $HOROLOG
        
        // Initialize capture global for WRITE output
        Kill ^MCPCapture
        Set ^MCPCapture = ""
        
        // Check if command contains WRITE statements that need capture
        Set tNeedsCapture = 0
        Set tCommandUpper = $ZCONVERT(pCommand, "U")
        If (tCommandUpper [ "WRITE") {
            Set tNeedsCapture = 1
        }
        
        // Execute the command
        If tNeedsCapture {
            // Build a modified command that captures WRITE output
            // Parse the command to find WRITE statements
            Set tModifiedCommand = ""
            Set tPos = 1
            Set tLen = $LENGTH(pCommand)
            
            While tPos <= tLen {
                // Find next WRITE statement
                Set tWritePos = $FIND(tCommandUpper, "WRITE", tPos)
                
                If tWritePos = 0 {
                    // No more WRITE statements, add rest of command
                    If tPos <= tLen {
                        Set tRest = $EXTRACT(pCommand, tPos, tLen)
                        If tModifiedCommand '= "" {
                            Set tModifiedCommand = tModifiedCommand _ " " _ tRest
                        } Else {
                            Set tModifiedCommand = tRest
                        }
                    }
                    Set tPos = tLen + 1
                } Else {
                    // Found a WRITE statement
                    // Add everything before WRITE
                    If (tWritePos - 5) > tPos {
                        Set tBefore = $EXTRACT(pCommand, tPos, tWritePos - 6)
                        If tModifiedCommand '= "" {
                            Set tModifiedCommand = tModifiedCommand _ " " _ tBefore
                        } Else {
                            Set tModifiedCommand = tBefore
                        }
                    }
                    
                    // Find what's being written (everything up to next statement separator or end)
                    Set tStartWrite = tWritePos
                    Set tEndWrite = tLen
                    
                    // Look for statement separators
                    For tSep = " SET", " KILL", " DO", " FOR", " IF", " QUIT", " WRITE" {
                        Set tSepPos = $FIND(tCommandUpper, tSep, tStartWrite)
                        If (tSepPos > 0) && (tSepPos < tEndWrite) {
                            Set tEndWrite = tSepPos - $LENGTH(tSep)
                        }
                    }
                    
                    // Extract the WRITE argument
                    Set tWriteArg = $EXTRACT(pCommand, tStartWrite, tEndWrite)
                    Set tWriteArg = $ZSTRIP(tWriteArg, "<>W")
                    
                    // Add modified WRITE that captures to global
                    If tModifiedCommand '= "" {
                        Set tModifiedCommand = tModifiedCommand _ " "
                    }
                    Set tModifiedCommand = tModifiedCommand _ "SET ^MCPCapture = ^MCPCapture _ (" _ tWriteArg _ ")"
                    
                    Set tPos = tEndWrite + 1
                }
            }
            
            // Execute the modified command if we built one
            If tModifiedCommand '= "" {
                XECUTE tModifiedCommand
            } Else {
                // Fallback: execute original command
                XECUTE pCommand
            }
            
            // Get captured output
            Set tOutput = $GET(^MCPCapture, "")
            Kill ^MCPCapture
            
        } Else {
            // No WRITE statements, just execute normally
            XECUTE pCommand
            Set tOutput = "Command executed successfully"
        }
        
        Set tEndTime = $HOROLOG
        Set tExecutionTime = $PIECE(tEndTime,",",2) - $PIECE(tStartTime,",",2)
        
        // Build success response
        Set tResult.status = "success"
        Set tResult.output = tOutput
        Set tResult.namespace = pNamespace
        Set tResult.executionTimeMs = (tExecutionTime * 1000)
        Set tResult.mode = "direct"
        Set tResult.timestamp = $ZDateTime($HOROLOG, 3)
        
    } Catch ex {
        // Clean up capture global on error
        Kill ^MCPCapture
        
        Set tResult.status = "error"
        Set tResult.errorMessage = ex.DisplayString()
        Set tResult.namespace = pNamespace
        Set tResult.timestamp = $ZDateTime($HOROLOG, 3)
    }
    
    // Always restore original namespace
    Set $NAMESPACE = tOriginalNamespace
    
    Set tJSON = tResult.%ToJSON()
    
    Quit tJSON
}

/// <h3>Get Global Value</h3>
/// <p>Class method to get global value dynamically.</p>
/// <p>Handles globals like ^TempGlobal, ^TempGlobal(1,2), ^TempGlobal("This","That").</p>
ClassMethod GetGlobal(pGlobalRef As %String, pNamespace As %String = "HSCUSTOM") As %String
{
    Set tSC = $$$OK
    Set tResult = {}
    Set tOriginalNamespace = $NAMESPACE
    
    Try {
        // Switch namespace if needed
        If (pNamespace '= $NAMESPACE) {
            Set $NAMESPACE = pNamespace
        }
        
        // Check security permissions
        If '$SYSTEM.Security.Check("%Development","USE") {
            Set tResult.status = "error"
            Set tResult.errorMessage = "Insufficient privileges for global access (requires %Development:USE)"
            Quit
        }
        
        // Validate global reference format
        // The Python bridge might be stripping the ^ character or encoding it differently
        Set tGlobalRef = pGlobalRef
        
        // If it doesn't start with ^, add it
        If $EXTRACT(tGlobalRef,1) '= "^" {
            Set tGlobalRef = "^"_tGlobalRef
        }
        
        // Use $GET with @ for safe dynamic access
        Set tValue = $GET(@tGlobalRef)
        Set tExists = $DATA(@tGlobalRef)
        
        // Build success response
        Set tResult.status = "success"
        Set tResult.globalRef = tGlobalRef
        Set tResult.value = tValue
        Set tResult.exists = tExists
        Set tResult.namespace = pNamespace
        Set tResult.timestamp = $ZDateTime($HOROLOG, 3)
        Set tResult.mode = "get_global"
        
    } Catch ex {
        Set tResult.status = "error"
        Set tResult.errorMessage = ex.DisplayString()
        Set tResult.globalRef = pGlobalRef
        Set tResult.namespace = pNamespace
        Set tResult.timestamp = $ZDateTime($HOROLOG, 3)
    }
    
    // Always restore original namespace
    Set $NAMESPACE = tOriginalNamespace
    
    Quit tResult.%ToJSON()
}

/// <h3>Set Global Value</h3>
/// <p>Class method to set global value dynamically.</p>
/// <p>Handles globals like ^TempGlobal, ^TempGlobal(1,2), ^TempGlobal("This","That").</p>
ClassMethod SetGlobal(pGlobalRef As %String, pValue As %String, pNamespace As %String = "HSCUSTOM") As %String
{
    Set tSC = $$$OK
    Set tResult = {}
    Set tOriginalNamespace = $NAMESPACE
    
    Try {
        // Switch namespace if needed
        If (pNamespace '= $NAMESPACE) {
            Set $NAMESPACE = pNamespace
        }
        
        // Check security permissions
        If '$SYSTEM.Security.Check("%Development","USE") {
            Set tResult.status = "error"
            Set tResult.errorMessage = "Insufficient privileges for global access (requires %Development:USE)"
            Quit
        }
        
        // Validate and fix global reference format
        // The Python bridge might be stripping the ^ character or encoding it differently
        Set tGlobalRef = pGlobalRef
        
        // If it doesn't start with ^, add it
        If $EXTRACT(tGlobalRef,1) '= "^" {
            Set tGlobalRef = "^"_tGlobalRef
        }
        
        // Set the global value using @ for dynamic access
        Set @tGlobalRef = pValue
        
        // Verify the set operation
        Set tVerifyValue = $GET(@tGlobalRef)
        Set tExists = $DATA(@tGlobalRef)
        
        // Build success response
        Set tResult.status = "success"
        Set tResult.globalRef = tGlobalRef
        Set tResult.setValue = pValue
        Set tResult.verifyValue = tVerifyValue
        Set tResult.exists = tExists
        Set tResult.namespace = pNamespace
        Set tResult.timestamp = $ZDateTime($HOROLOG, 3)
        Set tResult.mode = "set_global"
        
    } Catch ex {
        Set tResult.status = "error"
        Set tResult.errorMessage = ex.DisplayString()
        Set tResult.globalRef = pGlobalRef
        Set tResult.namespace = pNamespace
        Set tResult.timestamp = $ZDateTime($HOROLOG, 3)
    }
    
    // Always restore original namespace
    Set $NAMESPACE = tOriginalNamespace
    
    Quit tResult.%ToJSON()
}

/// <h3>Get System Info</h3>
/// <p>Class method to get basic IRIS system information.</p>
/// <p>Useful for connectivity testing and system validation.</p>
ClassMethod GetSystemInfo() As %String
{
    Set tSC = $$$OK
    Set tResult = {}
    
    Try {
        Set tResult.status = "success"
        Set tResult.version = $SYSTEM.Version.GetVersion()
        Set tResult.namespace = $NAMESPACE
        Set tResult.timestamp = $ZDateTime($HOROLOG, 3)
        Set tResult.serverTime = $HOROLOG
        Set tResult.mode = "info"
        
    } Catch ex {
        Set tResult.status = "error"
        Set tResult.errorMessage = ex.DisplayString()
    }
    
    Quit tResult.%ToJSON()
}

/// <h3>Execute Class Method</h3>
/// <p>Class method to dynamically invoke ObjectScript class methods with support for output parameters.</p>
/// <p>Handles both input and output parameters, captures WRITE output, and returns comprehensive results.</p>
/// <p>Parameters are passed as JSON array with metadata about each parameter.</p>
ClassMethod ExecuteClassMethod(pClassName As %String, pMethodName As %String, pParameters As %String = "[]", pNamespace As %String = "HSCUSTOM") As %String
{
    Set tSC = $$$OK
    Set tResult = {}
    Set tOriginalNamespace = $NAMESPACE
    
    Try {
        // Switch namespace if needed
        If (pNamespace '= $NAMESPACE) {
            Set $NAMESPACE = pNamespace
        }
        
        // Check security permissions before execution
        If '$SYSTEM.Security.Check("%Development","USE") {
            Set tResult.status = "error"
            Set tResult.errorMessage = "Insufficient privileges for method execution (requires %Development:USE)"
            Quit
        }
        
        // Parse parameters JSON
        Set tParamsObj = {}.%FromJSON(pParameters)
        Set tParamCount = tParamsObj.%Size()
        
        // Initialize local variables for parameters
        // We'll use v1, v2, v3... as local variable names
        Set tParamList = ""
        Set tOutputParams = {}
        
        // Build parameter list and initialize variables
        For i=1:1:tParamCount {
            Set tParam = tParamsObj.%Get(i-1)
            // Get value property
            Set tValue = ""
            If tParam.%IsDefined("value") {
                Set tValue = tParam.%Get("value")
            }
            // Get isOutput property
            Set tIsOutput = 0
            If tParam.%IsDefined("isOutput") {
                Set tIsOutput = tParam.%Get("isOutput")
            }
            
            // Set the local variable
            Set @("v"_i) = tValue
            
            // Build parameter list for XECUTE
            If tParamList '= "" {
                Set tParamList = tParamList_", "
            }
            
            // Add parameter with . prefix if it's an output parameter
            If tIsOutput {
                Set tParamList = tParamList_".v"_i
                // Track output parameters for later extraction
                Do tOutputParams.%Set("param"_i, i)
            } Else {
                Set tParamList = tParamList_"v"_i
            }
        }
        
        // Prepare for output capture
        Set ^MCPCapture = ""
        Set tCapturedOutput = ""
        
        // Execute timing
        Set tStartTime = $HOROLOG
        
        // Build and execute the dynamic method call
        Set tExecuteCmd = "Set tMethodResult = $CLASSMETHOD("""_pClassName_""", """_pMethodName_""""
        If tParamList '= "" {
            Set tExecuteCmd = tExecuteCmd_", "_tParamList
        }
        Set tExecuteCmd = tExecuteCmd_")"
        
        // Execute the method call
        Try {
            // For methods that might have WRITE statements, we need to capture output
            // Use a global to capture the method result due to XECUTE scope
            Kill ^MCPMethodResult
            
            // Modify the execute command to use a global for result capture
            Set tExecuteCmd = "Set ^MCPMethodResult = $CLASSMETHOD("""_pClassName_""", """_pMethodName_""""
            If tParamList '= "" {
                Set tExecuteCmd = tExecuteCmd_", "_tParamList
            }
            Set tExecuteCmd = tExecuteCmd_")"
            
            // Execute the method
            XECUTE tExecuteCmd
            
            // Get the method result from the global
            Set tMethodResult = $GET(^MCPMethodResult, "")
            Kill ^MCPMethodResult
            
            // Get any captured output from methods that use WRITE
            Set tCapturedOutput = $GET(^MCPCapture, "")
            
        } Catch execEx {
            // Clean up on error
            Kill ^MCPCapture
            Kill ^MCPMethodResult
            Set tResult.status = "error"
            Set tResult.errorMessage = "Method execution failed: "_execEx.DisplayString()
            Set tResult.className = pClassName
            Set tResult.methodName = pMethodName
            
            // Exit the outer try block
            Throw execEx
        }
        
        // Clean up capture global
        Kill ^MCPCapture
        
        // Calculate execution time
        Set tEndTime = $HOROLOG
        Set tExecutionTime = $PIECE(tEndTime,",",2) - $PIECE(tStartTime,",",2)
        
        // Extract output parameter values
        Set tOutputValues = {}
        // Check each parameter to see if it was an output parameter
        For i=1:1:tParamCount {
            Set tParamKey = "param"_i
            Try {
                Set tVarIndex = tOutputParams.%Get(tParamKey)
                Set tVarName = "v"_tVarIndex
                Do tOutputValues.%Set(tParamKey, @tVarName)
            } Catch {
                // Not an output parameter, skip it
            }
        }
        
        // Build success response
        Set tResult.status = "success"
        Set tResult.methodResult = $GET(tMethodResult, "")
        Set tResult.outputParameters = tOutputValues
        Set tResult.capturedOutput = tCapturedOutput
        Set tResult.executionTimeMs = (tExecutionTime * 1000)
        Set tResult.className = pClassName
        Set tResult.methodName = pMethodName
        Set tResult.namespace = pNamespace
        Set tResult.timestamp = $ZDateTime($HOROLOG, 3)
        
    } Catch ex {
        Set tResult.status = "error"
        Set tResult.errorMessage = ex.DisplayString()
        Set tResult.className = pClassName
        Set tResult.methodName = pMethodName
        Set tResult.namespace = pNamespace
        Set tResult.timestamp = $ZDateTime($HOROLOG, 3)
    }
    
    // Always restore original namespace
    Set $NAMESPACE = tOriginalNamespace
    
    Quit tResult.%ToJSON()
}

}
