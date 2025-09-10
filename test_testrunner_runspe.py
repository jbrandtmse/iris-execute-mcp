#!/usr/bin/env python3
"""
Test the TestRunner using the proper RunTestSpec entry point.
This should handle all Manager-Executor-Context linkage correctly.
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import from iris_execute_mcp.py
from iris_execute_mcp import call_iris_sync

def test_runtestspec():
    """Test RunTestSpec with a simple test class"""
    print("\n1. Testing RunTestSpec with ExecuteMCP.Test.SimpleTest...")
    try:
        # Use the proper entry point that handles all linkage
        cmd = 'SET result = ##class(ExecuteMCP.TestRunner.Manager).RunTestSpec("ExecuteMCP.Test.SimpleTest", "HSCUSTOM") WRITE result'
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand", 
            cmd,
            "HSCUSTOM"
        )
        result_json = json.loads(result)
        output = result_json.get('output', '')
        
        if output and output != 'No output':
            # Parse the test results
            try:
                test_results = json.loads(output)
                print(f"   ✓ RunTestSpec executed successfully")
                print(f"   Test Results:")
                if 'error' in test_results:
                    print(f"     Error: {test_results['error']}")
                    return False
                else:
                    summary = test_results.get('summary', {})
                    print(f"     Total: {summary.get('total', 0)}")
                    print(f"     Passed: {summary.get('passed', 0)}")
                    print(f"     Failed: {summary.get('failed', 0)}")
                    return summary.get('total', 0) > 0
            except json.JSONDecodeError:
                print(f"   Output (not JSON): {output}")
                return False
        else:
            print(f"   No output received")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_simple_executetest():
    """Test ExecuteTestMethod with simpler approach"""
    print("\n2. Testing simpler ExecuteTestMethod approach...")
    try:
        # Use RunTestSpec to execute a single method
        cmd = 'SET result = ##class(ExecuteMCP.TestRunner.Manager).RunTestSpec("ExecuteMCP.Test.SimpleTest:TestBasic", "HSCUSTOM") WRITE result'
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            cmd,
            "HSCUSTOM"
        )
        result_json = json.loads(result)
        output = result_json.get('output', '')
        
        if output and output != 'No output':
            try:
                test_results = json.loads(output)
                print(f"   ✓ Single method execution successful")
                if 'error' not in test_results:
                    summary = test_results.get('summary', {})
                    print(f"     Executed: {summary.get('total', 0)} test(s)")
                    return summary.get('total', 0) == 1
                else:
                    print(f"     Error: {test_results['error']}")
                    return False
            except json.JSONDecodeError:
                print(f"   Output (not JSON): {output}")
                return False
        else:
            print(f"   No output received")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_validate_testrunner():
    """Test ValidateTestRunner method"""
    print("\n3. Testing ValidateTestRunner...")
    try:
        cmd = 'SET result = ##class(ExecuteMCP.TestRunner.Manager).ValidateTestRunner("HSCUSTOM") WRITE result'
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            cmd,
            "HSCUSTOM"
        )
        result_json = json.loads(result)
        output = result_json.get('output', '')
        
        if output and output != 'No output':
            try:
                validation = json.loads(output)
                print(f"   Validation Results:")
                print(f"     Manager Ready: {validation.get('ManagerReady', False)}")
                print(f"     Discovery Working: {validation.get('DiscoveryWorking', False)}")
                print(f"     Test Classes Found: {validation.get('TestClassesFound', 0)}")
                print(f"     Can Execute Tests: {validation.get('CanExecuteTests', False)}")
                return validation.get('Success', False)
            except json.JSONDecodeError:
                print(f"   Output (not JSON): {output}")
                return False
        else:
            print(f"   No output received")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("TestRunner RunTestSpec Testing")
    print("=" * 60)
    
    results = {
        "ValidateTestRunner": test_validate_testrunner(),
        "RunTestSpec Full Class": test_runtestspec(),
        "RunTestSpec Single Method": test_simple_executetest()
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    total_passed = sum(1 for r in results.values() if r)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    
    if total_passed == len(results):
        print("\n✅ TestRunner is working properly using RunTestSpec!")
        print("   The Manager-Executor-Context linkage is handled correctly")
        print("   when using the proper entry points.")
    else:
        print("\n⚠️  Some tests failed. The Executor might need fixes")
        print("   for direct ExecuteTestMethod calls.")

if __name__ == "__main__":
    main()
