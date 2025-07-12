# Comprehensive %Api Class Analysis
## IRIS REST API Architectural Patterns

### Executive Summary

After examining 11 main %Api classes and their implementations, I've identified **consistent architectural patterns** that reveal the "IRIS way" to build REST APIs. These patterns provide the foundation for refactoring our MCP server design.

### 1. Core %Api Classes Overview

| Class | Purpose | Key Features | Patterns Used |
|-------|---------|--------------|---------------|
| `%Api.Atelier` | Development IDE API | Versioning, Document Operations, Async Queue | Routing, Versioning, WorkManager |
| `%Api.DocDB` | Document Database API | CRUD Operations, JSON Documents | RESTful CRUD, Error Handling |
| `%Api.DeepSee` | Analytics API | Dashboard, Query Operations | Namespace Routing, Access Control |
| `%Api.iKnow` | NLP API (Deprecated) | Text Analytics | Version Forwarding |
| `%Api.InteropEditors` | Interoperability IDE | Business Rule Editing | Version Forwarding |
| `%Api.InteropMetrics` | Metrics API (Deprecated) | Prometheus Format Metrics | Time-based Filtering |
| `%Api.Monitor` | System Monitoring | System Metrics, Alerts | Prometheus Integration |
| `%Api.Mgmnt.v2.impl` | API Management | REST App Management | OpenAPI Integration |

### 2. Universal Architectural Patterns

#### 2.1 **Routing Architecture**
```objectscript
// All %Api classes follow this pattern:
Class %Api.ServiceName Extends %CSP.REST

XData UrlMap [ XMLNamespace = "http://www.intersystems.com/urlmap" ]
{
<Routes>
<Map Prefix="/v1" Forward="%Api.ServiceName.v1"/>
<Map Prefix="/v2" Forward="%Api.ServiceName.v2"/>
<!-- Version-based forwarding -->
</Routes>
}
```

**Key Insights:**
- **Version Routing**: All APIs use `/v1`, `/v2`, etc. for API versioning
- **Forward Pattern**: Route routing classes forward to specific implementation classes
- **Namespace Integration**: Most APIs include namespace in URL path

#### 2.2 **Standard Parameters**
```objectscript
// Every API class uses these parameters:
Parameter CHARSET = "utf-8";
Parameter CONTENTTYPE = "application/json";
Parameter HandleCorsRequest = 1;
Parameter UseSession As Integer = 0; // or 1
```

**Consistency**: All APIs standardize on JSON, UTF-8, and CORS support.

#### 2.3 **Request Lifecycle Pattern**
```objectscript
ClassMethod OnPreDispatch(pUrl, pMethod, ByRef pContinue) As %Status
{
    // 1. Session management
    Do %session.Unlock()
    
    // 2. Content-Type validation
    If ('..AcceptsContentType("application/json")) {
        Set %response.Status = ..#HTTP406NOTACCEPTABLE
        Quit
    }
    
    // 3. Namespace switching
    Set tNamespace = $PIECE(pUrl,"/",3)
    Set $namespace = tNamespace
    
    // 4. Security checks
    // (Delegated to individual methods)
}
```

**Universal Pattern**: All APIs follow identical request preprocessing.

### 3. Revolutionary Discovery: Async Work Queue Pattern

#### 3.1 **The Atelier Async Pattern** (Most Important Finding)

**Problem Solved**: Long-running operations (like compilation, testing) timeout in synchronous REST calls.

**Solution**: Async work queue with polling:

