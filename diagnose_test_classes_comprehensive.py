#!/usr/bin/env python3
"""
Comprehensive diagnostic to find all test classes and investigate namespace issues.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from iris_execute_mcp import call_iris_sync

# Load environment variables
load_dotenv()

def diagnose_test_classes():
    """Comprehensive diagnostic of test class issues."""
    print("=" * 80)
    print("COMPREHENSIVE TEST CLASS DIAGNOSTIC")
    print("=" * 80)
    
    # 1. Check what test classes exist in HSCUSTOM
    print("\n1. SEARCHING FOR ALL TEST CLASSES IN HSCUSTOM:")
    print("-" * 50)
    
    # Find all classes with "Test" in the name - use simple single-line command
    command = "Set tCount=0 Set tClass=$ORDER(^oddDEF(\"\")) While tClass'=\"\" { If (tClass[\"Test\") { Set tCount=tCount+1 } Set tClass=$ORDER(^oddDEF(tClass)) } Write \"Total Test classes found: \",tCount"
    
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        [command, "HSCUSTOM"]
    )
    print(f"Test classes in HSCUSTOM: {result}")
    
    # 2. Check specifically for ExecuteMCP.Test classes
    print("\n2. CHECKING ExecuteMCP.Test HIERARCHY:")
    print("-" * 50)
    
    execute_test_classes = [
        "ExecuteMCP.Test.SampleUnitTest",
        "ExecuteMCP.Test.SimpleTest",
        "ExecuteMCP.Test.ErrorTest"
    ]
    
    for cls in execute_test_classes:
        # Single-line command
        command = f"If ##class(%Dictionary.CompiledClass).%ExistsId(\"{cls}\") {{ Write \"{cls}: EXISTS (Compiled)\" }} ElseIf ##class(%Dictionary.ClassDefinition).%ExistsId(\"{cls}\") {{ Write \"{cls}: EXISTS (Not compiled)\" }} Else {{ Write \"{cls}: NOT FOUND\" }}"
        result = call_iris_sync(
            "ExecuteMCP.Core.Command",
            "ExecuteCommand",
            [command, "HSCUSTOM"]
        )
        print(result)
    
    # 3. Check source files on disk
    print("\n3. CHECKING SOURCE FILES ON DISK:")
    print("-" * 50)
    
    src_path = "src/ExecuteMCP/Test"
    if os.path.exists(src_path):
        files = os.listdir(src_path)
        print(f"Files in {src_path}:")
        for f in files:
            if f.endswith('.cls'):
                print(f"  - {f}")
    else:
        print(f"Directory {src_path} not found!")
    
    # 4. Check if Patterns package exists anywhere
    print("\n4. SEARCHING FOR Patterns PACKAGE:")
    print("-" * 50)
    
    # Single-line command
    command = "Set tFound=0 Set tClass=$ORDER(^oddDEF(\"\")) While tClass'=\"\" { If $PIECE(tClass,\".\",1)=\"Patterns\" { Set tFound=1 } Set tClass=$ORDER(^oddDEF(tClass)) } If tFound Write \"Patterns package found\" Else Write \"No Patterns.* classes found in namespace\""
    
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        [command, "HSCUSTOM"]
    )
    print(f"Patterns package search: {result}")
    
    # 5. Check compilation status
    print("\n5. ATTEMPTING TO COMPILE ExecuteMCP.Test CLASSES:")
    print("-" * 50)
    
    # Try to compile the test classes - single line
    command = "Set tSC=$SYSTEM.OBJ.CompilePackage(\"ExecuteMCP.Test\",\"bckry\") If $$$ISOK(tSC) { Write \"Compilation successful\" } Else { Write \"Compilation failed\" }"
    
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        [command, "HSCUSTOM"]
    )
    print(f"Compilation result: {result}")
    
    # 6. Check ^UnitTestRoot global
    print("\n6. CHECKING ^UnitTestRoot CONFIGURATION:")
    print("-" * 50)
    
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "GetGlobal",
        ["^UnitTestRoot", "HSCUSTOM"]
    )
    print(f"^UnitTestRoot value: {result}")
    
    # 7. List all namespaces to see if tests are elsewhere
    print("\n7. LISTING ALL NAMESPACES:")
    print("-" * 50)
    
    # Single-line command
    command = "Set tList=\"\" Set tRS=##class(%SQL.Statement).%ExecDirect(,\"SELECT Name FROM %SYS.Namespace\") While tRS.%Next() { Set tList=tList_tRS.Name_\", \" } Write tList"
    
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        [command, "%SYS"]
    )
    print(f"Available namespaces:\n{result}")
    
    # 8. Check if tests run despite "not found" status
    print("\n8. ATTEMPTING DIRECT TEST EXECUTION:")
    print("-" * 50)
    
    # Single-line command
    command = "Try { Do ##class(ExecuteMCP.Test.SampleUnitTest).TestAddition() Write \"Direct method call succeeded\" } Catch ex { Write \"Direct method call failed: \",ex.Name }"
    
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        [command, "HSCUSTOM"]
    )
    print(f"Direct execution test: {result}")
    
    # 9. Check actual file system vs IRIS sync
    print("\n9. VERIFYING VS CODE OBJECTSCRIPT SYNC:")
    print("-" * 50)
    
    # Check if VS Code ObjectScript extension files exist
    vscode_path = ".vscode/settings.json"
    if os.path.exists(vscode_path):
        print("VS Code settings.json exists - checking content...")
        with open(vscode_path, 'r') as f:
            content = f.read()
            if 'objectscript' in content.lower():
                print("ObjectScript extension configured in VS Code")
            else:
                print("ObjectScript extension not configured in VS Code settings")
    else:
        print("No .vscode/settings.json found")
    
    # 10. Count ExecuteMCP classes in namespace
    print("\n10. COUNTING ExecuteMCP CLASSES:")
    print("-" * 50)
    
    command = "Set tCount=0 Set tClass=$ORDER(^oddDEF(\"\")) While tClass'=\"\" { If $EXTRACT(tClass,1,10)=\"ExecuteMCP\" { Set tCount=tCount+1 } Set tClass=$ORDER(^oddDEF(tClass)) } Write \"ExecuteMCP classes found: \",tCount"
    
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        [command, "HSCUSTOM"]
    )
    print(result)
    
    # 11. Try to list some actual test class names that do exist
    print("\n11. LISTING FIRST 10 CLASSES WITH 'Test' IN NAME:")
    print("-" * 50)
    
    command = "Set tCount=0 Set tClass=$ORDER(^oddDEF(\"\")) While (tClass'=\"\")&(tCount<10) { If (tClass[\"Test\") { Write tClass,\" \" Set tCount=tCount+1 } Set tClass=$ORDER(^oddDEF(tClass)) }"
    
    result = call_iris_sync(
        "ExecuteMCP.Core.Command",
        "ExecuteCommand",
        [command, "HSCUSTOM"]
    )
    print(f"Test classes found: {result}")
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    diagnose_test_classes()
