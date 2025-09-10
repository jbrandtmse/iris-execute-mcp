#!/usr/bin/env python3
"""
Test script to validate the fixed Discovery class using direct IRIS calls
"""

import os
import sys
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

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
        error_msg = f"IRIS call failed: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "status": "error",
            "error": error_msg
        })

def main():
    print("=" * 80)
    print("Testing Fixed Discovery Class with %Dictionary.CompiledClass.ID")
    print("=" * 80)
    
    # Step 1: Compile the updated Discovery class
    print("\n1. Compiling ExecuteMCP.TestRunner.Discovery.cls...")
    compile_result = call_iris_sync(
        "ExecuteMCP.Core.Compile",
        "CompileClasses",
        "ExecuteMCP.TestRunner.Discovery.cls",
        "bckry",
        "HSCUSTOM"
    )
    print(f"   Result: {compile_result}")
    
    # Step 2: Test DiscoverTestClasses method
    print("\n2. Testing Discovery.DiscoverTestClasses('ExecuteMCP.Test')...")
    discover_result = call_iris_sync(
        "ExecuteMCP.TestRunner.Discovery",
        "DiscoverTestClasses",
        "ExecuteMCP.Test"
    )
    print(f"   Raw result: {discover_result}")
    
    try:
        # The result should be a JSON array directly
        classes = json.loads(discover_result)
        print(f"   Found {len(classes)} test classes:")
        for cls in classes:
            print(f"   - {cls}")
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
        is_test_result = call_iris_sync(
            "ExecuteMCP.TestRunner.Discovery",
            "IsTestClass",
            cls_name
        )
        print(f"   {cls_name}: {is_test_result}")
    
    # Step 4: Test DiscoverTestMethods for a specific class
    print("\n4. Testing DiscoverTestMethods for ExecuteMCP.Test.SimpleTest...")
    methods_result = call_iris_sync(
        "ExecuteMCP.TestRunner.Discovery",
        "DiscoverTestMethods",
        "ExecuteMCP.Test.SimpleTest"
    )
    
    try:
        methods = json.loads(methods_result)
        print(f"   Found {len(methods)} test methods:")
        for method in methods:
            print(f"   - {method}")
    except json.JSONDecodeError as e:
        print(f"   Failed to parse result: {e}")
    
    # Step 5: Test BuildTestManifest for comprehensive discovery
    print("\n5. Testing BuildTestManifest('ExecuteMCP.Test')...")
    manifest_result = call_iris_sync(
        "ExecuteMCP.TestRunner.Discovery",
        "BuildTestManifest",
        "ExecuteMCP.Test"
    )
    
    try:
        manifest = json.loads(manifest_result)
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
    except json.JSONDecodeError as e:
        print(f"   Failed to parse result: {e}")
    
    # Step 6: Test ValidateDiscovery for quick validation
    print("\n6. Testing ValidateDiscovery()...")
    validate_result = call_iris_sync(
        "ExecuteMCP.TestRunner.Discovery",
        "ValidateDiscovery"
    )
    
    try:
        validation = json.loads(validate_result)
        print(f"   Success: {validation.get('success')}")
        print(f"   Test Package: {validation.get('testPackage')}")
        print(f"   Classes Found: {validation.get('classesFound')}")
        print(f"   Tests Found: {validation.get('testsFound')}")
        print(f"   Method: {validation.get('method')}")
        
        if validation.get('classes'):
            print("   Classes:")
            for cls_summary in validation['classes']:
                print(f"   - {cls_summary}")
    except json.JSONDecodeError as e:
        print(f"   Failed to parse result: {e}")
    
    print("\n" + "=" * 80)
    print("Discovery Testing Complete")
    print("=" * 80)

if __name__ == "__main__":
    main()
