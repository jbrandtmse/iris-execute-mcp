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


# =====================================================================================
# ASYNC UNIT TESTING TOOLS - WORKMANAGER-BASED IMPLEMENTATION
# =====================================================================================

@mcp.tool()
def queue_unit_tests(test_spec: str, qualifiers: str = None, test_root_path: str = "", namespace: str = "HSCUSTOM") -> str:
    """
    Queue unit test execution using WorkMgr async pattern for process isolation.
    
    This tool uses %SYSTEM.WorkMgr to execute tests in an isolated worker process,
    avoiding %UnitTest.Manager singleton conflicts. Tests run with full assertion
    macro support and return immediately with a job ID for polling.
    
    Args:
        test_spec: Test specification (e.g., "ExecuteMCP.Test.SampleUnitTest")
                   Can also target specific methods: "ExecuteMCP.Test.SampleUnitTest:TestAddition"
        qualifiers: Optional test run qualifiers. If not provided, defaults to:
                   "/noload/nodelete/recursive" for VS Code workflow.
                   Common qualifiers:
                   - /noload: Don't load classes from filesystem (VS Code auto-syncs)
                   - /nodelete: Don't delete test classes after run
                   - /recursive: Run all test methods in the class/package
                   - /debug: Enable debug output
                   - /verbose: Verbose output
        test_root_path: Optional test root directory (default: uses ^UnitTestRoot)
        namespace: Optional IRIS namespace (default: HSCUSTOM)
    
    Returns:
        JSON string with jobID and queue status. Use poll_unit_tests to retrieve results.
    """
    logger.info(f"Queueing unit tests with WorkMgr: {test_spec} in namespace {namespace}")
    
    # Pass empty string if None to let IRIS handle defaults
    if qualifiers is None:
        qualifiers = ""
    
    try:
        # Call IRIS backend using new WorkMgr pattern (namespace used for connection, not as parameter)
        result = call_iris_sync("ExecuteMCP.Core.UnitTestQueue", "QueueTestExecution", test_spec, qualifiers, test_root_path)
        
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
def poll_unit_tests(job_id: str, namespace: str = "HSCUSTOM") -> str:
    """
    Poll for unit test results from WorkMgr execution.
    
    Checks the status of tests executing in an isolated worker process.
    Returns current status if running, or complete results if finished.
    
    Args:
        job_id: Job ID returned from queue_unit_tests
        namespace: Optional IRIS namespace (default: HSCUSTOM)
    
    Returns:
        JSON string with test status or complete results including pass/fail counts.
    """
    logger.info(f"Polling unit test results: Job ID {job_id}")
    
    try:
        # Call IRIS backend (namespace used for connection, not as parameter)
        result = call_iris_sync("ExecuteMCP.Core.UnitTestQueue", "PollResults", job_id)
        
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


# =====================================================================================
# OBJECTSCRIPT COMPILATION TOOLS
# =====================================================================================

@mcp.tool()
def compile_objectscript_class(class_names: str, qspec: str = "bckry", namespace: str = "HSCUSTOM") -> str:
    """
    Compile one or more ObjectScript classes in IRIS.
    
    IMPORTANT: Class names MUST include the .cls suffix for proper compilation.
    
    Args:
        class_names: Class name(s) to compile with .cls suffix required
                    (e.g., "MyClass.cls" or "Class1.cls,Class2.cls")
        qspec: Compilation flags (default: "bckry")
               b = Rebuild dependencies
               c = Compile
               k = Keep generated source
               r = Recursive compile
               y = Display compilation information
        namespace: Target namespace (default: HSCUSTOM)
    
    Returns:
        JSON string with compilation results including any errors
    """
    logger.info(f"Compiling classes: {class_names} with qspec: {qspec} in namespace: {namespace}")
    
    try:
        # Call IRIS backend with timeout for compilation
        result = call_iris_with_timeout(
            "ExecuteMCP.Core.Compile",
            "CompileClasses",
            60.0,  # 60 second timeout for compilation
            class_names,
            qspec,
            namespace
        )
        
        # Parse result to ensure it's valid JSON
        parsed_result = json.loads(result)
        
        # Log compilation status
        status = parsed_result.get("status", "unknown")
        if status == "success":
            logger.info(f"Classes compiled successfully: {parsed_result.get('compiledCount', 0)} compiled")
        elif status == "partial":
            logger.warning(f"Partial compilation: {parsed_result.get('compiledCount', 0)} compiled, {parsed_result.get('errorCount', 0)} failed")
        elif status == "error":
            logger.error(f"Compilation failed: {parsed_result.get('errorCount', 0)} errors")
        
        return result
        
    except json.JSONDecodeError as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"Invalid JSON response from IRIS: {str(e)}",
            "classNames": class_names,
            "namespace": namespace
        })
        logger.error(f"JSON decode error: {str(e)}")
        return error_response
        
    except Exception as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "classNames": class_names,
            "namespace": namespace
        })
        logger.error(f"Unexpected error: {str(e)}")
        return error_response

@mcp.tool()
def compile_objectscript_package(package_name: str, qspec: str = "bckry", namespace: str = "HSCUSTOM") -> str:
    """
    Compile all classes in an ObjectScript package.
    
    Args:
        package_name: Package name (e.g., "ExecuteMCP.Core")
        qspec: Compilation flags (default: "bckry")
               b = Rebuild dependencies
               c = Compile
               k = Keep generated source
               r = Recursive compile
               y = Display compilation information
        namespace: Target namespace (default: HSCUSTOM)
    
    Returns:
        JSON string with compilation results including any errors
    """
    logger.info(f"Compiling package: {package_name} with qspec: {qspec} in namespace: {namespace}")
    
    try:
        # Call IRIS backend with longer timeout for package compilation
        result = call_iris_with_timeout(
            "ExecuteMCP.Core.Compile",
            "CompilePackage",
            120.0,  # 2 minute timeout for package compilation
            package_name,
            qspec,
            namespace
        )
        
        # Parse result to ensure it's valid JSON
        parsed_result = json.loads(result)
        
        # Log compilation status
        status = parsed_result.get("status", "unknown")
        if status == "success":
            logger.info(f"Package compiled successfully: {parsed_result.get('compiledCount', 0)} classes compiled")
        elif status == "partial":
            logger.warning(f"Partial package compilation: {parsed_result.get('compiledCount', 0)} compiled, {parsed_result.get('errorCount', 0)} failed")
        elif status == "error":
            logger.error(f"Package compilation failed: {parsed_result.get('errorCount', 0)} errors")
        
        return result
        
    except json.JSONDecodeError as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"Invalid JSON response from IRIS: {str(e)}",
            "packageName": package_name,
            "namespace": namespace
        })
        logger.error(f"JSON decode error: {str(e)}")
        return error_response
        
    except Exception as e:
        error_response = json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "packageName": package_name,
            "namespace": namespace
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
