#!/usr/bin/env python3
"""
Test ExecuteCommand with valid single-line ObjectScript commands.
ObjectScript If statements and While loops with curly braces are multi-line
constructs and cannot be executed as single-line XECUTE commands.
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

def test_valid_objectscript_commands():
    """Test ExecuteCommand with valid single-line ObjectScript commands"""
    
    print("Testing Valid ObjectScript Commands")
    print("=" * 60)
    
    # Valid single-line ObjectScript commands - NO SPACES around equals!
    commands = [
        ("Simple SET command", "SET x=5"),
        ("Simple WRITE command", "WRITE \"Hello from IRIS\""),
        ("Single-line IF post-conditional", "SET x=1 IF x=1 WRITE \"x is 1\""),
        ("SET with arithmetic", "SET result=10+20"),
        ("Multiple SETs with comma", "SET a=1,b=2,c=3"),
        ("WRITE with concatenation", "SET msg=\"Test\" WRITE msg_\" Complete\""),
        ("FOR loop single line", "FOR i=1:1:3 WRITE i,\" \""),
        ("WRITE with newline", "WRITE \"Line 1\",! WRITE \"Line 2\""),
        ("SET and WRITE combined", "SET value=42 WRITE \"Value is: \",value"),
        ("Simple global test", "SET ^TestGlobal=\"Hello\""),
        ("Kill global", "KILL ^TestGlobal"),
        ("Quit command", "QUIT \"Test Return\"")
    ]
    
    for description, command in commands:
        print(f"\n{description}:")
        print(f"Command: {command}")
        
        try:
            result = call_iris_sync(
                "ExecuteMCP.Core.Command",
                "ExecuteCommand", 
                [command, "HSCUSTOM"]
            )
            
            print(f"Result: {result}")
            
            # Parse result if it's a string
            if isinstance(result, str):
                try:
                    result_obj = json.loads(result)
                    if result_obj.get("status") == "error":
                        print(f"  ERROR: {result_obj.get('errorMessage', 'Unknown error')}")
                    else:
                        print(f"  SUCCESS: {result_obj.get('output', 'Command executed')}")
                except json.JSONDecodeError:
                    print(f"  Raw result: {result}")
                    
        except Exception as e:
            print(f"  Exception: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete")

if __name__ == "__main__":
    test_valid_objectscript_commands()
