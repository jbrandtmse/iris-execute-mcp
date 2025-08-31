#!/usr/bin/env python3
"""
IRIS Execute MCP Server - Production FastMCP Implementation
Provides execute_command tool for IRIS ObjectScript execution via MCP protocol.
"""

import logging
import sys
import json
import os
import signal
from concurrent.futures import TimeoutError, ThreadPoolExecutor
import threading

try:
    import iris
    IRIS_AVAILABLE = True
except ImportError:
    IRIS_AVAILABLE = False
    iris = None

from fastmcp import FastMCP

# Setup logging to stderr (MCP requirement)
logging.basicConfig(
    level=logging.INFO, 
    stream=sys.stderr, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("iris-execute-mcp")

# Global thread pool executor for timeout handling
executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="iris-mcp")

def call_iris_with_timeout(class_name: str, method_name: str, timeout: float = 30.0, *args):
    """
    Call IRIS with explicit timeout to prevent FastMCP STDIO blocking.
    Uses ThreadPoolExecutor to ensure response delivery.
    """
    logger.info(f"Starting IRIS call with {timeout}s timeout: {class_name}.{method_name}")
    
    try:
        # Submit to thread pool with timeout
        future = executor.submit(call_iris_sync, class_name, method_name, *args)
        result = future.result(timeout=timeout)
        logger.info(f"IRIS call completed within timeout: {class_name}.{method_name}")
        return result
        
    except TimeoutError:
        error_msg = f"IRIS call timed out after {timeout}s: {class_name}.{method_name}"
        logger.error(error_msg)
        return json.dumps({
            "status": "error",
            "error": error_msg,
            "output": "",
            "namespace": "N/A",
            "timeout": timeout
        })
    except Exception as e:
        error_msg = f"IRIS call failed: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "status": "error",
            "error": error_msg,
            "output": "",
            "namespace": "N/A"
        })

def call_iris_sync(class_name: str, method_name: str, *args):
    """
    Synchronous IRIS class method call.
    Returns JSON string response from IRIS.
    """
    if not IRIS_AVAILABLE:
        return json.dumps({
            "status": "error",
            "error": "IRIS not available - intersystems-irispython not installed",
            "output": "",
            "namespace": "N/A"
        })
    
    try:
        # IRIS connection parameters from environment
        hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
        port = int(os.getenv('IRIS_PORT', '1972'))
        namespace = os.getenv('IRIS_NAMESPACE', 'HSCUSTOM')
        username = os.getenv('IRIS_USERNAME', '_SYSTEM')
        password = os.getenv('IRIS_PASSWORD', '_SYSTEM')
        
        # Connect to IRIS
        conn = iris.connect(hostname, port, namespace, username, password)
        iris_obj = iris.createIRIS(conn)
        
        # Call the class method
        result = iris_obj.classMethodString(class_name, method_name, *args)
        
        # Close connection
        conn.close()
        
        logger.info(f"IRIS call successful: {class_name}.{method_name}")
        return result
        
    except Exception as e:
        error_msg = f"IRIS call failed: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "status": "error",
            "error": error_msg,
            "output": "",
            "namespace": "N/A"
        })

@mcp.tool()
def execute_command(command: str, namespace: str = "HSCUSTOM") -> str:
    """
    Execute an ObjectScript command directly in IRIS.
    
    NOTE: For executing ObjectScript class methods (e.g., ##class(MyClass).MyMethod()),
    use the execute_classmethod tool instead, which provides better parameter handling,
    return value capture, and output parameter support.
    
    Args:
        command: The ObjectScript command to execute (WRITE, SET, KILL, etc.)
        namespace: Optional IRIS namespace (default: HSCUSTOM)
    
    Returns:
        JSON string with execution results
    """
    logger.info(f"Executing command in {namespace}: {command}")
    
    try:
        # Call IRIS backend with timeout to prevent FastMCP STDIO blocking
        result = call_iris_with_timeout("ExecuteMCP.Core.Command", "ExecuteCommand", 10.0, command, namespace)
        
        # Parse result to ensure it's valid JSON
        parsed_result = json.loads(result)
        
        # Log success
        if parsed_result.get("status") == "success":
            logger.info("Command executed successfully")
        else:
            logger.warning(f"Command execution issues: {parsed_result.get('error', 'Unknown error')}")
            
        return result
        
    except json.JSONDecodeError as e:
        error_response = json.dumps({
            "status": "error", 
            "error": f"Invalid JSON response from IRIS: {str(e)}",
            "output": result if 'result' in locals() else "",
            "namespace": namespace
        })
        logger.error(f"JSON decode error: {str(e)}")
        return error_response
        
    except Exception as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "output": "",
            "namespace": namespace
        })
        logger.error(f"Unexpected error: {str(e)}")
        return error_response

