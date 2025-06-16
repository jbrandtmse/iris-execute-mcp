#!/usr/bin/env python3
"""
Test Hello World functionality with IRIS Session MCP Server
"""

import json
import requests
import sys

def test_hello_world():
    """Test Hello World via MCP server."""
    print("🧪 Testing Hello World with IRIS Session MCP Server")
    print("=" * 50)
    
    # MCP server endpoint
    url = "http://localhost:8765/mcp"
    headers = {"Content-Type": "application/json"}
    
    try:
        # Test 1: Connection test
        print("1️⃣ Testing IRIS connection...")
        test_request = {
            "jsonrpc": "2.0",
            "method": "call_tool",
            "params": {
                "name": "test_connection",
                "arguments": {}
            },
            "id": 1
        }
        
        response = requests.post(url, headers=headers, json=test_request, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'result' in result:
                content = json.loads(result['result']['content'][0]['text'])
                print(f"   ✅ Connection: {content.get('status', 'unknown')}")
                print(f"   📋 IRIS Version: {content.get('iris_version', 'unknown')}")
                print(f"   📁 Namespace: {content.get('namespace', 'unknown')}")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
        
        print()
        
        # Test 2: Hello World command
        print("2️⃣ Testing Hello World command...")
        hello_request = {
            "jsonrpc": "2.0",
            "method": "call_tool",
            "params": {
                "name": "execute_command",
                "arguments": {
                    "command": "write \"Hello World from IRIS via MCP!\"",
                    "namespace": "HSCUSTOM"
                }
            },
            "id": 2
        }
        
        response = requests.post(url, headers=headers, json=hello_request, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'result' in result:
                content = json.loads(result['result']['content'][0]['text'])
                print(f"   ✅ Command Status: {content.get('status', 'unknown')}")
                print(f"   🆔 Session ID: {content.get('sessionId', 'unknown')}")
                print(f"   ⏱️  Execution Time: {content.get('executionTimeMs', 0)}ms")
                print(f"   📜 Output: {content.get('output', 'No output')}")
                
                if content.get('status') == 'success':
                    print("\n🎉 SUCCESS: Hello World executed in IRIS!")
                    return True
                else:
                    print(f"\n❌ Command failed: {content.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {str(e)}")
        print("💡 Make sure the MCP server is running: python iris_session_mcp_standard.py")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_hello_world()
    sys.exit(0 if success else 1)
