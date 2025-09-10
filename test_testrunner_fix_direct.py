#!/usr/bin/env python3
"""
Test the TestRunner fix directly without MCP.
This will help identify if the timeout is in the TestRunner or MCP layer.
"""

import json
from iris_execute_mcp import call_iris_sync

def main():
    print("=== Direct TestRunner Fix Test ===\n")
    
    # First compile the TestRunner package to ensure our fix is applied
    print("1. Compiling TestRunner package...")
    result = call_iris_sync(
        "ExecuteMCP.Core.Compile",
        "CompilePackage", 
        ["ExecuteMCP.TestRunner", "bckry", "HSCUSTOM"]
    )
    print(f"   Compilation result: {result}\n")
    
    # Now test the RunTestSpec method directly
    print("2. Testing RunTestSpec directly...")
    try:
        result = call_iris_sync(
            "ExecuteMCP.TestRunner.Manager",
            "RunTestSpec",
            ["ExecuteMCP.Test.SimpleTest:TestCalculations", "HSCUSTOM"]
        )
        
        # Parse the JSON result
        if isinstance(result, str):
            result_obj = json.loads(result)
            print(f"   Result: {json.dumps(result_obj, indent=2)}\n")
        else:
            print(f"   Raw result: {result}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # Test running a full class
    print("3. Testing full class execution...")
    try:
        result = call_iris_sync(
            "ExecuteMCP.TestRunner.Manager",
            "RunTestSpec",
            ["ExecuteMCP.Test.SimpleTest", "HSCUSTOM"]
        )
        
        # Parse the JSON result
        if isinstance(result, str):
            result_obj = json.loads(result)
            print(f"   Result: {json.dumps(result_obj, indent=2)}\n")
        else:
            print(f"   Raw result: {result}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    main()