@mcp.tool()
def get_global(global_ref: str, namespace: str = "HSCUSTOM") -> str:
    """
    Get the value of an IRIS global dynamically.
    
    Args:
        global_ref: The global reference (e.g., "^TempGlobal", "^TempGlobal(1,2)", "^TempGlobal(\"This\",\"That\")")
        namespace: Optional IRIS namespace (default: HSCUSTOM)
    
    Returns:
        JSON string with global value and metadata
    """
    logger.info(f"Getting global {global_ref} in {namespace}")
    
    try:
        # Call IRIS backend
        result = call_iris_sync("ExecuteMCP.Core.Command", "GetGlobal", global_ref, namespace)
        
        # Parse result to ensure it's valid JSON
        parsed_result = json.loads(result)
        
        # Log success
        if parsed_result.get("status") == "success":
            logger.info(f"Global retrieved successfully: {global_ref}")
        else:
            logger.warning(f"Global retrieval issues: {parsed_result.get('errorMessage', 'Unknown error')}")
            
        return result
        
    except json.JSONDecodeError as e:
        error_response = json.dumps({
            "status": "error", 
            "error": f"Invalid JSON response from IRIS: {str(e)}",
            "globalRef": global_ref,
            "namespace": namespace
        })
        logger.error(f"JSON decode error: {str(e)}")
        return error_response
        
    except Exception as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "globalRef": global_ref,
            "namespace": namespace
        })
        logger.error(f"Unexpected error: {str(e)}")
        return error_response

@mcp.tool()
def set_global(global_ref: str, value: str, namespace: str = "HSCUSTOM") -> str:
    """
    Set the value of an IRIS global dynamically.
    
    Args:
        global_ref: The global reference (e.g., "^TempGlobal", "^TempGlobal(1,2)", "^TempGlobal(\"This\",\"That\")")
        value: The value to set
        namespace: Optional IRIS namespace (default: HSCUSTOM)
    
    Returns:
        JSON string with operation result and verification
    """
    logger.info(f"Setting global {global_ref} = '{value}' in {namespace}")
    
    try:
        # Call IRIS backend
        result = call_iris_sync("ExecuteMCP.Core.Command", "SetGlobal", global_ref, value, namespace)
        
        # Parse result to ensure it's valid JSON
        parsed_result = json.loads(result)
        
        # Log success
        if parsed_result.get("status") == "success":
            logger.info(f"Global set successfully: {global_ref}")
        else:
            logger.warning(f"Global set issues: {parsed_result.get('errorMessage', 'Unknown error')}")
            
        return result
        
    except json.JSONDecodeError as e:
        error_response = json.dumps({
            "status": "error", 
            "error": f"Invalid JSON response from IRIS: {str(e)}",
            "globalRef": global_ref,
            "namespace": namespace
        })
        logger.error(f"JSON decode error: {str(e)}")
        return error_response
        
    except Exception as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "globalRef": global_ref,
            "namespace": namespace
        })
        logger.error(f"Unexpected error: {str(e)}")
        return error_response

@mcp.tool()
def get_system_info() -> str:
    """
    Get IRIS system information for connectivity testing.
    
    Returns:
        JSON string with system information
    """
    logger.info("Getting IRIS system information")
    
    try:
        result = call_iris_sync("ExecuteMCP.Core.Command", "GetSystemInfo")
        logger.info("System info retrieved successfully")
        return result
        
    except Exception as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"System info retrieval failed: {str(e)}",
            "output": "",
            "namespace": "N/A"
        })
        logger.error(f"System info error: {str(e)}")
        return error_response

