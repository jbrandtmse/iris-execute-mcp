#!/usr/bin/env python3
"""
Test script to compile ExecuteMCP.Test package and then test Discovery
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from iris_execute_mcp import mcp
import json

def main():
    
    print("=" * 80)
    print("Step 1: Compiling ExecuteMCP.Test package")
    print("=" * 80)
    
    # Compile the ExecuteMCP.Test package
    compile_package_tool = mcp._tool_manager.get_tool("compile_objectscript_package")
    result = compile_package_tool.fn(
        package_name="ExecuteMCP.Test",
        qspec="bckry",
        namespace="HSCUSTOM"
    )
    
    compile_data = json.loads(result)
    print(f"Compile Status: {compile_data.get('status')}")
    if compile_data.get('classes_compiled'):
        print(f"Classes Compiled: {compile_data.get('classes_compiled')}")
    if compile_data.get('output'):
        print(f"Compile Output:\n{compile_data.get('output')}")
    if compile_data.get('errors'):
        print(f"Compile Errors:\n{compile_data.get('errors')}")
    
    print("\n" + "=" * 80)
    print("Step 2: Compiling ExecuteMCP.TestRunner package")
    print("=" * 80)
    
    # Also compile the TestRunner package
    result = compile_package_tool.fn(
        package_name="ExecuteMCP.TestRunner",
        qspec="bckry",
        namespace="HSCUSTOM"
    )
    
    compile_data = json.loads(result)
    print(f"Compile Status: {compile_data.get('status')}")
    if compile_data.get('classes_compiled'):
        print(f"Classes Compiled: {compile_data.get('classes_compiled')}")
    if compile_data.get('output'):
        print(f"Compile Output:\n{compile_data.get('output')}")
    if compile_data.get('errors'):
        print(f"Compile Errors:\n{compile_data.get('errors')}")
    
    print("\n" + "=" * 80)
    print("Step 3: Testing Discovery.DiscoverTestClasses")
    print("=" * 80)
    
    # Now test Discovery
    execute_classmethod_tool = mcp._tool_manager.get_tool("execute_classmethod")
    result = execute_classmethod_tool.fn(
        class_name="ExecuteMCP.TestRunner.Discovery",
        method_name="DiscoverTestClasses",
        parameters=[{"value": "ExecuteMCP.Test"}],
        namespace="HSCUSTOM"
    )
    
    discovery_data = json.loads(result)
    print(f"Discovery Status: {discovery_data.get('status')}")
    
    if discovery_data.get('status') == 'success':
        if discovery_data.get('result'):
            # Parse the JSON result from Discovery
            test_classes = json.loads(discovery_data['result'])
            print(f"Test Classes Found: {len(test_classes)}")
            for cls in test_classes:
                print(f"  - {cls}")
        else:
            print("No test classes found")
    else:
        print(f"Discovery Error: {discovery_data.get('error')}")
    
    print("\n" + "=" * 80)
    print("Step 4: Testing Discovery.BuildTestManifest")
    print("=" * 80)
    
    # Test BuildTestManifest
    result = execute_classmethod_tool.fn(
        class_name="ExecuteMCP.TestRunner.Discovery",
        method_name="BuildTestManifest",
        parameters=[{"value": "ExecuteMCP.Test"}],
        namespace="HSCUSTOM"
    )
    
    manifest_data = json.loads(result)
    print(f"Manifest Status: {manifest_data.get('status')}")
    
    if manifest_data.get('status') == 'success':
        if manifest_data.get('result'):
            # Parse the JSON manifest
            manifest = json.loads(manifest_data['result'])
            print(f"Manifest Package: {manifest.get('package')}")
            print(f"Test Classes in Manifest: {len(manifest.get('classes', []))}")
            for cls_info in manifest.get('classes', []):
                print(f"  Class: {cls_info.get('className')}")
                print(f"    Methods: {cls_info.get('methods', [])}")
        else:
            print("Empty manifest returned")
    else:
        print(f"Manifest Error: {manifest_data.get('error')}")
    
    print("\n" + "=" * 80)
    print("Step 5: Testing Direct Method Calls to Debug Discovery")
    print("=" * 80)
    
    # Test IsTestClass directly with one of the compiled classes
    result = execute_classmethod_tool.fn(
        class_name="ExecuteMCP.TestRunner.Discovery",
        method_name="IsTestClass",
        parameters=[{"value": "ExecuteMCP.Test.SimpleTest"}],
        namespace="HSCUSTOM"
    )
    
    is_test_data = json.loads(result)
    print(f"IsTestClass Status: {is_test_data.get('status')}")
    if is_test_data.get('status') == 'success':
        print(f"IsTestClass(ExecuteMCP.Test.SimpleTest) = {is_test_data.get('result')}")
    else:
        print(f"IsTestClass Error: {is_test_data.get('error')}")
        
    # Also test with another class
    result = execute_classmethod_tool.fn(
        class_name="ExecuteMCP.TestRunner.Discovery",
        method_name="IsTestClass",
        parameters=[{"value": "ExecuteMCP.Test.ErrorTest"}],
        namespace="HSCUSTOM"
    )
    
    is_test_data = json.loads(result)
    if is_test_data.get('status') == 'success':
        print(f"IsTestClass(ExecuteMCP.Test.ErrorTest) = {is_test_data.get('result')}")

if __name__ == "__main__":
    main()
