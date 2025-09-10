#!/usr/bin/env python
"""Test the complete TestRunner workflow with Manager orchestration"""

import json
import iris
import os

def call_iris_sync(func, *args):
    """Synchronous IRIS call wrapper"""
    try:
        return func(*args)
    except Exception as e:
        return f"Error: {e}"

def main():
    print("="*80)
    print("Testing Complete TestRunner Workflow")
    print("="*80)
    
    # IRIS connection parameters
    hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
    port = int(os.getenv('IRIS_PORT', '1972'))
    namespace = os.getenv('IRIS_NAMESPACE', 'HSCUSTOM')
    username = os.getenv('IRIS_USERNAME', '_SYSTEM')
    password = os.getenv('IRIS_PASSWORD', '_SYSTEM')
    
    # Connect to IRIS
    conn = iris.connect(hostname, port, namespace, username, password)
    irispy = iris.createIRIS(conn)
    
    print("\n1. Compiling TestRunner classes...")
    # Compile Manager class (which will compile dependencies)
    result = call_iris_sync(
        irispy.classMethodString,
        "%SYSTEM.OBJ", "CompilePackage", "ExecuteMCP.TestRunner", "bckry"
    )
    print(f"   Compilation result: {result}")
    
    print("\n2. Testing Manager.RunTests('ExecuteMCP.Test.SimpleTest')...")
    # Test running a single test class
    result = call_iris_sync(
        irispy.classMethodString,
        "ExecuteMCP.TestRunner.Manager", "RunTests", "ExecuteMCP.Test.SimpleTest"
    )
    
    try:
        result_json = json.loads(result)
        print("   Success! Result structure:")
        print(f"   - TestsRun: {result_json.get('TestsRun', 'N/A')}")
        print(f"   - Passed: {result_json.get('Passed', 'N/A')}")
        print(f"   - Failed: {result_json.get('Failed', 'N/A')}")
        print(f"   - Duration: {result_json.get('Duration', 'N/A')}ms")
        print(f"   - Success: {result_json.get('Success', 'N/A')}")
        
        if 'TestClasses' in result_json:
            for test_class in result_json['TestClasses']:
                print(f"\n   Class: {test_class['ClassName']}")
                print(f"   - Tests Run: {test_class['TestsRun']}")
                print(f"   - Passed: {test_class['Passed']}")
                print(f"   - Failed: {test_class['Failed']}")
                
                if 'TestMethods' in test_class:
                    for method in test_class['TestMethods']:
                        status = "✓" if method['Success'] else "✗"
                        print(f"     {status} {method['MethodName']}: {method['Status']}")
                        if 'Assertions' in method:
                            for assertion in method['Assertions']:
                                assert_status = "✓" if assertion['Success'] else "✗"
                                print(f"       {assert_status} {assertion['Description']}")
    except json.JSONDecodeError:
        print(f"   Raw result: {result}")
    except Exception as e:
        print(f"   Error parsing result: {e}")
        print(f"   Raw result: {result}")
    
    print("\n3. Testing Manager.RunPackageTests('ExecuteMCP.Test')...")
    # Test running all tests in a package
    result = call_iris_sync(
        irispy.classMethodString,
        "ExecuteMCP.TestRunner.Manager", "RunPackageTests", "ExecuteMCP.Test"
    )
    
    try:
        result_json = json.loads(result)
        print("   Success! Package test results:")
        print(f"   - Total Tests: {result_json.get('TestsRun', 'N/A')}")
        print(f"   - Passed: {result_json.get('Passed', 'N/A')}")
        print(f"   - Failed: {result_json.get('Failed', 'N/A')}")
        print(f"   - Classes Tested: {len(result_json.get('TestClasses', []))}")
        
        # Show summary for each class
        if 'TestClasses' in result_json:
            for test_class in result_json['TestClasses']:
                status = "✓" if test_class['Success'] else "✗"
                print(f"     {status} {test_class['ClassName']}: {test_class['Passed']}/{test_class['TestsRun']} passed")
    except json.JSONDecodeError:
        print(f"   Raw result: {result}")
    except Exception as e:
        print(f"   Error parsing result: {e}")
        print(f"   Raw result: {result}")
    
    print("\n4. Testing Manager.ValidateTestRunner()...")
    # Validate the test runner setup
    result = call_iris_sync(
        irispy.classMethodString,
        "ExecuteMCP.TestRunner.Manager", "ValidateTestRunner"
    )
    
    try:
        result_json = json.loads(result)
        print("   TestRunner validation:")
        print(f"   - Success: {result_json.get('Success', 'N/A')}")
        print(f"   - Manager Ready: {result_json.get('ManagerReady', 'N/A')}")
        print(f"   - Discovery Working: {result_json.get('DiscoveryWorking', 'N/A')}")
        print(f"   - Test Classes Found: {result_json.get('TestClassesFound', 'N/A')}")
        print(f"   - Can Execute Tests: {result_json.get('CanExecuteTests', 'N/A')}")
    except json.JSONDecodeError:
        print(f"   Raw result: {result}")
    
    print("\n" + "="*80)
    print("TestRunner Complete Workflow Testing Complete")
    print("="*80)

if __name__ == "__main__":
    main()
