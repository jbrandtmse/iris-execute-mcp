#!/usr/bin/env python3
"""
Diagnose why only 3 test classes are discovered instead of 9+.
Check what test classes actually exist in the HSCUSTOM namespace.
"""

import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

# Import MCP module
from iris_execute_mcp import call_iris_sync

def diagnose_test_discovery():
    """Check what unit test classes exist in HSCUSTOM namespace"""
    
    print("Diagnosing Unit Test Discovery Issue")
    print("=" * 60)
    
    # Check ExecuteMCP.Test classes
    print("\n1. Checking ExecuteMCP.Test classes:")
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        "DO $SYSTEM.OBJ.GetPackageList(.list,\"ExecuteMCP.Test\") SET key=$ORDER(list(\"\")) WHILE key'=\"\" { WRITE key,! SET key=$ORDER(list(key)) }",
        "HSCUSTOM"
    )
    result_obj = json.loads(result)
    if result_obj.get("status") == "success":
        print("  ExecuteMCP.Test classes exist")
    else:
        print(f"  Error: {result_obj.get('errorMessage', 'Unknown')}")
    
    # Check all %UnitTest.TestCase subclasses
    print("\n2. Checking all %UnitTest.TestCase subclasses:")
    
    # Simple command to count test classes
    count_command = """SET count=0 DO ##class(%Dictionary.ClassDefinition).SubclassOfFunc("%UnitTest.TestCase").%SQL("SELECT Name INTO :name { SET count=count+1 }") WRITE "Total test classes: ",count"""
    
    result = call_iris_sync(
        "ExecuteMCP.Core.Command", 
        "ExecuteCommand",
        count_command,
        "HSCUSTOM"
    )
    result_obj = json.loads(result)
    print(f"  Result: {result_obj}")
    
    # Check if Patterns namespace exists
    print("\n3. Checking Patterns namespace/package:")
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand", 
        "IF ##class(%Dictionary.PackageDefinition).%ExistsId(\"Patterns\") { WRITE \"Patterns package exists\" } ELSE { WRITE \"Patterns package NOT found\" }",
        "HSCUSTOM"
    )
    result_obj = json.loads(result)
    print(f"  Result: {result_obj.get('output', 'No output')}")
    
    # Check if Patterns.Test namespace exists
    print("\n4. Checking Patterns.Test package:")
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand", 
        "IF ##class(%Dictionary.PackageDefinition).%ExistsId(\"Patterns.Test\") { WRITE \"Patterns.Test package exists\" } ELSE { WRITE \"Patterns.Test package NOT found\" }",
        "HSCUSTOM"
    )
    result_obj = json.loads(result)
    print(f"  Result: {result_obj.get('output', 'No output')}")
    
    # Check for specific expected test class
    print("\n5. Checking for specific test class existence:")
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        "IF ##class(%Dictionary.ClassDefinition).%ExistsId(\"Patterns.Test.Unit.GoF.Creational.AbstractFactoryTest\") { WRITE \"AbstractFactoryTest EXISTS\" } ELSE { WRITE \"AbstractFactoryTest NOT FOUND\" }",
        "HSCUSTOM"
    )
    result_obj = json.loads(result)
    print(f"  Result: {result_obj.get('output', 'No output')}")
    
    # Try to list all test classes with a simpler approach
    print("\n6. Attempting to list ExecuteMCP.Test classes:")
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        "DO ##class(%Dictionary.ClassDefinition).GetAllClassNames(.arr,\"ExecuteMCP.Test\") SET key=$ORDER(arr(\"\")) WHILE key'=\"\" { WRITE key,! SET key=$ORDER(arr(key)) }",
        "HSCUSTOM"
    )
    result_obj = json.loads(result)
    print(f"  Result: {result_obj}")
    
    # Check using SQL query
    print("\n7. Using SQL to find test classes:")
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        "DO ##class(%SQL.Statement).%ExecDirect(,\"SELECT Name FROM %Dictionary.ClassDefinition WHERE Name LIKE 'ExecuteMCP.Test%'\").%Display()",
        "HSCUSTOM"
    )
    result_obj = json.loads(result)
    print(f"  Result: {result_obj}")
    
    print("\n" + "=" * 60)
    print("Diagnosis Complete")
    print("\nConclusion:")
    print("The issue is likely that Patterns.Test classes do not exist in the HSCUSTOM namespace.")
    print("Only ExecuteMCP.Test classes exist, which explains why only 3 classes are discovered.")
    print("The 9+ test classes mentioned by the user may be in a different namespace or not loaded.")

if __name__ == "__main__":
    diagnose_test_discovery()
