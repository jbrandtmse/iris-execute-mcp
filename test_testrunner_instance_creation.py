#!/usr/bin/env python3
"""
Diagnostic test for TestRunner instance creation
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from iris_execute_mcp import call_iris_method

def test_instance_creation():
    """Test creating an instance of SimpleTest directly"""
    print("Testing instance creation of ExecuteMCP.Test.SimpleTest...")
    
    # Try to create instance directly
    result = call_iris_method(
        "ExecuteMCP.TestRunner.Wrapper",
        "TestInstanceCreation",
        [],
        "HSCUSTOM"
    )
    
    print(f"Instance creation test: {result}")
    
    # Also test if the Manager is being created properly
    print("\nTesting Manager creation...")
    result = call_iris_method(
        "ExecuteMCP.TestRunner.Wrapper",
        "TestManagerCreation",
        [],
        "HSCUSTOM"
    )
    
    print(f"Manager creation test: {result}")

if __name__ == "__main__":
    test_instance_creation()
