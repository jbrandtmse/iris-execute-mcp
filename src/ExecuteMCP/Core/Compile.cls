Class ExecuteMCP.Core.Compile Extends %RegisteredObject
{

/// <h3>Compile one or more ObjectScript classes</h3>
/// <p>Compiles a comma-separated list of ObjectScript classes with comprehensive error reporting.</p>
/// <h4>Parameters:</h4>
/// <ul>
/// <li><b>pClassList</b> - Comma-separated list of class names (e.g., "Class1,Class2")</li>
/// <li><b>pQSpec</b> - Compilation flags (default: "bckry")</li>
/// <li><b>pNamespace</b> - Target namespace for compilation</li>
/// </ul>
/// <h4>Returns:</h4>
/// <p>JSON string with compilation results including any errors</p>
ClassMethod CompileClasses(pClassList As %String, pQSpec As %String = "bckry", pNamespace As %String = "HSCUSTOM") As %String
{
    Set tSC = $$$OK
    Set tStartTime = $ZHOROLOG
    Set tOriginalNS = $NAMESPACE
    
    // Initialize response structure
    Set tResponse = ##class(%DynamicObject).%New()
    Set tResponse.namespace = pNamespace
    Set tResponse.qspec = pQSpec
    Set tCompiledItems = ##class(%DynamicArray).%New()
    Set tFailedItems = ##class(%DynamicArray).%New()
    Set tErrors = ##class(%DynamicArray).%New()
    Set tWarnings = ##class(%DynamicArray).%New()
    
    Try {
        // Switch to target namespace
        Set $NAMESPACE = pNamespace
        
        // Build properly formatted list with .cls suffixes
        Set tClassCount = $LENGTH(pClassList, ",")
        Set tFormattedList = ""
        
        For i=1:1:tClassCount {
            Set tClassName = $ZSTRIP($PIECE(pClassList, ",", i), "<>W")
            If tClassName'="" {
                // Add .cls suffix if not already present
                If $ZCONVERT(tClassName,"L")'[".cls" {
                    Set tClassName = tClassName_".cls"
                }
                If tFormattedList'="" {
                    Set tFormattedList = tFormattedList_","_tClassName
                } Else {
                    Set tFormattedList = tClassName
                }
            }
        }
        
        // Call $System.OBJ.CompileList
        Kill tErrorLog, tUpdatedList
        Set tCompileSC = $SYSTEM.OBJ.CompileList(tFormattedList, pQSpec, .tErrorLog, .tUpdatedList)
        
        // Process compilation results
        If $$$ISOK(tCompileSC) {
            // All classes compiled successfully
            Set tResponse.status = "success"
            
            // Add compiled items from the formatted list since compilation succeeded
            For i=1:1:$LENGTH(tFormattedList, ",") {
                Set tClassName = $PIECE(tFormattedList, ",", i)
                If tClassName'="" {
                    Do tCompiledItems.%Push(tClassName)
                }
            }
        } Else {
            // Process error log
            Set tErrorCount = $GET(tErrorLog, 0)
            
            If tErrorCount > 0 {
                // Process each error in the errorlog array
                For i=1:1:tErrorCount {
                    Set tError = ##class(%DynamicObject).%New()
                    Set tError.message = $GET(tErrorLog(i), "Unknown error")
                    
                    // Extract additional error details if available
                    If $DATA(tErrorLog(i, "code")) {
                        Set tError.code = tErrorLog(i, "code")
                    }
                    If $DATA(tErrorLog(i, "namespace")) {
                        Set tError.namespace = tErrorLog(i, "namespace")
                    }
                    If $DATA(tErrorLog(i, "caller")) {
                        Set tError.caller = tErrorLog(i, "caller")
                    }
                    If $DATA(tErrorLog(i, "param", 1)) {
                        Set tError.class = tErrorLog(i, "param", 1)
                        Do tFailedItems.%Push(tErrorLog(i, "param", 1))
                    }
                    
                    Do tErrors.%Push(tError)
                }
            }
            
            // Also decompose the status for additional error details
            Do $SYSTEM.Status.DecomposeStatus(tCompileSC, .tStatusErrors)
            Set tStatusErrorCount = $GET(tStatusErrors, 0)
            
            For i=1:1:tStatusErrorCount {
                Set tError = ##class(%DynamicObject).%New()
                Set tError.message = $GET(tStatusErrors(i), "Unknown error")
                Set tError.source = "status"
                Do tErrors.%Push(tError)
            }
            
            // Check if we had partial success
            If tCompiledItems.%Size() > 0 {
                Set tResponse.status = "partial"
            } Else {
                Set tResponse.status = "error"
            }
        }
        
        // Add arrays to response
        Set tResponse.compiledItems = tCompiledItems
        Set tResponse.failedItems = tFailedItems
        Set tResponse.compiledCount = tCompiledItems.%Size()
        Set tResponse.errorCount = tErrors.%Size()
        Set tResponse.errors = tErrors
        Set tResponse.warnings = tWarnings
        
        // Calculate execution time in milliseconds
        Set tEndTime = $ZHOROLOG
        Set tResponse.executionTime = ($PIECE(tEndTime,",",2) - $PIECE(tStartTime,",",2)) * 1000
        
    } Catch ex {
        // Handle unexpected exceptions
        Set tResponse.status = "error"
        Set tResponse.error = "Exception during compilation: "_ex.DisplayString()
        Set tResponse.compiledCount = 0
        Set tResponse.errorCount = 1
    }
    
    // Restore original namespace
    Set $NAMESPACE = tOriginalNS
    
    // Return JSON response
    Quit tResponse.%ToJSON()
}

