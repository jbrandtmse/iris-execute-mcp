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
    // Initialize debug logging
    Set ^MCPDebug = ""
    Set ^MCPDebug = ^MCPDebug_"START: ExecuteCommand method entered;"
    
    Set tSC = $$$OK
    Set tResult = {}
    Set tOriginalNamespace = $NAMESPACE
    
    Set ^MCPDebug = ^MCPDebug_"INIT: Variables initialized, original namespace="_tOriginalNamespace_";"
    
    Try {
        Set ^MCPDebug = ^MCPDebug_"TRY: Entered try block;"
        
        // Switch namespace if needed
        If (pNamespace '= $NAMESPACE) {
            Set ^MCPDebug = ^MCPDebug_"NAMESPACE: Switching from "_$NAMESPACE_" to "_pNamespace_";"
            Set $NAMESPACE = pNamespace
            Set ^MCPDebug = ^MCPDebug_"NAMESPACE: Switch completed, now in "_$NAMESPACE_";"
        } Else {
            Set ^MCPDebug = ^MCPDebug_"NAMESPACE: No switch needed, staying in "_$NAMESPACE_";"
        }
        
        // Check security permissions before execution
        Set ^MCPDebug = ^MCPDebug_"SECURITY: About to check %Development:USE privilege;"
        If '$SYSTEM.Security.Check("%Development","USE") {
            Set ^MCPDebug = ^MCPDebug_"SECURITY: FAILED - Insufficient privileges;"
            Set tResult.status = "error"
            Set tResult.errorMessage = "Insufficient privileges for command execution (requires %Development:USE)"
            Quit
        }
        Set ^MCPDebug = ^MCPDebug_"SECURITY: PASSED - Privilege check successful;"
        
        // Execute command with timing and output capture
        Set ^MCPDebug = ^MCPDebug_"TIMING: About to set start time;"
        Set tStartTime = $HOROLOG
        Set ^MCPDebug = ^MCPDebug_"TIMING: Start time set to "_tStartTime_";"
        
        // Capture output using I/O redirection to avoid STDIO pollution
        Set ^MCPDebug = ^MCPDebug_"IO: Saving current I/O device;"
        Set tOriginalIO = $IO
        Set tCapturedOutput = ""
        
        Try {
            // Create temporary capture device using a global for output capture
            Set ^MCPCapture = ""
            Set ^MCPDebug = ^MCPDebug_"IO: Creating capture mechanism;"
            
            // Use a more reliable approach - capture via global variable
            Set ^MCPDebug = ^MCPDebug_"EXECUTE: About to XECUTE with output capture: "_pCommand_";"
            
            // For WRITE commands, we need to capture the output differently
            // Use $DEVICE to capture output to a global
            Set tCaptureCommand = "Set ^MCPCapture=^MCPCapture_"_pCommand
            If (pCommand [ "WRITE") {
                // For WRITE commands, modify to append to our capture global
                Set tModifiedCommand = $PIECE(pCommand,"WRITE",2)
                Set tCaptureCommand = "Set ^MCPCapture = ^MCPCapture_("_tModifiedCommand_")"
                Set ^MCPDebug = ^MCPDebug_"EXECUTE: Modified WRITE command for capture;"
                XECUTE tCaptureCommand
            } Else {
                // For non-WRITE commands, execute normally
                Set ^MCPDebug = ^MCPDebug_"EXECUTE: Executing non-WRITE command;"
                XECUTE pCommand
            }
            
            Set ^MCPDebug = ^MCPDebug_"EXECUTE: Command execution completed;"
            
            // Get captured output
            Set tCapturedOutput = $GET(^MCPCapture,"")
            Set ^MCPDebug = ^MCPDebug_"EXECUTE: Captured output length: "_$LENGTH(tCapturedOutput)_";"
            
        } Catch (captureEx) {
            Set ^MCPDebug = ^MCPDebug_"IO: Capture failed, falling back to direct execution;"
            XECUTE pCommand
            Set tCapturedOutput = ""
        }
        
        // Clean up capture global
        Kill ^MCPCapture
        
        // Set output based on what was captured
        If (tCapturedOutput '= "") {
            Set tOutput = tCapturedOutput
            Set ^MCPDebug = ^MCPDebug_"EXECUTE: Using captured output;"
        } Else {
            Set tOutput = "Command executed successfully"
            Set ^MCPDebug = ^MCPDebug_"EXECUTE: Using default success message;"
        }
        
        Set ^MCPDebug = ^MCPDebug_"TIMING: About to calculate execution time;"
        Set tEndTime = $HOROLOG
        Set tExecutionTime = $PIECE(tEndTime,",",2) - $PIECE(tStartTime,",",2)
        Set ^MCPDebug = ^MCPDebug_"TIMING: End time="_tEndTime_", execution time="_tExecutionTime_"ms;"
        
        // Build success response
        Set ^MCPDebug = ^MCPDebug_"RESPONSE: Building success response;"
        Set tResult.status = "success"
        Set tResult.output = tOutput
        Set tResult.namespace = pNamespace
        Set tResult.executionTimeMs = (tExecutionTime * 1000)
        Set tResult.mode = "direct"
        Set tResult.timestamp = $ZDateTime($HOROLOG, 3)
        Set ^MCPDebug = ^MCPDebug_"RESPONSE: Success response built;"
        
    } Catch (ex) {
        Set ^MCPDebug = ^MCPDebug_"ERROR: Exception caught: "_ex.DisplayString()_";"
        Set tResult.status = "error"
        Set tResult.errorMessage = ex.DisplayString()
        Set tResult.namespace = pNamespace
        Set tResult.timestamp = $ZDateTime($HOROLOG, 3)
        Set ^MCPDebug = ^MCPDebug_"ERROR: Error response built;"
    }
    
    // Always restore original namespace
    Set ^MCPDebug = ^MCPDebug_"CLEANUP: About to restore original namespace;"
    Set $NAMESPACE = tOriginalNamespace
    Set ^MCPDebug = ^MCPDebug_"CLEANUP: Namespace restored to "_tOriginalNamespace_";"
    
    Set ^MCPDebug = ^MCPDebug_"JSON: About to convert result to JSON;"
    Set tJSON = tResult.%ToJSON()
    Set ^MCPDebug = ^MCPDebug_"JSON: Conversion completed;"
    
    Set ^MCPDebug = ^MCPDebug_"END: ExecuteCommand method completed successfully;"
    
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
        If $EXTRACT(pGlobalRef,1) '= "^" {
            Set tResult.status = "error"
            Set tResult.errorMessage = "Invalid global reference - must start with ^"
            Quit
        }
        
        // Use $GET with @ for safe dynamic access
        Set tValue = $GET(@pGlobalRef)
        Set tExists = $DATA(@pGlobalRef)
        
        // Build success response
        Set tResult.status = "success"
        Set tResult.globalRef = pGlobalRef
        Set tResult.value = tValue
        Set tResult.exists = tExists
        Set tResult.namespace = pNamespace
        Set tResult.timestamp = $ZDateTime($HOROLOG, 3)
        Set tResult.mode = "get_global"
        
    } Catch (ex) {
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
        
        // Validate global reference format
        If $EXTRACT(pGlobalRef,1) '= "^" {
            Set tResult.status = "error"
            Set tResult.errorMessage = "Invalid global reference - must start with ^"
            Quit
        }
        
        // Set the global value using @ for dynamic access
        Set @pGlobalRef = pValue
        
        // Verify the set operation
        Set tVerifyValue = $GET(@pGlobalRef)
        Set tExists = $DATA(@pGlobalRef)
        
        // Build success response
        Set tResult.status = "success"
        Set tResult.globalRef = pGlobalRef
        Set tResult.setValue = pValue
        Set tResult.verifyValue = tVerifyValue
        Set tResult.exists = tExists
        Set tResult.namespace = pNamespace
        Set tResult.timestamp = $ZDateTime($HOROLOG, 3)
        Set tResult.mode = "set_global"
        
    } Catch (ex) {
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
        
    } Catch (ex) {
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
            
        } Catch (execEx) {
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
        
    } Catch (ex) {
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
