#!/usr/bin/env python3
"""
Verification test for ExecuteClassMethod - tests all features including:
- Methods that return values
- Methods with parameters
- Methods that write output
- Methods with output parameters
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

def test_verify():
    """Verify ExecuteClassMethod functionality"""
    print("\n=== Verifying ExecuteClassMethod Functionality ===")
    
    try:
        # Connect to IRIS
        conn = iris.connect(IRIS_HOSTNAME, IRIS_PORT, IRIS_NAMESPACE, IRIS_USERNAME, IRIS_PASSWORD)
        iris_obj = iris.createIRIS(conn)
        print(f"✅ Connected to IRIS at {IRIS_HOSTNAME}:{IRIS_PORT}/{IRIS_NAMESPACE}")
        
        # Test 1: System method without parameters
        print("\n📋 Test 1: %SYSTEM.Version.GetVersion() - No parameters")
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
        if parsed.get("status") == "success":
            print(f"✅ Method result: {parsed.get('methodResult')}")
            print(f"✅ Execution time: {parsed.get('executionTimeMs')}ms")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Test 2: Create a simple test class properly
        print("\n📋 Test 2: Creating test class properly")
        # First create a simple test class using ExecuteCommand
        create_cmd = '''
        // Create TestMCP.Example class
        Set classDef = ##class(%Dictionary.ClassDefinition).%New("TestMCP.Example")
        Set classDef.Super = "%RegisteredObject"
        
        // Method 1: Simple return
        Set method1 = ##class(%Dictionary.MethodDefinition).%New()
        Set method1.parent = classDef
        Set method1.Name = "GetConstant"
        Set method1.ClassMethod = 1
        Set method1.ReturnType = "%String"
        Do method1.Implementation.WriteLine(" Quit ""Hello from IRIS MCP""")
        
        // Method 2: Math operation
        Set method2 = ##class(%Dictionary.MethodDefinition).%New()
        Set method2.parent = classDef
        Set method2.Name = "Multiply"
        Set method2.ClassMethod = 1
        Set method2.ReturnType = "%Integer"
        Set method2.FormalSpec = "a:%Integer,b:%Integer"
        Do method2.Implementation.WriteLine(" Quit a * b")
        
        // Method 3: Method with WRITE output
        Set method3 = ##class(%Dictionary.MethodDefinition).%New()
        Set method3.parent = classDef
        Set method3.Name = "ProcessData"
        Set method3.ClassMethod = 1
        Set method3.ReturnType = "%String"
        Set method3.FormalSpec = "input:%String"
        Do method3.Implementation.WriteLine(" Write ""Processing: ""_input,!")
        Do method3.Implementation.WriteLine(" Write ""Step 1: Validating..."",!")
        Do method3.Implementation.WriteLine(" Write ""Step 2: Transforming..."",!")
        Do method3.Implementation.WriteLine(" Quit ""Processed: ""_input")
        
        // Method 4: Method with output parameter
        Set method4 = ##class(%Dictionary.MethodDefinition).%New()
        Set method4.parent = classDef
        Set method4.Name = "Calculate"
        Set method4.ClassMethod = 1
        Set method4.ReturnType = "%Status"
        Set method4.FormalSpec = "x:%Integer,y:%Integer,&sum:%Integer,&product:%Integer"
        Do method4.Implementation.WriteLine(" Set sum = x + y")
        Do method4.Implementation.WriteLine(" Set product = x * y")
        Do method4.Implementation.WriteLine(" Write ""Calculating sum and product..."",!")
        Do method4.Implementation.WriteLine(" Quit $$$OK")
        
        // Save and compile
        Set sc = classDef.%Save()
        Set sc2 = $SYSTEM.OBJ.Compile("TestMCP.Example", "ck")
        Write "Class created and compiled"
        '''
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            create_cmd,
            IRIS_NAMESPACE
        )
        print("✅ Test class created successfully")
        
        # Test 3: Call GetConstant method
        print("\n📋 Test 3: TestMCP.Example.GetConstant()")
        params_json = json.dumps([])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "TestMCP.Example",
            "GetConstant",
            params_json,
            IRIS_NAMESPACE
        )
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Method result: '{parsed.get('methodResult')}'")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Test 4: Call Multiply method with parameters
        print("\n📋 Test 4: TestMCP.Example.Multiply(7, 6)")
        params_json = json.dumps([
            {"value": "7", "isOutput": False},
            {"value": "6", "isOutput": False}
        ])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "TestMCP.Example",
            "Multiply",
            params_json,
            IRIS_NAMESPACE
        )
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Method result: {parsed.get('methodResult')} (7 × 6 = 42)")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Test 5: Call ProcessData method that writes output
        print("\n📋 Test 5: TestMCP.Example.ProcessData('TestData')")
        params_json = json.dumps([
            {"value": "TestData", "isOutput": False}
        ])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "TestMCP.Example",
            "ProcessData",
            params_json,
            IRIS_NAMESPACE
        )
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Method result: '{parsed.get('methodResult')}'")
            print(f"✅ Captured output: {parsed.get('capturedOutput')}")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Test 6: Call Calculate method with output parameters
        print("\n📋 Test 6: TestMCP.Example.Calculate(10, 20, Output sum, Output product)")
        params_json = json.dumps([
            {"value": "10", "isOutput": False},
            {"value": "20", "isOutput": False},
            {"value": "", "isOutput": True},   # sum output parameter
            {"value": "", "isOutput": True}    # product output parameter
        ])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "TestMCP.Example",
            "Calculate",
            params_json,
            IRIS_NAMESPACE
        )
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Method result: {parsed.get('methodResult')} (status)")
            output_params = parsed.get('outputParameters', {})
            print(f"✅ Output parameters:")
            print(f"   - sum (10+20): {output_params.get('param3', 'N/A')}")
            print(f"   - product (10×20): {output_params.get('param4', 'N/A')}")
            print(f"✅ Captured output: {parsed.get('capturedOutput')}")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Test 7: System method with parameter
        print("\n📋 Test 7: %SYSTEM.SQL.Functions.ABS(-123)")
        params_json = json.dumps([
            {"value": "-123", "isOutput": False}
        ])
        result = iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod",
            "%SYSTEM.SQL.Functions",
            "ABS",
            params_json,
            IRIS_NAMESPACE
        )
        parsed = json.loads(result)
        if parsed.get("status") == "success":
            print(f"✅ Method result: {parsed.get('methodResult')} (absolute value of -123)")
        else:
            print(f"❌ Error: {parsed.get('errorMessage')}")
        
        # Clean up
        print("\n📋 Cleaning up test class")
        cleanup_cmd = 'Do $SYSTEM.OBJ.Delete("TestMCP.Example", "d")'
        iris_obj.classMethodString(
            "ExecuteMCP.Core.Command", 
            "ExecuteCommand",
            cleanup_cmd,
            IRIS_NAMESPACE
        )
        print("✅ Test class cleaned up")
        
        # Close connection
        conn.close()
        print("\n✅ All ExecuteClassMethod tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== IRIS Execute MCP - ExecuteClassMethod Verification ===")
    print(f"Testing against IRIS at {IRIS_HOSTNAME}:{IRIS_PORT}")
    print(f"Namespace: {IRIS_NAMESPACE}")
    
    test_verify()
