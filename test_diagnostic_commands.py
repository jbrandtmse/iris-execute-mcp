#!/usr/bin/env python3
"""
Test specific commands from the diagnostic script to identify the issue.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from iris_execute_mcp import call_iris_sync

# Load environment variables
load_dotenv()

def test_diagnostic_commands():
    """Test specific commands that are failing in the diagnostic script."""
    print("Testing Diagnostic Commands")
    print("=" * 60)
    
    # Test 1: Command with If statement containing Write
    print("\n1. Testing If statement with Write inside:")
    command = 'If ##class(%Dictionary.CompiledClass).%ExistsId("ExecuteMCP.Test.SampleUnitTest") { Write "ExecuteMCP.Test.SampleUnitTest: EXISTS (Compiled)" } ElseIf ##class(%Dictionary.ClassDefinition).%ExistsId("ExecuteMCP.Test.SampleUnitTest") { Write "ExecuteMCP.Test.SampleUnitTest: EXISTS (Not compiled)" } Else { Write "ExecuteMCP.Test.SampleUnitTest: NOT FOUND" }'
    
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        [command, "HSCUSTOM"]
    )
    print(f"Result: {result}")
    
    # Test 2: Simpler If statement
    print("\n2. Testing simpler If statement:")
    command = 'Set x=1 If x=1 { Write "x equals 1" } Else { Write "x not 1" }'
    
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        [command, "HSCUSTOM"]
    )
    print(f"Result: {result}")
    
    # Test 3: Command with While loop
    print("\n3. Testing While loop with counter:")
    command = 'Set tCount=0 Set tClass=$ORDER(^oddDEF("")) While tClass\'="" { If (tClass["Test") { Set tCount=tCount+1 } Set tClass=$ORDER(^oddDEF(tClass)) } Write "Total Test classes found: ",tCount'
    
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        [command, "HSCUSTOM"]
    )
    print(f"Result: {result}")
    
    # Test 4: Simple Write at the end
    print("\n4. Testing command ending with Write:")
    command = 'Set x=5 Set y=10 Set z=x+y Write "Result: ",z'
    
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        [command, "HSCUSTOM"]
    )
    print(f"Result: {result}")
    
    print("\n" + "=" * 60)
    print("Test Complete")

if __name__ == "__main__":
    test_diagnostic_commands()
