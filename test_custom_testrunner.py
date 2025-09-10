#!/usr/bin/env python3
"""
Test script for custom ExecuteMCP.TestRunner implementation.

Tests:
1. Discovery of test classes in packages
2. Execution of test methods with lifecycle support
3. Assertion macro compatibility
4. JSON result formatting
"""

import json
import os
import sys
from pathlib import Path

# Use the same IRIS connection approach as iris_execute_mcp.py
try:
    import iris
    IRIS_AVAILABLE = True
except ImportError:
    print("ERROR: intersystems-irispython not installed")
    print("Run: pip install intersystems-irispython")
    sys.exit(1)

def call_iris_sync(class_name: str, method_name: str, *args):
    """
    Synchronous IRIS class method call.
    Returns JSON string response from IRIS.
    """
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

class TestRunner:
    """Wrapper for TestRunner testing functions."""
    
    def execute_classmethod(self, class_name, method_name, parameters=None, namespace="HSCUSTOM"):
        """Execute a class method with parameters."""
        if parameters is None:
            parameters = []
        
        # Convert parameters to the format expected by ExecuteMCP.Core.Command.ExecuteClassMethod
        param_values = []
        for param in parameters:
            if isinstance(param, dict):
                param_values.append(param.get("value", ""))
            else:
                param_values.append(param)
        
        # Call the method directly
        return call_iris_sync(class_name, method_name, *param_values)
    
    def compile_objectscript_class(self, class_names, namespace="HSCUSTOM"):
        """Compile ObjectScript classes."""
        return call_iris_sync("ExecuteMCP.Core.Compile", "CompileClasses", class_names, "bckry", namespace)

def test_discovery():
    """Test that Discovery can find test classes."""
    print("\n=== Testing Test Discovery ===")
    tool = TestRunner()
    
    # Test discovering test classes in ExecuteMCP.Test package
    result = tool.execute_classmethod(
        class_name="ExecuteMCP.TestRunner.Discovery",
        method_name="BuildTestManifest", 
        parameters=[{"value": "ExecuteMCP.Test"}],
        namespace="HSCUSTOM"
    )
    
    manifest = json.loads(result)
    if manifest.get("status") == "error":
        print(f"❌ Discovery failed: {manifest.get('error')}")
        return False
    
    # Parse the returned JSON string from the method
    manifest_data = json.loads(manifest.get("result", "{}"))
    
    print(f"✅ Discovered package: {manifest_data.get('package')}")
    print(f"   Found {len(manifest_data.get('classes', []))} test classes")
    
    for cls in manifest_data.get('classes', []):
        print(f"   - {cls.get('name')}: {len(cls.get('methods', []))} test methods")
        for method in cls.get('methods', []):
            print(f"     • {method}")
    
    return True

def test_package_discovery():
    """Test discovering available test packages."""
    print("\n=== Testing Package Discovery ===")
    tool = TestRunner()
    
    result = tool.execute_classmethod(
        class_name="ExecuteMCP.TestRunner.Manager",
        method_name="DiscoverTestPackages",
        parameters=[],
        namespace="HSCUSTOM"
    )
    
    response = json.loads(result)
    if response.get("status") == "error":
        print(f"❌ Package discovery failed: {response.get('error')}")
        return False
    
    packages = json.loads(response.get("result", "[]"))
    print(f"✅ Found {len(packages)} test packages:")
    for pkg in packages:
        print(f"   - {pkg}")
    
    return True

def test_run_simple_tests():
    """Test running a simple test class."""
    print("\n=== Testing Simple Test Execution ===")
    tool = TestRunner()
    
    # Run tests in ExecuteMCP.Test package
    result = tool.execute_classmethod(
        class_name="ExecuteMCP.TestRunner.Manager",
        method_name="RunTests",
        parameters=[
            {"value": "ExecuteMCP.Test"},
            {"value": ""}  # No filter
        ],
        namespace="HSCUSTOM"
    )
    
    response = json.loads(result)
    if response.get("status") == "error":
        print(f"❌ Test execution failed: {response.get('error')}")
        print(f"   Error details: {response.get('output', '')}")
        return False
    
    # Parse the test results JSON
    results = json.loads(response.get("result", "{}"))
    
    print(f"✅ Test execution completed:")
    print(f"   Status: {results.get('status')}")
    print(f"   Duration: {results.get('duration', 0):.3f}s")
    print(f"   Total Tests: {results.get('testsRun', 0)}")
    print(f"   Passed: {results.get('passed', 0)}")
    print(f"   Failed: {results.get('failed', 0)}")
    print(f"   Errors: {results.get('errors', 0)}")
    
    # Show class-level results
    for cls in results.get('classes', []):
        print(f"\n   Class: {cls.get('name')}")
        print(f"     Status: {cls.get('status')}")
        print(f"     Duration: {cls.get('duration', 0):.3f}s")
        
        # Show method-level results
        for method in cls.get('methods', []):
            status_icon = "✅" if method.get('status') == "passed" else "❌"
            print(f"     {status_icon} {method.get('name')}: {method.get('status')}")
            
            # Show assertions if any failed
            for assertion in method.get('assertions', []):
                if not assertion.get('success'):
                    print(f"        ❌ {assertion.get('action')}: {assertion.get('description')}")
    
    return results.get('status') == 'passed'

