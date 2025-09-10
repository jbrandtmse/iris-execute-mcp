#!/usr/bin/env python3
"""
Debug TestRunner execution to understand why tests aren't running properly
"""

import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# IRIS connection settings
hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
port = int(os.getenv('IRIS_PORT', '1972'))
namespace = os.getenv('IRIS_NAMESPACE', 'HSCUSTOM')
username = os.getenv('IRIS_USERNAME', '_SYSTEM')
password = os.getenv('IRIS_PASSWORD', 'SYS')

print("=" * 80)
print("TestRunner Execution Debugging")
print("=" * 80)

try:
    # Import IRIS module
    import iris
    
    # Connect to IRIS using _SYSTEM credentials
    conn = iris.connect(hostname, port, namespace, username, password)
    irispy = iris.createIRIS(conn)
    
    # Helper function for synchronous IRIS calls
    def call_iris_sync(method, *args):
        """Execute IRIS method synchronously"""
        try:
            result = method(*args)
            if result is None:
                return ""
            return result
        except Exception as e:
            print(f"   Error: {e}")
            return None
    
    # Step 1: Test Discovery directly
    print("\n1. Testing Discovery.BuildTestManifest('ExecuteMCP.Test')...")
    manifest_json = call_iris_sync(
        irispy.classMethodString,
        "ExecuteMCP.TestRunner.Discovery",
        "BuildTestManifest",
        "ExecuteMCP.Test"
    )
    
    if manifest_json:
        try:
            manifest = json.loads(manifest_json)
            print(f"   Discovery found {len(manifest.get('classes', []))} classes")
            for cls in manifest.get('classes', []):
                print(f"     - {cls.get('className')}: {len(cls.get('methods', []))} methods")
        except:
            print(f"   Raw manifest: {manifest_json[:200]}...")
    else:
        print("   Discovery returned empty/null")
    
    # Step 2: Run a specific test and capture raw output
    print("\n2. Running ExecuteMCP.Test.SimpleTest with raw output...")
    raw_result = call_iris_sync(
        irispy.classMethodString,
        "ExecuteMCP.TestRunner.Manager",
        "RunTests",
        "ExecuteMCP.Test.SimpleTest"
    )
    
    print(f"   Raw result type: {type(raw_result)}")
    print(f"   Raw result: {raw_result}")
    
    # Try to parse if it's JSON
    if raw_result:
        try:
            result_obj = json.loads(raw_result)
            print("\n   Parsed JSON structure:")
            for key, value in result_obj.items():
                print(f"     {key}: {value}")
        except Exception as e:
            print(f"   Could not parse as JSON: {e}")
    
    # Step 3: Test the Manager's ExecuteTestManifest through a debug method
    print("\n3. Creating a debug method to test ExecuteTestManifest...")
    debug_code = """Class ExecuteMCP.TestRunner.Debug
{
ClassMethod TestExecute() As %String
{
    Try {
        ; Create manager and context
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set tManager.Context = ##class(ExecuteMCP.TestRunner.Context).%New()
        Set tManager.Context.StartTime = $ZTIMESTAMP
        
        ; Get manifest
        Set tManifestJSON = ##class(ExecuteMCP.TestRunner.Discovery).BuildTestManifest("ExecuteMCP.Test")
        If tManifestJSON = "" {
            Return "{\\"error\\":\\"No manifest returned\\"}"
        }
        
        ; Parse manifest
        Set tManifest = {}.%FromJSON(tManifestJSON)
        
        ; Execute tests
        Set tStatus = tManager.ExecuteTestManifest(tManifest, "ExecuteMCP.Test.SimpleTest")
        
        If $$$ISERR(tStatus) {
            Return "{\\"error\\":\\""_$SYSTEM.Status.GetErrorText(tStatus)_"\\"}"
        }
        
        ; Get results
        Set tManager.Context.EndTime = $ZTIMESTAMP
        Set tResults = tManager.Context.GetResults()
        
        Return tResults
    }
    Catch ex {
        Return "{\\"error\\":\\""_ex.DisplayString()_"\\"}"
    }
}
}
"""
    
    # Write debug class to file
    with open("src/ExecuteMCP/TestRunner/Debug.cls", "w") as f:
        f.write(debug_code)
    
    print("   Debug class created at src/ExecuteMCP/TestRunner/Debug.cls")
    print("   Compiling debug class...")
    
    # Compile the debug class
    compile_result = call_iris_sync(
        irispy.classMethodValue,
        "$SYSTEM.OBJ",
        "Compile",
        "ExecuteMCP.TestRunner.Debug.cls",
        "bckry"
    )
    print(f"   Compilation result: {compile_result}")
    
    # Execute debug method
    print("\n4. Executing Debug.TestExecute()...")
    debug_result = call_iris_sync(
        irispy.classMethodString,
        "ExecuteMCP.TestRunner.Debug",
        "TestExecute"
    )
    
    print(f"   Debug result: {debug_result}")
    
    if debug_result:
        try:
            debug_obj = json.loads(debug_result)
            print("\n   Debug result structure:")
            for key, value in debug_obj.items():
                if key == "classes" and isinstance(value, list):
                    print(f"     {key}: {len(value)} classes")
                    for cls in value:
                        print(f"       - {cls.get('name')}: {cls.get('status')}")
                else:
                    print(f"     {key}: {value}")
        except Exception as e:
            print(f"   Could not parse debug result: {e}")
    
    # Step 4: Check Context.GetResults() directly using a simpler test
    print("\n5. Testing Context.GetResults() with ExecuteMCP.Core.Command...")
    
    # Create a simple test command that creates context and tests it
    context_cmd = """Set tContext = ##class(ExecuteMCP.TestRunner.Context).%New() Set tContext.StartTime = $ZTIMESTAMP Do tContext.StartClass("TestClass") Do tContext.StartMethod("TestMethod") Do tContext.AddAssertion(1, "Test assertion", "This should pass") Do tContext.EndMethod($$$OK) Do tContext.EndClass() Set tContext.EndTime = $ZTIMESTAMP WRITE tContext.GetResults()"""
    
    context_result = call_iris_sync(
        irispy.classMethodString,
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        context_cmd
    )
    
    print(f"   Context test result: {context_result}")
    
    # Step 5: Test actual test class exists and can be instantiated
    print("\n6. Testing if ExecuteMCP.Test.SimpleTest can be instantiated...")
    
    test_instance_cmd = """Set tTest = ##class(ExecuteMCP.Test.SimpleTest).%New() If $ISOBJECT(tTest) { WRITE "Instance created successfully" } Else { WRITE "Failed to create instance" }"""
    
    instance_result = call_iris_sync(
        irispy.classMethodString,
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        test_instance_cmd
    )
    
    print(f"   Instance test result: {instance_result}")
    
    # Step 6: Check test method exists
    print("\n7. Checking if test methods exist on SimpleTest...")
    
    method_check_cmd = """Set tTest = ##class(ExecuteMCP.Test.SimpleTest).%New() Try { Do tTest.TestAddition() WRITE "TestAddition exists and executed" } Catch { WRITE "TestAddition failed: "_$ZERROR }"""
    
    method_result = call_iris_sync(
        irispy.classMethodString,
        "ExecuteMCP.Core.Command",  
        "ExecuteCommand",
        method_check_cmd
    )
    
    print(f"   Method test result: {method_result}")

except ImportError as e:
    print(f"Error: Could not import iris module - {e}")
    print("Make sure intersystems-irispython is installed:")
    print("  pip install intersystems-irispython")
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Clean up connection
    if 'conn' in locals():
        conn.close()

print("\n" + "=" * 80)
print("TestRunner Execution Debugging Complete")
print("=" * 80)