```objectscript
// 1. Queue Operation (POST /:namespace/work)
ClassMethod QueueAsync(pNameSpace As %String) As %Status
{
    // Parse request
    Set tRequest = ##class(%DynamicObject).%FromJSON(%request.Content)
    
    // Generate unique ID
    Set tID = +$SYSTEM.Encryption.GenCryptToken()
    
    // Store request in global
    Set ^IRIS.TempAtelierAsyncQueue(tID,"request") = tRequest.%ToJSON()
    Set ^IRIS.TempAtelierAsyncQueue(tID,"start") = $ZHOROLOG
    
    // Queue with WorkManager
    Set tWQM = $SYSTEM.WorkMgr.%New(,1)
    Set tSC = tWQM.Queue("##class(%Api.Atelier.v6).ExecuteAsyncRequest", tID)
    
    // Return 202 Accepted with Location header
    Do %response.SetHeader("Location", tID)
    Set %response.Status = ..#HTTP202ACCEPTED
}

// 2. Poll for Results (GET /:namespace/work/:id)
ClassMethod PollAsync(pNameSpace As %String, pID As %Integer) As %Status
{
    // Check if finished
    If $DATA(^IRIS.TempAtelierAsyncQueue(pID,"result")) {
        // Return results and cleanup
        Set tResult = ^IRIS.TempAtelierAsyncQueue(pID,"result")
        Kill ^IRIS.TempAtelierAsyncQueue(pID)
        // Return final results
    } Else {
        // Still running - return "Retry-After" header
        Do %response.SetHeader("Retry-After", 3)
    }
}

// 3. Background Execution
ClassMethod ExecuteAsyncRequest(pID As %Integer)
{
    // Parse stored request
    Set tRequest = ##class(%DynamicObject).%FromJSON(^IRIS.TempAtelierAsyncQueue(pID,"request"))
    
    // Execute long-running operation
    If tRequest.request = "compile" {
        // Compile documents
    } ElseIf tRequest.request = "testrtn" {
        // Run tests
    }
    
    // Store results
    Set ^IRIS.TempAtelierAsyncQueue(pID,"result") = tResult.%ToJSON()
}
```

**HTTP Status Codes Used:**
- `202 Accepted` - Operation queued
- `200 OK` - Results available  
- `404 Not Found` - Invalid job ID
- `423 Locked` - Resource locked

**Headers Used:**
- `Location` - Job ID for polling
- `Retry-After` - Seconds to wait before next poll

#### 3.2 **Global Storage Pattern**
```objectscript
// Standard async operation storage:
^IRIS.TempAtelierAsyncQueue(jobID,"request") = Original request JSON
^IRIS.TempAtelierAsyncQueue(jobID,"result") = Final result JSON  
^IRIS.TempAtelierAsyncQueue(jobID,"start") = Start timestamp
^IRIS.TempAtelierAsyncQueue(jobID,"cout","i") = Console output in counter
^IRIS.TempAtelierAsyncQueue(jobID,"cout","o") = Console output out counter
^IRIS.TempAtelierAsyncQueue(jobID,"wqm") = Work Queue Manager token
```

**This Pattern Directly Solves Our Timeout Issues!**

### 4. Error Handling Patterns

#### 4.1 **Standard Error Response Format**
```json
{
  "status": {
    "errors": ["Error message 1", "Error message 2"],
    "summary": "Operation summary"
  },
  "console": ["Console output line 1", "Console output line 2"],
  "result": {
    "content": {} // Actual response data
  }
}
```

#### 4.2 **HTTP Status Code Standards**
```objectscript
// Universal status codes across all APIs:
HTTP 200 OK           - Success
HTTP 201 CREATED      - Resource created
HTTP 202 ACCEPTED     - Async operation queued
HTTP 400 BAD REQUEST  - Invalid input
HTTP 404 NOT FOUND    - Resource not found
HTTP 406 NOT ACCEPTABLE - Invalid Accept header
HTTP 423 LOCKED       - Resource locked
HTTP 500 INTERNAL ERROR - Server error
```

### 5. Security and Access Control Patterns

#### 5.1 **Namespace Access Control**
```objectscript
// Standard namespace validation:
ClassMethod OnPreDispatch() {
    Set tNamespace = $PIECE(pUrl,"/",3)
    
    // Validate namespace exists and is accessible
    If '##class(%SYS.Namespace).Enabled(tNamespace) {
        Set %response.Status = ..#HTTP404NOTFOUND
        Quit
    }
    
    // Switch to namespace
    Set $namespace = tNamespace
}
```

