#!/usr/bin/env python3
"""
Test script for ObjectScript compilation tools.
Tests the ExecuteMCP.Core.Compile class methods directly.
"""

import os
import sys
import json

# Add the iris module path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import iris
    print("✅ IRIS module imported successfully")
except ImportError:
    print("❌ IRIS module not available - install intersystems-irispython")
    sys.exit(1)

# Test configuration from environment variables
IRIS_HOSTNAME = os.getenv('IRIS_HOSTNAME', 'localhost')
IRIS_PORT = int(os.getenv('IRIS_PORT', '1972'))
IRIS_NAMESPACE = os.getenv('IRIS_NAMESPACE', 'HSCUSTOM')
IRIS_USERNAME = os.getenv('IRIS_USERNAME', '_SYSTEM')
IRIS_PASSWORD = os.getenv('IRIS_PASSWORD', '_SYSTEM')

def test_compile_tools():
    """Test ObjectScript compilation tools directly through IRIS"""
    
    print("\n============================================================")
    print("Testing ObjectScript Compilation Tools")
    print("============================================================\n")
    
    passed = 0
    failed = 0
    
    try:
        # Connect to IRIS
        conn = iris.connect(IRIS_HOSTNAME, IRIS_PORT, IRIS_NAMESPACE, IRIS_USERNAME, IRIS_PASSWORD)
        iris_obj = iris.createIRIS(conn)
        print(f"✅ Connected to IRIS at {IRIS_HOSTNAME}:{IRIS_PORT}/{IRIS_NAMESPACE}\n")
        
        # Test 1: Compile single class
        print("=== Test 1: Compile single class ===")
        print("Compiling ExecuteMCP.Core.Command...")
        try:
            result = iris_obj.classMethodString(
                "ExecuteMCP.Core.Compile", 
                "CompileClasses",
                "ExecuteMCP.Core.Command",
                "bckry",
                IRIS_NAMESPACE
            )
            parsed = json.loads(result)
            if parsed.get("status") == "success":
                print(f"✅ PASS: Single class compiled successfully")
                print(f"   Compiled: {', '.join(parsed.get('compiledItems', []))}")
                passed += 1
            else:
                print(f"❌ FAIL: Compilation returned status: {parsed.get('status')}")
                if parsed.get('errors'):
                    for error in parsed['errors']:
                        print(f"   Error: {error['message']}")
                failed += 1
        except Exception as e:
            print(f"❌ FAIL: Test failed with exception: {str(e)}")
            failed += 1
        
        # Test 2: Compile multiple classes
        print("\n=== Test 2: Compile multiple classes ===")
        print("Compiling ExecuteMCP.Core.Command, ExecuteMCP.Core.Compile...")
        try:
            result = iris_obj.classMethodString(
                "ExecuteMCP.Core.Compile", 
                "CompileClasses",
                "ExecuteMCP.Core.Command,ExecuteMCP.Core.Compile",
                "bckry",
                IRIS_NAMESPACE
            )
            parsed = json.loads(result)
            if parsed.get("status") == "success":
                print(f"✅ PASS: Multiple classes compiled successfully")
                print(f"   Compiled: {', '.join(parsed.get('compiledItems', []))}")
                passed += 1
            else:
                print(f"❌ FAIL: Compilation returned status: {parsed.get('status')}")
                failed += 1
        except Exception as e:
            print(f"❌ FAIL: Test failed with exception: {str(e)}")
            failed += 1
        
        # Test 3: Compile entire package
        print("\n=== Test 3: Compile entire package ===")
        print("Compiling ExecuteMCP.Core package...")
        try:
            result = iris_obj.classMethodString(
                "ExecuteMCP.Core.Compile", 
                "CompilePackage",
                "ExecuteMCP.Core",
                "bckry",
                IRIS_NAMESPACE
            )
            parsed = json.loads(result)
            if parsed.get("status") == "success":
                print(f"✅ PASS: Package compiled successfully")
                print(f"   Total classes: {parsed.get('totalClasses', 0)}")
                print(f"   Compiled: {parsed.get('compiledCount', 0)}")
                passed += 1
            else:
                print(f"❌ FAIL: Compilation returned status: {parsed.get('status')}")
                failed += 1
        except Exception as e:
            print(f"❌ FAIL: Test failed with exception: {str(e)}")
            failed += 1
        
        # Test 4: Compile with custom qspec
        print("\n=== Test 4: Compile with custom qspec ===")
        print("Compiling ExecuteMCP.Test.SampleUnitTest with qspec='ck'...")
        try:
            result = iris_obj.classMethodString(
                "ExecuteMCP.Core.Compile", 
                "CompileClasses",
                "ExecuteMCP.Test.SampleUnitTest",
                "ck",
                IRIS_NAMESPACE
            )
            parsed = json.loads(result)
            if parsed.get("status") == "success":
                print(f"✅ PASS: Class compiled with custom qspec")
                print(f"   Compiled: {', '.join(parsed.get('compiledItems', []))}")
                passed += 1
            else:
                print(f"❌ FAIL: Compilation returned status: {parsed.get('status')}")
                failed += 1
        except Exception as e:
            print(f"❌ FAIL: Test failed with exception: {str(e)}")
            failed += 1
        
        # Test 5: Compile non-existent class (error test)
        print("\n=== Test 5: Compile non-existent class (error test) ===")
        print("Attempting to compile NonExistent.Class...")
        try:
            result = iris_obj.classMethodString(
                "ExecuteMCP.Core.Compile", 
                "CompileClasses",
                "NonExistent.Class",
                "bckry",
                IRIS_NAMESPACE
            )
            parsed = json.loads(result)
            if parsed.get("status") in ["error", "partial"]:
                print(f"✅ PASS: Error handling worked correctly")
                print(f"   Status: {parsed.get('status')}")
                if parsed.get('failedItems'):
                    print(f"   Failed items: {', '.join(parsed['failedItems'])}")
                if parsed.get('errors'):
                    print(f"   Error count: {len(parsed['errors'])}")
                passed += 1
            else:
                print(f"❌ FAIL: Expected error status but got: {parsed.get('status')}")
                failed += 1
        except Exception as e:
            print(f"❌ FAIL: Test failed with exception: {str(e)}")
            failed += 1
        
        # Test 6: Create and compile class with syntax error
        print("\n=== Test 6: Compile class with syntax error ===")
        print("\n=== Creating test class with syntax error ===")
        
        # First create the error test class file
        error_class_path = "src/ExecuteMCP/Test/ErrorTest.cls"
        if not os.path.exists(error_class_path):
            error_class_content = """Class ExecuteMCP.Test.ErrorTest
{
/// <description>
/// Test class with intentional syntax error
/// </description>
ClassMethod TestMethod() As %Status
{
    Set tSC = $$$OK
    
    // Intentional syntax error: missing closing quote
    Set tMessage = "This string has no closing quote
    
    Quit tSC
}

}
"""
            os.makedirs(os.path.dirname(error_class_path), exist_ok=True)
            with open(error_class_path, 'w') as f:
                f.write(error_class_content)
            print(f"Created {error_class_path} with syntax error")
        
        print("Attempting to compile ExecuteMCP.Test.ErrorTest...")
        try:
            result = iris_obj.classMethodString(
                "ExecuteMCP.Core.Compile", 
                "CompileClasses",
                "ExecuteMCP.Test.ErrorTest",
                "bckry",
                IRIS_NAMESPACE
            )
            parsed = json.loads(result)
            if parsed.get("status") in ["error", "partial"]:
                print(f"✅ PASS: Syntax error detected correctly")
                print(f"   Status: {parsed.get('status')}")
                if parsed.get('errors'):
                    for error in parsed['errors'][:2]:  # Show first 2 errors
                        print(f"   Error: {error.get('message', 'No message')}")
                passed += 1
            else:
                print(f"❌ FAIL: Expected error status but got: {parsed.get('status')}")
                failed += 1
        except Exception as e:
            print(f"❌ FAIL: Test failed with exception: {str(e)}")
            failed += 1
        
        # Close connection
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Connection failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Print summary
    print("\n============================================================")
    print("TEST SUMMARY")
    print("============================================================")
    
    test_names = [
        "Single class compilation",
        "Multiple classes compilation",
        "Package compilation",
        "Custom qspec flags",
        "Non-existent class (error handling)",
        "Class with syntax error"
    ]
    
    for i in range(min(len(test_names), passed + failed)):
        if i < passed:
            print(f"✅ PASS: {test_names[i]}")
        else:
            print(f"❌ FAIL: {test_names[i]}")
    
    print(f"\nTotal: {passed} passed, {failed} failed out of {passed + failed} tests")
    
    if failed == 0:
        print("\n✅ All tests passed successfully!")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review the errors above.")
    
    return passed, failed

if __name__ == "__main__":
    print("============================================================")
    print("IRIS Execute MCP - Compilation Tools Test Suite")
    print(f"Testing against IRIS at {IRIS_HOSTNAME}:{IRIS_PORT}")
    print(f"Namespace: {IRIS_NAMESPACE}")
    print("============================================================")
    
    test_compile_tools()
