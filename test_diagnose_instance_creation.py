#!/usr/bin/env python3
"""
Diagnose instance creation issue in TestRunner
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from iris_execute_mcp import call_iris_sync

def test_instance_creation_methods():
    """Test different instance creation approaches"""
    print("\n=== Testing Instance Creation Methods ===\n")
    
    # Test 1: Direct ##class().%New() approach
    print("1. Testing direct ##class().%New() approach:")
    cmd = '''
    Set tTest = ##class(ExecuteMCP.Test.SimpleTest).%New("")
    Write "Direct creation: ", $ISOBJECT(tTest), !
    '''
    result = call_iris_sync("execute_command", {
        "command": cmd,
        "namespace": "HSCUSTOM"
    })
    print(f"Result: {result}")
    
    # Test 2: $CLASSMETHOD approach
    print("\n2. Testing $CLASSMETHOD approach:")
    cmd = '''
    Set tClass = "ExecuteMCP.Test.SimpleTest"
    Set tTest = $CLASSMETHOD(tClass, "%New", "")
    Write "CLASSMETHOD creation: ", $ISOBJECT(tTest), !
    '''
    result = call_iris_sync("execute_command", {
        "command": cmd,
        "namespace": "HSCUSTOM"
    })
    print(f"Result: {result}")
    
    # Test 3: XECUTE with global variable approach
    print("\n3. Testing XECUTE with global variable:")
    cmd = '''
    Set ^TempTestInstance = ""
    Set tCmd = "Set ^TempTestInstance = ##class(ExecuteMCP.Test.SimpleTest).%New("""")"
    XECUTE tCmd
    Set tTest = ^TempTestInstance
    Write "XECUTE via global: ", $ISOBJECT(tTest), !
    Kill ^TempTestInstance
    '''
    result = call_iris_sync("execute_command", {
        "command": cmd,
        "namespace": "HSCUSTOM"
    })
    print(f"Result: {result}")
    
    # Test 4: XECUTE with local variable (testing scope)
    print("\n4. Testing XECUTE with local variable (scope test):")
    cmd = '''
    Set tTestInstance = ""
    Set tCmd = "Set tTestInstance = ##class(ExecuteMCP.Test.SimpleTest).%New("""")"
    XECUTE tCmd
    Write "XECUTE local var: ", $ISOBJECT(tTestInstance), !
    '''
    result = call_iris_sync("execute_command", {
        "command": cmd,
        "namespace": "HSCUSTOM"
    })
    print(f"Result: {result}")
    
    # Test 5: Using $XECUTE function
    print("\n5. Testing $XECUTE function:")
    cmd = '''
    Set tTestInstance = $XECUTE("##class(ExecuteMCP.Test.SimpleTest).%New("""")")
    Write "$XECUTE function: ", $ISOBJECT(tTestInstance), !
    '''
    result = call_iris_sync("execute_command", {
        "command": cmd,
        "namespace": "HSCUSTOM"
    })
    print(f"Result: {result}")

if __name__ == "__main__":
    test_instance_creation_methods()