@mcp.tool()
def execute_classmethod(
    class_name: str, 
    method_name: str, 
    parameters: list = None, 
    namespace: str = "HSCUSTOM"
) -> str:
    """
    Execute an ObjectScript class method dynamically with support for output parameters.
    
    Args:
        class_name: The ObjectScript class name (e.g., "MyPackage.MyClass")
        method_name: The method name to invoke
        parameters: Optional list of parameter objects, each with:
            - value: The parameter value (required)
            - isOutput: Whether this is an output/ByRef parameter (default: false)
            - type: Optional type hint for the parameter
        namespace: Optional IRIS namespace (default: HSCUSTOM)
    
    Returns:
        JSON string with method result, output parameters, and any captured output
    """
    logger.info(f"Executing class method {class_name}.{method_name} in {namespace}")
    
    try:
        # Default to empty list if no parameters provided
        if parameters is None:
            parameters = []
            
        # Convert parameters list to JSON string for IRIS
        parameters_json = json.dumps(parameters)
        
        # Call IRIS backend with timeout
        result = call_iris_with_timeout(
            "ExecuteMCP.Core.Command", 
            "ExecuteClassMethod", 
            30.0,  # 30 second timeout for class methods
            class_name, 
            method_name, 
            parameters_json, 
            namespace
        )
        
        # Parse result to ensure it's valid JSON
        parsed_result = json.loads(result)
        
        # Log success
        if parsed_result.get("status") == "success":
            logger.info(f"Class method executed successfully: {class_name}.{method_name}")
        else:
            logger.warning(f"Class method execution issues: {parsed_result.get('errorMessage', 'Unknown error')}")
            
        return result
        
    except json.JSONDecodeError as e:
        error_response = json.dumps({
            "status": "error", 
            "error": f"Invalid JSON response from IRIS: {str(e)}",
            "className": class_name,
            "methodName": method_name,
            "namespace": namespace
        })
        logger.error(f"JSON decode error: {str(e)}")
        return error_response
        
    except Exception as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "className": class_name,
            "methodName": method_name,
            "namespace": namespace
        })
        logger.error(f"Unexpected error: {str(e)}")
        return error_response

@mcp.tool()
def list_unit_tests(test_root_path: str) -> str:
    """
    Lists all available unit tests found at the specified root path.
    
    Args:
        test_root_path: The root directory path containing unit test suites
    
    Returns:
        JSON string with discovered test suites, classes, and methods
    """
    logger.info(f"Listing unit tests from root path: {test_root_path}")
    
    try:
        # Call IRIS backend
        result = call_iris_sync("ExecuteMCP.Core.UnitTest", "ListTests", test_root_path)
        
        # Parse result to ensure it's valid JSON
        parsed_result = json.loads(result)
        
        # Log success
        if parsed_result.get("status") == "success":
            logger.info("Unit tests listed successfully")
        else:
            logger.warning(f"Unit test listing issues: {parsed_result.get('error', 'Unknown error')}")
            
        return result
        
    except json.JSONDecodeError as e:
        error_response = json.dumps({
            "status": "error", 
            "error": f"Invalid JSON response from IRIS: {str(e)}",
            "testRootPath": test_root_path
        })
        logger.error(f"JSON decode error: {str(e)}")
        return error_response
        
    except Exception as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "testRootPath": test_root_path
        })
        logger.error(f"Unexpected error: {str(e)}")
        return error_response

@mcp.tool()
def run_unit_tests(test_spec: str, qualifiers: str = "/recursive", test_root_path: str = "") -> str:
    """
    Runs unit tests based on the specified test specification.
    
    Args:
        test_spec: Test specification (e.g., "MySuite:MyClass:MyMethod")
        qualifiers: Test run qualifiers (e.g., "/recursive/nodelete")
        test_root_path: The root directory path containing unit test suites
    
    Returns:
        JSON string with test execution results and result ID
    """
    logger.info(f"Running unit tests: {test_spec} with qualifiers: {qualifiers}")
    
    try:
        # Call IRIS backend with timeout for potentially long-running tests
        result = call_iris_with_timeout(
            "ExecuteMCP.Core.UnitTest", 
            "RunTests", 
            120.0,  # 2 minute timeout for test execution
            test_spec, 
            qualifiers, 
            test_root_path
        )
        
        # Parse result to ensure it's valid JSON
        parsed_result = json.loads(result)
        
        # Log success
        if parsed_result.get("status") == "success":
            logger.info("Unit tests executed successfully")
        else:
            logger.warning(f"Unit test execution issues: {parsed_result.get('error', 'Unknown error')}")
            
        return result
        
    except json.JSONDecodeError as e:
        error_response = json.dumps({
            "status": "error", 
            "error": f"Invalid JSON response from IRIS: {str(e)}",
            "testSpec": test_spec,
            "qualifiers": qualifiers
        })
        logger.error(f"JSON decode error: {str(e)}")
        return error_response
        
    except Exception as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "testSpec": test_spec,
            "qualifiers": qualifiers
        })
        logger.error(f"Unexpected error: {str(e)}")
        return error_response

