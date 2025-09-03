#!/usr/bin/env python3
"""
Test script for MCP compilation tools
Tests both compile_objectscript_class and compile_objectscript_package
"""

import json
from iris_execute_mcp import mcp
from pydantic import BaseModel

def test_compile_tools():
    """Test compilation tools through MCP server"""
    
    # Get the compilation tools
    compile_class_tool = mcp._tool_manager.get_tool("compile_objectscript_class")
    compile_package_tool = mcp._tool_manager.get_tool("compile_objectscript_package")
    
    if not compile_class_tool:
        print("ERROR: compile_objectscript_class tool not found")
        return
    
    if not compile_package_tool:
        print("ERROR: compile_objectscript_package tool not found")
        return
    
    print("=" * 60)
    print("Testing MCP Compilation Tools")
    print("=" * 60)
    
    # Test 1: Single class compilation
    print("\nTest 1: Compile single class with .cls suffix")
    print("-" * 40)
    try:
        result = compile_class_tool.fn(
            class_names="ExecuteMCP.Test.SimpleTest.cls", 
            qspec="cuk",
            namespace="HSCUSTOM"
        )
        response = json.loads(result)
        print(f"Status: {response.get('status')}")
        print(f"Compiled: {response.get('compiledItems', [])}")
        print(f"Count: {response.get('compiledCount', 0)}")
        print(f"Errors: {response.get('errors', [])}")
        print(f"Time: {response.get('executionTime', 0)}ms")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 2: Multiple classes compilation  
    print("\nTest 2: Compile multiple classes with .cls suffix")
    print("-" * 40)
    try:
        result = compile_class_tool.fn(
            class_names="ExecuteMCP.Core.Command.cls,ExecuteMCP.Core.UnitTest.cls,ExecuteMCP.Test.ErrorTest.cls", 
            qspec="cuk",
            namespace="HSCUSTOM"
        )
        response = json.loads(result)
        print(f"Status: {response.get('status')}")
        print(f"Compiled: {response.get('compiledItems', [])}")
        print(f"Count: {response.get('compiledCount', 0)}")
        print(f"Errors: {response.get('errors', [])}")
        print(f"Time: {response.get('executionTime', 0)}ms")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 3: Package compilation
    print("\nTest 3: Compile entire package")
    print("-" * 40)
    try:
        result = compile_package_tool.fn(
            package_name="ExecuteMCP.Test",
            qspec="cuk",
            namespace="HSCUSTOM"
        )
        response = json.loads(result)
        print(f"Status: {response.get('status')}")
        print(f"Package: {response.get('packageName')}")
        print(f"Compiled Classes: {response.get('compiledItems', [])}")
        print(f"Count: {response.get('compiledCount', 0)}")
        print(f"Errors: {response.get('errors', [])}")
        print(f"Time: {response.get('executionTime', 0)}ms")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 4: Test without .cls suffix (should be auto-added)
    print("\nTest 4: Compile without .cls suffix (auto-add test)")
    print("-" * 40)
    try:
        result = compile_class_tool.fn(
            class_names="ExecuteMCP.Core.UnitTestAsync",  # No .cls suffix
            qspec="cuk",
            namespace="HSCUSTOM"
        )
        response = json.loads(result)
        print(f"Status: {response.get('status')}")
        print(f"Compiled: {response.get('compiledItems', [])}")
        print(f"Note: .cls suffix auto-added: {'.cls' in str(response.get('compiledItems', []))}")
        print(f"Time: {response.get('executionTime', 0)}ms")
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("All compilation tool tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_compile_tools()
