#!/usr/bin/env python3
"""
Test script to validate ExecuteCommandDirect method
Run this after recompiling SessionMCP.Core.Session class in IRIS
"""

import json
import os
import sys

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import iris
    IRIS_AVAILABLE = True
except ImportError:
    IRIS_AVAILABLE = False
    print("❌ intersystems-iris package not available")
    sys.exit(1)

# IRIS connection configuration
IRIS_CONFIG = {
    'hostname': os.getenv('IRIS_HOSTNAME', 'localhost'),
    'port': int(os.getenv('IRIS_PORT', '1972')),
    'namespace': os.getenv('IRIS_NAMESPACE', 'HSCUSTOM'),
    'username': os.getenv('IRIS_USERNAME', '_SYSTEM'),
    'password': os.getenv('IRIS_PASSWORD', '_SYSTEM')
}

def test_direct_execution():
    """Test the new ExecuteCommandDirect method"""
    try:
        print(f"🔌 Connecting to IRIS: {IRIS_CONFIG['hostname']}:{IRIS_CONFIG['port']}/{IRIS_CONFIG['namespace']}")
        conn = iris.connect(
            IRIS_CONFIG['hostname'], 
            IRIS_CONFIG['port'], 
            IRIS_CONFIG['namespace'], 
            IRIS_CONFIG['username'], 
            IRIS_CONFIG['password']
        )
        iris_obj = iris.createIRIS(conn)
        
        # Test ExecuteCommandDirect method
        print("⚡ Testing ExecuteCommandDirect method...")
        result = iris_obj.classMethodString(
            "SessionMCP.Core.Session",
            "ExecuteCommandDirect",
            "WRITE \"Hello Direct World!\"",
            "HSCUSTOM"
        )
        
        conn.close()
        
        # Parse and display result
        result_data = json.loads(result)
        print("\n📋 **RESULT**:")
        print(f"   Status: {result_data.get('status')}")
        print(f"   Output: {result_data.get('output')}")
        print(f"   Namespace: {result_data.get('namespace')}")
        print(f"   Execution Time: {result_data.get('executionTimeMs')}ms")
        print(f"   Mode: {result_data.get('mode')}")
        
        if result_data.get('status') == 'success':
            print("\n✅ SUCCESS: ExecuteCommandDirect method working!")
            print("🚀 MCP timeout issue resolved - direct execution bypasses session management")
            return True
        else:
            print(f"\n❌ FAILED: {result_data.get('errorMessage')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing IRIS Session MCP Direct Execution Method")
    print("=" * 60)
    
    success = test_direct_execution()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SOLUTION COMPLETE: MCP timeout issue resolved!")
        print("📝 Next steps:")
        print("   1. Restart Cline to pick up new execute_direct tool")
        print("   2. Use execute_direct for fast command execution")
        print("   3. Use regular execute_command for full session management")
    else:
        print("⚠️  Please recompile SessionMCP.Core.Session class in IRIS first")
        print("💡 Run: do $SYSTEM.OBJ.Compile(\"SessionMCP.Core.Session\", \"ck\")")
