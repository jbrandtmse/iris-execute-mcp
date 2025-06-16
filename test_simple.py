#!/usr/bin/env python3
"""Simple test using built-in urllib."""

import json
import urllib.request
import urllib.parse

def test_mcp():
    """Test MCP server with built-in libraries."""
    url = "http://localhost:8765/mcp"
    
    # Test connection
    test_data = {
        "jsonrpc": "2.0",
        "method": "call_tool",
        "params": {
            "name": "test_connection",
            "arguments": {}
        },
        "id": 1
    }
    
    try:
        # Create request
        data = json.dumps(test_data).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        req.add_header('Content-Type', 'application/json')
        
        print("🧪 Testing IRIS Session MCP Server...")
        print("Sending test_connection request...")
        
        # Send request
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✅ Response received: {response.status}")
            print(f"📋 Result: {json.dumps(result, indent=2)}")
            
            if 'result' in result:
                content = json.loads(result['result']['content'][0]['text'])
                if content.get('status') == 'success':
                    print("🎉 SUCCESS: IRIS connection test passed!")
                    return True
            
        return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_mcp()
