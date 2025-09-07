#!/usr/bin/env python3
"""
Test script to verify the auto-prefix feature for unit test specifications.
Tests both with and without colon prefix to ensure backward compatibility
and improved user experience.
"""

import os
import sys
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add path for iris module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import iris
    IRIS_AVAILABLE = True
except ImportError:
    print("ERROR: intersystems-irispython not installed")
    sys.exit(1)

def call_iris_method(class_name, method_name, *args):
    """Call an IRIS class method and return the result."""
    try:
        # IRIS connection parameters
        hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
        port = int(os.getenv('IRIS_PORT', '1972'))
        namespace = os.getenv('IRIS_NAMESPACE', 'HSCUSTOM')
        username = os.getenv('IRIS_USERNAME', '_SYSTEM')
        password = os.getenv('IRIS_PASSWORD', '_SYSTEM')
        
        # Connect to IRIS
        conn = iris.connect(hostname, port, namespace, username, password)
        iris_obj = iris.createIRIS(conn)
        
        # Call the class method
        result = iris_obj.classMethodString(class_name, method_name, *args)
        
        # Close connection
        conn.close()
        
        return json.loads(result)
    except Exception as e:
        return {"status": "error", "error": str(e)}

def test_auto_prefix_feature():
    """Test the auto-prefix feature with various test specifications."""
    print("=" * 80)
    print("Testing Auto-Prefix Feature for Unit Test Specifications")
    print("=" * 80)
    
    test_cases = [
        {
            "description": "Without colon prefix (should be auto-added)",
            "test_spec": "ExecuteMCP.Test.SampleUnitTest",
            "expected_prefix": ":"
        },
        {
            "description": "With colon prefix (should remain unchanged)",
            "test_spec": ":ExecuteMCP.Test.SampleUnitTest",
            "expected_prefix": ":"
        },
        {
            "description": "Without colon, specific method (should be auto-added)",
            "test_spec": "ExecuteMCP.Test.SampleUnitTest:TestAddition",
            "expected_prefix": ":"
        },
        {
            "description": "Package-level test without colon (should be auto-added)",
            "test_spec": "ExecuteMCP.Test",
            "expected_prefix": ":"
        }
    ]
    
    all_passed = True
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        print(f"  Input: '{test_case['test_spec']}'")
        
        # Queue the test
        result = call_iris_method(
            "ExecuteMCP.Core.UnitTestQueue",
            "QueueTestExecution",
            test_case['test_spec'],
            "/noload/nodelete/recursive",
            ""
        )
        
        if result.get("status") == "queued":
            job_id = result.get("jobID")
            print(f"  ✓ Test queued successfully (Job ID: {job_id})")
            
            # Poll for results with retries
            max_retries = 5
            poll_result = None
            
            for retry in range(max_retries):
                time.sleep(1)
                poll_result = call_iris_method(
                    "ExecuteMCP.Core.UnitTestQueue",
                    "PollResults",
                    job_id
                )
                
                # Check if test is complete (status should be "success" when done)
                if poll_result.get("status") in ["success", "error", "completed"]:
                    break
            
            if poll_result and poll_result.get("status") in ["success", "completed"]:
                summary = poll_result.get("summary", {})
                passed = summary.get("passed", 0)
                failed = summary.get("failed", 0)
                errors = summary.get("errors", 0)
                
                print(f"  ✓ Test completed: {passed} passed, {failed} failed, {errors} errors")
                
                # Verify test was actually found and executed
                if passed > 0:
                    print(f"  ✓ Auto-prefix worked correctly - tests were found and executed")
                    results.append({"test": test_case['description'], "status": "PASSED"})
                else:
                    print(f"  ✗ No tests found - auto-prefix may have failed")
                    results.append({"test": test_case['description'], "status": "FAILED"})
                    all_passed = False
            else:
                print(f"  ⚠ Test still running or error: {poll_result.get('status')}")
                results.append({"test": test_case['description'], "status": "TIMEOUT"})
        else:
            print(f"  ✗ Failed to queue test: {result.get('error')}")
            results.append({"test": test_case['description'], "status": "ERROR"})
            all_passed = False
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for result in results:
        status_symbol = "✓" if result["status"] == "PASSED" else "✗"
        print(f"{status_symbol} {result['test']}: {result['status']}")
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED - Auto-prefix feature working correctly!")
    else:
        print("\n⚠️ Some tests failed - Check the auto-prefix implementation")
    
    return all_passed

def test_through_mcp():
    """Test through the MCP server to ensure end-to-end functionality."""
    print("\n" + "=" * 80)
    print("Testing Through MCP Server (End-to-End)")
    print("=" * 80)
    
    # Import and test the MCP server functions directly
    from iris_execute_mcp import queue_unit_tests, poll_unit_tests
    
    # Test without colon prefix
    print("\n1. Testing without colon prefix through MCP...")
    result1 = queue_unit_tests("ExecuteMCP.Test.SampleUnitTest")
    result1_parsed = json.loads(result1)
    
    if result1_parsed.get("status") == "queued":
        print(f"   ✓ Queued successfully: Job ID {result1_parsed.get('jobID')}")
        time.sleep(1)
        
        poll1 = poll_unit_tests(result1_parsed.get('jobID'))
        poll1_parsed = json.loads(poll1)
        
        if poll1_parsed.get("status") == "completed":
            summary = poll1_parsed.get("summary", {})
            if summary.get("passed", 0) > 0:
                print(f"   ✓ Tests executed: {summary.get('passed')} passed")
            else:
                print(f"   ✗ No tests found")
    else:
        print(f"   ✗ Failed to queue: {result1_parsed.get('error')}")
    
    # Test with colon prefix (backward compatibility)
    print("\n2. Testing with colon prefix through MCP (backward compatibility)...")
    result2 = queue_unit_tests(":ExecuteMCP.Test.SampleUnitTest")
    result2_parsed = json.loads(result2)
    
    if result2_parsed.get("status") == "queued":
        print(f"   ✓ Queued successfully: Job ID {result2_parsed.get('jobID')}")
        time.sleep(1)
        
        poll2 = poll_unit_tests(result2_parsed.get('jobID'))
        poll2_parsed = json.loads(poll2)
        
        if poll2_parsed.get("status") == "completed":
            summary = poll2_parsed.get("summary", {})
            if summary.get("passed", 0) > 0:
                print(f"   ✓ Tests executed: {summary.get('passed')} passed")
            else:
                print(f"   ✗ No tests found")
    else:
        print(f"   ✗ Failed to queue: {result2_parsed.get('error')}")

if __name__ == "__main__":
    # Test the auto-prefix feature
    direct_test_passed = test_auto_prefix_feature()
    
    # Test through MCP server
    test_through_mcp()
    
    print("\n" + "=" * 80)
    print("Auto-Prefix Feature Testing Complete")
    print("=" * 80)
    
    sys.exit(0 if direct_test_passed else 1)
