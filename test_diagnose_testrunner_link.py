#!/usr/bin/env python3
"""
Diagnose TestRunner Manager-Executor-Context linkage issue.
Testing why ExecuteTestMethod throws "PRIVATE METHOD" error at line 28.
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import from iris_execute_mcp.py
from iris_execute_mcp import call_iris_sync

def test_manager_context_init():
    """Test if Manager's Context initializes properly"""
    print("\n1. Testing Manager Context initialization...")
    try:
        # Create Manager instance and check Context
        cmd = 'SET tManager = ##class(ExecuteMCP.TestRunner.Manager).%New() WRITE "Manager created: ",$ISOBJECT(tManager),"|Context: ",$ISOBJECT(tManager.Context)'
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand", 
            cmd,
            "HSCUSTOM"
        )
        result_json = json.loads(result)
        print(f"   Result: {result_json.get('output', 'No output')}")
        return "Manager created: 1|Context: 1" in str(result_json.get('output', ''))
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_executor_creation():
    """Test Executor creation and Manager linkage"""
    print("\n2. Testing Executor creation and Manager linkage...")
    try:
        # Create Manager, then Executor, link them
        cmd = 'SET tManager = ##class(ExecuteMCP.TestRunner.Manager).%New() SET tExecutor = ##class(ExecuteMCP.TestRunner.Executor).%New() SET tExecutor.Manager = tManager WRITE "Executor created: ",$ISOBJECT(tExecutor),"|Manager linked: ",$ISOBJECT(tExecutor.Manager)'
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            cmd,
            "HSCUSTOM"
        )
        result_json = json.loads(result)
        print(f"   Result: {result_json.get('output', 'No output')}")
        return "Executor created: 1|Manager linked: 1" in str(result_json.get('output', ''))
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_context_access_through_chain():
    """Test accessing Context through Executor->Manager chain"""
    print("\n3. Testing Context access through Executor chain...")
    try:
        # Create full chain and test Context access
        cmd = 'SET tManager = ##class(ExecuteMCP.TestRunner.Manager).%New() SET tExecutor = ##class(ExecuteMCP.TestRunner.Executor).%New() SET tExecutor.Manager = tManager WRITE "Context accessible: ",$ISOBJECT(tExecutor.Manager.Context)'
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            cmd,
            "HSCUSTOM"
        )
        result_json = json.loads(result)
        print(f"   Result: {result_json.get('output', 'No output')}")
        return "Context accessible: 1" in str(result_json.get('output', ''))
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_startmethod_direct():
    """Test calling StartMethod directly on Context"""
    print("\n4. Testing StartMethod call directly...")
    try:
        # Create Context and call StartMethod directly
        cmd = 'SET tContext = ##class(ExecuteMCP.TestRunner.Context).%New() DO tContext.StartMethod("TestMethod") WRITE "StartMethod called successfully"'
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            cmd,
            "HSCUSTOM"
        )
        result_json = json.loads(result)
        print(f"   Result: {result_json.get('output', 'No output')}")
        if result_json.get('status') == 'success':
            return True
        else:
            print(f"   Error details: {result_json.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_executor_executetest():
    """Test ExecuteTestMethod with proper linkage"""
    print("\n5. Testing ExecuteTestMethod with full linkage...")
    try:
        # Create Manager, Executor, link them, then call ExecuteTestMethod
        # Using simpler approach - let Manager create the Executor
        cmd = 'SET tManager = ##class(ExecuteMCP.TestRunner.Manager).%New() SET tExecutor = ##class(ExecuteMCP.TestRunner.Executor).%New() SET tExecutor.Manager = tManager SET tSC = tExecutor.ExecuteTestMethod("ExecuteMCP.Test.SimpleTest", "TestBasic") WRITE "Status: ",$SYSTEM.Status.GetErrorText(tSC)'
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            cmd,
            "HSCUSTOM"
        )
        result_json = json.loads(result)
        print(f"   Result: {result_json.get('output', 'No output')}")
        if result_json.get('status') == 'error':
            print(f"   Error: {result_json.get('error', 'Unknown error')}")
        return result_json.get('status') == 'success'
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_context_methods():
    """Test Context methods exist and are callable"""
    print("\n6. Testing Context methods existence...")
    try:
        # Check if Context methods exist
        cmd = 'SET exists = ##class(%Dictionary.CompiledMethod).%ExistsId("ExecuteMCP.TestRunner.Context||StartMethod") WRITE "StartMethod exists: ",exists'
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            cmd,
            "HSCUSTOM"
        )
        result_json = json.loads(result)
        print(f"   StartMethod: {result_json.get('output', 'No output')}")
        
        # Check EndMethod
        cmd = 'SET exists = ##class(%Dictionary.CompiledMethod).%ExistsId("ExecuteMCP.TestRunner.Context||EndMethod") WRITE "EndMethod exists: ",exists'
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            cmd,
            "HSCUSTOM"
        )
        result_json = json.loads(result)
        print(f"   EndMethod: {result_json.get('output', 'No output')}")
        
        return True
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print("=" * 60)
    print("TestRunner Manager-Executor-Context Linkage Diagnostics")
    print("=" * 60)
    
    results = {
        "Manager Context Init": test_manager_context_init(),
        "Executor Creation": test_executor_creation(),
        "Context Chain Access": test_context_access_through_chain(),
        "StartMethod Direct": test_startmethod_direct(),
        "ExecuteTestMethod": test_executor_executetest(),
        "Context Methods Exist": test_context_methods()
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    total_passed = sum(1 for r in results.values() if r)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    
    if not results["ExecuteTestMethod"]:
        print("\n⚠️  ExecuteTestMethod is failing - this is the core issue to fix")
        print("   The 'PRIVATE METHOD' error suggests the Context methods are not")
        print("   accessible through the Manager->Context chain in Executor")

if __name__ == "__main__":
    main()
