#!/usr/bin/env python3
"""
Test script for the new IRIS Execute MCP architecture.
Validates direct command execution without session management.
"""

import os
import json
import sys

# Test environment setup
TEST_ENV = {
    'IRIS_HOSTNAME': 'localhost',
    'IRIS_PORT': '1972',
    'IRIS_NAMESPACE': 'HSCUSTOM',
    'IRIS_USERNAME': '_SYSTEM',
    'IRIS_PASSWORD': '_SYSTEM'
}

# Set environment variables for testing
for key, value in TEST_ENV.items():
    os.environ[key] = value

try:
    import iris
    IRIS_AVAILABLE = True
    print("✅ intersystems-iris package available")
except ImportError:
    IRIS_AVAILABLE = False
    print("❌ intersystems-iris package not available")
    print("   Run: pip install intersystems-irispython")
    sys.exit(1)

def call_iris_sync(class_name: str, method_name: str, *args):
    """Test IRIS connectivity with new ExecuteMCP.Core.Command class"""
    try:
        print(f"📞 Calling {class_name}.{method_name}({', '.join(map(str, args))})")
        
        conn = iris.connect(
            TEST_ENV['IRIS_HOSTNAME'], 
            int(TEST_ENV['IRIS_PORT']), 
            TEST_ENV['IRIS_NAMESPACE'], 
            TEST_ENV['IRIS_USERNAME'], 
            TEST_ENV['IRIS_PASSWORD']
        )
        iris_obj = iris.createIRIS(conn)
        result = iris_obj.classMethodString(class_name, method_name, *args)
        conn.close()
        
        print(f"✅ IRIS call successful")
        return result
        
    except Exception as e:
        print(f"❌ IRIS call failed: {e}")
        return json.dumps({
            "status": "error",
            "errorMessage": str(e),
            "errorCode": "IRIS_CONNECTION_ERROR"
        })

def test_system_info():
    """Test GetSystemInfo method"""
    print("\n🔍 Testing GetSystemInfo...")
    result = call_iris_sync("ExecuteMCP.Core.Command", "GetSystemInfo")
    
    try:
        data = json.loads(result)
        if data.get('status') == 'success':
            print(f"✅ System Info Success:")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Namespace: {data.get('namespace', 'unknown')}")
            print(f"   Timestamp: {data.get('timestamp', 'unknown')}")
            return True
        else:
            print(f"❌ System Info Failed: {data.get('errorMessage', 'unknown error')}")
            return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print(f"Raw result: {result}")
        return False

def test_execute_command(command: str, namespace: str = "HSCUSTOM"):
    """Test ExecuteCommand method"""
    print(f"\n🚀 Testing ExecuteCommand: '{command}' in {namespace}")
    result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", command, namespace)
    
    try:
        data = json.loads(result)
        if data.get('status') == 'success':
            print(f"✅ Command Success:")
            print(f"   Command: {command}")
            print(f"   Namespace: {data.get('namespace', 'unknown')}")
            print(f"   Execution Time: {data.get('executionTimeMs', 0)}ms")
            print(f"   Output: {data.get('output', 'none')}")
            return True
        else:
            print(f"❌ Command Failed: {data.get('errorMessage', 'unknown error')}")
            return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print(f"Raw result: {result}")
        return False

def main():
    """Run comprehensive test suite"""
    print("🧪 IRIS Execute MCP Architecture Test")
    print("=====================================")
    
    print(f"📊 Test Configuration:")
    print(f"   IRIS: {TEST_ENV['IRIS_HOSTNAME']}:{TEST_ENV['IRIS_PORT']}")
    print(f"   Namespace: {TEST_ENV['IRIS_NAMESPACE']}")
    print(f"   User: {TEST_ENV['IRIS_USERNAME']}")
    
    # Test sequence
    tests = [
        ("System Info", lambda: test_system_info()),
        ("Hello World", lambda: test_execute_command("WRITE 'Hello World!'")),
        ("Simple Math", lambda: test_execute_command("WRITE 2+2")),
        ("Namespace Check", lambda: test_execute_command("WRITE $NAMESPACE")),
        ("Timestamp", lambda: test_execute_command("WRITE $ZDATETIME($HOROLOG,3)")),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
    
    print(f"\n📋 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! New architecture working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check IRIS connectivity and class compilation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
