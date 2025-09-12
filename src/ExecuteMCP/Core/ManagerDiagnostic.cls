/// ExecuteMCP.Core.ManagerDiagnostic - Debug Manager property issues
Class ExecuteMCP.Core.ManagerDiagnostic Extends %RegisteredObject
{

/// Test Manager property assignment
ClassMethod TestManagerProperty() As %String
{
    Try {
        Write "=== Manager Property Diagnostic ===",!
        
        ; Create mock manager
        Set mockManager = ##class(ExecuteMCP.Core.MockTestManager).%New()
        Write "Mock manager created: "_$ISOBJECT(mockManager),!
        
        ; Create test instance
        Set testInstance = ##class(ExecuteMCP.Test.SampleUnitTest).%New("")
        Write "Test instance created: "_$ISOBJECT(testInstance),!
        
        ; Set Manager property
        Set testInstance.Manager = mockManager
        Write "Manager property set",!
        
        ; Verify Manager is set
        Write "Manager is object: "_$ISOBJECT(testInstance.Manager),!
        Write "Manager class: "_$CLASSNAME(testInstance.Manager),!
        
        ; Test GetSourceLocation
        Set location = testInstance.Manager.GetSourceLocation()
        Write "GetSourceLocation result: "_location,!
        
        Write !,"=== Test with %testmanager variable ===",!
        
        ; Try with %testmanager variable (used by assertion macros)
        New %testmanager
        Set %testmanager = ##class(ExecuteMCP.Core.MockTestManager).%New()
        Write "%testmanager created: "_$ISOBJECT(%testmanager),!
        
        ; Create new test instance
        Set testInstance2 = ##class(ExecuteMCP.Test.SampleUnitTest).%New("")
        Set testInstance2.Manager = %testmanager
        
        ; Test if Manager can access GetSourceLocation
        Write "Testing Manager.GetSourceLocation: ",!
        Try {
            Set loc2 = testInstance2.Manager.GetSourceLocation()
            Write "Success: "_loc2,!
        } Catch ex2 {
            Write "Error: "_ex2.DisplayString(),!
        }
        
        Return "Diagnostic complete"
    }
    Catch ex {
        Return "ERROR: "_ex.DisplayString()
    }
}

/// Test assertion macro behavior
ClassMethod TestAssertionMacro() As %String
{
    Try {
        Write "=== Assertion Macro Test ===",!
        
        ; Set up %testmanager
        New %testmanager
        Set %testmanager = ##class(ExecuteMCP.Core.MockTestManager).%New()
        Write "%testmanager created",!
        
        ; Create test instance
        Set testInstance = ##class(ExecuteMCP.Test.SampleUnitTest).%New("")
        Set testInstance.Manager = %testmanager
        Write "Test instance created with Manager",!
        
        ; Try to run a test method
        Write "Attempting to run TestAlwaysPass...",!
        Set result = ""
        Try {
            ; Call the test method
            Set result = testInstance.TestAlwaysPass()
            Write "Test executed, result: "_result,!
            
            ; Check assertion counts
            Write "Assertions passed: "_%testmanager.AssertionsPassed,!
            Write "Assertions failed: "_%testmanager.AssertionsFailed,!
        } Catch testEx {
            Write "Test error: "_testEx.DisplayString(),!
            Write "Error code: "_testEx.Code,!
        }
        
        Return "Test complete"
    }
    Catch ex {
        Return "ERROR: "_ex.DisplayString()
    }
}

}
