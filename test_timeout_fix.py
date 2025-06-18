#!/usr/bin/env python3
"""
Test the timeout fix implementation
"""

import sys
import os
sys.path.append('.')

from iris_execute_fastmcp import call_iris_with_timeout
import json

def test_timeout_fix():
    print("🔧 Testing Timeout Fix Implementation")
    print("=" * 50)
    
    try:
        # Test with 5 second timeout (should be plenty for simple command)
        result = call_iris_with_timeout(
            'ExecuteMCP.Core.Command', 
            'ExecuteCommand', 
            5.0,  # 5 second timeout
            'WRITE $ZV', 
            'HSCUSTOM'
        )
        
        print("✅ TIMEOUT FIX RESULT:")
        print(result)
        
        # Parse the result
        parsed = json.loads(result)
        
        if parsed.get("status") == "success":
            print("\n🎉 SUCCESS: Timeout fix is working!")
        elif "timeout" in parsed:
            print(f"\n⚠️  TIMEOUT: Operation timed out after {parsed['timeout']}s")
        else:
            print(f"\n❌ ERROR: {parsed.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n💥 EXCEPTION: {str(e)}")

if __name__ == "__main__":
    test_timeout_fix()
