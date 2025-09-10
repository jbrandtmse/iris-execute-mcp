#!/usr/bin/env python3
"""
Comprehensive test script to diagnose Discovery issues
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from iris_execute_mcp import mcp
import json

def main():
    execute_command_tool = mcp._tool_manager.get_tool("execute_command")
    execute_classmethod_tool = mcp._tool_manager.get_tool("execute_classmethod")
    
    print("=" * 80)
    print("Comprehensive Discovery Diagnostics")
    print("=" * 80)
    
    # Test 1: Direct SQL query using execute_command
    print("\nTest 1: Direct SQL query for ExecuteMCP.Test classes")
    print("-" * 40)
    
    sql_command = """
    Set ^ClineDebug = ""
    Set rs = ##class(%SQL.Statement).%ExecDirect(,"SELECT Name FROM %Dictionary.CompiledClassDefinition WHERE Name %STARTSWITH 'ExecuteMCP.Test.'")
    Set count = 0
    While rs.%Next() {
        Set count = count + 1
        Set ^ClineDebug = ^ClineDebug _ "Found: " _ rs.%Get("Name") _ "; "
    }
    Set ^ClineDebug = ^ClineDebug _ "Total count: " _ count
    WRITE ^ClineDebug
    """
    
    result = execute_command_tool.fn(
        command=sql_command,
        namespace="HSCUSTOM"
    )
    result_data = json.loads(result)
    if result_data.get('status') == 'success':
        print(f"SQL Query Result: {result_data.get('output')}")
    else:
        print(f"SQL Query Error: {result_data.get('error')}")
    
    # Test 2: Check if classes exist using %Dictionary.CompiledClass
    print("\n\nTest 2: Direct check for compiled classes")
    print("-" * 40)
    
    test_classes = [
        "ExecuteMCP.Test.SimpleTest",
        "ExecuteMCP.Test.ErrorTest",
        "ExecuteMCP.Test.SampleUnitTest",
        "ExecuteMCP.Test.AssertionTest"
    ]
    
    for class_name in test_classes:
        check_command = f"""
        Set exists = ##class(%Dictionary.CompiledClass).%ExistsId("{class_name}")
        WRITE "{class_name}: " _ $SELECT(exists:"EXISTS",1:"NOT FOUND")
        """
        
        result = execute_command_tool.fn(
            command=check_command,
            namespace="HSCUSTOM"
        )
        result_data = json.loads(result)
        if result_data.get('status') == 'success':
            print(result_data.get('output'))
    
    # Test 3: Check Super property of a test class
    print("\n\nTest 3: Check inheritance chain of test classes")
    print("-" * 40)
    
    for class_name in ["ExecuteMCP.Test.SimpleTest", "ExecuteMCP.Test.ErrorTest"]:
        inheritance_command = f"""
        Set ^ClineDebug = ""
        Set cls = ##class(%Dictionary.CompiledClass).%OpenId("{class_name}")
        If $ISOBJECT(cls) {{
            Set ^ClineDebug = "Class: {class_name}, Super: " _ cls.Super
        }} Else {{
            Set ^ClineDebug = "Could not open class: {class_name}"
        }}
        WRITE ^ClineDebug
        """
        
        result = execute_command_tool.fn(
            command=inheritance_command,
            namespace="HSCUSTOM"
        )
        result_data = json.loads(result)
        if result_data.get('status') == 'success':
            print(result_data.get('output'))
    
    # Test 4: Alternative SQL query without trailing dot
    print("\n\nTest 4: SQL query without trailing dot")
    print("-" * 40)
    
    sql_command2 = """
    Set ^ClineDebug = ""
    Set rs = ##class(%SQL.Statement).%ExecDirect(,"SELECT Name FROM %Dictionary.CompiledClassDefinition WHERE Name %STARTSWITH 'ExecuteMCP.Test'")
    Set count = 0
    While rs.%Next() {
        Set count = count + 1
        Set ^ClineDebug = ^ClineDebug _ "Found: " _ rs.%Get("Name") _ "; "
    }
    Set ^ClineDebug = ^ClineDebug _ "Total count: " _ count
    WRITE ^ClineDebug
    """
    
    result = execute_command_tool.fn(
        command=sql_command2,
        namespace="HSCUSTOM"
    )
    result_data = json.loads(result)
    if result_data.get('status') == 'success':
        print(f"SQL Query Result: {result_data.get('output')}")
    
    # Test 5: Try using LIKE instead of %STARTSWITH
    print("\n\nTest 5: SQL query using LIKE")
    print("-" * 40)
    
    sql_command3 = """
    Set ^ClineDebug = ""
    Set rs = ##class(%SQL.Statement).%ExecDirect(,"SELECT Name FROM %Dictionary.CompiledClassDefinition WHERE Name LIKE 'ExecuteMCP.Test%'")
    Set count = 0
    While rs.%Next() {
        Set count = count + 1
        Set ^ClineDebug = ^ClineDebug _ "Found: " _ rs.%Get("Name") _ "; "
    }
    Set ^ClineDebug = ^ClineDebug _ "Total count: " _ count
    WRITE ^ClineDebug
    """
    
    result = execute_command_tool.fn(
        command=sql_command3,
        namespace="HSCUSTOM"
    )
    result_data = json.loads(result)
    if result_data.get('status') == 'success':
        print(f"SQL Query Result: {result_data.get('output')}")
    
    # Test 6: List ALL classes starting with ExecuteMCP
    print("\n\nTest 6: List ALL ExecuteMCP classes")
    print("-" * 40)
    
    sql_command4 = """
    Set ^ClineDebug = ""
    Set rs = ##class(%SQL.Statement).%ExecDirect(,"SELECT Name FROM %Dictionary.CompiledClassDefinition WHERE Name LIKE 'ExecuteMCP%' ORDER BY Name")
    Set count = 0
    While rs.%Next() {
        Set count = count + 1
        Set ^ClineDebug = ^ClineDebug _ rs.%Get("Name") _ "; "
    }
    Set ^ClineDebug = ^ClineDebug _ " [Total: " _ count _ "]"
    WRITE ^ClineDebug
    """
    
    result = execute_command_tool.fn(
        command=sql_command4,
        namespace="HSCUSTOM"
    )
    result_data = json.loads(result)
    if result_data.get('status') == 'success':
        print(f"All ExecuteMCP Classes: {result_data.get('output')}")
    
    # Test 7: Debug the IsTestClass method with actual values
    print("\n\nTest 7: Debug IsTestClass return values")
    print("-" * 40)
    
    for class_name in ["ExecuteMCP.Test.SimpleTest", "ExecuteMCP.Test.ErrorTest"]:
        debug_command = f"""
        Set result = ##class(ExecuteMCP.TestRunner.Discovery).IsTestClass("{class_name}")
        WRITE "{class_name} IsTestClass result: " _ result _ " (type: " _ $SELECT(result=1:"TRUE",result=0:"FALSE",1:"OTHER="_result) _ ")"
        """
        
        result = execute_command_tool.fn(
            command=debug_command,
            namespace="HSCUSTOM"
        )
        result_data = json.loads(result)
        if result_data.get('status') == 'success':
            print(result_data.get('output'))

if __name__ == "__main__":
    main()
