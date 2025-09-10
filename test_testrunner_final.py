#!/usr/bin/env python3
"""
Final test of custom TestRunner with fixed instantiation
"""

import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# IRIS connection settings
hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
port = int(os.getenv('IRIS_PORT', '1972'))
namespace = os.getenv('IRIS_NAMESPACE', 'HSCUSTOM')
username = os.getenv('IRIS_USERNAME', '_SYSTEM')
password = os.getenv('IRIS_PASSWORD', 'SYS')

print("=" * 80)
print("TestRunner Final Validation")
print("=" * 80)

try:
    # Import IRIS module
    import iris
    
    # Connect to IRIS using _SYSTEM credentials
    conn = iris.connect(hostname, port, namespace, username, password)
    irispy = iris.createIRIS(conn)
    
    # Helper function for synchronous IRIS calls
    def call_iris_sync(method, *args):
        """Execute IRIS method synchronously"""
        try:
            result = method(*args)
            if result is None:
                return ""
            return result
        except Exception as e:
            print(f"   Error: {e}")
            return None
    
    # First delete the problematic Debug.cls if it exists
    print("\n1. Cleaning up Debug.cls if it exists...")
    cleanup_result = call_iris_sync(
        irispy.classMethodValue,
        "$SYSTEM.OBJ",
        "Delete",
        "ExecuteMCP.TestRunner.Debug.cls",
        "ck"
    )
    print(f"   Cleanup result: {cleanup_result}")
    
    # Compile only the TestRunner classes (not Debug)
    print("\n2. Compiling TestRunner classes (Manager, Discovery, Context)...")
    compile_result = call_iris_sync(
        irispy.classMethodValue,
        "$SYSTEM.OBJ",
        "Compile",
        "ExecuteMCP.TestRunner.Manager.cls,ExecuteMCP.TestRunner.Discovery.cls,ExecuteMCP.TestRunner.Context.cls",
        "bckry"
    )
    print(f"   Compilation result: {compile_result}")
    
    # Test Discovery
    print("\n3. Testing Discovery.BuildTestManifest('ExecuteMCP.Test')...")
    manifest_json = call_iris_sync(
        irispy.classMethodString,
        "ExecuteMCP.TestRunner.Discovery",
        "BuildTestManifest",
        "ExecuteMCP.Test"
    )
    
    if manifest_json:
        try:
            manifest = json.loads(manifest_json)
            print(f"   ✓ Discovery found {len(manifest.get('classes', []))} test classes")
            for cls in manifest.get('classes', []):
                print(f"     - {cls.get('className')}: {len(cls.get('methods', []))} methods")
        except:
            print(f"   × Discovery returned invalid JSON: {manifest_json[:100]}...")
    else:
        print("   × Discovery returned empty/null")
    
    # Test Manager validation
    print("\n4. Testing Manager.ValidateTestRunner()...")
    validation = call_iris_sync(
        irispy.classMethodString,
        "ExecuteMCP.TestRunner.Manager",
        "ValidateTestRunner"
    )
    
    if validation:
        try:
            val_obj = json.loads(validation)
            print(f"   ✓ Manager Ready: {val_obj.get('ManagerReady', False)}")
            print(f"   ✓ Discovery Working: {val_obj.get('DiscoveryWorking', False)}")
            print(f"   ✓ Test Classes Found: {val_obj.get('TestClassesFound', 0)}")
            print(f"   ✓ Can Execute Tests: {val_obj.get('CanExecuteTests', False)}")
        except:
            print(f"   × Validation returned invalid JSON: {validation[:100]}...")
    
    # Test running a single test class
    print("\n5. Testing Manager.RunTests('ExecuteMCP.Test.SimpleTest')...")
    test_result = call_iris_sync(
        irispy.classMethodString,
        "ExecuteMCP.TestRunner.Manager",
        "RunTests",
        "ExecuteMCP.Test.SimpleTest"
    )
    
    if test_result:
        try:
            result_obj = json.loads(test_result)
            if "error" in result_obj:
                print(f"   × Error: {result_obj['error']}")
            else:
                print(f"   ✓ Tests Run: {result_obj.get('testsRun', 'N/A')}")
                print(f"   ✓ Passed: {result_obj.get('passed', 'N/A')}")
                print(f"   ✓ Failed: {result_obj.get('failed', 'N/A')}")
                print(f"   ✓ Success: {result_obj.get('success', 'N/A')}")
                
                # Show test details if available
                if "classes" in result_obj:
                    for cls_result in result_obj["classes"]:
                        print(f"\n   Class: {cls_result.get('name', 'Unknown')}")
                        print(f"     Status: {cls_result.get('status', 'Unknown')}")
                        if "methods" in cls_result:
                            for method in cls_result["methods"]:
                                status_icon = "✓" if method.get("status") == "passed" else "×"
                                print(f"       {status_icon} {method.get('name', 'Unknown')}: {method.get('status', 'Unknown')}")
                                if "assertions" in method:
                                    for assertion in method["assertions"]:
                                        assert_icon = "✓" if assertion.get("success") else "×"
                                        print(f"         {assert_icon} {assertion.get('description', assertion.get('action', 'Unknown'))}")
        except Exception as e:
            print(f"   × Could not parse result: {e}")
            print(f"   Raw result: {test_result[:200]}...")
    else:
        print("   × No result returned")
    
    # Test running all tests in a package
    print("\n6. Testing Manager.RunPackageTests('ExecuteMCP.Test')...")
    package_result = call_iris_sync(
        irispy.classMethodString,
        "ExecuteMCP.TestRunner.Manager",
        "RunPackageTests",
        "ExecuteMCP.Test"
    )
    
    if package_result:
        try:
            pkg_obj = json.loads(package_result)
            if "error" in pkg_obj:
                print(f"   × Error: {pkg_obj['error']}")
            else:
                print(f"   ✓ Total Tests: {pkg_obj.get('testsRun', 'N/A')}")
                print(f"   ✓ Total Passed: {pkg_obj.get('passed', 'N/A')}")
                print(f"   ✓ Total Failed: {pkg_obj.get('failed', 'N/A')}")
                print(f"   ✓ Classes Tested: {len(pkg_obj.get('classes', []))}")
        except Exception as e:
            print(f"   × Could not parse package result: {e}")
    
except ImportError as e:
    print(f"Error: Could not import iris module - {e}")
    print("Make sure intersystems-irispython is installed:")
    print("  pip install intersystems-irispython")
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Clean up connection
    if 'conn' in locals():
        conn.close()

print("\n" + "=" * 80)
print("TestRunner Final Validation Complete")
print("=" * 80)
