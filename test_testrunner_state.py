#!/usr/bin/env python
"""
Check the current state of TestRunner classes and identify issues
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iris_execute_mcp import call_iris_sync

def check_testrunner_state():
    """Check if TestRunner classes exist and their state"""
    print("="*80)
    print("TestRunner State Check")
    print("="*80)
    print()
    
    # Check if classes exist
    classes = [
        "ExecuteMCP.TestRunner.Manager",
        "ExecuteMCP.TestRunner.Context",
        "ExecuteMCP.TestRunner.Discovery"
    ]
    
    for class_name in classes:
        print(f"Checking {class_name}...")
        try:
            result = call_iris_sync("execute_command", {
                "command": f"WRITE ##class(%Dictionary.CompiledClass).%ExistsId(\"{class_name}\")",
                "namespace": "HSCUSTOM"
            })
            
            result_dict = json.loads(result)
            if result_dict.get("status") == "success":
                output = result_dict.get("output", "")
                exists = output.strip() == "1"
                print(f"  Exists: {exists}")
                
                if exists:
                    # Check for key methods
                    if class_name == "ExecuteMCP.TestRunner.Manager":
                        # Check if Context property has InitialExpression
                        check_result = call_iris_sync("execute_command", {
                            "command": f"SET prop = ##class(%Dictionary.CompiledProperty).%OpenId(\"{class_name}||Context\") WRITE $ISOBJECT(prop)",
                            "namespace": "HSCUSTOM"
                        })
                        prop_dict = json.loads(check_result)
                        print(f"  Context property exists: {prop_dict.get('output', '').strip()}")
                        
                        # Check if RunTests method exists
                        method_result = call_iris_sync("execute_command", {
                            "command": f"WRITE ##class(%Dictionary.CompiledMethod).%ExistsId(\"{class_name}||RunTests\")",
                            "namespace": "HSCUSTOM"
                        })
                        method_dict = json.loads(method_result)
                        print(f"  RunTests method exists: {method_dict.get('output', '').strip() == '1'}")
            else:
                print(f"  Error checking class: {result_dict.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"  Exception: {e}")
        print()
    
    # Now try a simple test with the Manager
    print("Testing Manager instantiation...")
    try:
        result = call_iris_sync("execute_command", {
            "command": "SET mgr = ##class(ExecuteMCP.TestRunner.Manager).%New() WRITE $ISOBJECT(mgr)",
            "namespace": "HSCUSTOM"
        })
        
        result_dict = json.loads(result)
        if result_dict.get("status") == "success":
            output = result_dict.get("output", "")
            print(f"  Manager can be instantiated: {output.strip() == '1'}")
            
            # Check if Context is initialized
            ctx_result = call_iris_sync("execute_command", {
                "command": "SET mgr = ##class(ExecuteMCP.TestRunner.Manager).%New() WRITE $ISOBJECT(mgr.Context)",
                "namespace": "HSCUSTOM"
            })
            ctx_dict = json.loads(ctx_result)
            print(f"  Context auto-initialized: {ctx_dict.get('output', '').strip() == '1'}")
        else:
            print(f"  Error instantiating Manager: {result_dict.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  Exception: {e}")
    
    # Try to run a simple method directly
    print("\nTesting direct method call...")
    try:
        result = call_iris_sync("execute_classmethod", {
            "class_name": "ExecuteMCP.TestRunner.Manager",
            "method_name": "ValidateTestRunner",
            "namespace": "HSCUSTOM"
        })
        
        result_dict = json.loads(result)
        if result_dict.get("status") == "success":
            print("  ValidateTestRunner result:")
            output = result_dict.get("result", "")
            try:
                output_json = json.loads(output) if output else {}
                print(f"    Status: {output_json.get('status', 'Unknown')}")
                if output_json.get('status') != 'success':
                    print(f"    Error: {output_json.get('error', 'Unknown error')}")
                    print(f"    Details: {output_json.get('details', 'No details')}")
            except:
                print(f"    Raw output: {output}")
        else:
            print(f"  Error calling method: {result_dict.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  Exception: {e}")
    
    print("\n" + "="*80)
    print("State Check Complete")
    print("="*80)

if __name__ == "__main__":
    check_testrunner_state()
