#!/usr/bin/env python
"""Debug SQL query in Discovery.DiscoverTestClasses"""

import json
from iris_execute_mcp import call_iris_sync

def test_sql_variations():
    """Test different SQL query variations to find classes"""
    
    print("=" * 80)
    print("TESTING SQL QUERY VARIATIONS")
    print("=" * 80)
    
    # Test 1: Direct query with exact prefix
    print("\n1. Testing with exact prefix 'ExecuteMCP.Test.'")
    command = """
    SET tSQL = "SELECT Name FROM %Dictionary.CompiledClassDefinition WHERE Name %STARTSWITH ?"
    SET tStatement = ##class(%SQL.Statement).%New()
    SET tSC = tStatement.%Prepare(tSQL)
    SET tResultSet = tStatement.%Execute("ExecuteMCP.Test.")
    SET tCount = 0
    WHILE tResultSet.%Next() {
        SET tCount = tCount + 1
        WRITE "Found: " _ tResultSet.%Get("Name"), !
    }
    WRITE "Total found with 'ExecuteMCP.Test.': " _ tCount, !
    """
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        command,
        "HSCUSTOM"
    )
    print(f"Result: {json.loads(result).get('output', 'No output')}")
    
    # Test 2: Query without the dot
    print("\n2. Testing without trailing dot - 'ExecuteMCP.Test'")
    command = """
    SET tSQL = "SELECT Name FROM %Dictionary.CompiledClassDefinition WHERE Name %STARTSWITH ?"
    SET tStatement = ##class(%SQL.Statement).%New()
    SET tSC = tStatement.%Prepare(tSQL)
    SET tResultSet = tStatement.%Execute("ExecuteMCP.Test")
    SET tCount = 0
    WHILE tResultSet.%Next() {
        SET tCount = tCount + 1
        WRITE "Found: " _ tResultSet.%Get("Name"), !
    }
    WRITE "Total found with 'ExecuteMCP.Test': " _ tCount, !
    """
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        command,
        "HSCUSTOM"
    )
    print(f"Result: {json.loads(result).get('output', 'No output')}")
    
    # Test 3: Use LIKE instead of %STARTSWITH
    print("\n3. Testing with LIKE pattern 'ExecuteMCP.Test%'")
    command = """
    SET tSQL = "SELECT Name FROM %Dictionary.CompiledClassDefinition WHERE Name LIKE ?"
    SET tStatement = ##class(%SQL.Statement).%New()
    SET tSC = tStatement.%Prepare(tSQL)
    SET tResultSet = tStatement.%Execute("ExecuteMCP.Test%")
    SET tCount = 0
    WHILE tResultSet.%Next() {
        SET tCount = tCount + 1
        WRITE "Found: " _ tResultSet.%Get("Name"), !
    }
    WRITE "Total found with LIKE 'ExecuteMCP.Test%': " _ tCount, !
    """
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        command,
        "HSCUSTOM"
    )
    print(f"Result: {json.loads(result).get('output', 'No output')}")
    
    # Test 4: Check if the classes exist at all
    print("\n4. Checking if specific classes exist in %Dictionary.CompiledClassDefinition")
    for class_name in ["ExecuteMCP.Test.SampleUnitTest", "ExecuteMCP.Test.SimpleTest", "ExecuteMCP.Test.ErrorTest"]:
        command = f"""
        SET tSQL = "SELECT Name FROM %Dictionary.CompiledClassDefinition WHERE Name = ?"
        SET tStatement = ##class(%SQL.Statement).%New()
        SET tSC = tStatement.%Prepare(tSQL)
        SET tResultSet = tStatement.%Execute("{class_name}")
        IF tResultSet.%Next() {{
            WRITE "FOUND: {class_name}", !
        }} ELSE {{
            WRITE "NOT FOUND: {class_name}", !
        }}
        """
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            command,
            "HSCUSTOM"
        )
        print(f"  {json.loads(result).get('output', 'No output')}")
    
    # Test 5: Query %Dictionary.CompiledClass instead
    print("\n5. Testing with %Dictionary.CompiledClass table")
    command = """
    SET tSQL = "SELECT ID FROM %Dictionary.CompiledClass WHERE ID %STARTSWITH ?"
    SET tStatement = ##class(%SQL.Statement).%New()
    SET tSC = tStatement.%Prepare(tSQL)
    SET tResultSet = tStatement.%Execute("ExecuteMCP.Test.")
    SET tCount = 0
    WHILE tResultSet.%Next() {
        SET tCount = tCount + 1
        WRITE "Found: " _ tResultSet.%Get("ID"), !
    }
    WRITE "Total found in CompiledClass: " _ tCount, !
    """
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        command,
        "HSCUSTOM"
    )
    print(f"Result: {json.loads(result).get('output', 'No output')}")
    
    print("\n" + "=" * 80)
    print("SQL debug complete")
    print("=" * 80)

if __name__ == "__main__":
    test_sql_variations()