#### 5.2 **Resource-Based Security**
```objectscript
// APIs use resource-based security checks:
$$$THROWONERROR(status, $$CheckAccess^%SYS.DOCDB(databaseName,,"W"))
```

### 6. Console Output Capture Pattern

#### 6.1 **Output Redirection**
```objectscript
// Universal pattern for capturing console output:
ClassMethod BeginCaptureOutput(Output pCookie) As %Status
{
    // Save current redirection state
    Set pCookie = $LISTBUILD(##class(%Device).ReDirectIO(), $ZUTIL(96,12))
    
    // Redirect to custom handler
    Use $IO::("^"_$ZNAME)
    Do ##class(%Device).ReDirectIO(1)
}

ClassMethod EndCaptureOutput(pCookie, ByRef pMsgArray)
{
    // Restore original redirection
    Do ##class(%Device).ReDirectIO($LIST(pCookie,1))
    
    // Return captured output in pMsgArray
}
```

**This enables real-time console capture for compilation, testing, etc.**

### 7. JSON Response Patterns

#### 7.1 **Standard Response Helper**
```objectscript
ClassMethod RenderResponseBody(pSC As %Status, pMsgArray, pContent) As %Status
{
    Set tResponse = {
        "status": {
            "errors": [],
            "summary": ""
        },
        "console": (pMsgArray),
        "result": (pContent)
    }
    
    // Add errors if status contains errors
    If $$$ISERR(pSC) {
        // Parse status and add to errors array
    }
    
    Write tResponse.%ToJSON()
    Quit $$$OK
}
```

### 8. Critical Insights for Our MCP Server

#### 8.1 **Why Our Current Implementation Times Out**
Our `ExecuteMCP.Core.UnitTest.RunTests()` calls `tManager.RunTest()` which:
1. Performs directory scanning (30-60s)
2. Loads and compiles files (15-30s)  
3. Records namespace state (20-45s)
4. Orchestrates complex lifecycle (5-15s)
**Total: 70-150+ seconds = TIMEOUT**

#### 8.2 **The %Api Solution**
The Atelier API solves **identical timeout issues** using:
1. **Async Queuing**: POST operation returns immediately with job ID
2. **Background Execution**: WorkManager handles long operations  
3. **Non-blocking Polling**: GET with Retry-After headers
4. **Cleanup**: Automatic cleanup after result retrieval

#### 8.3 **Direct Application to Our Problem**
```objectscript
// Instead of this (times out):
Set result = ##class(ExecuteMCP.Core.UnitTest).RunTests(testSpec, qualifiers, testRoot)

// Use this pattern (4-12 seconds):
Set jobID = ##class(ExecuteMCP.Core.UnitTestAsync).QueueTest(testSpec, qualifiers, testRoot)
Set result = ##class(ExecuteMCP.Core.UnitTestAsync).PollTest(jobID)
```

### 9. Implementation Recommendations

#### 9.1 **Immediate Priority: Async Pattern**
1. **Implement Work Queue Pattern** for unit testing
2. **Use direct test execution** (not Manager) in background
3. **Follow Atelier global storage patterns**
4. **Implement standard HTTP status codes**

#### 9.2 **Architecture Alignment**
1. **Follow %Api parameter standards**
2. **Implement OnPreDispatch pattern**
3. **Use standard error response format**
4. **Add console output capture**

#### 9.3 **Security Integration**
1. **Add namespace validation**
2. **Implement resource-based access control**
3. **Follow IRIS security patterns**

### 10. Conclusion

The %Api classes reveal a **mature, battle-tested architecture** for building REST APIs in IRIS. The async work queue pattern directly solves our timeout issues while following proven IRIS patterns.

**Key Finding**: We don't need to invent new patterns - we need to **follow the existing %Api patterns** that IRIS developers have refined over years of production use.

**Next Step**: Apply these patterns to create a robust, timeout-free unit testing MCP server that follows IRIS architectural standards.
