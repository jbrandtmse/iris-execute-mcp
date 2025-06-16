#!/usr/bin/env python3
"""Basic HTTP test without JSON-RPC complexity."""

import socket
import sys

def test_basic_http():
    """Test basic HTTP connection."""
    try:
        print("🧪 Testing basic HTTP connection to localhost:8765...")
        
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        # Connect
        print("📡 Connecting...")
        sock.connect(('127.0.0.1', 8765))
        print("✅ Connected!")
        
        # Send simple GET request
        request = b"GET /mcp HTTP/1.1\r\nHost: localhost:8765\r\n\r\n"
        print("📤 Sending GET request...")
        sock.send(request)
        
        # Receive response
        print("📥 Waiting for response...")
        response = sock.recv(1024)
        print("✅ Response received!")
        print(f"📋 Response (first 200 chars): {response[:200]}")
        
        sock.close()
        print("🎉 SUCCESS: Server is responding to HTTP requests!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_basic_http()
    sys.exit(0 if success else 1)
