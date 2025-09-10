#!/usr/bin/env python3
"""
Test ExecuteCommand after syntax fix.
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
from dotenv import load_dotenv
load_dotenv()

from iris_execute_mcp import call_iris_sync

def test_execute_command():
    """Test ExecuteCommand method after syntax fix."""
    print("Testing ExecuteCommand after syntax fix...")
    print("-" * 50)
    
    # Test simple command
    command = 'Set x = 123'
    print(f"Testing command: {command}")
    
    try:
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            command,
            "HSCUSTOM"
        )
        
        # Parse JSON result
        if result:
            result_obj = json.loads(result)
            if result_obj.get("status") == "success":
                print(f"✓ Command executed successfully")
                print(f"  Output: {result_obj.get('output')}")
                print(f"  Execution time: {result_obj.get('executionTimeMs')}ms")
            else:
                print(f"✗ Command failed: {result_obj.get('errorMessage')}")
                return False
        else:
            print("✗ No result returned")
            return False
            
    except Exception as e:
        print(f"✗ Error executing command: {e}")
        return False
    
    print()
    
    # Test WRITE command
    command = 'Write "Hello from IRIS"'
    print(f"Testing WRITE command: {command}")
    
    try:
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            command,
            "HSCUSTOM"
        )
        
        # Parse JSON result
        if result:
            result_obj = json.loads(result)
            if result_obj.get("status") == "success":
                print(f"✓ WRITE command executed successfully")
                print(f"  Output: {result_obj.get('output')}")
                print(f"  Execution time: {result_obj.get('executionTimeMs')}ms")
            else:
                print(f"✗ WRITE command failed: {result_obj.get('errorMessage')}")
                return False
        else:
            print("✗ No result returned")
            return False
            
    except Exception as e:
        print(f"✗ Error executing WRITE command: {e}")
        return False
    
    print()
    print("✓ All ExecuteCommand tests passed!")
    return True

if __name__ == "__main__":
    success = test_execute_command()
    sys.exit(0 if success else 1)
