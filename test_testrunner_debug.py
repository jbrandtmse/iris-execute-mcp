#!/usr/bin/env python3
"""
Debug script for TestRunner implementation.
Tests each component individually with detailed output.
"""

import json
import os
import sys
from pathlib import Path

try:
    import iris
    IRIS_AVAILABLE = True
except ImportError:
    print("ERROR: intersystems-irispython not installed")
    sys.exit(1)

def call_iris_sync(class_name: str, method_name: str, *args):
    """Synchronous IRIS class method call."""
    try:
        # IRIS connection parameters from environment
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
        
        return result
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"IRIS call failed: {str(e)}",
            "output": "",
            "namespace": "N/A"
        })

def test_discovery():
    """Test Discovery.BuildTestManifest directly."""
    print("\n=== Testing Discovery.BuildTestManifest ===")
    
    # Call BuildTestManifest
    result = call_iris_sync("ExecuteMCP.TestRunner.Discovery", "BuildTestManifest", "ExecuteMCP.Test")
    
    print(f"Raw result type: {type(result)}")
    print(f"Raw result (first 500 chars): {result[:500] if len(result) > 500 else result}")
    
    # Try to parse as JSON
    try:
        parsed = json.loads(result)
        print(f"\n✅ Valid JSON returned")
        print(f"Package: {parsed.get('package')}")
        print(f"Classes found: {len(parsed.get('classes', []))}")
        
        for cls in parsed.get('classes', []):
            print(f"  - {cls.get('name')}: {len(cls.get('methods', []))} methods")
            for method in cls.get('methods', []):
                print(f"    • {method}")
                
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON parse error: {e}")
        print(f"Result was: {result}")

def test_manager_run():
    """Test Manager.RunTests directly."""
    print("\n=== Testing Manager.RunTests ===")
    
    # Call RunTests
    result = call_iris_sync("ExecuteMCP.TestRunner.Manager", "RunTests", "ExecuteMCP.Test", "")
    
    print(f"Raw result type: {type(result)}")
    print(f"Raw result (first 500 chars): {result[:500] if len(result) > 500 else result}")
    
    # Try to parse as JSON
    try:
        parsed = json.loads(result)
        print(f"\n✅ Valid JSON returned")
        print(f"Status: {parsed.get('status')}")
        print(f"Tests run: {parsed.get('testsRun', 0)}")
        print(f"Passed: {parsed.get('passed', 0)}")
        print(f"Failed: {parsed.get('failed', 0)}")
        
        for cls in parsed.get('classes', []):
            print(f"\nClass: {cls.get('name')}")
            print(f"  Status: {cls.get('status')}")
            for method in cls.get('methods', []):
                print(f"  - {method.get('name')}: {method.get('status')}")
                
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON parse error: {e}")
        print(f"Result was: {result}")

def test_package_discovery():
    """Test Manager.DiscoverTestPackages directly."""
    print("\n=== Testing Manager.DiscoverTestPackages ===")
    
    # Call DiscoverTestPackages
    result = call_iris_sync("ExecuteMCP.TestRunner.Manager", "DiscoverTestPackages")
    
    print(f"Raw result type: {type(result)}")
    print(f"Raw result: {result}")
    
    # Try to parse as JSON
    try:
        parsed = json.loads(result)
        print(f"\n✅ Valid JSON returned")
        print(f"Packages found: {parsed}")
                
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON parse error: {e}")

def test_simple_execute():
    """Test executing a simple ObjectScript command to verify connectivity."""
    print("\n=== Testing Simple Command Execution ===")
    
    # Use ExecuteMCP.Core.Command to execute a simple command
    result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", "WRITE \"Hello from TestRunner debug\"", "HSCUSTOM")
    
    print(f"Raw result: {result}")
    
    try:
        parsed = json.loads(result)
        print(f"Status: {parsed.get('status')}")
        print(f"Output: {parsed.get('output')}")
    except:
        print("Could not parse as JSON")

def main():
    print("=" * 60)
    print("TestRunner Debug Suite")
    print("=" * 60)
    
    # Test basic connectivity first
    test_simple_execute()
    
    # Test each component
    test_discovery()
    test_package_discovery()
    test_manager_run()
    
    print("\n" + "=" * 60)
    print("Debug complete - check output above for issues")
    print("=" * 60)

if __name__ == "__main__":
    main()