@mcp.tool()
def get_unit_test_results(result_id: int) -> str:
    """
    Fetches the results for a given test run ID.
    
    Args:
        result_id: The ID of the test run to retrieve results for
    
    Returns:
        JSON string with test results including failures and errors
    """
    logger.info(f"Getting unit test results for ID: {result_id}")
    
    try:
        # Call IRIS backend
        result = call_iris_sync("ExecuteMCP.Core.UnitTest", "GetTestResult", result_id)
        
        # Parse result to ensure it's valid JSON
        parsed_result = json.loads(result)
        
        # Log success
        if parsed_result.get("status") == "success":
            logger.info(f"Unit test results retrieved successfully for ID: {result_id}")
        else:
            logger.warning(f"Unit test result retrieval issues: {parsed_result.get('error', 'Unknown error')}")
            
        return result
        
    except json.JSONDecodeError as e:
        error_response = json.dumps({
            "status": "error", 
            "error": f"Invalid JSON response from IRIS: {str(e)}",
            "resultId": result_id
        })
        logger.error(f"JSON decode error: {str(e)}")
        return error_response
        
    except Exception as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "resultId": result_id
        })
        logger.error(f"Unexpected error: {str(e)}")
        return error_response

# =====================================================================================
# ASYNC UNIT TESTING TOOLS - REVOLUTIONARY TIMEOUT-FREE IMPLEMENTATION
# =====================================================================================

@mcp.tool()
def queue_unit_tests(test_spec: str, qualifiers: str = "/recursive", test_root_path: str = "", namespace: str = "HSCUSTOM") -> str:
    """
    Queue unit test execution using async pattern that returns immediately without blocking.
    
    This tool uses an async work queue pattern to eliminate MCP timeouts by queueing test 
    execution in the background and returning a job ID immediately. Tests execute using 
    direct TestCase method calls, bypassing the heavyweight %UnitTest.Manager overhead.
    
    Args:
        test_spec: Test specification (e.g., "ExecuteMCP.Test.SampleUnitTest" for all methods, 
                  "ExecuteMCP.Test.SampleUnitTest:TestMethodName" for specific method)
        qualifiers: Test run qualifiers (default: "/recursive")
        test_root_path: The root directory path containing unit test suites (default: "")
        namespace: Optional IRIS namespace (default: HSCUSTOM)
    
    Returns:
        JSON string with jobID and queue status. Use poll_unit_tests with the jobID to retrieve results.
    """
    logger.info(f"Queueing async unit tests: {test_spec} in namespace {namespace}")
    
    try:
        # Call IRIS backend using async pattern
        result = call_iris_sync("ExecuteMCP.Core.UnitTestAsync", "QueueTest", test_spec, qualifiers, test_root_path, namespace)
        
        # Parse result to ensure it's valid JSON
        parsed_result = json.loads(result)
        
        # Log success
        if parsed_result.get("status") == "queued":
            logger.info(f"Unit tests queued successfully with job ID: {parsed_result.get('jobID')}")
        else:
            logger.warning(f"Unit test queueing issues: {parsed_result.get('error', 'Unknown error')}")
            
        return result
        
    except json.JSONDecodeError as e:
        error_response = json.dumps({
            "status": "error", 
            "error": f"Invalid JSON response from IRIS: {str(e)}",
            "testSpec": test_spec,
            "qualifiers": qualifiers
        })
        logger.error(f"JSON decode error: {str(e)}")
        return error_response
        
    except Exception as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "testSpec": test_spec,
            "qualifiers": qualifiers
        })
        logger.error(f"Unexpected error: {str(e)}")
        return error_response

@mcp.tool()
def poll_unit_tests(job_id: str) -> str:
    """
    Poll for async unit test execution results in a non-blocking manner.
    
    This tool checks for completion of queued unit tests without blocking the MCP 
    communication channel. Returns either the complete test results or current status.
    
    Args:
        job_id: Job ID returned from queue_unit_tests
    
    Returns:
        JSON string with complete test results if finished, or running status if still executing.
        Results include summary statistics and individual method results with pass/fail status.
    """
    logger.info(f"Polling async unit tests: Job ID {job_id}")
    
    try:
        # Call IRIS backend
        result = call_iris_sync("ExecuteMCP.Core.UnitTestAsync", "PollTest", job_id)
        
        # Parse result to ensure it's valid JSON
        parsed_result = json.loads(result)
        
        # Log appropriate status
        status = parsed_result.get("status", "unknown")
        if status == "success":
            logger.info(f"Unit tests completed successfully for job {job_id}")
        elif status == "running":
            logger.info(f"Unit tests still running for job {job_id}")
        elif status == "error":
            logger.warning(f"Unit test execution failed for job {job_id}: {parsed_result.get('error', 'Unknown error')}")
        else:
            logger.warning(f"Unknown status for job {job_id}: {status}")
            
        return result
        
    except json.JSONDecodeError as e:
        error_response = json.dumps({
            "status": "error", 
            "error": f"Invalid JSON response from IRIS: {str(e)}",
            "jobId": job_id
        })
        logger.error(f"JSON decode error: {str(e)}")
        return error_response
        
    except Exception as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "jobId": job_id
        })
        logger.error(f"Unexpected error: {str(e)}")
        return error_response

