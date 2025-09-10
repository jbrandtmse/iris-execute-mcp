#!/usr/bin/env python3
"""Debug Manager property injection for assertion macro support"""

import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the functions directly
from iris_execute_mcp import call_iris_sync

def main():
    print("=" * 80)
    print("Manager Property Injection Debug")
    print("=" * 80)
    
    # Test 1: Direct test instance creation and Manager injection
    print("\n1. Testing direct instance creation with Manager injection...")
    try:
        # Create a test instance
        result = call_iris_sync(
            "ExecuteMCP.Test.SimpleTest",
            "%New",
            ""
        )
        result_data = json.loads(result)
        print(f"   Instance creation: {result_data.get('status', 'unknown')}")
        if result_data.get('status') == 'error':
            print(f"   Error: {result_data.get('error', 'Unknown error')}")
        
        # Create a Manager instance
        result = call_iris_sync(
            "ExecuteMCP.TestRunner.Manager",
            "%New"
        )
        result_data = json.loads(result)
        print(f"   Manager creation: {result_data.get('status', 'unknown')}")
        if result_data.get('status') == 'error':
            print(f"   Error: {result_data.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Execute a simple test with detailed debugging
    print("\n2. Creating debug test execution method...")
    debug_code = '''Class ExecuteMCP.TestRunner.Debug
{

ClassMethod TestManagerInjection() As %String
{
    Set result = {}
    Set result.steps = []
    
    Try {
        ; Step 1: Create Manager instance
        Do result.steps.%Push("Creating Manager instance")
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Do result.steps.%Push("Manager created: "_$ISOBJECT(tManager))
        
        ; Step 2: Create test instance
        Do result.steps.%Push("Creating test instance")
        Set tTestInstance = ##class(ExecuteMCP.Test.SimpleTest).%New("")
        Do result.steps.%Push("Test instance created: "_$ISOBJECT(tTestInstance))
        
        ; Step 3: Inject Manager
        Do result.steps.%Push("Injecting Manager property")
        Set tTestInstance.Manager = tManager
        Do result.steps.%Push("Manager injected: "_$ISOBJECT(tTestInstance.Manager))
        
        ; Step 4: Try to call a test method with assertion
        Do result.steps.%Push("Calling test method")
        Set tSC = tTestInstance.TestAlwaysPass()
        Do result.steps.%Push("Test method called: "_$$$ISOK(tSC))
        
        Set result.success = 1
    }
    Catch ex {
        Set result.error = ex.DisplayString()
        Set result.success = 0
    }
    
    Return result.%ToJSON()
}

ClassMethod TestAssertionMacro() As %String
{
    Set result = {}
    
    Try {
        ; Create Manager and Context
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set tManager.Context = ##class(ExecuteMCP.TestRunner.Context).%New()
        
        ; Create test instance and inject Manager
        Set tTestInstance = ##class(ExecuteMCP.Test.SimpleTest).%New("")
        Set tTestInstance.Manager = tManager
        
        ; Test direct assertion
        Do tTestInstance.AssertEquals(1, 1, "Test direct assertion")
        
        Set result.success = 1
        Set result.message = "Assertion executed successfully"
    }
    Catch ex {
        Set result.error = ex.DisplayString()
        Set result.location = ex.Location
        Set result.code = ex.Code
        Set result.success = 0
    }
    
    Return result.%ToJSON()
}

ClassMethod TestManagerLogAssert() As %String
{
    Set result = {}
    
    Try {
        ; Create Manager with Context
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set tContext = ##class(ExecuteMCP.TestRunner.Context).%New()
        Set tManager.Context = tContext
        
        ; Test LogAssert directly
        Do result.steps.%Push("Testing LogAssert method")
        Do tManager.LogAssert(1, "test", "Testing LogAssert")
        Do result.steps.%Push("LogAssert called successfully")
        
        ; Get context results
        Set tResults = tContext.GetResults()
        Set result.contextResults = tResults
        
        Set result.success = 1
    }
    Catch ex {
        Set result.error = ex.DisplayString()
        Set result.success = 0
    }
    
    Return result.%ToJSON()
}

}'''
    
    # Write debug class
    with open("src/ExecuteMCP/TestRunner/Debug.cls", "w") as f:
        f.write(debug_code)
    print("   Debug class created")
    
    # Test 3: Run debug methods
    print("\n3. Testing Manager injection...")
    try:
        result = call_iris_sync(
            "ExecuteMCP.TestRunner.Debug",
            "TestManagerInjection"
        )
        result_data = json.loads(result)
        
        if result_data.get("status") == "success":
            debug_result = json.loads(result_data.get("output", "{}"))
            print(f"   Success: {debug_result.get('success', False)}")
            if "steps" in debug_result:
                for step in debug_result["steps"]:
                    print(f"     - {step}")
            if "error" in debug_result:
                print(f"   Error: {debug_result['error']}")
        else:
            print(f"   Execution failed: {result_data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. Testing assertion macro directly...")
    try:
        result = call_iris_sync(
            "ExecuteMCP.TestRunner.Debug",
            "TestAssertionMacro"
        )
        result_data = json.loads(result)
        
        if result_data.get("status") == "success":
            debug_result = json.loads(result_data.get("output", "{}"))
            print(f"   Success: {debug_result.get('success', False)}")
            print(f"   Message: {debug_result.get('message', '')}")
            if "error" in debug_result:
                print(f"   Error: {debug_result['error']}")
                print(f"   Location: {debug_result.get('location', 'N/A')}")
                print(f"   Code: {debug_result.get('code', 'N/A')}")
        else:
            print(f"   Execution failed: {result_data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Check LogAssert implementation
    print("\n5. Testing Manager LogAssert method...")
    try:
        result = call_iris_sync(
            "ExecuteMCP.TestRunner.Debug",
            "TestManagerLogAssert"
        )
        result_data = json.loads(result)
        
        if result_data.get("status") == "success":
            debug_result = json.loads(result_data.get("output", "{}"))
            print(f"   Success: {debug_result.get('success', False)}")
            if "error" in debug_result:
                print(f"   Error: {debug_result['error']}")
            if "contextResults" in debug_result:
                print(f"   Context captured results successfully")
        else:
            print(f"   Execution failed: {result_data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 6: Check Manager class structure
    print("\n6. Checking Manager class for LogAssert method...")
    check_code = '''
    Set tHasMethod = ##class(%Dictionary.CompiledMethod).%ExistsId("ExecuteMCP.TestRunner.Manager||LogAssert")
    Write "LogAssert exists: ", tHasMethod, !
    
    Set tHasMethod2 = ##class(%Dictionary.CompiledMethod).%ExistsId("ExecuteMCP.TestRunner.Manager||LogMessage")
    Write "LogMessage exists: ", tHasMethod2, !
    '''
    
    try:
        result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", check_code, "HSCUSTOM")
        result_data = json.loads(result)
        print(f"   {result_data.get('output', 'No output')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
