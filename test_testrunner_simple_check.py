#!/usr/bin/env python3
"""
Simple diagnostic check for TestRunner classes using direct execute_command
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from iris_execute_mcp import call_iris_sync

def check_class_exists(class_name):
    """Check if a class exists using simpler command"""
    try:
        # Use simpler WRITE command
        command = f'WRITE $CLASSMETHOD("%Dictionary.CompiledClass","%ExistsId","{class_name}")'
        result = call_iris_sync("execute_command", {
            "command": command,
            "namespace": "HSCUSTOM"
        })
        if result and "output" in result:
            return result["output"] == "1"
        return False
    except Exception as e:
        print(f"  Error checking {class_name}: {e}")
        return False

def test_manager_instantiation():
    """Test Manager instantiation with simpler approach"""
    try:
        # Create instance and check if it's an object
        command = 'SET manager = ##class(ExecuteMCP.TestRunner.Manager).%New() WRITE $ISOBJECT(manager)'
        result = call_iris_sync("execute_command", {
            "command": command,
            "namespace": "HSCUSTOM"
        })
        if result and "output" in result:
            return result["output"] == "1"
        return False
    except Exception as e:
        print(f"  Error instantiating Manager: {e}")
        return False

def test_context_property():
    """Test if Context property is properly initialized"""
    try:
        # Create Manager and check Context property
        command = 'SET m = ##class(ExecuteMCP.TestRunner.Manager).%New() WRITE $ISOBJECT(m.Context)'
        result = call_iris_sync("execute_command", {
            "command": command,
            "namespace": "HSCUSTOM"
        })
        if result and "output" in result:
            return result["output"] == "1"
        return False
    except Exception as e:
        print(f"  Error checking Context: {e}")
        return False

def test_validate_method():
    """Test ValidateTestRunner method"""
    try:
        # Call method and check return
        command = 'SET result = ##class(ExecuteMCP.TestRunner.Manager).ValidateTestRunner() WRITE result'
        result = call_iris_sync("execute_command", {
            "command": command,
            "namespace": "HSCUSTOM"
        })
        if result and "output" in result:
            # Parse JSON result
            try:
                json_result = json.loads(result["output"])
                return json_result
            except:
                return result["output"]
        return None
    except Exception as e:
        print(f"  Error calling ValidateTestRunner: {e}")
        return None

def main():
    """Run simple diagnostic checks"""
    print("=" * 80)
    print("TestRunner Simple Diagnostic")
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
    
    # Test ValidateTestRunner
    print("\n4. Testing ValidateTestRunner method...")
    validate_result = test_validate_method()
    if validate_result:
        print(f"   Result: {validate_result}")
    else:
        print("   Result: FAILED")
    
    print("\n" + "=" * 80)
    print("Diagnostic Complete")
    print("=" * 80)

if __name__ == "__main__":
    main()
