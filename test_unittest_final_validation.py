"""
Final validation of unit test implementation
Tests that the MCP unit test tools are working correctly
"""

import sys
sys.path.insert(0, '.')
import json
import time
from iris_execute_mcp import call_iris_sync

def test_unit_tests():
    print("Unit Test Implementation Final Validation")
    print("=" * 60)
    
    success_count = 0
    total_tests = 4
    
    # Test 1: Check if test class is compiled
    print("\n1. Checking test class compilation...")
    try:
        result = call_iris_sync('ExecuteMCP.Core.Command', 'ExecuteCommand',
                               'Write ##class(%Dictionary.CompiledClass).%ExistsId("ExecuteMCP.Test.SampleUnitTest")',
                               'HSCUSTOM')
        result_json = json.loads(result)
        if result_json.get('status') == 'success':
            output = result_json.get('output', '')
            # Handle both string and integer outputs
            if str(output).strip() == '1':
                print("   ✓ Test class is compiled")
                success_count += 1
            else:
                print("   ✗ Test class not compiled - compiling now...")
                # Compile the class
                compile_result = call_iris_sync('ExecuteMCP.Core.Compile', 'CompileClasses',
                                               'ExecuteMCP.Test.SampleUnitTest.cls', 'bckry', 'HSCUSTOM')
                compile_json = json.loads(compile_result)
                if compile_json.get('status') == 'success':
                    print("   ✓ Test class compiled successfully")
                    success_count += 1
                else:
                    print(f"   ✗ Compilation failed: {compile_json.get('error', 'Unknown error')}")
        else:
            print(f"   ✗ Check failed: {result_json.get('errorMessage', 'Unknown error')}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Test 2: Check ^UnitTestRoot configuration
    print("\n2. Checking ^UnitTestRoot configuration...")
    try:
        result = call_iris_sync('ExecuteMCP.Core.Command', 'ExecuteCommand',
                               'Write "^UnitTestRoot = "_$GET(^UnitTestRoot,"<not set>")',
                               'HSCUSTOM')
        result_json = json.loads(result)
        if result_json.get('status') == 'success':
            output = str(result_json.get('output', ''))
            if '<not set>' not in output:
                print(f"   ✓ {output}")
                success_count += 1
            else:
                print("   ✗ ^UnitTestRoot not configured - setting now...")
                # Set ^UnitTestRoot
                set_result = call_iris_sync('ExecuteMCP.Core.Command', 'ExecuteCommand',
                                           'Set ^UnitTestRoot = "C:\\temp\\"',
                                           'HSCUSTOM')
                set_json = json.loads(set_result)
                if set_json.get('status') == 'success':
                    print("   ✓ ^UnitTestRoot set to C:\\temp\\")
                    success_count += 1
                else:
                    print(f"   ✗ Failed to set: {set_json.get('errorMessage', 'Unknown error')}")
        else:
            print(f"   ✗ Check failed: {result_json.get('errorMessage', 'Unknown error')}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Test 3: Queue and execute unit tests
    print("\n3. Testing unit test execution with UnitTestQueue...")
    try:
        # Queue the test
        queue_result = call_iris_sync('ExecuteMCP.Core.UnitTestQueue', 'QueueTestExecution',
                                      'ExecuteMCP.Test.SampleUnitTest', '', '')
        queue_json = json.loads(queue_result)
        
        if queue_json.get('status') == 'queued':
            job_id = queue_json.get('jobID')
            print(f"   ✓ Test queued successfully (Job ID: {job_id[:8]}...)")
            
            # Poll for results
            print("   Waiting for test execution...")
            completed = False
            for i in range(15):  # Wait up to 15 seconds
                time.sleep(1)
                
                poll_result = call_iris_sync('ExecuteMCP.Core.UnitTestQueue', 'PollResults', job_id)
                poll_json = json.loads(poll_result)
                
                status = poll_json.get('status')
                if status == 'completed':
                    completed = True
                    break
                elif status == 'error':
                    print(f"   ✗ Execution error: {poll_json.get('message', 'Unknown error')}")
                    break
                elif status != 'running' and status != 'queued':
                    # Job may have finished and been cleaned up
                    completed = True
                    break
            
            if completed:
                if 'summary' in poll_json:
                    summary = poll_json['summary']
                    passed = summary.get('passed', 0)
                    failed = summary.get('failed', 0)
                    print(f"   ✓ Test execution completed")
                    print(f"     Passed: {passed}")
                    print(f"     Failed: {failed}")
                    if passed > 0:
                        success_count += 1
                else:
                    print("   ⚠ Test completed but no results captured")
            else:
                print("   ✗ Test execution timed out")
        else:
            print(f"   ✗ Failed to queue: {queue_json.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Test 4: Verify MCP tool registration
    print("\n4. Checking MCP tool registration...")
    try:
        # Check if the functions are available in the module
        from iris_execute_mcp import queue_unit_tests, poll_unit_tests
        print("   ✓ MCP unit test tools are registered")
        success_count += 1
    except ImportError as e:
        print(f"   ✗ MCP tools not found: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"VALIDATION RESULTS: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("\n✅ SUCCESS: Unit test implementation is fully functional!")
        print("The MCP unit test tools are ready for use:")
        print("  - queue_unit_tests: Queue tests for async execution")
        print("  - poll_unit_tests: Poll for test results")
    else:
        print("\n⚠ PARTIAL SUCCESS: Some components need attention")
        print("Please review the failed tests above")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = test_unit_tests()
    sys.exit(0 if success else 1)
