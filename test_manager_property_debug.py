#!/usr/bin/env python3
"""Debug Manager property setting in TestRunner"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from iris_execute_mcp import call_iris_sync

def test_manager_property():
    """Test setting Manager property on test instance"""
    from intersystems_irispython import iris
    
    # Connect to IRIS
    connection_config = {
        "hostname": "localhost",
        "port": 1972,
        "namespace": "HSCUSTOM",
        "username": "_SYSTEM",
        "password": "1234"
    }
    
    connection = iris.connect(**connection_config)
    
    print("Testing Manager property setting...")
    
    # Test 1: Create test instance and check Manager property
    command = """
    Set tTestClass = "ExecuteMCP.Test.SimpleTest"
    Set tTestInstance = $CLASSMETHOD(tTestClass, "%New", "")
    Write "Test instance created: ", $ISOBJECT(tTestInstance), !
    
    ; Check if Manager property exists and is accessible
    Try {
        Set tHasManager = $ISOBJECT(tTestInstance.Manager)
        Write "Manager property exists but is null: ", 'tHasManager, !
    } Catch ex {
        Write "Cannot access Manager property: ", ex.DisplayString(), !
    }
    
    ; Try setting Manager directly
    Try {
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set tTestInstance.Manager = tManager
        Write "Direct assignment succeeded", !
    } Catch ex {
        Write "Direct assignment failed: ", ex.DisplayString(), !
    }
    
    ; Try indirect reference
    Try {
        Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
        Set @("tTestInstance.Manager") = tManager
        Write "Indirect reference succeeded", !
    } Catch ex {
        Write "Indirect reference failed: ", ex.DisplayString(), !
    }
    
    Write "Done", !
    """
    
    result = call_iris_sync(connection, "ExecuteMCP.Core.Command", "ExecuteCommand", command, "HSCUSTOM")
    result_json = json.loads(result)
    print("Result:", result_json.get("output", ""))
    
    # Test 2: Check if Manager is a private property
    print("\nChecking Manager property definition...")
    command = """
    Set tClass = ##class(%Dictionary.CompiledClass).%OpenId("ExecuteMCP.Test.SimpleTest")
    If $ISOBJECT(tClass) {
        Set tProp = ##class(%Dictionary.CompiledProperty).%OpenId("ExecuteMCP.Test.SimpleTest||Manager")
        If $ISOBJECT(tProp) {
            Write "Manager property found in SimpleTest", !
            Write "Private: ", tProp.Private, !
        } Else {
            Write "Manager property not found in SimpleTest", !
            ; Check parent class
            Set tProp = ##class(%Dictionary.CompiledProperty).%OpenId("%UnitTest.TestCase||Manager")
            If $ISOBJECT(tProp) {
                Write "Manager property found in %UnitTest.TestCase", !
                Write "Private: ", tProp.Private, !
            } Else {
                Write "Manager property not found in parent either", !
            }
        }
    }
    """
    
    result = call_iris_sync(connection, "ExecuteMCP.Core.Command", "ExecuteCommand", command, "HSCUSTOM")
    result_json = json.loads(result)
    print("Result:", result_json.get("output", ""))
    
    # Test 3: Try to create a working test with Manager
    print("\nTrying to create working test with Manager...")
    command = """
    ; Create Manager and Context
    Set tManager = ##class(ExecuteMCP.TestRunner.Manager).%New()
    Set tManager.Context = ##class(ExecuteMCP.TestRunner.Context).%New()
    Write "Manager created: ", $ISOBJECT(tManager), !
    
    ; Create test instance
    Set tTestInstance = ##class(ExecuteMCP.Test.SimpleTest).%New("")
    Write "Test instance created: ", $ISOBJECT(tTestInstance), !
    
    ; Try various methods to set Manager
    Set tSuccess = 0
    
    ; Method 1: Direct property access
    Try {
        Set tTestInstance.Manager = tManager
        Set tSuccess = 1
        Write "Method 1 (direct): SUCCESS", !
    } Catch {
        Write "Method 1 (direct): FAILED", !
    }
    
    ; Method 2: Indirect reference
    If 'tSuccess {
        Try {
            Set @("tTestInstance.Manager") = tManager
            Set tSuccess = 1
            Write "Method 2 (indirect): SUCCESS", !
        } Catch {
            Write "Method 2 (indirect): FAILED", !
        }
    }
    
    ; Method 3: %Set method
    If 'tSuccess {
        Try {
            Do tTestInstance.%Set("Manager", tManager)
            Set tSuccess = 1
            Write "Method 3 (%Set): SUCCESS", !
        } Catch {
            Write "Method 3 (%Set): FAILED", !
        }
    }
    
    ; If we succeeded, try to call an assertion
    If tSuccess {
        Write "Manager set successfully, trying assertion...", !
        Try {
            Do $$$AssertEquals(1, 1, "Test assertion")
            Write "Assertion succeeded!", !
        } Catch ex {
            Write "Assertion failed: ", ex.DisplayString(), !
        }
    } Else {
        Write "Could not set Manager property at all", !
    }
    """
    
    result = call_iris_sync(connection, "ExecuteMCP.Core.Command", "ExecuteCommand", command, "HSCUSTOM")
    result_json = json.loads(result)
    print("Result:", result_json.get("output", ""))
    
    connection.close()

if __name__ == "__main__":
    test_manager_property()
