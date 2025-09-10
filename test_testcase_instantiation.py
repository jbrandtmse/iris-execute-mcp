#!/usr/bin/env python3
"""
Diagnose %UnitTest.TestCase instantiation issue
"""

import json
from iris_execute_mcp import call_iris_sync

def execute_command(command: str, namespace: str = "HSCUSTOM"):
    """Execute an ObjectScript command and return the result."""
    result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", command, namespace)
    return json.loads(result)

print("=" * 80)
print("TestCase Instantiation Diagnosis")
print("=" * 80)

# Test 1: Try to instantiate test class directly without parameters
print("\n1. Testing direct instantiation without parameters...")
command = 'SET tTest = ##class(ExecuteMCP.Test.SimpleTest).%New() SET result = $ISOBJECT(tTest) WRITE "Object created: "_result'
result = execute_command(command)
print(f"   Result: {result}")

# Test 2: Try with empty string parameter
print("\n2. Testing instantiation with empty string parameter...")
command = 'SET tTest = ##class(ExecuteMCP.Test.SimpleTest).%New("") SET result = $ISOBJECT(tTest) WRITE "Object created: "_result'
result = execute_command(command)
print(f"   Result: {result}")

# Test 3: Check %UnitTest.TestCase %New signature
print("\n3. Checking %UnitTest.TestCase constructor signature...")
command = 'SET tClass = ##class(%Dictionary.CompiledClass).%OpenId("%UnitTest.TestCase") SET tMethod = tClass.Methods.GetAt("%OnNew") IF $ISOBJECT(tMethod) { WRITE "FormalSpec: "_tMethod.FormalSpec } ELSE { WRITE "Method not found" }'
result = execute_command(command)
print(f"   Result: {result}")

# Test 4: Look for initialization pattern in %UnitTest.Manager
print("\n4. Checking how %UnitTest.Manager creates test instances...")
command = 'SET ^ClineDebug = "" SET tSC = ##class(%UnitTest.Manager).RunTest(":ExecuteMCP.Test.SimpleTest:TestAlwaysPass","/noload/nodelete") SET result = ^ClineDebug WRITE "Debug: "_$E(result,1,200)'
result = execute_command(command)
print(f"   Result: {result}")

# Test 5: Try a simpler approach - don't use %New, use static call
print("\n5. Testing direct method invocation without instance...")
command = '''
SET tResult = {} 
SET tResult.test = "DirectCall" 
SET tTest = ##class(ExecuteMCP.Test.SimpleTest).%New("TestAlwaysPass") 
IF $ISOBJECT(tTest) { 
    SET tResult.created = "yes" 
} ELSE { 
    SET tResult.created = "no" 
} 
WRITE tResult.%ToJSON()
'''
# Flatten to single line
command = ' '.join(command.split())
result = execute_command(command)
print(f"   Result: {result}")

print("\n" + "=" * 80)
print("Diagnosis Complete")
print("=" * 80)
