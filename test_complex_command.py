#!/usr/bin/env python3
"""
Test complex ObjectScript command to isolate the timeout issue
"""

import json
import os
import sys

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

def test_command(command):
    """Test a specific command"""
    try:
        print(f"🔌 Connecting to IRIS...")
        conn = iris.connect(
            IRIS_CONFIG['hostname'], 
            IRIS_CONFIG['port'], 
            IRIS_CONFIG['namespace'], 
            IRIS_CONFIG['username'], 
            IRIS_CONFIG['password']
        )
        iris_obj = iris.createIRIS(conn)
        
        print(f"⚡ Testing command: {command}")
        result = iris_obj.classMethodString(
            "SessionMCP.Core.Session",
            "ExecuteCommandDirect",
            command,
            "HSCUSTOM"
        )
        
        conn.close()
        
        # Parse and display result
        result_data = json.loads(result)
        print(f"\n📋 Status: {result_data.get('status')}")
        print(f"📋 Output: {result_data.get('output')}")
        print(f"📋 Time: {result_data.get('executionTimeMs')}ms")
        
        if result_data.get('errorMessage'):
            print(f"📋 Error: {result_data.get('errorMessage')}")
            
        return result_data.get('status') == 'success'
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Complex ObjectScript Commands")
    print("=" * 50)
    
    # Test the commands
    commands = [
        'WRITE "Simple test"',
        'SET result = $HOROLOG WRITE "Current IRIS time: ", result',
        'SET x=5 SET y=10 WRITE "Sum: ", x+y'
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n🔹 Test {i}: {cmd}")
        success = test_command(cmd)
        print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
