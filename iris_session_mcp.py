#!/usr/bin/env python3
"""
IRIS Session MCP Server
Execute ObjectScript commands in IRIS terminal sessions via MCP protocol.
Production version with proven IRIS connectivity and MCP protocol integration.
"""

import asyncio
import json
import logging
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

# Simple stderr logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr, 
                   format='INFO:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Create server
app = Server("iris-session-mcp")

def call_iris_sync(class_name: str, method_name: str, *args):
    """Synchronous IRIS call - proven to work from our tests"""
    try:
        if not IRIS_AVAILABLE:
            raise RuntimeError("intersystems-iris package not available")
        
        # Use the exact connection pattern that works
        conn = iris.connect('localhost', 1972, 'HSCUSTOM', '_SYSTEM', '_SYSTEM')
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
            description="Execute an ObjectScript command in an IRIS terminal session",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The ObjectScript command to execute"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Optional: Existing session ID. If not provided, a new session will be created."
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Optional: IRIS namespace to use (default: HSCUSTOM)",
                        "default": "HSCUSTOM"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Optional: Command timeout in seconds (default: 30)",
                        "default": 30
                    }
                },
                "required": ["command"]
            }
        ),
        types.Tool(
            name="list_sessions",
            description="List all active IRIS sessions",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
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
            session_id = arguments.get("session_id")
            namespace = arguments.get("namespace", "HSCUSTOM")
            timeout = arguments.get("timeout", 30)
            
            if not command:
                return [types.TextContent(
                    type="text",
                    text="❌ Error: 'command' parameter is required"
                )]
            
            # Create session if not provided (using proven sync call)
            if not session_id:
                logger.info(f"Creating new session in namespace: {namespace}")
                session_result = call_iris_sync(
                    "SessionMCP.Core.Session",
                    "CreateSession",
                    namespace, ""
                )
                
                session_data = json.loads(session_result)
                if session_data.get('status') != 'success':
                    error_msg = session_data.get('errorMessage', 'Unknown error')
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Failed to create session: {error_msg}"
                    )]
                
                session_id = session_data.get('sessionId')
                logger.info(f"Created session: {session_id}")
            
            # Execute the command (using proven sync call)
            logger.info(f"Executing command in session {session_id}: {command}")
            execute_result = call_iris_sync(
                "SessionMCP.Core.Session",
                "ExecuteCommand",
                session_id, command, timeout
            )
            
            # Parse and format response
            result_data = json.loads(execute_result)
            
            if result_data.get('status') == 'success':
                response_text = "✅ Command executed successfully\n"
                response_text += f"Session: {result_data.get('sessionId', 'unknown')}\n"
                response_text += f"Namespace: {result_data.get('namespace', 'unknown')}\n"
                response_text += f"Execution time: {result_data.get('executionTimeMs', 0)}ms\n"
                
                if result_data.get('output'):
                    response_text += f"\nOutput:\n{result_data.get('output')}"
                
                return [types.TextContent(type="text", text=response_text)]
            else:
                error_msg = result_data.get('errorMessage', 'Unknown error')
                return [types.TextContent(
                    type="text",
                    text=f"❌ Command execution failed: {error_msg}"
                )]
        
        elif name == "list_sessions":
            logger.info("Listing active sessions")
            result = call_iris_sync(
                "SessionMCP.Core.Session",
                "ListActiveSessions"
            )
            
            sessions_data = json.loads(result)
            
            if sessions_data.get('status') == 'success':
                sessions = sessions_data.get('sessions', [])
                count = sessions_data.get('count', 0)
                
                response_text = f"📋 Active Sessions ({count} total)\n\n"
                
                if count == 0:
                    response_text += "No active sessions found."
                else:
                    for session in sessions:
                        response_text += f"Session ID: {session.get('sessionId')}\n"
                        response_text += f"  Namespace: {session.get('namespace')}\n"
                        response_text += f"  Created: {session.get('created')}\n"
                        response_text += f"  Last Access: {session.get('lastAccess')}\n"
                        response_text += f"  Status: {session.get('status')}\n\n"
                
                return [types.TextContent(type="text", text=response_text)]
            else:
                error_msg = sessions_data.get('errorMessage', 'Unknown error')
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to list sessions: {error_msg}"
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
    logger.info("Starting IRIS Session MCP Server")
    
    # Test IRIS connectivity on startup
    if IRIS_AVAILABLE:
        try:
            test_result = call_iris_sync("%SYSTEM.Version", "GetVersion")
            logger.info(f"✅ IRIS connectivity test passed: {test_result}")
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
