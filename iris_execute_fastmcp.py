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
    
    Args:
        command: The ObjectScript command to execute
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
