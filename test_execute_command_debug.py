#!/usr/bin/env python3
"""
Test script to debug the execute_command timeout issue.
This script will:
1. Test the ExecuteCommand method through our existing MCP infrastructure
2. Use our working get_global tool to read debug information
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def test_mcp_execute_command():
    """Test execute_command through MCP protocol (this may timeout)"""
    print("\n⏱️  Testing execute_command through MCP protocol...")
    print("   (This test may timeout - that's what we're debugging)")
    
    try:
        # Use our own IRIS calling function from the FastMCP server
        from iris_execute_fastmcp import call_iris_sync
        
        # Create a simple test command
        command = 'WRITE "MCP Test Debug!"'
        namespace = "HSCUSTOM"
        
        print(f"   Command: {command}")
        print(f"   Namespace: {namespace}")
        print("   Starting execution...")
        
        # This may timeout - call the method directly like the MCP tool does
        result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", command, namespace)
        print(f"✅ MCP execute_command successful: {result}")
        return result
        
    except Exception as e:
        print(f"⚠️  MCP execute_command failed/timeout: {e}")
        return None

def test_debug_read():
    """Read debug information using our working get_global MCP tool"""
    print("\n🔍 Reading debug information from ^MCPDebug...")
    
    try:
        # Use our working get_global function
        from iris_execute_fastmcp import call_iris_sync
        
        # Read the debug global using our working get_global method
        debug_info = call_iris_sync("ExecuteMCP.Core.Command", "GetGlobal", "^MCPDebug", "HSCUSTOM")
        debug_data = json.loads(debug_info)
        
        if debug_data.get("status") == "success":
            print(f"✅ Debug information retrieved:")
            print(f"   Value: {debug_data.get('value', 'No debug info')}")
            print(f"   Exists: {debug_data.get('exists', 0)}")
            
            # Parse debug steps if available
            debug_value = debug_data.get('value', '')
            if debug_value:
                steps = debug_value.split(';')
                print(f"\n📋 Debug Steps ({len(steps)} total):")
                for i, step in enumerate(steps, 1):
                    if step.strip():
                        print(f"   {i:2d}. {step.strip()}")
            
            return debug_data
        else:
            print(f"❌ Failed to retrieve debug info: {debug_data}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to read debug info: {e}")
        return None

def clear_debug_global():
    """Clear debug global for fresh test"""
    print("\n🧹 Clearing debug global for fresh test...")
    try:
        from iris_execute_fastmcp import call_iris_sync
        result = call_iris_sync("ExecuteMCP.Core.Command", "SetGlobal", "^MCPDebug", "", "HSCUSTOM")
        print("   Debug global cleared")
        return True
    except Exception as e:
        print(f"   Warning: Could not clear debug global: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 IRIS Execute Command Debug Test")
    print("=" * 60)
    
    # Step 1: Clear debug global for fresh start
    clear_debug_global()
    
    # Step 2: Test execute_command (may timeout)
    mcp_result = test_mcp_execute_command()
    
    # Step 3: Read debug information from the test
    print("\n🔍 Reading debug information from test...")
    debug_info = test_debug_read()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEBUG TEST SUMMARY")
    print("=" * 60)
    print(f"MCP execute_command:  {'✅ SUCCESS' if mcp_result else '⚠️  TIMEOUT/FAILED'}")
    print(f"Debug information:    {'✅ CAPTURED' if debug_info else '❌ NOT AVAILABLE'}")
    
    if debug_info and debug_info.get('value'):
        print("\n🔍 Debug Analysis:")
        debug_value = debug_info.get('value', '')
        steps = debug_value.split(';')
        last_step = ""
        for step in steps:
            if step.strip():
                last_step = step.strip()
        
        print(f"   Last completed step: {last_step}")
        print(f"   Total steps logged: {len([s for s in steps if s.strip()])}")
        
        if "END:" in debug_value:
            print("   ✅ Method completed normally")
        elif "EXECUTE:" in debug_value and "XECUTE completed successfully" in debug_value:
            print("   ✅ XECUTE command completed, issue may be in JSON conversion")
        elif "EXECUTE:" in debug_value:
            print("   ⚠️  Timeout likely occurred during XECUTE command execution")
        elif "SECURITY:" in debug_value:
            print("   ⚠️  Timeout likely occurred during security check or after")
        else:
            print("   ⚠️  Timeout occurred very early in method execution")
            
        # Show detailed analysis of where it stopped
        if "JSON:" in debug_value:
            if "JSON: Conversion completed" in debug_value:
                print("   🔍 JSON conversion completed - issue may be in method return")
            else:
                print("   🔍 Timeout occurred during JSON conversion")
        
        if "TIMING:" in debug_value:
            print("   🔍 Timing calculations reached")
            
        if "RESPONSE:" in debug_value:
            print("   🔍 Response building reached")

if __name__ == "__main__":
    main()
