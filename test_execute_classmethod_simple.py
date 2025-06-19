#!/usr/bin/env python3
"""
Simple test script for the execute_classmethod tool in IRIS Execute MCP Server.
Tests dynamic ObjectScript class method execution with known IRIS methods.
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

def test_execute_classmethod():
    """Test the ExecuteClassMethod functionality with simple examples"""
    print("\n=== Testing ExecuteMCP.Core.Command.ExecuteClassMethod ===")
    
    try:
        # Connect to IRIS
        conn = iris.connect(IRIS_HOSTNAME, IRIS_PORT, IRIS_NAMESPACE, IRIS_USERNAME, IRIS_PASSWORD)
        iris_obj = iris.createIRIS(conn)
        print(f"✅ Connected to IRIS at {IRIS_HOSTNAME}:{IRIS_PORT}/{IRIS_NAMESPACE}")
        
        # Test 1: Call a method that returns the current namespace
        print("\n📋 Test 1: %SYSTEM.Process.NameSpace() - Get current namespace")
        params_json = json.dumps([])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "%SYSTEM.Process",
            "NameSpace",
            params_json,
            IRIS_NAMESPACE
        )
        print(f"Response: {result}")
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Method result: {parsed.get('methodResult')}")
            print(f"✅ Execution time: {parsed.get('executionTimeMs')}ms")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Test 2: Call a method with parameters - $JUSTIFY
        print("\n📋 Test 2: %SYSTEM.SQL.TOCHAR with parameter")
        params_json = json.dumps([
            {"value": "12345", "isOutput": False}
        ])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "%SYSTEM.SQL",
            "TOCHAR",
            params_json,
            IRIS_NAMESPACE
        )
        print(f"Response: {result}")
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Method result: {parsed.get('methodResult')}")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Test 3: First create a test utility class
        print("\n📋 Test 3: Creating a test utility class")
        create_class_cmd = '''
        Class TestMCP.Utils Extends %RegisteredObject
        {
            ClassMethod Add(a As %Integer, b As %Integer) As %Integer
            {
                Quit a + b
            }
            
            ClassMethod Concat(s1 As %String, s2 As %String) As %String
            {
                Write "Concatenating: "_s1_" and "_s2,!
                Quit s1_s2
            }
            
            ClassMethod GetInfo(name As %String, Output info As %String) As %Status
            {
                Set info = "Info for: "_name_" at "_$ZDateTime($HOROLOG,3)
                Write "Getting info for: "_name,!
                Quit $$$OK
            }
        }
        '''
        # Save the class using %Dictionary.ClassDefinition
        save_class_cmd = '''
        Set cls = ##class(%Dictionary.ClassDefinition).%New("TestMCP.Utils")
        Set cls.Super = "%RegisteredObject"
        
        // Add Add method
        Set meth1 = ##class(%Dictionary.MethodDefinition).%New()
        Set meth1.parent = cls
        Set meth1.Name = "Add"
        Set meth1.ClassMethod = 1
        Set meth1.ReturnType = "%Integer"
        Set meth1.FormalSpec = "a:%Integer,b:%Integer"
        Do meth1.Implementation.WriteLine(" Quit a + b")
        
        // Add Concat method
        Set meth2 = ##class(%Dictionary.MethodDefinition).%New()
        Set meth2.parent = cls
        Set meth2.Name = "Concat"
        Set meth2.ClassMethod = 1
        Set meth2.ReturnType = "%String"
        Set meth2.FormalSpec = "s1:%String,s2:%String"
        Do meth2.Implementation.WriteLine(" Write ""Concatenating: ""_s1_"" and ""_s2,!")
        Do meth2.Implementation.WriteLine(" Quit s1_s2")
        
        // Add GetInfo method
        Set meth3 = ##class(%Dictionary.MethodDefinition).%New()
        Set meth3.parent = cls
        Set meth3.Name = "GetInfo"
        Set meth3.ClassMethod = 1
        Set meth3.ReturnType = "%Status"
        Set meth3.FormalSpec = "name:%String,&info:%String"
        Do meth3.Implementation.WriteLine(" Set info = ""Info for: ""_name_"" at ""_$ZDateTime($HOROLOG,3)")
        Do meth3.Implementation.WriteLine(" Write ""Getting info for: ""_name,!")
        Do meth3.Implementation.WriteLine(" Quit $$$OK")
        
        Do cls.%Save()
        Do $SYSTEM.OBJ.Compile("TestMCP.Utils", "ck")
        '''
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            save_class_cmd,
            IRIS_NAMESPACE
        )
        print("✅ Test class created and compiled")
        
        # Test 4: Call Add method with two parameters
        print("\n📋 Test 4: TestMCP.Utils.Add(5, 3)")
        params_json = json.dumps([
            {"value": "5", "isOutput": False},
            {"value": "3", "isOutput": False}
        ])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "TestMCP.Utils",
            "Add",
            params_json,
            IRIS_NAMESPACE
        )
        print(f"Response: {result}")
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Method result (5 + 3): {parsed.get('methodResult')}")
            print(f"✅ Execution time: {parsed.get('executionTimeMs')}ms")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Test 5: Call Concat method that writes output
        print("\n📋 Test 5: TestMCP.Utils.Concat('Hello', 'World')")
        params_json = json.dumps([
            {"value": "Hello", "isOutput": False},
            {"value": "World", "isOutput": False}
        ])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "TestMCP.Utils",
            "Concat",
            params_json,
            IRIS_NAMESPACE
        )
        print(f"Response: {result}")
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Method result: {parsed.get('methodResult')}")
            print(f"✅ Captured WRITE output: {parsed.get('capturedOutput')}")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Test 6: Call GetInfo method with output parameter
        print("\n📋 Test 6: TestMCP.Utils.GetInfo('TestUser', Output info)")
        params_json = json.dumps([
            {"value": "TestUser", "isOutput": False},
            {"value": "", "isOutput": True}  # Output parameter
        ])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "TestMCP.Utils",
            "GetInfo",
            params_json,
            IRIS_NAMESPACE
        )
        print(f"Response: {result}")
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Method result: {parsed.get('methodResult')}")
            print(f"✅ Output parameters: {parsed.get('outputParameters')}")
            print(f"✅ Captured WRITE output: {parsed.get('capturedOutput')}")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Clean up test class
        print("\n📋 Cleaning up test class")
        cleanup_cmd = 'Do $SYSTEM.OBJ.Delete("TestMCP.Utils", "d")'
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            cleanup_cmd,
            IRIS_NAMESPACE
        )
        print("✅ Test class cleaned up")
        
        # Close connection
        conn.close()
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== IRIS Execute MCP - ExecuteClassMethod Simple Test ===")
    print(f"Testing against IRIS at {IRIS_HOSTNAME}:{IRIS_PORT}")
    print(f"Namespace: {IRIS_NAMESPACE}")
    
    test_execute_classmethod()