/// <h3>Compile all classes in an ObjectScript package</h3>
/// <p>Compiles all classes within a specified package with comprehensive error reporting.</p>
/// <h4>Parameters:</h4>
/// <ul>
/// <li><b>pPackageName</b> - Package name (e.g., "ExecuteMCP.Core")</li>
/// <li><b>pQSpec</b> - Compilation flags (default: "bckry")</li>
/// <li><b>pNamespace</b> - Target namespace for compilation</li>
/// </ul>
/// <h4>Returns:</h4>
/// <p>JSON string with compilation results including any errors</p>
ClassMethod CompilePackage(pPackageName As %String, pQSpec As %String = "bckry", pNamespace As %String = "HSCUSTOM") As %String
{
    Set tSC = $$$OK
    Set tStartTime = $ZHOROLOG
    Set tOriginalNS = $NAMESPACE
    
    // Initialize response structure
    Set tResponse = ##class(%DynamicObject).%New()
    Set tResponse.namespace = pNamespace
    Set tResponse.packageName = pPackageName
    Set tResponse.qspec = pQSpec
    Set tCompiledItems = ##class(%DynamicArray).%New()
    Set tFailedItems = ##class(%DynamicArray).%New()
    Set tErrors = ##class(%DynamicArray).%New()
    Set tWarnings = ##class(%DynamicArray).%New()
    
    Try {
        // Switch to target namespace
        Set $NAMESPACE = pNamespace
        
        // First, get list of classes in the package using SQL
        Set tSQL = "SELECT Name FROM %Dictionary.ClassDefinition WHERE Name %STARTSWITH ?"
        Set tStatement = ##class(%SQL.Statement).%New()
        Set tSC = tStatement.%Prepare(tSQL)
        
        If $$$ISOK(tSC) {
            Set tRS = tStatement.%Execute(pPackageName_".")
            Set tClassList = ""
            
            While tRS.%Next() {
                Set tClassName = tRS.%Get("Name")
                If tClassList'="" {
                    Set tClassList = tClassList_","_tClassName_".cls"
                } Else {
                    Set tClassList = tClassName_".cls"
                }
                Do tCompiledItems.%Push(tClassName_".cls")
            }
        }
        
        // Call $System.OBJ.CompilePackage
        Kill tErrorLog
        Set tCompileSC = $SYSTEM.OBJ.CompilePackage(pPackageName, pQSpec, .tErrorLog)
        
        // Process compilation results
        If $$$ISOK(tCompileSC) {
            // Package compiled successfully
            Set tResponse.status = "success"
            Set tResponse.message = "Package "_pPackageName_" compiled successfully"
        } Else {
            // Process error log
            Set tErrorCount = $GET(tErrorLog, 0)
            
            If tErrorCount > 0 {
                // Process each error in the errorlog array
                For i=1:1:tErrorCount {
                    Set tError = ##class(%DynamicObject).%New()
                    Set tError.message = $GET(tErrorLog(i), "Unknown error")
                    
                    // Extract additional error details if available
                    If $DATA(tErrorLog(i, "code")) {
                        Set tError.code = tErrorLog(i, "code")
                    }
                    If $DATA(tErrorLog(i, "namespace")) {
                        Set tError.namespace = tErrorLog(i, "namespace")
                    }
                    If $DATA(tErrorLog(i, "caller")) {
                        Set tError.caller = tErrorLog(i, "caller")
                    }
                    If $DATA(tErrorLog(i, "param", 1)) {
                        Set tError.class = tErrorLog(i, "param", 1)
                        Do tFailedItems.%Push(tErrorLog(i, "param", 1))
                    }
                    
                    Do tErrors.%Push(tError)
                }
            }
            
            // Also decompose the status for additional error details
            Do $SYSTEM.Status.DecomposeStatus(tCompileSC, .tStatusErrors)
            Set tStatusErrorCount = $GET(tStatusErrors, 0)
            
            For i=1:1:tStatusErrorCount {
                Set tError = ##class(%DynamicObject).%New()
                Set tError.message = $GET(tStatusErrors(i), "Unknown error")
                Set tError.source = "status"
                Do tErrors.%Push(tError)
            }
            
            // Determine if partial or complete failure
            If (tCompiledItems.%Size() > 0) && (tFailedItems.%Size() > 0) {
                Set tResponse.status = "partial"
            } Else {
                Set tResponse.status = "error"
            }
        }
        
        // Add arrays to response
        Set tResponse.compiledItems = tCompiledItems
        Set tResponse.failedItems = tFailedItems
        Set tResponse.compiledCount = tCompiledItems.%Size()
        Set tResponse.errorCount = tErrors.%Size()
        Set tResponse.errors = tErrors
        Set tResponse.warnings = tWarnings
        
        // Calculate execution time in milliseconds
        Set tEndTime = $ZHOROLOG
        Set tResponse.executionTime = ($PIECE(tEndTime,",",2) - $PIECE(tStartTime,",",2)) * 1000
        
    } Catch ex {
        // Handle unexpected exceptions
        Set tResponse.status = "error"
        Set tResponse.error = "Exception during package compilation: "_ex.DisplayString()
        Set tResponse.compiledCount = 0
        Set tResponse.errorCount = 1
    }
    
    // Restore original namespace
    Set $NAMESPACE = tOriginalNS
    
    // Return JSON response
    Quit tResponse.%ToJSON()
}

}