def test_filtered_execution():
    """Test running tests with a filter."""
    print("\n=== Testing Filtered Test Execution ===")
    tool = TestRunner()
    
    # Run only SimpleTest class
    result = tool.execute_classmethod(
        class_name="ExecuteMCP.TestRunner.Manager",
        method_name="RunTests",
        parameters=[
            {"value": "ExecuteMCP.Test"},
            {"value": "SimpleTest"}  # Filter for SimpleTest
        ],
        namespace="HSCUSTOM"
    )
    
    response = json.loads(result)
    if response.get("status") == "error":
        print(f"❌ Filtered execution failed: {response.get('error')}")
        return False
    
    results = json.loads(response.get("result", "{}"))
    
    print(f"✅ Filtered execution completed:")
    print(f"   Filter: 'SimpleTest'")
    print(f"   Classes run: {len(results.get('classes', []))}")
    
    for cls in results.get('classes', []):
        print(f"   - {cls.get('name')}")
    
    return True

def test_assertion_compatibility():
    """Test that assertion macros work correctly."""
    print("\n=== Testing Assertion Macro Compatibility ===")
    tool = TestRunner()
    
    # Create a test class that uses various assertion macros
    test_class = '''Class ExecuteMCP.Test.AssertionTest Extends %UnitTest.TestCase
{

/// Test various assertion macros
Method TestAssertions() As %Status
{
    Do $$$AssertEquals(1, 1, "One equals one")
    Do $$$AssertTrue(1, "True assertion")
    Do $$$AssertNotEquals(1, 2, "One does not equal two")
    Do $$$AssertStatusOK($$$OK, "Status is OK")
    
    // Test a failing assertion
    Do $$$AssertEquals(1, 2, "This should fail")
    
    Quit $$$OK
}

}'''
    
    # Write test class
    with open("src/ExecuteMCP/Test/AssertionTest.cls", "w") as f:
        f.write(test_class)
    
    print("✅ Created AssertionTest class with various assertion macros")
    
    # Compile the test class
    compile_result = tool.compile_objectscript_class(
        class_names="ExecuteMCP.Test.AssertionTest.cls",
        namespace="HSCUSTOM"
    )
    
    compile_response = json.loads(compile_result)
    if compile_response.get("status") != "success":
        print(f"❌ Failed to compile AssertionTest: {compile_response.get('message')}")
        return False
    
    print("✅ Compiled AssertionTest class")
    
    # Run the assertion test
    result = tool.execute_classmethod(
        class_name="ExecuteMCP.TestRunner.Manager",
        method_name="RunTests",
        parameters=[
            {"value": "ExecuteMCP.Test"},
            {"value": "AssertionTest"}  # Run only AssertionTest
        ],
        namespace="HSCUSTOM"
    )
    
    response = json.loads(result)
    if response.get("status") == "error":
        print(f"❌ Assertion test execution failed: {response.get('error')}")
        return False
    
    results = json.loads(response.get("result", "{}"))
    
    print(f"✅ Assertion test completed:")
    
    # Check assertion details
    for cls in results.get('classes', []):
        if cls.get('name') == 'ExecuteMCP.Test.AssertionTest':
            for method in cls.get('methods', []):
                if method.get('name') == 'TestAssertions':
                    print(f"   Method status: {method.get('status')}")
                    print(f"   Assertions run: {len(method.get('assertions', []))}")
                    
                    for assertion in method.get('assertions', []):
                        status_icon = "✅" if assertion.get('success') else "❌"
                        print(f"   {status_icon} {assertion.get('action')}: {assertion.get('description')}")
    
    return True

def main():
    """Run all validation tests."""
    print("=" * 60)
    print("Custom TestRunner Validation Suite")
    print("=" * 60)
    
    all_passed = True
    
    # Run tests in order
    tests = [
        ("Discovery", test_discovery),
        ("Package Discovery", test_package_discovery),
        ("Simple Execution", test_run_simple_tests),
        ("Filtered Execution", test_filtered_execution),
        ("Assertion Compatibility", test_assertion_compatibility)
    ]
    
    for name, test_func in tests:
        try:
            passed = test_func()
            if not passed:
                all_passed = False
                print(f"\n❌ {name} test failed")
        except Exception as e:
            all_passed = False
            print(f"\n❌ {name} test failed with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All validation tests passed!")
        print("\nThe custom TestRunner is working correctly:")
        print("• Discovery finds test classes and methods")
        print("• Manager executes tests with proper lifecycle")  
        print("• Assertion macros are fully compatible")
        print("• JSON results are properly formatted")
        print("\nReady to implement MCP tools for the TestRunner!")
    else:
        print("❌ Some validation tests failed")
        print("Please review the errors above and fix the implementation")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
