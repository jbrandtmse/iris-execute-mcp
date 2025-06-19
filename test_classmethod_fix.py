#!/usr/bin/env python3
"""
Test to fix and verify ExecuteClassMethod functionality.
"""

import os
import sys
import json

# Add the iris module path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import iris
    print("✅ IRIS module imported successfully")
except ImportError:
    print("❌ IRIS module not available - install intersystems-irispython")
    sys.exit(1)

# Test configuration
IRIS_HOSTNAME = os.getenv('IRIS_HOSTNAME', 'localhost')
IRIS_PORT = int(os.getenv('IRIS_PORT', '1972'))
IRIS_NAMESPACE = os.getenv('IRIS_NAMESPACE', 'HSCUSTOM')
IRIS_USERNAME = os.getenv('IRIS_USERNAME', '_SYSTEM')
IRIS_PASSWORD = os.getenv('IRIS_PASSWORD', '_SYSTEM')

def test_fix():
    """Test and fix ExecuteClassMethod"""
    print("\n=== Testing ExecuteClassMethod Fix ===")
    
    try:
        # Connect to IRIS
        conn = iris.connect(IRIS_HOSTNAME, IRIS_PORT, IRIS_NAMESPACE, IRIS_USERNAME, IRIS_PASSWORD)
        iris_obj = iris.createIRIS(conn)
        print(f"✅ Connected to IRIS at {IRIS_HOSTNAME}:{IRIS_PORT}/{IRIS_NAMESPACE}")
        
        # Test 1: First recompile the ExecuteMCP.Core.Command class
        print("\n📋 Test 1: Recompile ExecuteMCP.Core.Command")
        compile_cmd = 'Do $SYSTEM.OBJ.Compile("ExecuteMCP.Core.Command", "ck")'
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            compile_cmd,
            IRIS_NAMESPACE
        )
        parsed = json.loads(result)
        print(f"Compile result: {parsed.get('output', 'Compiled')}")
        
        # Test 2: Test direct $CLASSMETHOD with a method that doesn't write
        print("\n📋 Test 2: Test direct $CLASSMETHOD")
        test_cmd = 'Set tMethodResult = "" Set tMethodResult = $CLASSMETHOD("%SYSTEM.Version", "GetVersion") Write "Version: "_tMethodResult'
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            test_cmd,
            IRIS_NAMESPACE
        )
        parsed = json.loads(result)
        print(f"Direct output: {parsed.get('output')}")
        
        # Test 3: Create a simple test to verify ExecuteClassMethod
        print("\n📋 Test 3: Verify ExecuteClassMethod return value")
        # Call ExecuteClassMethod directly in IRIS and check result
        verify_cmd = '''Set json = ##class(ExecuteMCP.Core.Command).ExecuteClassMethod("%SYSTEM.Version", "GetVersion", "[]", "HSCUSTOM") Write json'''
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            verify_cmd,
            IRIS_NAMESPACE
        )
        parsed = json.loads(result)
        print(f"ExecuteClassMethod JSON output: {parsed.get('output')}")
        
        # Test 4: Parse the JSON to see what's in methodResult
        if parsed.get('output'):
            try:
                method_result = json.loads(parsed.get('output'))
                print(f"Parsed method result: {method_result.get('methodResult')}")
            except:
                pass
        
        # Test 5: Test through Python API
        print("\n📋 Test 5: Call ExecuteClassMethod through Python")
        params_json = json.dumps([])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "%SYSTEM.Version",
            "GetVersion",
            params_json,
            IRIS_NAMESPACE
        )
        parsed = json.loads(result)
        print(f"Full response: {json.dumps(parsed, indent=2)}")
        
        # Test 6: Create and test a simple class with clear output
        print("\n📋 Test 6: Create test class for clear verification")
        # Use simpler approach to create class
        create_steps = [
            'Kill ^||cls',
            'Set ^||cls(1) = "Class TestMCP.Demo"',
            'Set ^||cls(2) = "{"',
            'Set ^||cls(3) = "ClassMethod GetAnswer() As %Integer"',
            'Set ^||cls(4) = "{"',
            'Set ^||cls(5) = "    Quit 42"',
            'Set ^||cls(6) = "}"',
            'Set ^||cls(7) = ""',
            'Set ^||cls(8) = "ClassMethod SayHello(name As %String) As %String"',  
            'Set ^||cls(9) = "{"',
            'Set ^||cls(10) = "    Write ""Hello there, ""_name,!"',
            'Set ^||cls(11) = "    Quit ""Greeting sent to ""_name"',
            'Set ^||cls(12) = "}"',
            'Set ^||cls(13) = "}"'
        ]
        
        for step in create_steps:
            iris_obj.classMethodString(
                "ExecuteMCP.Core.Command", 
                "ExecuteCommand",
                step,
                IRIS_NAMESPACE
            )
        
        # Load the class
        load_cmd = 'Set stream = ##class(%Stream.TmpCharacter).%New() For i=1:1:13 { Do stream.WriteLine(^||cls(i)) } Do ##class(%Compiler.UDL.TextServices).SetTextFromStream("TestMCP.Demo", stream) Kill ^||cls'
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            load_cmd,
            IRIS_NAMESPACE
        )
        
        # Compile it
        compile_cmd = 'Set sc = $SYSTEM.OBJ.Compile("TestMCP.Demo", "ck") Write $SYSTEM.Status.GetErrorText(sc)'
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            compile_cmd,
            IRIS_NAMESPACE
        )
        print(f"Compile status: {json.loads(result).get('output')}")
        
        # Test 7: Call GetAnswer method
        print("\n📋 Test 7: Call TestMCP.Demo.GetAnswer()")
        params_json = json.dumps([])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "TestMCP.Demo",
            "GetAnswer",
            params_json,
            IRIS_NAMESPACE
        )
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Method result: {parsed.get('methodResult')}")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Test 8: Call SayHello with parameter
        print("\n📋 Test 8: Call TestMCP.Demo.SayHello('World')")
        params_json = json.dumps([
            {"value": "World", "isOutput": False}
        ])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "TestMCP.Demo",
            "SayHello",
            params_json,
            IRIS_NAMESPACE
        )
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Method result: {parsed.get('methodResult')}")
            print(f"✅ Captured output: {parsed.get('capturedOutput')}")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Clean up
        print("\n📋 Cleaning up")
        cleanup_cmd = 'Do $SYSTEM.OBJ.Delete("TestMCP.Demo", "d")'
        iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            cleanup_cmd,
            IRIS_NAMESPACE
        )
        print("✅ Cleanup completed")
        
        # Close connection
        conn.close()
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== IRIS Execute MCP - ExecuteClassMethod Fix Test ===")
    print(f"Testing against IRIS at {IRIS_HOSTNAME}:{IRIS_PORT}")
    print(f"Namespace: {IRIS_NAMESPACE}")
    
    test_fix()
