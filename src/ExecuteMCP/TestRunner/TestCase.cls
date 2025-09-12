/// ExecuteMCP.TestRunner.TestCase - Custom base class for tests that works with our TestRunner
/// This class extends %UnitTest.TestCase and properly initializes the Manager property
Class ExecuteMCP.TestRunner.TestCase Extends %UnitTest.TestCase
{

/// Override %OnNew to pass Manager from global to parent constructor
/// The Manager property in %UnitTest.TestCase is PRIVATE and can only be set via constructor
Method %OnNew(initvalue As %String = "") As %Status
{
    Set tSC = $$$OK
    Try {
        ; Determine which Manager to use
        Set tManager = initvalue
        
        ; If no Manager provided, check globals
        If '$ISOBJECT(tManager) {
            If $DATA(^||TestRunnerManager) {
                ; Use the Manager provided by TestRunner (process-local)
                Set tManager = ^||TestRunnerManager
            }
            ElseIf $DATA(^TestRunnerManager) {
                ; Fallback to standard global if process-private not available
                Set tManager = ^TestRunnerManager
            }
            Else {
                ; Create a default Manager if none provided
                ; This ensures assertions won't fail with INVALID OREF
                Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
                
                ; Also set up a basic Context for the Manager
                Set tContext = ##class(ExecuteMCP.TestRunner.Context).%New()
                Set tManager.Context = tContext
            }
        }
        
        ; CRITICAL: Pass the Manager to parent constructor
        ; The parent %OnNew sets the private r%Manager property
        Set tSC = ##super(tManager)
        If $$$ISERR(tSC) Quit
    }
    Catch ex {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}

}
