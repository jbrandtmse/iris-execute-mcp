#!/usr/bin/env python3
"""
Direct MCP Server Test
Tests the iris-execute-mcp server independently of Cline extension.
"""

import asyncio
import json
import subprocess
import sys
import os
from typing import Dict, Any

async def test_mcp_server():
    """Test the MCP server directly via subprocess communication."""
    print("🧪 Testing IRIS Execute MCP Server directly...")
    
    # MCP server command from configuration
    venv_python = "D:/iris-session-mcp/venv/Scripts/python.exe"
    server_script = "D:/iris-session-mcp/iris_execute_fastmcp.py"
    
    # Environment variables
    env = os.environ.copy()
    env.update({
        "IRIS_HOSTNAME": "localhost",
        "IRIS_PORT": "1972", 
        "IRIS_NAMESPACE": "HSCUSTOM",
        "IRIS_USERNAME": "_SYSTEM",
        "IRIS_PASSWORD": "_SYSTEM"
    })
    
    try:
        # Start the MCP server process
        print(f"⚡ Starting server: {venv_python} {server_script}")
        process = subprocess.Popen(
            [venv_python, server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        # Give server time to initialize
        await asyncio.sleep(2)
        
        # Test 1: Initialize request
        print("📨 Sending initialize request...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send initialize
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Initialize response: {response}")
        else:
            print("❌ No initialize response received")
            return False
            
        # Step 3: Send initialized notification (required!)
        print("📨 Sending initialized notification...")
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        
        # Small delay for handshake completion
        await asyncio.sleep(0.5)
        
        # Test 2: List tools request  
        print("📨 Sending list tools request...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Tools response: {response}")
            
            # Check if execute_command tool is available
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                execute_tool = next((t for t in tools if t["name"] == "execute_command"), None)
                if execute_tool:
                    print(f"✅ execute_command tool found: {execute_tool.get('description', 'No description')}")
                else:
                    print("❌ execute_command tool not found")
                    print(f"Available tools: {[t.get('name') for t in tools]}")
                    return False
            else:
                print("❌ Invalid tools response format")
                return False
        else:
            print("❌ No tools response received") 
            return False
            
        # Test 3: Execute command request
        print("📨 Sending IRIS execute command request...")
        command_request = {
            "jsonrpc": "2.0", 
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "execute_command",
                "arguments": {
                    "command": "WRITE \"MCP FastMCP Test Success!\"",
                    "namespace": "HSCUSTOM"
                }
            }
        }
        
        process.stdin.write(json.dumps(command_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            try:
                # Handle WRITE output mixed with JSON response
                raw_response = response_line.strip()
                
                # Find JSON part (starts with '{')
                json_start = raw_response.find('{"jsonrpc"')
                if json_start > 0:
                    # Extract WRITE output and JSON separately
                    write_output = raw_response[:json_start]
                    json_part = raw_response[json_start:]
                    print(f"📤 WRITE output: '{write_output}'")
                    response = json.loads(json_part)
                else:
                    response = json.loads(raw_response)
                    
                print(f"✅ Command response: {response}")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: '{raw_response}'")
                return False
            
            # Check if command executed successfully
            if "result" in response and "content" in response["result"]:
                content = response["result"]["content"]
                if content and len(content) > 0:
                    text_content = content[0].get("text", "")
                    # Parse the JSON response from IRIS
                    try:
                        iris_result = json.loads(text_content)
                        if iris_result.get("status") == "success":
                            print("🎉 IRIS Execute FastMCP test successful!")
                            print(f"✅ IRIS Response: {iris_result}")
                            return True
                        else:
                            print(f"⚠️ IRIS execution failed: {iris_result}")
                            return False
                    except json.JSONDecodeError:
                        # Fallback to string matching
                        if "success" in text_content.lower() or "MCP FastMCP Test Success!" in write_output:
                            print("🎉 IRIS Execute FastMCP test successful!")
                            return True
                        else:
                            print(f"⚠️ Unexpected command response: {text_content}")
                            return False
                else:
                    print("❌ Empty command response content")
                    return False
            else:
                print("❌ Invalid command response format")
                return False
        else:
            print("❌ No command response received")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False
    finally:
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            print("� Server process terminated")
    
    return True

async def main():
    """Main test function."""
    print("=" * 60)
    print("🔍 IRIS Execute MCP Server - Direct Connection Test")
    print("=" * 60)
    
    success = await test_mcp_server()
    
    print("=" * 60)
    if success:
        print("✅ ALL TESTS PASSED - MCP Server is working correctly!")
        print("❓ Issue likely in Cline extension connection, not server")
        print("💡 Try: Restart VS Code and disable/enable Cline extension")
    else:
        print("❌ TESTS FAILED - MCP Server has issues")
        print("� Check server logs and IRIS connectivity")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
