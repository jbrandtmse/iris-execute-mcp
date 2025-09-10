#!/usr/bin/env python3
"""
Detailed diagnosis of TestRunner Discovery issues
"""

import os
import sys
from pathlib import Path
import iris

# Connect to IRIS
namespace = "HSCUSTOM"
conn = iris.connect("localhost", 1972, namespace, "_SYSTEM", "_SYSTEM")
irispy = iris.createIRIS(conn)

print("=" * 80)
print("TESTRUNNER DISCOVERY DETAILED DIAGNOSIS")
print("=" * 80)

# Step 1: Check if test classes exist
print("\n1. Checking if ExecuteMCP.Test classes exist:")
test_classes = ["ExecuteMCP.Test.SampleUnitTest", "ExecuteMCP.Test.SimpleTest", "ExecuteMCP.Test.ErrorTest"]
for cls in test_classes:
    try:
        result = irispy.classMethodValue("ExecuteMCP.Core.Command", "ExecuteCommand", 
                                        f"IF ##class(%Dictionary.CompiledClass).%ExistsId(\"{cls}\") WRITE \"EXISTS\" ELSE WRITE \"NOT FOUND\"")
        output = result if isinstance(result, str) else str(result)
        if "EXISTS" in output:
            print(f"  ✓ {cls}: EXISTS")
        else:
            print(f"  ✗ {cls}: NOT FOUND")
    except Exception as e:
        print(f"  ? {cls}: Error checking - {e}")

# Step 2: Check if they extend %UnitTest.TestCase
print("\n2. Checking inheritance for existing classes:")
for cls in test_classes:
    try:
        # Check Super property
        result = irispy.classMethodValue("ExecuteMCP.Core.Command", "ExecuteCommand",
            f"SET tClass = ##class(%Dictionary.CompiledClass).%OpenId(\"{cls}\") IF $ISOBJECT(tClass) WRITE \"Super: \",tClass.Super ELSE WRITE \"Class not found\"")
        output = result if isinstance(result, str) else str(result)
        print(f"  {cls}: {output}")
    except Exception as e:
        print(f"  {cls}: Error - {e}")

# Step 3: Test Discovery.DiscoverTestClasses directly
print("\n3. Testing Discovery.DiscoverTestClasses(\"ExecuteMCP.Test\"):")
try:
    # Create temporary debug method to test discovery
    debug_code = """
    Set tClasses = ##class(ExecuteMCP.TestRunner.Discovery).DiscoverTestClasses("ExecuteMCP.Test")
    Write "Classes found: ", tClasses.%Size(), !
    Set tIter = tClasses.%GetIterator()
    While tIter.%GetNext(.tKey, .tClass) {
        Write "  - ", tClass, !
    }
    """
    result = irispy.classMethodValue("ExecuteMCP.Core.Command", "ExecuteCommand", debug_code)
    output = result if isinstance(result, str) else str(result)
    print(output)
except Exception as e:
    print(f"  Error: {e}")

# Step 4: Test the SQL query directly
print("\n4. Testing SQL query used in DiscoverTestClasses:")
try:
    sql_test = """
    SET tSQL = "SELECT Name FROM %Dictionary.CompiledClassDefinition WHERE Name %STARTSWITH ?"
    SET tStatement = ##class(%SQL.Statement).%New()
    SET tSC = tStatement.%Prepare(tSQL)
    IF $$$ISERR(tSC) WRITE "Prepare failed" QUIT
    SET tResultSet = tStatement.%Execute("ExecuteMCP.Test.")
    SET tCount = 0
    WHILE tResultSet.%Next() {
        SET tCount = tCount + 1
        WRITE "Found: ", tResultSet.%Get("Name"), !
    }
    WRITE "Total found: ", tCount, !
    """
    result = irispy.classMethodValue("ExecuteMCP.Core.Command", "ExecuteCommand", sql_test)
    output = result if isinstance(result, str) else str(result)
    print(output)
except Exception as e:
    print(f"  Error: {e}")

# Step 5: Test IsTestClass method for each class
print("\n5. Testing Discovery.IsTestClass for each class:")
for cls in test_classes:
    try:
        result = irispy.classMethodValue("ExecuteMCP.TestRunner.Discovery", "IsTestClass", cls)
        print(f"  {cls}: IsTestClass = {result}")
    except Exception as e:
        print(f"  {cls}: Error - {e}")

# Step 6: Debug IsTestClass method internals
print("\n6. Debugging IsTestClass logic:")
for cls in test_classes:
    try:
        debug_istest = f"""
        SET tClassName = "{cls}"
        TRY {{
            SET tClassDef = ##class(%Dictionary.CompiledClass).%OpenId(tClassName)
            IF '$ISOBJECT(tClassDef) {{
                WRITE "Class not found", !
                QUIT
            }}
            WRITE "Class opened", !
            SET tSuper = tClassDef.Super
            WRITE "Super: ", tSuper, !
            IF tSuper [ "%UnitTest.TestCase" {{
                WRITE "Direct inheritance detected", !
            }} ELSE {{
                WRITE "No direct inheritance", !
                // Try %Extends check
                IF ##class({cls}).%Extends("%UnitTest.TestCase") {{
                    WRITE "Extends check: YES", !
                }} ELSE {{
                    WRITE "Extends check: NO", !
                }}
            }}
        }} CATCH ex {{
            WRITE "Error: ", ex.DisplayString(), !
        }}
        """
        result = irispy.classMethodValue("ExecuteMCP.Core.Command", "ExecuteCommand", debug_istest)
        output = result if isinstance(result, str) else str(result)
        print(f"\n  {cls}:")
        print(f"    {output}")
    except Exception as e:
        print(f"  {cls}: Error - {e}")

# Step 7: Alternative inheritance check
print("\n7. Alternative inheritance check using %Extends:")
for cls in test_classes:
    try:
        check_extends = f"""
        IF ##class({cls}).%Extends("%UnitTest.TestCase") {{
            WRITE "YES - Extends %UnitTest.TestCase"
        }} ELSE {{
            WRITE "NO - Does not extend %UnitTest.TestCase"
        }}
        """
        result = irispy.classMethodValue("ExecuteMCP.Core.Command", "ExecuteCommand", check_extends)
        output = result if isinstance(result, str) else str(result)
        print(f"  {cls}: {output}")
    except Exception as e:
        print(f"  {cls}: Error - {e}")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
