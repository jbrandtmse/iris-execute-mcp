#!/usr/bin/env python3
"""
Direct test of TestRunner using proper IRIS backend calls
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the IRIS connection function properly
from iris_execute_mcp import call_iris_sync

def check_class_exists(class_name):
    """Check if a class exists using direct IRIS call"""
    try:
        # Use ExecuteMCP.Core.Command backend directly
        command = f'WRITE $CLASSMETHOD("%Dictionary.CompiledClass","%ExistsId","{class_name}")'
        result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", command, "HSCUSTOM")
        
        if result:
            parsed = json.loads(result)
            if parsed.get("status") == "success":
                return parsed.get("output") == "1"
        return False
    except Exception as e:
        print(f"  Error checking {class_name}: {e}")
        return False

def test_manager_instantiation():
    """Test Manager instantiation"""
    try:
        command = 'SET manager = ##class(ExecuteMCP.TestRunner.Manager).%New() WRITE $ISOBJECT(manager)'
        result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", command, "HSCUSTOM")
        
        if result:
            parsed = json.loads(result)
            if parsed.get("status") == "success":
                return parsed.get("output") == "1"
        return False
    except Exception as e:
        print(f"  Error instantiating Manager: {e}")
        return False

def test_context_property():
    """Test if Context property is properly initialized"""
    try:
        command = 'SET m = ##class(ExecuteMCP.TestRunner.Manager).%New() WRITE $ISOBJECT(m.Context)'
        result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", command, "HSCUSTOM")
        
        if result:
            parsed = json.loads(result)
            if parsed.get("status") == "success":
                return parsed.get("output") == "1"
        return False
    except Exception as e:
        print(f"  Error checking Context: {e}")
        return False

def test_validate_method():
    """Test ValidateTestRunner method"""
    try:
        command = 'SET result = ##class(ExecuteMCP.TestRunner.Manager).ValidateTestRunner() WRITE result'
        result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", command, "HSCUSTOM")
        
        if result:
            parsed = json.loads(result)
            if parsed.get("status") == "success":
                output = parsed.get("output", "")
                # Try to parse as JSON if it looks like JSON
                if output.startswith("{"):
                    try:
                        return json.loads(output)
                    except:
                        pass
                return output
        return None
    except Exception as e:
        print(f"  Error calling ValidateTestRunner: {e}")
        return None

def test_discovery():
    """Test Discovery class directly"""
    try:
        # Test DiscoverTestClasses method
        command = 'SET result = ##class(ExecuteMCP.TestRunner.Discovery).DiscoverTestClasses("ExecuteMCP.Test") WRITE result'
        result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", command, "HSCUSTOM")
        
        if result:
            parsed = json.loads(result)
            if parsed.get("status") == "success":
                output = parsed.get("output", "")
                print(f"   Discovery output: {output}")
                return output != ""
        return False
    except Exception as e:
        print(f"  Error testing Discovery: {e}")
        return False

def main():
    """Run direct TestRunner diagnostics"""
    print("=" * 80)
    print("TestRunner Direct Diagnostic")
    print("=" * 80)
    
    # Check classes exist
    print("\n1. Checking class existence...")
    classes = [
        "ExecuteMCP.TestRunner.Manager",
        "ExecuteMCP.TestRunner.Context",
        "ExecuteMCP.TestRunner.Discovery"
    ]
    
    for class_name in classes:
        exists = check_class_exists(class_name)
        status = "✓ EXISTS" if exists else "✗ NOT FOUND"
        print(f"   {class_name}: {status}")
    
    # Test Manager instantiation
    print("\n2. Testing Manager instantiation...")
    can_instantiate = test_manager_instantiation()
    status = "✓ SUCCESS" if can_instantiate else "✗ FAILED"
    print(f"   Manager instantiation: {status}")
    
    # Test Context property
    print("\n3. Testing Context auto-initialization...")
    context_ok = test_context_property()
    status = "✓ INITIALIZED" if context_ok else "✗ NOT INITIALIZED"
    print(f"   Context property: {status}")
    
    # Test Discovery
    print("\n4. Testing Discovery class...")
    discovery_ok = test_discovery()
    status = "✓ WORKING" if discovery_ok else "✗ FAILED"
    print(f"   Discovery: {status}")
    
    # Test ValidateTestRunner
    print("\n5. Testing ValidateTestRunner method...")
    validate_result = test_validate_method()
    if validate_result:
        print(f"   Result: {validate_result}")
    else:
        print("   Result: FAILED")
    
    # Check test classes
    print("\n6. Checking test classes exist...")
    test_classes = [
        "ExecuteMCP.Test.SampleUnitTest",
        "ExecuteMCP.Test.SimpleTest",
        "ExecuteMCP.Test.ErrorTest"
    ]
    
    for class_name in test_classes:
        exists = check_class_exists(class_name)
        status = "✓ EXISTS" if exists else "✗ NOT FOUND"
        print(f"   {class_name}: {status}")
    
    print("\n" + "=" * 80)
    print("Diagnostic Complete")
    print("=" * 80)

if __name__ == "__main__":
    main()