@mcp.tool()
def get_job_status(job_id: str) -> str:
    """
    Get job status without returning results (for progress monitoring)
    
    Args:
        job_id: Job ID to check
    
    Returns:
        JSON string with job status (queued, running, completed, failed, cancelled)
    """
    logger.info(f"Getting job status for: {job_id}")
    
    try:
        # Call IRIS backend
        result = call_iris_sync("ExecuteMCP.Core.UnitTestAsync", "GetJobStatus", job_id)
        
        # Parse result to ensure it's valid JSON
        parsed_result = json.loads(result)
        
        # Log status
        status = parsed_result.get("status", "unknown")
        logger.info(f"Job {job_id} status: {status}")
            
        return result
        
    except json.JSONDecodeError as e:
        error_response = json.dumps({
            "status": "error", 
            "error": f"Invalid JSON response from IRIS: {str(e)}",
            "jobId": job_id
        })
        logger.error(f"JSON decode error: {str(e)}")
        return error_response
        
    except Exception as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "jobId": job_id
        })
        logger.error(f"Unexpected error: {str(e)}")
        return error_response

@mcp.tool()
def cancel_job(job_id: str) -> str:
    """
    Cancel a running async job (cleanup)
    
    Args:
        job_id: Job ID to cancel
    
    Returns:
        JSON string with cancellation status
    """
    logger.info(f"Cancelling job: {job_id}")
    
    try:
        # Call IRIS backend
        result = call_iris_sync("ExecuteMCP.Core.UnitTestAsync", "CancelJob", job_id)
        
        # Parse result to ensure it's valid JSON
        parsed_result = json.loads(result)
        
        # Log cancellation
        if parsed_result.get("status") == "cancelled":
            logger.info(f"Job {job_id} cancelled successfully")
        else:
            logger.warning(f"Job cancellation issues: {parsed_result.get('error', 'Unknown error')}")
            
        return result
        
    except json.JSONDecodeError as e:
        error_response = json.dumps({
            "status": "error", 
            "error": f"Invalid JSON response from IRIS: {str(e)}",
            "jobId": job_id
        })
        logger.error(f"JSON decode error: {str(e)}")
        return error_response
        
    except Exception as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "jobId": job_id
        })
        logger.error(f"Unexpected error: {str(e)}")
        return error_response

@mcp.tool()
def list_active_jobs() -> str:
    """
    List all active async jobs (for debugging/monitoring)
    
    Returns:
        JSON string with active jobs and their statuses
    """
    logger.info("Listing all active async jobs")
    
    try:
        # Call IRIS backend
        result = call_iris_sync("ExecuteMCP.Core.UnitTestAsync", "ListActiveJobs")
        
        # Parse result to ensure it's valid JSON
        parsed_result = json.loads(result)
        
        # Log job count
        if "jobs" in parsed_result:
            job_count = len(parsed_result["jobs"])
            logger.info(f"Found {job_count} active jobs")
        else:
            logger.info("No active jobs found")
            
        return result
        
    except json.JSONDecodeError as e:
        error_response = json.dumps({
            "status": "error", 
            "error": f"Invalid JSON response from IRIS: {str(e)}"
        })
        logger.error(f"JSON decode error: {str(e)}")
        return error_response
        
    except Exception as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}"
        })
        logger.error(f"Unexpected error: {str(e)}")
        return error_response

if __name__ == "__main__":
    logger.info("Starting IRIS Execute FastMCP Server")
    logger.info(f"IRIS Available: {IRIS_AVAILABLE}")
    
    if IRIS_AVAILABLE:
        # Test IRIS connectivity on startup
        try:
            test_result = call_iris_sync("ExecuteMCP.Core.Command", "GetSystemInfo")
            test_parsed = json.loads(test_result)
            if test_parsed.get("status") == "success":
                logger.info("✅ IRIS connectivity test passed")
            else:
                logger.warning(f"⚠️ IRIS connectivity test failed: {test_parsed.get('error')}")
        except Exception as e:
            logger.error(f"❌ IRIS connectivity test error: {str(e)}")
    else:
        logger.warning("⚠️ IRIS not available - running in mock mode")
    
    # Start the FastMCP server
    logger.info("🚀 FastMCP server ready for connections")
    mcp.run()
