#!/usr/bin/env python3
"""Diagnose LogAssert syntax error in TestRunner Manager"""

import os
import sys
import asyncio
from pathlib import Path
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import our IRIS connection module
from iris_execute_mcp import call_iris_sync

def test_logassert():
    """Test LogAssert interface"""
    print("\n" + "="*80)
    print("Testing LogAssert Interface")
    print("="*80)
    
    try:
        # First create a Manager instance
        print("\n1. Creating Manager instance...")
        create_result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            "Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New() WRITE $ISOBJECT(tManager)",
            "HSCUSTOM"
        )
        result = json.loads(create_result)
        print(f"   Manager created: {result.get('output', 'No output')}")
        
        # Test LogAssert as instance method
        print("\n2. Testing LogAssert as instance method...")
        test_command = """
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set tResult = tManager.LogAssert(1, "Test Pass", "Sample assertion")
        WRITE "Result: "_tResult
        """
        logassert_result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            test_command,
            "HSCUSTOM"
        )
        result = json.loads(logassert_result)
        print(f"   LogAssert result: {result.get('output', result)}")
        
        # Test LogMessage as instance method
        print("\n3. Testing LogMessage as instance method...")
        test_command = """
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set tResult = tManager.LogMessage("Test message")
        WRITE "Result: "_tResult
        """
        logmessage_result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            test_command,
            "HSCUSTOM"
        )
        result = json.loads(logmessage_result)
        print(f"   LogMessage result: {result.get('output', result)}")
        
        # Test Context tracking after assertions
        print("\n4. Testing Context tracking after assertions...")
        test_command = """
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Do tManager.LogAssert(1, "Pass1", "First pass")
        Do tManager.LogAssert(0, "Fail1", "First fail")
        Do tManager.LogAssert(1, "Pass2", "Second pass")
        Do tManager.LogMessage("Test in progress")
        WRITE "Passed: "_tManager.Context.AssertionsPassed_", Failed: "_tManager.Context.AssertionsFailed
        """
        context_result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            test_command,
            "HSCUSTOM"
        )
        result = json.loads(context_result)
        print(f"   Context tracking: {result.get('output', result)}")
        
        # Look at the exact command that was failing (from validation script)
        print("\n5. Testing the exact failing command from validation script...")
        failing_command = "Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New() Set tResult = ##class(ExecuteMCP.TestRunner.Manager).LogAssert(1, \"Test\", \"Description\") WRITE tResult"
        
        print(f"   Command: {failing_command}")
        failing_result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            failing_command,
            "HSCUSTOM"
        )
        result = json.loads(failing_result)
        if 'error' in result:
            print(f"   ✗ Error: {result['error']}")
            print("\n   DIAGNOSIS: The error is trying to call LogAssert as a CLASS method")
            print("              instead of an INSTANCE method. It should be:")
            print("              tManager.LogAssert() not ##class().LogAssert()")
        else:
            print(f"   Result: {result.get('output', result)}")
        
        print("\n" + "="*80)
        print("DIAGNOSIS COMPLETE")
        print("="*80)
        print("\nThe issue is clear: LogAssert and LogMessage are INSTANCE methods,")
        print("not CLASS methods. They must be called on a Manager instance.")
        print("\nThe validation script needs to be fixed to use:")
        print("  tManager.LogAssert() instead of ##class().LogAssert()")
        
    except Exception as e:
        print(f"\n✗ Error during diagnostic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_logassert()
