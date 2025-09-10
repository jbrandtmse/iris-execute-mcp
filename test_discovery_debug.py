#!/usr/bin/env python3
"""
Debug the Discovery.IsTestClass method to understand why it's not finding test classes
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import the direct IRIS connection functions
from iris_execute_mcp import call_iris_sync

def test_is_test_class():
    """Test the IsTestClass method directly"""
    print("=" * 80)
    print("TESTING Discovery.IsTestClass METHOD")
    print("=" * 80)
    
    test_classes = [
        "ExecuteMCP.Test.SampleUnitTest",
        "ExecuteMCP.Test.SimpleTest",
        "ExecuteMCP.Test.ErrorTest"
    ]
    
    for class_name in test_classes:
        print(f"\nTesting: {class_name}")
        
        # Test IsTestClass method using execute_classmethod
        parameters_json = json.dumps([{"value": class_name}])
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteClassMethod",
            "ExecuteMCP.TestRunner.Discovery",
            "IsTestClass",
            parameters_json,
            "HSCUSTOM"
        )
        
        print(f"  IsTestClass result: {result}")
        
        # Also check the Super property directly
        cmd = f'Set tClassDef = ##class(%Dictionary.CompiledClass).%OpenId("{class_name}") If $ISOBJECT(tClassDef) {{ Write "Super: ",tClassDef.Super }} Else {{ Write "Class not found" }}'
        super_result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            cmd,
            "HSCUSTOM"
        )
        
        if super_result:
            super_data = json.loads(super_result)
            print(f"  Super property: {super_data.get('output', 'N/A')}")

def test_discover_test_classes():
    """Test DiscoverTestClasses method"""
    print("\n" + "=" * 80)
    print("TESTING Discovery.DiscoverTestClasses")
    print("=" * 80)
    
    parameters_json = json.dumps([{"value": "ExecuteMCP.Test"}])
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteClassMethod",
        "ExecuteMCP.TestRunner.Discovery",
        "DiscoverTestClasses",
        parameters_json,
        "HSCUSTOM"
    )
    
    print(f"DiscoverTestClasses result: {result}")
    
    # Parse the result to see what we got
    try:
        result_data = json.loads(result)
        if result_data.get("status") == "success" and "result" in result_data:
            # The result should be a JSON array
            test_classes = json.loads(result_data["result"])
            print(f"Found {len(test_classes)} test classes:")
            for cls in test_classes:
                print(f"  - {cls}")
    except Exception as e:
        print(f"Error parsing result: {e}")

def test_sql_query_directly():
    """Test the SQL query used in DiscoverTestClasses"""
    print("\n" + "=" * 80)
    print("TESTING SQL QUERY DIRECTLY")
    print("=" * 80)
    
    # Test the SQL query that finds classes in the package
    cmd = '''
    Set tSQL = "SELECT Name FROM %Dictionary.CompiledClassDefinition WHERE Name %STARTSWITH ?"
    Set tStatement = ##class(%SQL.Statement).%New()
    Set tSC = tStatement.%Prepare(tSQL)
    If $$$ISERR(tSC) {
        Write "SQL Prepare failed"
    } Else {
        Set tResultSet = tStatement.%Execute("ExecuteMCP.Test.")
        Set count = 0
        While tResultSet.%Next() {
            Set count = count + 1
            Write "Class: ",tResultSet.%Get("Name"),!
        }
        Write "Total classes found: ",count
    }
    '''
    
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        cmd,
        "HSCUSTOM"
    )
    
    if result:
        result_data = json.loads(result)
        print(result_data.get("output", "No output"))

def test_validate_discovery():
    """Test the ValidateDiscovery method"""
    print("\n" + "=" * 80)
    print("TESTING Discovery.ValidateDiscovery")
    print("=" * 80)
    
    parameters_json = json.dumps([])
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteClassMethod",
        "ExecuteMCP.TestRunner.Discovery",
        "ValidateDiscovery",
        parameters_json,
        "HSCUSTOM"
    )
    
    print(f"ValidateDiscovery result: {result}")
    
    # Parse and display the result
    try:
        result_data = json.loads(result)
        if result_data.get("status") == "success" and "result" in result_data:
            validation = json.loads(result_data["result"])
            print(f"\nValidation Results:")
            print(f"  Success: {validation.get('success')}")
            print(f"  Package: {validation.get('testPackage')}")
            print(f"  Classes Found: {validation.get('classesFound')}")
            print(f"  Tests Found: {validation.get('testsFound')}")
            if "classes" in validation:
                print(f"  Test Classes:")
                for cls in validation["classes"]:
                    print(f"    - {cls}")
    except Exception as e:
        print(f"Error parsing result: {e}")

if __name__ == "__main__":
    try:
        test_is_test_class()
        test_discover_test_classes()
        test_sql_query_directly()
        test_validate_discovery()
        
        print("\n" + "=" * 80)
        print("Discovery debug complete")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
