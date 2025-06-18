#!/usr/bin/env python3
"""
Test IRIS Execute MCP Server - Global Tools Test
Direct connection test for get_global and set_global tools
"""

import subprocess
import json
import time
import sys
import os

def send_jsonrpc_request(process, request_id, method, params=None):
    """Send a JSON-RPC request to the MCP server"""
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method
    }
    if params:
        request["params"] = params
    
    request_str = json.dumps(request) + "\n"
    process.stdin.write(request_str.encode())
    process.stdin.flush()
    
    # Read response
    response_line = process.stdout.readline()
    if response_line:
        return json.loads(response_line.decode().strip())
    return None

def test_mcp_global_tools():
    """Test MCP global tools directly"""
    print("============================================================")
    print("🔍 IRIS Execute MCP Server - Global Tools Test")
    print("============================================================")
    
    # Start the MCP server process
    python_exe = "D:/iris-session-mcp/venv/Scripts/python.exe"
    script_path = "D:/iris-session-mcp/iris_execute_fastmcp.py"
    
    print(f"⚡ Starting server: {python_exe} {script_path}")
    
    try:
        process = subprocess.Popen(
            [python_exe, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            bufsize=0
        )
        
        time.sleep(2)  # Give server time to start
        
        # Send initialize request
        print("📨 Sending initialize request...")
        init_response = send_jsonrpc_request(process, 1, "initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        })
        
        if not init_response or init_response.get("error"):
            print(f"❌ Initialize failed: {init_response}")
            return False
        
        print("✅ Initialize response received")
        
        # Send initialized notification
        print("📨 Sending initialized notification...")
        process.stdin.write(b'{"jsonrpc": "2.0", "method": "notifications/initialized"}\n')
        process.stdin.flush()
        
        # List tools to confirm new tools are available
        print("📨 Sending list tools request...")
        tools_response = send_jsonrpc_request(process, 2, "tools/list")
        
        if not tools_response or tools_response.get("error"):
            print(f"❌ Tools list failed: {tools_response}")
            return False
        
        tools = tools_response.get("result", {}).get("tools", [])
        tool_names = [tool["name"] for tool in tools]
        
        print(f"✅ Tools response: Found {len(tools)} tools")
        for tool_name in tool_names:
            print(f"   - {tool_name}")
        
        # Verify our new tools are present
        if "get_global" not in tool_names:
            print("❌ get_global tool not found!")
            return False
        if "set_global" not in tool_names:
            print("❌ set_global tool not found!")
            return False
        
        print("✅ Both get_global and set_global tools found!")
        
        # Test 1: Set a global
        print("\n📝 Test 1: Setting ^MCPServerTest global...")
        set_response = send_jsonrpc_request(process, 3, "tools/call", {
            "name": "set_global",
            "arguments": {
                "global_ref": "^MCPServerTest",
                "value": "MCP Global Test Success!"
            }
        })
        
        if not set_response or set_response.get("error"):
            print(f"❌ Set global failed: {set_response}")
            return False
        
        # Parse the result
        set_result = set_response.get("result", {})
        set_content = set_result.get("content", [{}])[0].get("text", "{}")
        set_data = json.loads(set_content)
        
        if set_data.get("status") == "success":
            print("✅ Set global successful!")
            print(f"   Global: {set_data.get('globalRef')}")
            print(f"   Value: {set_data.get('setValue')}")
        else:
            print(f"❌ Set global failed: {set_data.get('errorMessage')}")
            return False
        
        # Test 2: Get the global we just set
        print("\n📖 Test 2: Getting ^MCPServerTest global...")
        get_response = send_jsonrpc_request(process, 4, "tools/call", {
            "name": "get_global",
            "arguments": {
                "global_ref": "^MCPServerTest"
            }
        })
        
        if not get_response or get_response.get("error"):
            print(f"❌ Get global failed: {get_response}")
            return False
        
        # Parse the result
        get_result = get_response.get("result", {})
        get_content = get_result.get("content", [{}])[0].get("text", "{}")
        get_data = json.loads(get_content)
        
        if get_data.get("status") == "success":
            print("✅ Get global successful!")
            print(f"   Global: {get_data.get('globalRef')}")
            print(f"   Value: {get_data.get('value')}")
            print(f"   Exists: {get_data.get('exists')}")
        else:
            print(f"❌ Get global failed: {get_data.get('errorMessage')}")
            return False
        
        # Test 3: Set global with subscripts
        print('\n📝 Test 3: Setting ^MCPServerTest("Sub1","Sub2") global...')
        set_sub_response = send_jsonrpc_request(process, 5, "tools/call", {
            "name": "set_global",
            "arguments": {
                "global_ref": '^MCPServerTest("Sub1","Sub2")',
                "value": "Subscripted value test"
            }
        })
        
        if not set_sub_response or set_sub_response.get("error"):
            print(f"❌ Set subscripted global failed: {set_sub_response}")
            return False
        
        set_sub_result = set_sub_response.get("result", {})
        set_sub_content = set_sub_result.get("content", [{}])[0].get("text", "{}")
        set_sub_data = json.loads(set_sub_content)
        
        if set_sub_data.get("status") == "success":
            print("✅ Set subscripted global successful!")
            print(f"   Global: {set_sub_data.get('globalRef')}")
            print(f"   Value: {set_sub_data.get('setValue')}")
        else:
            print(f"❌ Set subscripted global failed: {set_sub_data.get('errorMessage')}")
            return False
        
        # Test 4: Get the subscripted global
        print('\n📖 Test 4: Getting ^MCPServerTest("Sub1","Sub2") global...')
        get_sub_response = send_jsonrpc_request(process, 6, "tools/call", {
            "name": "get_global",
            "arguments": {
                "global_ref": '^MCPServerTest("Sub1","Sub2")'
            }
        })
        
        if not get_sub_response or get_sub_response.get("error"):
            print(f"❌ Get subscripted global failed: {get_sub_response}")
            return False
        
        get_sub_result = get_sub_response.get("result", {})
        get_sub_content = get_sub_result.get("content", [{}])[0].get("text", "{}")
        get_sub_data = json.loads(get_sub_content)
        
        if get_sub_data.get("status") == "success":
            print("✅ Get subscripted global successful!")
            print(f"   Global: {get_sub_data.get('globalRef')}")
            print(f"   Value: {get_sub_data.get('value')}")
        else:
            print(f"❌ Get subscripted global failed: {get_sub_data.get('errorMessage')}")
            return False
        
        print("\n🎉 IRIS Execute MCP Global Tools test successful!")
        print("✅ All global manipulation tools working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        return False
        
    finally:
        # Cleanup
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
        print("🧹 Server process terminated")

def main():
    print("============================================================")
    print("🧪 Testing IRIS Execute MCP Server global tools...")
    print("============================================================")
    
    success = test_mcp_global_tools()
    
    if success:
        print("============================================================")
        print("✅ ALL TESTS PASSED - MCP Global Tools are working!")
        print("❓ Issue likely in Cline extension connection, not server")
        print("💡 Try: Restart VS Code and disable/enable Cline extension")
        print("============================================================")
    else:
        print("============================================================")
        print("❌ SOME TESTS FAILED")
        print("============================================================")
        sys.exit(1)

if __name__ == "__main__":
    main()
