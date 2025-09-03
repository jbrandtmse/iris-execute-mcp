#!/usr/bin/env python3
"""Test compiling single class and list of classes"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import iris_execute_mcp
import json

def test_compilation():
    """Test single class and list compilation"""
    # Access the FastMCP server instance from the module
    server = iris_execute_mcp.mcp
    
    print("=" * 60)
    print("Testing Compilation Tools")
    print("=" * 60)
    
    # Test 1: Compile a single class
    print("\n=== Test 1: Compile Single Class ===")
    print("Compiling: ExecuteMCP.Test.SimpleTest.cls")
    
    tools = server._tool_manager._tools
    compile_class_tool = tools.get("compile_objectscript_class")
    
    if compile_class_tool:
        result = compile_class_tool.fn(
            class_names="ExecuteMCP.Test.SimpleTest.cls", 
            qspec="cuk",
            namespace="HSCUSTOM"
        )
        result_data = json.loads(result)
        print(f"Status: {result_data.get('status')}")
        print(f"Compiled: {result_data.get('compiledItems', [])}")
        print(f"Errors: {result_data.get('errorCount', 0)}")
        if result_data.get('status') == 'success':
            print("✅ SUCCESS: Single class compiled")
        else:
            print("❌ FAILED: Single class compilation failed")
    
    # Test 2: Compile a list of classes
    print("\n=== Test 2: Compile List of Classes ===")
    print("Compiling: ExecuteMCP.Core.Command.cls,ExecuteMCP.Core.UnitTest.cls,ExecuteMCP.Test.ErrorTest.cls")
    
    if compile_class_tool:
        result = compile_class_tool.fn(
            class_names="ExecuteMCP.Core.Command.cls,ExecuteMCP.Core.UnitTest.cls,ExecuteMCP.Test.ErrorTest.cls", 
            qspec="cuk",
            namespace="HSCUSTOM"
        )
        result_data = json.loads(result)
        print(f"Status: {result_data.get('status')}")
        print(f"Compiled items ({len(result_data.get('compiledItems', []))}):")
        for item in result_data.get('compiledItems', []):
            print(f"  - {item}")
        print(f"Errors: {result_data.get('errorCount', 0)}")
        if result_data.get('status') == 'success':
            print("✅ SUCCESS: List of classes compiled")
        else:
            print("❌ FAILED: List compilation failed")
    
    print("\n" + "=" * 60)
    print("Compilation Tests Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_compilation()
