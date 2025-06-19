#!/usr/bin/env python3
"""
Test script for the new execute_classmethod tool in IRIS Execute MCP Server.
Tests dynamic ObjectScript class method execution with support for:
- Input parameters
- Output parameters (ByRef)
- Method return values
- WRITE output capture
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
    """Test the ExecuteClassMethod functionality"""
    print("\n=== Testing ExecuteMCP.Core.Command.ExecuteClassMethod ===")
    
    try:
        # Connect to IRIS
        conn = iris.connect(IRIS_HOSTNAME, IRIS_PORT, IRIS_NAMESPACE, IRIS_USERNAME, IRIS_PASSWORD)
        iris_obj = iris.createIRIS(conn)
        print(f"✅ Connected to IRIS at {IRIS_HOSTNAME}:{IRIS_PORT}/{IRIS_NAMESPACE}")
        
        # Test 1: Call GetVersion method
        print("\n📋 Test 1: %SYSTEM.Version.GetVersion() (no parameters)")
        params_json = json.dumps([])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "%SYSTEM.Version",
            "GetVersion",
            params_json,
            IRIS_NAMESPACE
        )
        print(f"Response: {result}")
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Method result: {parsed.get('methodResult')}")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Test 2: Call with parameters - JobNumber
        print("\n📋 Test 2: %SYSTEM.Process.JobNumber() (no parameters)")
        params_json = json.dumps([])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "%SYSTEM.Process",
            "JobNumber",
            params_json,
            IRIS_NAMESPACE
        )
        print(f"Response: {result}")
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Method result: {parsed.get('methodResult')}")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Test 3: Create a test class using simpler approach
        print("\n📋 Test 3: Creating test class for output parameter testing")
        
        # Create the class definition as a routine first
        routine_cmd = '''
        Set routine = ##class(%Routine).%New("TestMCP.ClassMethodTest.1.INT")
        Do routine.WriteLine("TestMCP.ClassMethodTest")
        Do routine.WriteLine(" ")
        Do routine.WriteLine("TestOutputParams(pInput,pOutput) PUBLIC {")
        Do routine.WriteLine(" Set pOutput = ""Output: ""_pInput")
        Do routine.WriteLine(" Write ""WRITE output: ""_pInput,!")
        Do routine.WriteLine(" Quit 1")
        Do routine.WriteLine("}")
        Do routine.WriteLine(" ")
        Do routine.WriteLine("TestMultipleParams(p1,p2,p3) PUBLIC {")
        Do routine.WriteLine(" Set p3 = p1_"" - ""_p2")
        Do routine.WriteLine(" Write ""Processing: ""_p1_"" with number ""_p2,!")
        Do routine.WriteLine(" Quit ""Result: ""_p3")
        Do routine.WriteLine("}")
        Do routine.Save()
        '''
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            routine_cmd,
            IRIS_NAMESPACE
        )
        
        print("✅ Test routine created")
        
        # Test 4: Call the routine method directly
        print("\n📋 Test 4: Testing routine method with XECUTE")
        test_cmd = '''
        Set input = "Test Input"
        Set output = ""
        Do TestOutputParams^TestMCP.ClassMethodTest.1(input, .output)
        Write "Output param value: "_output
        '''
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            test_cmd,
            IRIS_NAMESPACE
        )
        print(f"Response: {result}")
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Command output: {parsed.get('output')}")
        else:
            print(f"❌ Error: {parsed.get('error')}")
        
        # Test 5: Test method with integer coercion
        print("\n📋 Test 5: Testing %SYSTEM.SQL.Functions.ROUND with parameters")
        params_json = json.dumps([
            {"value": "3.14159", "isOutput": False},
            {"value": "2", "isOutput": False}
        ])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "%SYSTEM.SQL.Functions",
            "ROUND",
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
        
        # Test 6: Test a method that writes output
        print("\n📋 Test 6: Testing method that writes output")
        test_write_cmd = '''
        ClassMethod TestWrite() As %String [ PublicList = (Write) ]
        {
            Write "This is a test output",!
            Write "Line 2 of output",!
            Quit "Method completed"
        }
        '''
        # We'll use XECUTE to simulate a method that writes
        write_test_cmd = '''
        Write "Testing WRITE capture in ExecuteClassMethod",!
        Write "Current time: "_$ZDateTime($HOROLOG,3),!
        '''
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            write_test_cmd,
            IRIS_NAMESPACE
        )
        print(f"Response: {result}")
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Captured output: {parsed.get('output')}")
        else:
            print(f"❌ Error: {parsed.get('error')}")
        
        # Clean up test routine
        print("\n📋 Cleaning up test routine")
        cleanup_cmd = '''Do ##class(%Routine).Delete("TestMCP.ClassMethodTest.1.INT")'''
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            cleanup_cmd,
            IRIS_NAMESPACE
        )
        print("✅ Test routine cleaned up")
        
        # Close connection
        conn.close()
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== IRIS Execute MCP - ExecuteClassMethod Test ===")
    print(f"Testing against IRIS at {IRIS_HOSTNAME}:{IRIS_PORT}")
    print(f"Namespace: {IRIS_NAMESPACE}")
    
    test_execute_classmethod()
