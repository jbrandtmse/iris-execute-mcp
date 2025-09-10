#!/usr/bin/env python3
"""
Debug the parameter passing issue in TestRunner.
The spec is being received as an object reference instead of a string.
"""

import json
from iris_execute_mcp import call_iris_sync

def main():
    print("=== TestRunner Parameter Debug ===\n")
    
    # Test with execute_command to see if it's a call_iris_sync issue
    print("1. Testing with execute_command...")
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        ['SET result = ##class(ExecuteMCP.TestRunner.Manager).RunTestSpec("ExecuteMCP.Test.SimpleTest:TestCalculations", "HSCUSTOM") WRITE result', "HSCUSTOM"]
    )
    print(f"   Result: {result}\n")
    
    # Test using a wrapper method
    print("2. Creating a wrapper method...")
    wrapper_code = '''Class ExecuteMCP.TestRunner.DebugWrapper Extends %RegisteredObject
{

ClassMethod TestWithString() As %String
{
    // Hardcode the spec to avoid parameter issues
    Set spec = "ExecuteMCP.Test.SimpleTest:TestCalculations"
    Set namespace = "HSCUSTOM"
    Return ##class(ExecuteMCP.TestRunner.Manager).RunTestSpec(spec, namespace)
}

ClassMethod TestParamType(pParam As %String) As %String
{
    // Test what we're receiving
    Set result = {}
    Set result.paramValue = pParam
    Set result.paramType = $CLASSNAME(pParam)
    Set result.isObject = $ISOBJECT(pParam)
    Set result.isString = ($DATA(pParam) && ('$ISOBJECT(pParam)))
    
    If $ISOBJECT(pParam) {
        Try {
            Set result.objectClass = pParam.%ClassName(1)
        } Catch {
            Set result.objectClass = "Unknown"
        }
    }
    
    Return result.%ToJSON()
}

}'''
    
    # Write the wrapper class
    with open("src/ExecuteMCP/TestRunner/DebugWrapper.cls", "w") as f:
        f.write(wrapper_code)
    
    print("   Wrapper class created\n")
    
    import time
    time.sleep(2)  # Give VS Code time to sync
    
    # Test the parameter type
    print("3. Testing parameter type...")
    try:
        result = call_iris_sync(
            "ExecuteMCP.TestRunner.DebugWrapper",
            "TestParamType",
            ["ExecuteMCP.Test.SimpleTest:TestCalculations"]
        )
        print(f"   Parameter debug: {result}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # Test with hardcoded values
    print("4. Testing with hardcoded values...")
    try:
        result = call_iris_sync(
            "ExecuteMCP.TestRunner.DebugWrapper",
            "TestWithString",
            []
        )
        
        # Parse the JSON result
        if isinstance(result, str):
            result_obj = json.loads(result)
            print(f"   Result: {json.dumps(result_obj, indent=2)}\n")
        else:
            print(f"   Raw result: {result}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    print("=== Debug Complete ===")
    print("\nThe issue appears to be that parameters are being passed as")
    print("object references instead of strings through the Native API.")

if __name__ == "__main__":
    main()
