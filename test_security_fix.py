#!/usr/bin/env python3
"""Test the security fix for SessionMCP XECUTE permissions"""

import iris
import json

try:
    # Connect to IRIS
    conn = iris.connect('localhost', 1972, 'HSCUSTOM', '_SYSTEM', '_SYSTEM')
    iris_obj = iris.createIRIS(conn)
    
    # Test ExecuteCommand with security check
    result = iris_obj.classMethodString('SessionMCP.Core.Session', 'ExecuteCommand', 'TEST-SESSION-ID', 'write "Hello World"', 30)
    print('ExecuteCommand result:', result)
    
    # Parse JSON result
    result_data = json.loads(result)
    print('Status:', result_data.get('status'))
    print('Error Message:', result_data.get('errorMessage', 'None'))
    
    conn.close()
    
except Exception as e:
    print(f'Error: {e}')
