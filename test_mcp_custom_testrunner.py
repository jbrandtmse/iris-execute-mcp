#!/usr/bin/env python3
"""
Test script to verify ExecuteMCP.TestRunner is callable through iris-execute-mcp MCP server.
Tests the newly added run_custom_testrunner MCP tool.
"""

import json
import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import IRIS connection
try:
    import iris
    IRIS_AVAILABLE = True
except ImportError:
    IRIS_AVAILABLE = False
    print("WARNING: iris module not available. Using mock mode.")

# Global IRIS connection
irispy = None

def setup_iris_connection():
    """Setup IRIS connection once."""
    global irispy
    if not IRIS_AVAILABLE:
        return False
    
    try:
        # IRIS connection parameters
        hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
        port = int(os.getenv('IRIS_PORT', '1972'))
        namespace = os.getenv('IRIS_NAMESPACE', 'HSCUSTOM')
        username = os.getenv('IRIS_USERNAME', '_SYSTEM')
        password = os.getenv('IRIS_PASSWORD', '_SYSTEM')
        
        # Connect to IRIS
        conn = iris.connect(hostname, port, namespace, username, password)
        irispy = iris.createIRIS(conn)
        return True
    except Exception as e:
        print(f"Failed to connect to IRIS: {e}")
        return False

def call_iris_sync(class_name, method_name, *args):
    """Synchronous IRIS call to simulate MCP tool execution."""
    if not IRIS_AVAILABLE or irispy is None:
        # Mock response for testing
        return json.dumps({
            "status": "mock",
            "summary": {
                "passed": 2,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "duration": 0.5
            },
            "tests": [
                {
                    "class": "ExecuteMCP.Test.SimpleTest",
                    "method": "TestAddition",
                    "status": "passed",
                    "duration": 0.1
                },
                {
                    "class": "ExecuteMCP.Test.SimpleTest",  
                    "method": "TestSubtraction",
                    "status": "passed",
                    "duration": 0.1
                }
            ],
            "executionTime": 500
        })
    
    try:
        # Call IRIS class method
        result = irispy.classMethodString(class_name, method_name, *args)
        return result
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "error"
        })

def test_custom_testrunner():
    """Test the custom TestRunner through MCP-style calls."""
    
    print("=" * 80)
    print("Testing ExecuteMCP.TestRunner MCP Integration")
    print("=" * 80)
    
    # Setup IRIS connection
    if not setup_iris_connection():
        print("\n⚠️ WARNING: Running in mock mode (no IRIS connection)")
    
    # Test configurations
    test_cases = [
        {
            "name": "Package-level tests",
            "spec": "ExecuteMCP.Test",
            "description": "Run all tests in ExecuteMCP.Test package"
        },
        {
            "name": "Class-level tests",
            "spec": "ExecuteMCP.Test.SimpleTest",
            "description": "Run all tests in SimpleTest class"
        },
        {
            "name": "Method-level test",
            "spec": "ExecuteMCP.Test.SimpleTest:TestAddition",
            "description": "Run specific test method"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n### {test_case['name']}")
        print(f"Spec: {test_case['spec']}")
        print(f"Description: {test_case['description']}")
        print("-" * 40)
        
        # Simulate the MCP tool call (RunTestSpec takes only the spec parameter)
        result_json = call_iris_sync(
            "ExecuteMCP.TestRunner.Manager",
            "RunTestSpec",
            test_case["spec"]
        )
        
        try:
            result = json.loads(result_json)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Status: {result.get('status', 'unknown')}")
                
                # Display summary if available
                if "summary" in result:
                    summary = result["summary"]
                    print(f"\nTest Summary:")
                    print(f"  Passed: {summary.get('passed', 0)}")
                    print(f"  Failed: {summary.get('failed', 0)}")
                    print(f"  Errors: {summary.get('errors', 0)}")
                    print(f"  Skipped: {summary.get('skipped', 0)}")
                    print(f"  Duration: {summary.get('duration', 0):.3f}s")
                
                # Display individual test results
                if "tests" in result and result["tests"]:
                    print(f"\nIndividual Tests ({len(result['tests'])} total):")
                    for test in result["tests"][:5]:  # Show first 5 tests
                        status_icon = "✅" if test.get("status") == "passed" else "❌"
                        print(f"  {status_icon} {test.get('class', 'Unknown')}.{test.get('method', 'Unknown')}")
                        if test.get("duration"):
                            print(f"     Duration: {test['duration']:.3f}s")
                        if test.get("message"):
                            print(f"     Message: {test['message']}")
                    
                    if len(result["tests"]) > 5:
                        print(f"  ... and {len(result['tests']) - 5} more tests")
                
                # Display execution time
                if "executionTime" in result:
                    print(f"\nTotal Execution Time: {result['executionTime']}ms")
                    
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            print(f"Raw response: {result_json[:200]}...")
    
    print("\n" + "=" * 80)
    print("TestRunner MCP Integration Test Complete")
    print("=" * 80)
    
    # Verify the MCP tool is actually defined in iris_execute_mcp.py
    print("\n### Verifying MCP Tool Definition")
    try:
        with open("iris_execute_mcp.py", "r", encoding='utf-8') as f:
            content = f.read()
            if "run_custom_testrunner" in content:
                print("✅ run_custom_testrunner tool found in iris_execute_mcp.py")
                # Count occurrences
                count = content.count("def run_custom_testrunner")
                print(f"   Tool defined {count} time(s)")
            else:
                print("❌ run_custom_testrunner tool NOT found in iris_execute_mcp.py")
                print("   The MCP tool needs to be added to iris_execute_mcp.py")
    except Exception as e:
        print(f"❌ Could not verify MCP tool: {e}")

if __name__ == "__main__":
    test_custom_testrunner()
