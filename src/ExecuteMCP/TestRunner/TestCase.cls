/// ExecuteMCP.TestRunner.TestCase - Custom base class for tests that works with our TestRunner
/// This class extends %UnitTest.TestCase and properly initializes the Manager property
Class ExecuteMCP.TestRunner.TestCase Extends %UnitTest.TestCase
{

/// Override %OnNew to initialize Manager from a global variable
/// This allows our TestRunner to provide the Manager context
Method %OnNew(initvalue As %String = "") As %Status
{
    Set tSC = $$$OK
    Try {
        ; Call parent constructor first
        Set tSC = ##super(initvalue)
        If $$$ISERR(tSC) Quit
        
        ; Check if TestRunner has set a Manager in the global
        If $DATA(^||TestRunnerManager) {
            ; Use the Manager provided by TestRunner
            Set ..Manager = ^||TestRunnerManager
        }
        ElseIf $DATA(^TestRunnerManager) {
            ; Fallback to standard global if process-private not available
            Set ..Manager = ^TestRunnerManager
        }
        Else {
            ; Create a default Manager if none provided
            ; This ensures assertions won't fail with INVALID OREF
            Set ..Manager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        }
    }
    Catch ex {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}

/// Helper method to ensure Manager is available
Method EnsureManager() As %Status
{
    Set tSC = $$$OK
    Try {
        If '$ISOBJECT(..Manager) {
            ; Try to get Manager from globals
            If $DATA(^||TestRunnerManager) {
                Set ..Manager = ^||TestRunnerManager
            }
            ElseIf $DATA(^TestRunnerManager) {
                Set ..Manager = ^TestRunnerManager
            }
            Else {
                ; Create default Manager
                Set ..Manager = ##class(ExecuteMCP.TestRunner.Manager).%New()
            }
        }
    }
    Catch ex {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}

/// Override OnBeforeOneTest to ensure Manager is set
Method OnBeforeOneTest(testname As %String) As %Status
{
    ; Ensure Manager is available before test execution
    Set tSC = ..EnsureManager()
    If $$$ISERR(tSC) Quit tSC
    
    ; Call parent implementation if it exists
    Quit ##super(testname)
}

}
