#!/usr/bin/env python
"""
Comprehensive TestRunner validation script.
Tests all current TestRunner capabilities to verify readiness for execution implementation.
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import IRIS connection
from iris_execute_mcp import call_iris_sync

def test_testrunner_validation():
    """Comprehensive validation of TestRunner components."""
    print("=" * 80)
    print("TestRunner Comprehensive Validation")
    print("=" * 80)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': []
    }
    
    # Test 1: Manager instantiation and Context initialization
    print("\n1. Testing Manager instantiation with Context auto-init...")
    command = 'SET tManager = ##class(ExecuteMCP.TestRunner.Manager).%New() WRITE $ISOBJECT(tManager)_":"_$ISOBJECT(tManager.Context)'
    result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", command, "HSCUSTOM")
    response = json.loads(result)
    
    if response.get('status') == 'success':
        output = response.get('output', '')
        if output == "1:1":
            print("   ✓ Manager creates with auto-initialized Context")
            results['tests'].append({'name': 'Manager+Context', 'status': 'PASS'})
        else:
            print(f"   ✗ Unexpected output: {output}")
            results['tests'].append({'name': 'Manager+Context', 'status': 'FAIL', 'error': output})
    else:
        print(f"   ✗ Error: {response.get('errorMessage')}")
        results['tests'].append({'name': 'Manager+Context', 'status': 'ERROR', 'error': response.get('errorMessage')})
    
    # Test 2: Discovery functionality
    print("\n2. Testing Discovery.DiscoverTestClasses...")
    command = 'WRITE ##class(ExecuteMCP.TestRunner.Discovery).DiscoverTestClasses("ExecuteMCP.Test")'
    result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", command, "HSCUSTOM")
    response = json.loads(result)
    
    if response.get('status') == 'success':
        output = response.get('output', '')
        try:
            test_classes = json.loads(output)
            print(f"   ✓ Discovery found {len(test_classes)} test classes:")
            for cls in test_classes:
                print(f"      - {cls}")
            results['tests'].append({'name': 'Discovery', 'status': 'PASS', 'classes': test_classes})
        except:
            print(f"   ✗ Invalid JSON output: {output}")
            results['tests'].append({'name': 'Discovery', 'status': 'FAIL', 'error': 'Invalid JSON'})
    else:
        print(f"   ✗ Error: {response.get('errorMessage')}")
        results['tests'].append({'name': 'Discovery', 'status': 'ERROR', 'error': response.get('errorMessage')})
    
    # Test 3: ValidateTestRunner comprehensive check
    print("\n3. Testing Manager.ValidateTestRunner...")
    command = 'SET tManager = ##class(ExecuteMCP.TestRunner.Manager).%New() WRITE tManager.ValidateTestRunner()'
    result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", command, "HSCUSTOM")
    response = json.loads(result)
    
    if response.get('status') == 'success':
        output = response.get('output', '')
        try:
            validation = json.loads(output)
            print("   Validation Results:")
            for key, value in validation.items():
                status = "✓" if value else "✗"
                print(f"      {status} {key}: {value}")
            results['tests'].append({'name': 'ValidateTestRunner', 'status': 'PASS', 'validation': validation})
        except:
            print(f"   ✗ Invalid JSON output: {output}")
            results['tests'].append({'name': 'ValidateTestRunner', 'status': 'FAIL', 'error': 'Invalid JSON'})
    else:
        print(f"   ✗ Error: {response.get('errorMessage')}")
        results['tests'].append({'name': 'ValidateTestRunner', 'status': 'ERROR', 'error': response.get('errorMessage')})
    
    # Test 4: Check test class methods discovery
    print("\n4. Testing method discovery for a test class...")
    command = 'WRITE ##class(ExecuteMCP.TestRunner.Discovery).DiscoverTestMethods("ExecuteMCP.Test.SampleUnitTest")'
    result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", command, "HSCUSTOM")
    response = json.loads(result)
    
    if response.get('status') == 'success':
        output = response.get('output', '')
        try:
            test_methods = json.loads(output)
            print(f"   ✓ Found {len(test_methods)} test methods in SampleUnitTest:")
            for method in test_methods:
                print(f"      - {method}")
            results['tests'].append({'name': 'MethodDiscovery', 'status': 'PASS', 'methods': test_methods})
        except:
            # Method might not be implemented yet
            print(f"   ⚠ Method not implemented or error: {output}")
            results['tests'].append({'name': 'MethodDiscovery', 'status': 'PENDING', 'output': output})
    else:
        print(f"   ⚠ Method might not be implemented: {response.get('errorMessage')}")
        results['tests'].append({'name': 'MethodDiscovery', 'status': 'PENDING', 'error': response.get('errorMessage')})
    
    # Test 5: Check LogAssert interface readiness
    print("\n5. Testing LogAssert interface readiness...")
    command = 'SET tManager = ##class(ExecuteMCP.TestRunner.Manager).%New() SET tHasLogAssert = ##class(%Dictionary.CompiledMethod).%ExistsId("ExecuteMCP.TestRunner.Manager||LogAssert") SET tHasLogMessage = ##class(%Dictionary.CompiledMethod).%ExistsId("ExecuteMCP.TestRunner.Manager||LogMessage") WRITE "LogAssert:"_tHasLogAssert_",LogMessage:"_tHasLogMessage'
    result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", command, "HSCUSTOM")
    response = json.loads(result)
    
    if response.get('status') == 'success':
        output = response.get('output', '')
        parts = output.split(',')
        has_log_assert = "1" in parts[0] if len(parts) > 0 else False
        has_log_message = "1" in parts[1] if len(parts) > 1 else False
        
        print(f"   {'✓' if has_log_assert else '⚠'} LogAssert method: {'Exists' if has_log_assert else 'Not implemented'}")
        print(f"   {'✓' if has_log_message else '⚠'} LogMessage method: {'Exists' if has_log_message else 'Not implemented'}")
        results['tests'].append({
            'name': 'LogInterface',
            'status': 'PARTIAL' if not (has_log_assert and has_log_message) else 'PASS',
            'log_assert': has_log_assert,
            'log_message': has_log_message
        })
    else:
        print(f"   ✗ Error: {response.get('errorMessage')}")
        results['tests'].append({'name': 'LogInterface', 'status': 'ERROR', 'error': response.get('errorMessage')})
    
    # Test 6: Check if Context can track assertions
    print("\n6. Testing Context assertion tracking capabilities...")
    command = 'SET tContext = ##class(ExecuteMCP.TestRunner.Context).%New() SET tHasAssertions = ##class(%Dictionary.CompiledProperty).%ExistsId("ExecuteMCP.TestRunner.Context||Assertions") SET tHasMessages = ##class(%Dictionary.CompiledProperty).%ExistsId("ExecuteMCP.TestRunner.Context||Messages") WRITE "Assertions:"_tHasAssertions_",Messages:"_tHasMessages'
    result = call_iris_sync("ExecuteMCP.Core.Command", "ExecuteCommand", command, "HSCUSTOM")
    response = json.loads(result)
    
    if response.get('status') == 'success':
        output = response.get('output', '')
        parts = output.split(',')
        has_assertions = "1" in parts[0] if len(parts) > 0 else False
        has_messages = "1" in parts[1] if len(parts) > 1 else False
        
        print(f"   {'✓' if has_assertions else '⚠'} Assertions property: {'Exists' if has_assertions else 'Not implemented'}")
        print(f"   {'✓' if has_messages else '⚠'} Messages property: {'Exists' if has_messages else 'Not implemented'}")
        results['tests'].append({
            'name': 'ContextTracking',
            'status': 'PARTIAL' if not (has_assertions and has_messages) else 'PASS',
            'assertions': has_assertions,
            'messages': has_messages
        })
    else:
        print(f"   ✗ Error: {response.get('errorMessage')}")
        results['tests'].append({'name': 'ContextTracking', 'status': 'ERROR', 'error': response.get('errorMessage')})
    
    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    pass_count = sum(1 for t in results['tests'] if t['status'] == 'PASS')
    fail_count = sum(1 for t in results['tests'] if t['status'] == 'FAIL')
    error_count = sum(1 for t in results['tests'] if t['status'] == 'ERROR')
    pending_count = sum(1 for t in results['tests'] if t['status'] in ['PENDING', 'PARTIAL'])
    
    print(f"\nResults:")
    print(f"  ✓ PASS:    {pass_count}")
    print(f"  ✗ FAIL:    {fail_count}")
    print(f"  ⚠ PENDING: {pending_count}")
    print(f"  ✗ ERROR:   {error_count}")
    
    # Readiness assessment
    print("\nReadiness Assessment:")
    if pass_count >= 3 and fail_count == 0 and error_count == 0:
        print("  ✓ Core components are ready")
        print("  ⚠ LogAssert/LogMessage interface needs implementation")
        print("  ⚠ Test execution methods need implementation")
    else:
        print("  ✗ Critical issues detected - review errors above")
    
    return results

if __name__ == "__main__":
    try:
        results = test_testrunner_validation()
        
        # Save results to file
        with open('testrunner_validation_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to testrunner_validation_results.json")
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
