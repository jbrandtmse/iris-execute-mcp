#!/usr/bin/env python3
"""
Test IRIS global manipulation methods in ExecuteMCP.Core.Command
"""

import json
import sys
import os

try:
    import iris
    print("✅ IRIS package available")
except ImportError:
    print("❌ IRIS package not available")
    sys.exit(1)

def call_iris_method(class_name, method_name, *args):
    """Test helper to call IRIS class methods"""
    try:
        # IRIS connection parameters
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
        return json.dumps({"status": "error", "error": str(e)})

def test_globals():
    """Test global manipulation methods"""
    print("🧪 Testing IRIS Global Manipulation Methods")
    print("=" * 60)
    
    # Test 1: Set a simple global
    print("\n📝 Test 1: Set ^MCPTestGlobal")
    set_result = call_iris_method("ExecuteMCP.Core.Command", "SetGlobal", "^MCPTestGlobal", "Hello MCP World!")
    try:
        set_parsed = json.loads(set_result)
        if set_parsed.get("status") == "success":
            print("✅ Set global successful")
            print(f"   Global: {set_parsed.get('globalRef')}")
            print(f"   Value Set: {set_parsed.get('setValue')}")
            print(f"   Verified: {set_parsed.get('verifyValue')}")
        else:
            print(f"❌ Set failed: {set_parsed.get('errorMessage')}")
            return False
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON response: {set_result}")
        return False
    
    # Test 2: Get the global we just set
    print("\n📖 Test 2: Get ^MCPTestGlobal")
    get_result = call_iris_method("ExecuteMCP.Core.Command", "GetGlobal", "^MCPTestGlobal")
    try:
        get_parsed = json.loads(get_result)
        if get_parsed.get("status") == "success":
            print("✅ Get global successful")
            print(f"   Global: {get_parsed.get('globalRef')}")
            print(f"   Value: {get_parsed.get('value')}")
            print(f"   Exists: {get_parsed.get('exists')}")
        else:
            print(f"❌ Get failed: {get_parsed.get('errorMessage')}")
            return False
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON response: {get_result}")
        return False
    
    # Test 3: Set global with subscripts (numeric)
    print("\n📝 Test 3: Set ^MCPTestGlobal(1,2)")
    set_result2 = call_iris_method("ExecuteMCP.Core.Command", "SetGlobal", "^MCPTestGlobal(1,2)", "Numeric subscripts")
    try:
        set_parsed2 = json.loads(set_result2)
        if set_parsed2.get("status") == "success":
            print("✅ Set global with numeric subscripts successful")
            print(f"   Global: {set_parsed2.get('globalRef')}")
            print(f"   Value: {set_parsed2.get('setValue')}")
        else:
            print(f"❌ Set failed: {set_parsed2.get('errorMessage')}")
            return False
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON response: {set_result2}")
        return False
    
    # Test 4: Get global with subscripts (numeric)
    print("\n📖 Test 4: Get ^MCPTestGlobal(1,2)")
    get_result2 = call_iris_method("ExecuteMCP.Core.Command", "GetGlobal", "^MCPTestGlobal(1,2)")
    try:
        get_parsed2 = json.loads(get_result2)
        if get_parsed2.get("status") == "success":
            print("✅ Get global with numeric subscripts successful")
            print(f"   Value: {get_parsed2.get('value')}")
        else:
            print(f"❌ Get failed: {get_parsed2.get('errorMessage')}")
            return False
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON response: {get_result2}")
        return False
    
    # Test 5: Set global with string subscripts
    print('\n📝 Test 5: Set ^MCPTestGlobal("This","That")')
    set_result3 = call_iris_method("ExecuteMCP.Core.Command", "SetGlobal", '^MCPTestGlobal("This","That")', "String subscripts")
    try:
        set_parsed3 = json.loads(set_result3)
        if set_parsed3.get("status") == "success":
            print("✅ Set global with string subscripts successful")
            print(f"   Global: {set_parsed3.get('globalRef')}")
            print(f"   Value: {set_parsed3.get('setValue')}")
        else:
            print(f"❌ Set failed: {set_parsed3.get('errorMessage')}")
            return False
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON response: {set_result3}")
        return False
    
    # Test 6: Get global with string subscripts
    print('\n📖 Test 6: Get ^MCPTestGlobal("This","That")')
    get_result3 = call_iris_method("ExecuteMCP.Core.Command", "GetGlobal", '^MCPTestGlobal("This","That")')
    try:
        get_parsed3 = json.loads(get_result3)
        if get_parsed3.get("status") == "success":
            print("✅ Get global with string subscripts successful")
            print(f"   Value: {get_parsed3.get('value')}")
        else:
            print(f"❌ Get failed: {get_parsed3.get('errorMessage')}")
            return False
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON response: {get_result3}")
        return False
    
    # Test 7: Try to get non-existent global
    print("\n📖 Test 7: Get ^NonExistentGlobal")
    get_result4 = call_iris_method("ExecuteMCP.Core.Command", "GetGlobal", "^NonExistentGlobal")
    try:
        get_parsed4 = json.loads(get_result4)
        if get_parsed4.get("status") == "success":
            print("✅ Get non-existent global successful")
            print(f"   Value: '{get_parsed4.get('value')}'")
            print(f"   Exists: {get_parsed4.get('exists')}")
        else:
            print(f"❌ Get failed: {get_parsed4.get('errorMessage')}")
            return False
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON response: {get_result4}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL GLOBAL TESTS PASSED!")
    return True

if __name__ == "__main__":
    success = test_globals()
    if not success:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("✅ ALL TESTS SUCCESSFUL")
