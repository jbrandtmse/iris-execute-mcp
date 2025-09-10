#!/usr/bin/env python3
"""
Test script to validate the fixed Discovery class using %Dictionary.CompiledClass.ID
"""

import os
import sys
import json

# Use MCP tools via import
import iris_execute_mcp

# Access the decorated MCP tools
execute_command = iris_execute_mcp.execute_command
execute_classmethod = iris_execute_mcp.execute_classmethod
compile_objectscript_class = iris_execute_mcp.compile_objectscript_class

def main():
    print("=" * 80)
    print("Testing Fixed Discovery Class with %Dictionary.CompiledClass.ID")
    print("=" * 80)
    
    # Step 1: Compile the updated Discovery class
    print("\n1. Compiling ExecuteMCP.TestRunner.Discovery.cls...")
    compile_result = compile_objectscript_class("ExecuteMCP.TestRunner.Discovery.cls")
    print(f"   Result: {compile_result}")
    
    # Step 2: Test DiscoverTestClasses method
    print("\n2. Testing Discovery.DiscoverTestClasses('ExecuteMCP.Test')...")
    discover_result = execute_classmethod(
        class_name="ExecuteMCP.TestRunner.Discovery",
        method_name="DiscoverTestClasses",
        parameters=["ExecuteMCP.Test"]
    )
    print(f"   Raw result: {discover_result}")
    
    try:
        result_data = json.loads(discover_result)
        if result_data.get("success"):
            classes_json = result_data.get("result", "[]")
            classes = json.loads(classes_json)
            print(f"   Found {len(classes)} test classes:")
            for cls in classes:
                print(f"   - {cls}")
        else:
            print(f"   Error: {result_data.get('error')}")
    except json.JSONDecodeError as e:
        print(f"   Failed to parse result: {e}")
    
    # Step 3: Test IsTestClass for each known test class
    print("\n3. Testing IsTestClass for known test classes...")
    test_classes = [
        "ExecuteMCP.Test.SimpleTest",
        "ExecuteMCP.Test.ErrorTest",
        "ExecuteMCP.Test.SampleUnitTest"
    ]
    
    for cls_name in test_classes:
        is_test_result = execute_classmethod(
            class_name="ExecuteMCP.TestRunner.Discovery",
            method_name="IsTestClass",
            parameters=[cls_name]
        )
        try:
            result_data = json.loads(is_test_result)
            if result_data.get("success"):
                is_test = result_data.get("result")
                print(f"   {cls_name}: {is_test}")
            else:
                print(f"   {cls_name}: Error - {result_data.get('error')}")
        except json.JSONDecodeError:
            print(f"   {cls_name}: Failed to parse result")
    
    # Step 4: Test DiscoverTestMethods for a specific class
    print("\n4. Testing DiscoverTestMethods for ExecuteMCP.Test.SimpleTest...")
    methods_result = execute_classmethod(
        class_name="ExecuteMCP.TestRunner.Discovery",
        method_name="DiscoverTestMethods",
        parameters=["ExecuteMCP.Test.SimpleTest"]
    )
    
    try:
        result_data = json.loads(methods_result)
        if result_data.get("success"):
            methods_json = result_data.get("result", "[]")
            methods = json.loads(methods_json)
            print(f"   Found {len(methods)} test methods:")
            for method in methods:
                print(f"   - {method}")
        else:
            print(f"   Error: {result_data.get('error')}")
    except json.JSONDecodeError as e:
        print(f"   Failed to parse result: {e}")
    
    # Step 5: Test BuildTestManifest for comprehensive discovery
    print("\n5. Testing BuildTestManifest('ExecuteMCP.Test')...")
    manifest_result = execute_classmethod(
        class_name="ExecuteMCP.TestRunner.Discovery",
        method_name="BuildTestManifest",
        parameters=["ExecuteMCP.Test"]
    )
    
    try:
        result_data = json.loads(manifest_result)
        if result_data.get("success"):
            manifest_json = result_data.get("result", "{}")
            manifest = json.loads(manifest_json)
            print(f"   Package: {manifest.get('package')}")
            print(f"   Total Classes: {manifest.get('totalClasses')}")
            print(f"   Total Tests: {manifest.get('totalTests')}")
            print(f"   Discovery Method: {manifest.get('discoveryMethod')}")
            print(f"   Success: {manifest.get('success')}")
            
            if manifest.get('classes'):
                print("\n   Classes found:")
                for cls_info in manifest['classes']:
                    print(f"   - {cls_info['className']} ({cls_info['methodCount']} tests)")
                    if cls_info.get('methods'):
                        for method in cls_info['methods']:
                            print(f"     • {method}")
        else:
            print(f"   Error: {result_data.get('error')}")
    except json.JSONDecodeError as e:
        print(f"   Failed to parse result: {e}")
    
    # Step 6: Test ValidateDiscovery for quick validation
    print("\n6. Testing ValidateDiscovery()...")
    validate_result = execute_classmethod(
        class_name="ExecuteMCP.TestRunner.Discovery",
        method_name="ValidateDiscovery"
    )
    
    try:
        result_data = json.loads(validate_result)
        if result_data.get("success"):
            validation_json = result_data.get("result", "{}")
            validation = json.loads(validation_json)
            print(f"   Success: {validation.get('success')}")
            print(f"   Test Package: {validation.get('testPackage')}")
            print(f"   Classes Found: {validation.get('classesFound')}")
            print(f"   Tests Found: {validation.get('testsFound')}")
            print(f"   Method: {validation.get('method')}")
            
            if validation.get('classes'):
                print("   Classes:")
                for cls_summary in validation['classes']:
                    print(f"   - {cls_summary}")
        else:
            print(f"   Error: {result_data.get('error')}")
    except json.JSONDecodeError as e:
        print(f"   Failed to parse result: {e}")
    
    print("\n" + "=" * 80)
    print("Discovery Testing Complete")
    print("=" * 80)

if __name__ == "__main__":
    main()
