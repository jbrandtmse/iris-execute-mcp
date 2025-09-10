#!/usr/bin/env python3
"""
Check for Patterns.Test classes in other IRIS namespaces
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from iris_execute_mcp import call_iris_sync
import json

def check_namespace_for_patterns(namespace):
    """Check if Patterns.Test classes exist in a specific namespace"""
    print(f"\nChecking namespace: {namespace}")
    print("=" * 50)
    
    try:
        # Check if Patterns.Test package exists
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand", 
            f"IF ##class(%Dictionary.PackageDefinition).%ExistsId(\"Patterns.Test\") {{ WRITE \"Patterns.Test EXISTS\" }} ELSE {{ WRITE \"Patterns.Test NOT FOUND\" }}",
            namespace
        )
        
        if "error" not in str(result).lower():
            print(f"  Patterns.Test package: {result.get('output', 'Check failed')}")
        else:
            print(f"  Error checking Patterns.Test: {result}")
            
        # Try to count test classes using SQL
        sql_query = "SELECT COUNT(*) AS TestCount FROM %Dictionary.ClassDefinition WHERE Name LIKE 'Patterns.Test%' AND Super [ 'UnitTest.TestCase'"
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            f"&sql({sql_query})",
            namespace
        )
        
        if "error" not in str(result).lower():
            print(f"  SQL query result: {result.get('output', 'No output')}")
        else:
            print(f"  SQL query failed: {result}")
            
    except Exception as e:
        print(f"  Error accessing namespace {namespace}: {e}")

def main():
    print("Searching for Patterns.Test classes across namespaces")
    print("=" * 60)
    
    # Common namespaces to check
    namespaces = [
        "HSCUSTOM",
        "USER", 
        "SAMPLES",
        "%SYS",
        "ENSEMBLE",
        "HSLIB"
    ]
    
    for ns in namespaces:
        check_namespace_for_patterns(ns)
    
    print("\n" + "=" * 60)
    print("Search complete.")
    print("\nConclusion:")
    print("If Patterns.Test classes are not found in any namespace,")
    print("they may need to be:")
    print("  1. Imported from source files")
    print("  2. Created from scratch")
    print("  3. Loaded from a different IRIS instance")

if __name__ == "__main__":
    main()
