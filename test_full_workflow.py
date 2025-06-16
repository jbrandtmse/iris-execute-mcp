#!/usr/bin/env python3
"""Test complete IRIS SessionMCP workflow with security"""

import iris
import json

try:
    # Connect to IRIS
    conn = iris.connect('localhost', 1972, 'HSCUSTOM', '_SYSTEM', '_SYSTEM')
    iris_obj = iris.createIRIS(conn)
    
    print("=== Step 1: Create Session ===")
    create_result = iris_obj.classMethodString('SessionMCP.Core.Session', 'CreateSession', 'HSCUSTOM', '')
    print('CreateSession result:', create_result)
    
    create_data = json.loads(create_result)
    if create_data.get('status') == 'success':
        session_id = create_data.get('sessionId')
        print(f'✅ Session created: {session_id}')
        
        print("\n=== Step 2: Execute Command ===")
        execute_result = iris_obj.classMethodString('SessionMCP.Core.Session', 'ExecuteCommand', session_id, 'write "Hello World from IRIS via MCP - REAL Integration!"', 30)
        print('ExecuteCommand result:', execute_result)
        
        execute_data = json.loads(execute_result)
        print('Status:', execute_data.get('status'))
        if execute_data.get('status') == 'error':
            print('Error Message:', execute_data.get('errorMessage'))
        else:
            print('✅ Command executed successfully!')
            print('Output:', execute_data.get('output'))
            print('Execution Time:', execute_data.get('executionTimeMs'), 'ms')
    else:
        print('❌ Failed to create session:', create_data.get('errorMessage'))
    
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
