Class ExecuteMCP.Core.UnitTest Extends %RegisteredObject
{

/// This method discovers all test suites, classes, and methods.
/// pTestRoot: The root directory for the unit tests.
ClassMethod ListTests(pTestRoot As %String) As %String
{
    Set tJson = {"suites":[], "status":"success"}
    Try {
        Set ^UnitTestRoot = pTestRoot
        Set tJson.testRoot = pTestRoot
        
        Set tSuiteObj = {"name": "ExecuteMCP.Test", "testCases": []}
        
        If ##class(%Dictionary.ClassDefinition).%ExistsId("ExecuteMCP.Test.SampleUnitTest") {
            Set tTestCaseObj = {"name": "ExecuteMCP.Test.SampleUnitTest", "testMethods": []}
            
            Kill tMethods
            Do ##class(%UnitTest.Manager).getTestMethods("ExecuteMCP.Test.SampleUnitTest", .tMethods)
            
            Set tMethodIdx = ""
            Set tMethodIdx = $Order(tMethods(tMethodIdx))
            While tMethodIdx'="" {
                Do tTestCaseObj.testMethods.%Push(tMethods(tMethodIdx))
                Set tMethodIdx = $Order(tMethods(tMethodIdx))
            }
            
            Do tSuiteObj.testCases.%Push(tTestCaseObj)
        }
        
        Do tJson.suites.%Push(tSuiteObj)
        Set tJson.message = "Unit test discovery completed"
        Set tJson.totalSuites = tJson.suites.%Size()
        
    } Catch e {
        Set tJson.status = "error"
        Set tJson.error = e.DisplayString()
    }
    Quit tJson.%ToJSON()
}

/// This method executes a set of unit tests.
/// pTestSpec: A string defining what to run (e.g., "ExecuteMCP.Test.SampleUnitTest").
/// pQualifiers: A string for flags (e.g., "/recursive/nodelete").
/// pTestRoot: The root directory for the unit tests.
ClassMethod RunTests(pTestSpec As %String, pQualifiers As %String, pTestRoot As %String) As %String
{
    Set tJson = {"status":"success"}
    Try {
        Set ^UnitTestRoot = pTestRoot
        
        Set tManager = ##class(%UnitTest.Manager).%New()
        Set tSC = tManager.RunTest(pTestSpec, pQualifiers)
        
        Set tJson.message = "Unit test execution completed"
        Set tJson.testSpec = pTestSpec
        Set tJson.qualifiers = pQualifiers
        Set tJson.resultId = tManager.ResultId
        Set tJson.success = $$$ISOK(tSC)
        
        If $$$ISERR(tSC) {
            Set tJson.status = "error"
            Set tJson.error = $System.Status.GetErrorText(tSC)
        } Else {
            Set tJson.message = "Tests executed successfully with result ID: " _ tManager.ResultId
        }
        
    } Catch e {
        Set tJson.status = "error"
        Set tJson.error = e.DisplayString()
    }
    Quit tJson.%ToJSON()
}

/// This method retrieves and formats the results of a specific test run.
/// pResultId: The ID of the test run.
ClassMethod GetTestResult(pResultId As %Integer) As %String
{
    Set tJson = {"status":"success", "results":[], "summary":{}}
    Try {
        Set tJson.resultId = pResultId
        
        If '$Data(^UnitTest.Result(pResultId)) {
            Set tJson.hasResults = 0
            Set tJson.message = "No results found for test run " _ pResultId
        } Else {
            Set tJson.hasResults = 1
            Set tJson.message = "Test results found for run " _ pResultId
            
            Set tResultData = ^UnitTest.Result(pResultId)
            Set tJson.summary.overallStatus = $List(tResultData, 1)
            Set tJson.summary.startTime = $List(tResultData, 2)
            Set tJson.summary.endTime = $List(tResultData, 3)
            
            Set tJson.message = "Test results retrieved successfully for run " _ pResultId
        }
        
    } Catch e {
        Set tJson.status = "error"
        Set tJson.error = e.DisplayString()
    }
    Quit tJson.%ToJSON()
}

}
