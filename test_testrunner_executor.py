#!/usr/bin/env python3
"""Test the complete TestRunner with Executor implementation."""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iris_execute_mcp import call_iris_sync

def execute_command(command: str, namespace: str = "HSCUSTOM"):
    """Execute an ObjectScript command via MCP."""
    result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", command, namespace)
    return json.loads(result)

def main():
    """Test the TestRunner Executor functionality."""
    
    print("=" * 80)
    print("TestRunner Executor Test")
    print("=" * 80)
    
    # Test 1: Run a single test class using new RunTestSpec
    print("\n1. Testing RunTestSpec with single class...")
    try:
        command = 'SET tResult = ##class(ExecuteMCP.TestRunner.Manager).RunTestSpec("ExecuteMCP.Test.SimpleTest") WRITE tResult'
        result = execute_command(command)
        
        if result["status"] == "success" and result["output"]:
            try:
                test_results = json.loads(result["output"])
                print("   ✓ Test execution completed")
                
                # Check for summary
                if "summary" in test_results:
                    summary = test_results["summary"]
                    print(f"   Tests Run: {summary.get('total', 0)}")
                    print(f"   Passed: {summary.get('passed', 0)}")
                    print(f"   Failed: {summary.get('failed', 0)}")
                    
                    # Show class results
                    if "classes" in test_results:
                        for class_name, class_data in test_results["classes"].items():
                            print(f"\n   Class: {class_name}")
                            if "methods" in class_data:
                                for method_name, method_data in class_data["methods"].items():
                                    status = "✓" if method_data.get("passed") else "✗"
                                    print(f"      {status} {method_name}")
                else:
                    print(f"   Results: {json.dumps(test_results, indent=2)}")
                    
            except json.JSONDecodeError:
                print(f"   Raw output: {result['output']}")
        else:
            print(f"   ✗ Failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: Run a specific test method
    print("\n2. Testing RunTestSpec with specific method...")
    try:
        command = 'SET tResult = ##class(ExecuteMCP.TestRunner.Manager).RunTestSpec("ExecuteMCP.Test.SimpleTest:TestPass") WRITE tResult'
        result = execute_command(command)
        
        if result["status"] == "success" and result["output"]:
            try:
                test_results = json.loads(result["output"])
                print("   ✓ Single method execution completed")
                
                if "summary" in test_results:
                    summary = test_results["summary"]
                    print(f"   Tests Run: {summary.get('total', 0)}")
                    print(f"   Passed: {summary.get('passed', 0)}")
                    print(f"   Failed: {summary.get('failed', 0)}")
                    
            except json.JSONDecodeError:
                print(f"   Raw output: {result['output']}")
        else:
            print(f"   ✗ Failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Run all tests in package
    print("\n3. Testing RunTestSpec with entire package...")
    try:
        command = 'SET tResult = ##class(ExecuteMCP.TestRunner.Manager).RunTestSpec("ExecuteMCP.Test") WRITE tResult'
        result = execute_command(command)
        
        if result["status"] == "success" and result["output"]:
            try:
                test_results = json.loads(result["output"])
                print("   ✓ Package execution completed")
                
                if "summary" in test_results:
                    summary = test_results["summary"]
                    print(f"   Tests Run: {summary.get('total', 0)}")
                    print(f"   Passed: {summary.get('passed', 0)}")
                    print(f"   Failed: {summary.get('failed', 0)}")
                    
                    # List all test classes found
                    if "classes" in test_results:
                        print(f"   Classes tested: {len(test_results['classes'])}")
                        for class_name in test_results["classes"]:
                            print(f"      - {class_name}")
                            
            except json.JSONDecodeError:
                print(f"   Raw output: {result['output']}")
        else:
            print(f"   ✗ Failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Verify assertion tracking
    print("\n4. Testing assertion tracking in results...")
    try:
        command = 'SET tResult = ##class(ExecuteMCP.TestRunner.Manager).RunTestSpec("ExecuteMCP.Test.SampleUnitTest") WRITE tResult'
        result = execute_command(command)
        
        if result["status"] == "success" and result["output"]:
            try:
                test_results = json.loads(result["output"])
                print("   ✓ Test with assertions completed")
                
                # Look for assertion details
                if "classes" in test_results:
                    for class_name, class_data in test_results["classes"].items():
                        if "methods" in class_data:
                            for method_name, method_data in class_data["methods"].items():
                                if "assertionCount" in method_data:
                                    print(f"   {method_name}: {method_data['assertionCount']} assertions")
                                    
            except json.JSONDecodeError:
                print(f"   Raw output: {result['output']}")
        else:
            print(f"   ✗ Failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 80)
    print("TestRunner Executor Test Complete")
    print("=" * 80)

if __name__ == "__main__":
    main()
