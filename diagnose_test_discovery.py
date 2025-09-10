#!/usr/bin/env python

import os
import sys
import iris
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to IRIS
username = os.getenv('IRIS_USERNAME', '_SYSTEM')
password = os.getenv('IRIS_PASSWORD', 'SYS')
namespace = os.getenv('IRIS_NAMESPACE', 'HSCUSTOM')
hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
port = int(os.getenv('IRIS_PORT', '1972'))
connection_string = f"{hostname}:{port}/{namespace}"

print(f"Connecting to IRIS at {connection_string}...")
conn = iris.connect(connection_string, username, password)
irispy = iris.createIRIS(conn)

# Check what tests are in the latest result
print("\n=== Analyzing Test Result 287 ===")

# Get suite names
suites = []
suite = ""
while True:
    try:
        suite = irispy.get("^UnitTest.Result", 287, suite).decode() if isinstance(irispy.get("^UnitTest.Result", 287, suite), bytes) else irispy.get("^UnitTest.Result", 287, suite)
        if suite and not suite.startswith('\x00'):
            suites.append(suite)
            print(f"Suite found: {suite}")
    except:
        break

# For each suite, get test cases
for suite_name in suites:
    print(f"\n  Suite: {suite_name}")
    case = ""
    while True:
        try:
            case = irispy.get("^UnitTest.Result", 287, suite_name, case).decode() if isinstance(irispy.get("^UnitTest.Result", 287, suite_name, case), bytes) else irispy.get("^UnitTest.Result", 287, suite_name, case)
            if case:
                print(f"    Case: {case}")
                
                # Get methods for this case
                method = ""
                while True:
                    try:
                        method = irispy.get("^UnitTest.Result", 287, suite_name, case, method).decode() if isinstance(irispy.get("^UnitTest.Result", 287, suite_name, case, method), bytes) else irispy.get("^UnitTest.Result", 287, suite_name, case, method)
                        if method and not method.startswith('\x00'):
                            print(f"      Method: {method}")
                    except:
                        break
        except:
            break

# Now check ExecuteMCP.Test classes directly
print("\n=== Checking ExecuteMCP.Test Classes ===")
test_classes = ["ExecuteMCP.Test.SampleUnitTest", "ExecuteMCP.Test.SimpleTest", "ExecuteMCP.Test.ErrorTest"]
for class_name in test_classes:
    try:
        exists = irispy.classMethodValue(class_name, "%Extends", "%UnitTest.TestCase")
        print(f"{class_name}: {'EXISTS and extends TestCase' if exists else 'NOT FOUND or does not extend TestCase'}")
        
        # Try to list methods if class exists
        if exists:
            # Get method list (this is a simplified approach)
            print(f"  Checking for Test* methods...")
    except Exception as e:
        print(f"{class_name}: ERROR - {e}")

# Check the discovery process
print("\n=== Running Direct Discovery Test ===")
try:
    # Run a test directly using %UnitTest.Manager
    result = irispy.classMethodValue("%UnitTest.Manager", "RunTest", ":ExecuteMCP.Test", "/noload/nodelete")
    print(f"Direct RunTest result: {result}")
except Exception as e:
    print(f"Direct RunTest error: {e}")

conn.close()
print("\nDone!")
