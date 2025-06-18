#!/usr/bin/env python3
"""Quick test of ExecuteMCP.Core.Command class"""

import os
import json
import sys

# Set environment
os.environ['IRIS_HOSTNAME'] = 'localhost'
os.environ['IRIS_PORT'] = '1972'
os.environ['IRIS_NAMESPACE'] = 'HSCUSTOM'
os.environ['IRIS_USERNAME'] = '_SYSTEM'
os.environ['IRIS_PASSWORD'] = '_SYSTEM'

try:
    import iris
    print("✅ IRIS package available")
    
    # Test connection
    conn = iris.connect('localhost', 1972, 'HSCUSTOM', '_SYSTEM', '_SYSTEM')
    iris_obj = iris.createIRIS(conn)
    
    # Test if ExecuteMCP.Core.Command class exists
    try:
        result = iris_obj.classMethodString("ExecuteMCP.Core.Command", "GetSystemInfo")
        print("✅ ExecuteMCP.Core.Command.GetSystemInfo() works")
        print(f"Result: {result}")
        
        # Test simple command
        result2 = iris_obj.classMethodString("ExecuteMCP.Core.Command", "ExecuteCommand", "WRITE 5*5", "HSCUSTOM")
        print("✅ ExecuteMCP.Core.Command.ExecuteCommand() works")
        print(f"Result: {result2}")
        
    except Exception as e:
        print(f"❌ ExecuteMCP.Core.Command class error: {e}")
        print("This suggests the class needs to be compiled in IRIS")
    
    conn.close()
    
except ImportError:
    print("❌ intersystems-iris package not available")
except Exception as e:
    print(f"❌ IRIS connection error: {e}")
