#!/usr/bin/env python3
"""
IRIS Execute MCP Server
Direct ObjectScript command execution via MCP protocol.
Simplified architecture focused on reliable direct execution without session management.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Sequence

try:
    import iris
    IRIS_AVAILABLE = True
except ImportError:
    IRIS_AVAILABLE = False
    iris = None

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# IRIS connection configuration from environment variables
IRIS_CONFIG = {
    'hostname': os.getenv('IRIS_HOSTNAME', 'localhost'),
    'port': int(os.getenv('IRIS_PORT', '1972')),
    'namespace': os.getenv('IRIS_NAMESPACE', 'HSCUSTOM'),
    'username': os.getenv('IRIS_USERNAME', '_SYSTEM'),
    'password': os.getenv('IRIS_PASSWORD', '_SYSTEM')
}

# Simple stderr logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr, 
                   format='INFO:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Create server
app = Server("iris-execute-mcp")

def call_iris_sync(class_name: str, method_name: str, *args):
    """Synchronous IRIS call - proven reliable pattern"""
    try:
        if not IRIS_AVAILABLE:
            raise RuntimeError("intersystems-iris package not available")
        
        logger.debug(f"Connecting to IRIS: {IRIS_CONFIG['hostname']}:{IRIS_CONFIG['port']}/{IRIS_CONFIG['namespace']}")
        conn = iris.connect(
            IRIS_CONFIG['hostname'], 
            IRIS_CONFIG['port'], 
            IRIS_CONFIG['namespace'], 
            IRIS_CONFIG['username'], 
            IRIS_CONFIG['password']
        )
        iris_obj = iris.createIRIS(conn)
        result = iris_obj.classMethodString(class_name, method_name, *args)
        conn.close()
        return result
        
    except Exception as e:
        logger.error(f"IRIS call failed: {e}")
        # Return error in JSON format
        error_response = {
            "status": "error",
            "errorMessage": str(e),
            "errorCode": "IRIS_CONNECTION_ERROR"
        }
        return json.dumps(error_response)

@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available MCP tools."""
    logger.info("list_tools called")
    return [
        types.Tool(
            name="execute_command",
            description="Execute an ObjectScript command directly in IRIS",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The ObjectScript command to execute"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Optional: IRIS namespace to use (default: HSCUSTOM)",
                        "default": "HSCUSTOM"
                    }
                },
                "required": ["command"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[types.TextContent]:
    """Handle MCP tool calls."""
    logger.info(f"call_tool: name={name}, args={arguments}")
    
    try:
        if name == "execute_command":
            command = arguments.get("command")
            namespace = arguments.get("namespace", "HSCUSTOM")
            
            if not command:
                return [types.TextContent(
                    type="text",
                    text="❌ Error: 'command' parameter is required"
                )]
            
            logger.info(f"Executing command: {command} in namespace {namespace}")
            
            # Use the new simplified ExecuteMCP.Core.Command class
            result = call_iris_sync(
                "ExecuteMCP.Core.Command",
                "ExecuteCommand",
                command, namespace
            )
            
            # Parse and format response
            result_data = json.loads(result)
            
            if result_data.get('status') == 'success':
                response_text = "✅ **COMMAND EXECUTED SUCCESSFULLY**\n\n"
                response_text += f"**Command**: {command}\n"
                response_text += f"**Namespace**: {result_data.get('namespace', 'unknown')}\n"
                response_text += f"**Execution Time**: {result_data.get('executionTimeMs', 0)}ms\n"
                response_text += f"**Timestamp**: {result_data.get('timestamp', 'unknown')}\n"
                
                if result_data.get('output'):
                    response_text += f"\n**Output**: {result_data.get('output')}"
                
                return [types.TextContent(type="text", text=response_text)]
            else:
                error_msg = result_data.get('errorMessage', 'Unknown error')
                return [types.TextContent(
                    type="text",
                    text=f"❌ Command execution failed: {error_msg}"
                )]
        
        else:
            return [types.TextContent(type="text", text=f"❌ Unknown tool: {name}")]
    
    except Exception as e:
        logger.error(f"Error in call_tool: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"❌ Tool execution error: {str(e)}"
        )]

async def main():
    """Main entry point."""
    logger.info("Starting IRIS Execute MCP Server")
    logger.info(f"IRIS Configuration: {IRIS_CONFIG['hostname']}:{IRIS_CONFIG['port']}/{IRIS_CONFIG['namespace']} (user: {IRIS_CONFIG['username']})")
    
    # Test IRIS connectivity on startup
    if IRIS_AVAILABLE:
        try:
            test_result = call_iris_sync("ExecuteMCP.Core.Command", "GetSystemInfo")
            logger.info(f"✅ IRIS connectivity test passed")
        except Exception as e:
            logger.warning(f"⚠️ IRIS connectivity test failed: {str(e)}")
    else:
        logger.warning("⚠️ intersystems-iris package not available")
    
    try:
        async with stdio_server() as streams:
            logger.info("STDIO server initialized")
            await app.run(
                streams[0], streams[1], app.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
