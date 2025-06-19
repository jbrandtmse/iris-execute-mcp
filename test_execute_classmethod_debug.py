#!/usr/bin/env python3
"""
Debug test script for ExecuteClassMethod to understand what's happening.
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

def test_debug():
    """Debug the ExecuteClassMethod functionality"""
    print("\n=== Debug ExecuteMCP.Core.Command.ExecuteClassMethod ===")
    
    try:
        # Connect to IRIS
        conn = iris.connect(IRIS_HOSTNAME, IRIS_PORT, IRIS_NAMESPACE, IRIS_USERNAME, IRIS_PASSWORD)
        iris_obj = iris.createIRIS(conn)
        print(f"✅ Connected to IRIS at {IRIS_HOSTNAME}:{IRIS_PORT}/{IRIS_NAMESPACE}")
        
        # Test 1: Check if ExecuteClassMethod exists
        print("\n📋 Test 1: Verify ExecuteClassMethod exists")
        check_method = '''Write $SYSTEM.OBJ.IsUpToDate("ExecuteMCP.Core.Command")'''
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            check_method,
            IRIS_NAMESPACE
        )
        print(f"Class check: {result}")
        
        # Test 2: Direct test of %SYSTEM.Version.GetVersion() 
        print("\n📋 Test 2: Direct call to %SYSTEM.Version.GetVersion()")
        direct_cmd = '''Write ##class(%SYSTEM.Version).GetVersion()'''
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            direct_cmd,
            IRIS_NAMESPACE
        )
        parsed = json.loads(result)
        print(f"Direct call output: {parsed.get('output')}")
        
        # Test 3: Debug the ExecuteClassMethod call
        print("\n📋 Test 3: Debug ExecuteClassMethod internals")
        debug_cmd = '''
        Set ^MCPDebug = ""
        Set tResult = ##class(ExecuteMCP.Core.Command).ExecuteClassMethod("%SYSTEM.Version", "GetVersion", "[]", "HSCUSTOM")
        Write "Result: "_tResult,!
        Write "Debug log: "_^MCPDebug
        '''
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            debug_cmd,
            IRIS_NAMESPACE
        )
        parsed = json.loads(result)
        print(f"Debug output:\n{parsed.get('output')}")
        
        # Test 4: Check $CLASSMETHOD behavior
        print("\n📋 Test 4: Test $CLASSMETHOD directly")
        classmethod_cmd = '''
        Set tResult = $CLASSMETHOD("%SYSTEM.Version", "GetVersion")
        Write "Result from $CLASSMETHOD: "_tResult
        '''
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            classmethod_cmd,
            IRIS_NAMESPACE
        )
        parsed = json.loads(result)
        print(f"$CLASSMETHOD output: {parsed.get('output')}")
        
        # Test 5: Test method with parameters
        print("\n📋 Test 5: Test with simple math function")
        math_cmd = '''
        Set tResult = $CLASSMETHOD("%SYSTEM.SQL.Functions", "ABS", -42)
        Write "ABS(-42) = "_tResult
        '''
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            math_cmd,
            IRIS_NAMESPACE
        )
        parsed = json.loads(result)
        print(f"Math function output: {parsed.get('output')}")
        
        # Test 6: Create a simple test class properly
        print("\n📋 Test 6: Create simple test class using $SYSTEM.OBJ.Load")
        create_simple_class = '''
        Set stream = ##class(%Stream.TmpCharacter).%New()
        Do stream.WriteLine("Class TestMCP.Simple Extends %RegisteredObject")
        Do stream.WriteLine("{")
        Do stream.WriteLine("ClassMethod GetConstant() As %String")
        Do stream.WriteLine("{")
        Do stream.WriteLine("    Quit ""Hello from TestMCP""")
        Do stream.WriteLine("}")
        Do stream.WriteLine("ClassMethod Add(a As %Integer, b As %Integer) As %Integer")
        Do stream.WriteLine("{")
        Do stream.WriteLine("    Quit a + b")
        Do stream.WriteLine("}")
        Do stream.WriteLine("}")
        Do ##class(%Compiler.UDL.TextServices).SetTextFromStream("TestMCP.Simple", stream)
        Set sc = $SYSTEM.OBJ.Compile("TestMCP.Simple", "ck")
        Write "Compile status: "_$SYSTEM.Status.GetErrorText(sc)
        '''
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            create_simple_class,
            IRIS_NAMESPACE
        )
        parsed = json.loads(result)
        print(f"Class creation output: {parsed.get('output')}")
        
        # Test 7: Call the new class method via ExecuteClassMethod
        print("\n📋 Test 7: Call TestMCP.Simple.GetConstant() via ExecuteClassMethod")
        params_json = json.dumps([])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "TestMCP.Simple",
            "GetConstant",
            params_json,
            IRIS_NAMESPACE
        )
        print(f"Response: {result}")
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Method result: '{parsed.get('methodResult')}'")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Test 8: Call Add method with parameters
        print("\n📋 Test 8: Call TestMCP.Simple.Add(10, 32) via ExecuteClassMethod")
        params_json = json.dumps([
            {"value": "10", "isOutput": False},
            {"value": "32", "isOutput": False}
        ])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "TestMCP.Simple",
            "Add",
            params_json,
            IRIS_NAMESPACE
        )
        print(f"Response: {result}")
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Method result: '{parsed.get('methodResult')}'")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Clean up
        print("\n📋 Cleaning up")
        cleanup_cmd = 'Do $SYSTEM.OBJ.Delete("TestMCP.Simple", "d")'
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            cleanup_cmd,
            IRIS_NAMESPACE
        )
        print("✅ Cleanup completed")
        
        # Close connection
        conn.close()
        print("\n✅ Debug tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== IRIS Execute MCP - ExecuteClassMethod Debug ===")
    print(f"Testing against IRIS at {IRIS_HOSTNAME}:{IRIS_PORT}")
    print(f"Namespace: {IRIS_NAMESPACE}")
    
    test_debug()
