/// ExecuteMCP.TestRunner.Context - Tracks execution state and test results
/// Stores assertions, messages, and statistics for the current test run
Class ExecuteMCP.TestRunner.Context Extends %RegisteredObject
{

/// Current test class being executed
Property CurrentClass As %String;

/// Current test method being executed
Property CurrentMethod As %String;

/// Overall test run start time
Property StartTime As %TimeStamp;

/// Overall test run end time
Property EndTime As %TimeStamp;

/// Current test method start time
Property MethodStartTime As %TimeStamp;

/// Store assertion results for current test
Property CurrentAssertions As %DynamicArray [ Private ];

/// Store all test results
Property TestResults As %DynamicObject [ Private ];

/// Store test messages
Property Messages As %DynamicArray [ Private ];

/// Public accessor for assertions (for compatibility with validation scripts)
Property Assertions As %DynamicArray [ Calculated ];

/// Getter for Assertions property
Method AssertionsGet() As %DynamicArray
{
    Return ..CurrentAssertions
}

/// Check if this is the first test being executed
Method IsFirstTest() As %Boolean
{
    Try {
        Return (..TestResults.summary.total = 0)
    }
    Catch {
        Return 1  ; If error, assume it's the first test
    }
}

/// Get the current test count
Method GetTestCount() As %Integer
{
    Try {
        Return ..TestResults.summary.total
    }
    Catch {
        Return 0
    }
}

/// Initialize the context for a new test run
Method %OnNew() As %Status
{
    Set tSC = $$$OK
    Try {
        Set ..TestResults = {}
        Set ..TestResults.classes = {}
        Set ..TestResults.summary = {}
        Set ..TestResults.summary.passed = 0
        Set ..TestResults.summary.failed = 0
        Set ..TestResults.summary.errors = 0
        Set ..TestResults.summary.total = 0
        Set ..Messages = []
        Set ..CurrentAssertions = []
    }
    Catch ex {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}

/// Start a new test class
Method StartClass(pClassName As %String) As %Status
{
    Set tSC = $$$OK
    Try {
        Set ..CurrentClass = pClassName
        Set ..CurrentMethod = ""
        
        ; Initialize class results
        Set $PROPERTY(..TestResults.classes, pClassName) = {}
        Set $PROPERTY(..TestResults.classes, pClassName).methods = {}
        Set $PROPERTY(..TestResults.classes, pClassName).passed = 0
        Set $PROPERTY(..TestResults.classes, pClassName).failed = 0
    }
    Catch ex {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}

/// Start a new test method
Method StartMethod(pMethodName As %String) As %Status
{
    Set tSC = $$$OK
    Try {
        Set ..CurrentMethod = pMethodName
        Set ..CurrentAssertions = []
        Set ..MethodStartTime = $ZTIMESTAMP
    }
    Catch ex {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}

/// Add assertion result
Method AddAssertion(pSuccess As %Boolean, pAction As %String, pDescription As %String = "") As %Status
{
    Set tSC = $$$OK
    Try {
        Set tAssertion = {}
        Set tAssertion.success = pSuccess
        Set tAssertion.action = pAction
        Set tAssertion.description = pDescription
        Set tAssertion.timestamp = $ZTIMESTAMP
        
        Do ..CurrentAssertions.%Push(tAssertion)
    }
    Catch ex {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}

/// Add test message
Method AddMessage(pMessage As %String) As %Status
{
    Set tSC = $$$OK
    Try {
        Set tMessage = {}
        Set tMessage.message = pMessage
        Set tMessage.class = ..CurrentClass
        Set tMessage.method = ..CurrentMethod
        Set tMessage.timestamp = $ZTIMESTAMP
        
        Do ..Messages.%Push(tMessage)
    }
    Catch ex {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}

/// End current test method and store results
Method EndMethod(pStatus As %Status = {$$$OK}) As %Status
{
    Set tSC = $$$OK
    Try {
        If (..CurrentClass = "") || (..CurrentMethod = "") {
            Quit
        }
        
        ; Calculate duration
        Set tDuration = $SYSTEM.SQL.DATEDIFF("ms", ..MethodStartTime, $ZTIMESTAMP)
        
        ; Determine if test passed
        Set tPassed = 1
        Set tAssertionCount = ..CurrentAssertions.%Size()
        
        For i = 0:1:(tAssertionCount - 1) {
            Set tAssertion = ..CurrentAssertions.%Get(i)
            If 'tAssertion.success {
                Set tPassed = 0
                Quit
            }
        }
        
        ; If status indicates error, mark as failed
        If $$$ISERR(pStatus) {
            Set tPassed = 0
        }
        
        ; Store method results
        Set tMethodResult = {}
        Set tMethodResult.passed = tPassed
        Set tMethodResult.duration = tDuration
        Set tMethodResult.assertions = ..CurrentAssertions.%ToJSON()
        Set tMethodResult.assertionCount = tAssertionCount
        
        If $$$ISERR(pStatus) {
            Set tMethodResult.error = $SYSTEM.Status.GetErrorText(pStatus)
        }
        
        Set $PROPERTY($PROPERTY(..TestResults.classes, ..CurrentClass).methods, ..CurrentMethod) = tMethodResult
        
        ; Update counts
        If tPassed {
            Set $PROPERTY(..TestResults.classes, ..CurrentClass).passed = $PROPERTY(..TestResults.classes, ..CurrentClass).passed + 1
            Set ..TestResults.summary.passed = ..TestResults.summary.passed + 1
        } Else {
            Set $PROPERTY(..TestResults.classes, ..CurrentClass).failed = $PROPERTY(..TestResults.classes, ..CurrentClass).failed + 1
            Set ..TestResults.summary.failed = ..TestResults.summary.failed + 1
        }
        
        Set ..TestResults.summary.total = ..TestResults.summary.total + 1
    }
    Catch ex {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}

/// Get results as JSON string
Method GetResults() As %String
{
    Try {
        ; Add messages to results
        Set ..TestResults.messages = ..Messages
        
        ; Calculate overall duration if we have start/end times
        If (..StartTime '= "") && (..EndTime '= "") {
            Set ..TestResults.summary.duration = $SYSTEM.SQL.DATEDIFF("ms", ..StartTime, ..EndTime)
        }
        
        ; Add timestamp
        Set ..TestResults.timestamp = $ZDATETIME($ZTIMESTAMP, 3, 1, 3)
        
        Return ..TestResults.%ToJSON()
    }
    Catch ex {
        Return "{""error"":"""_$ZCONVERT($SYSTEM.Status.GetErrorText(ex.AsStatus()), "O", "JS")_"""}"
    }
}

/// End current test class
Method EndClass() As %Status
{
    Set tSC = $$$OK
    Try {
        ; Clear current class context
        Set ..CurrentClass = ""
        Set ..CurrentMethod = ""
    }
    Catch ex {
        Set tSC = ex.AsStatus()
    }
    Quit tSC
}

/// Get results as dynamic object
Method GetResultsObject() As %DynamicObject
{
    Return ..TestResults
}

}
