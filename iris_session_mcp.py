#!/usr/bin/env python3
"""
IRIS Session MCP Server
Execute ObjectScript commands in IRIS terminal sessions via MCP protocol.
Production version with proven IRIS connectivity and MCP protocol integration.
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
app = Server("iris-session-mcp")

def call_iris_sync(class_name: str, method_name: str, *args):
    """Synchronous IRIS call - proven to work from our tests"""
    try:
        if not IRIS_AVAILABLE:
            raise RuntimeError("intersystems-iris package not available")
        
        # Use environment configuration for IRIS connection
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
        ),
        types.Tool(
            name="diagnose_timeout",
            description="Diagnose step-by-step execution to isolate timeout issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The ObjectScript command to diagnose",
                        "default": "WRITE \"Hello World!\""
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Optional: Existing session ID. If not provided, will use a test session."
                    }
                },
                "required": ["command"]
            }
        ),
        types.Tool(
            name="execute_direct",
            description="Execute ObjectScript command directly without session management (for timeout testing)",
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
        
        elif name == "diagnose_timeout":
            command = arguments.get("command", "WRITE \"Hello World!\"")
            session_id = arguments.get("session_id")
            
            logger.info(f"Running diagnostic for command: {command}")
            
            # Create a test session if none provided
            if not session_id:
                logger.info("Creating test session for diagnostic")
                session_result = call_iris_sync(
                    "SessionMCP.Core.Session",
                    "CreateSession",
                    "HSCUSTOM", "diagnostic_test"
                )
                
                session_data = json.loads(session_result)
                if session_data.get('status') != 'success':
                    error_msg = session_data.get('errorMessage', 'Unknown error')
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Failed to create diagnostic session: {error_msg}"
                    )]
                
                session_id = session_data.get('sessionId')
                logger.info(f"Created diagnostic session: {session_id}")
            
            # Run the diagnostic
            logger.info(f"Running DiagnoseExecuteCommand for session {session_id}")
            diagnostic_result = call_iris_sync(
                "SessionMCP.Core.Session",
                "DiagnoseExecuteCommand",
                session_id, command, 10  # 10 second timeout for diagnostic
            )
            
            # Parse and format the detailed diagnostic response
            result_data = json.loads(diagnostic_result)
            
            if result_data.get('status') == 'diagnostic':
                response_text = "🔍 **DIAGNOSTIC RESULTS**\n\n"
                response_text += f"**Command**: {result_data.get('command', 'N/A')}\n"
                response_text += f"**Session ID**: {result_data.get('sessionId', 'N/A')}\n"
                response_text += f"**Total Duration**: {result_data.get('totalDuration', 0)}ms\n\n"
                
                steps = result_data.get('steps', [])
                response_text += "**Step-by-Step Analysis**:\n\n"
                
                for i, step in enumerate(steps, 1):
                    step_name = step.get('step', 'unknown')
                    duration = step.get('duration', 0)
                    status = step.get('status', 'unknown')
                    message = step.get('message', 'No message')
                    
                    # Status emoji
                    status_emoji = "✅" if status == "success" else "❌" if status == "error" else "⚠️" if status == "failed" else "⏭️"
                    
                    response_text += f"{i}. **{step_name.title()}** {status_emoji}\n"
                    response_text += f"   Duration: {duration}ms\n"
                    response_text += f"   Status: {status}\n"
                    response_text += f"   Message: {message}\n"
                    
                    # Add extra details for specific steps
                    if step_name == "namespace" and step.get('currentNamespace'):
                        response_text += f"   Current Namespace: {step.get('currentNamespace')}\n"
                    if step_name == "xecute" and step.get('command'):
                        response_text += f"   Command: {step.get('command')}\n"
                    
                    response_text += "\n"
                
                conclusion = result_data.get('conclusion', 'No conclusion')
                response_text += f"**Conclusion**: {conclusion}\n"
                
                return [types.TextContent(type="text", text=response_text)]
            else:
                error_msg = result_data.get('errorMessage', 'Unknown diagnostic error')
                return [types.TextContent(
                    type="text",
                    text=f"❌ Diagnostic failed: {error_msg}"
                )]
        
        elif name == "execute_direct":
            command = arguments.get("command")
            namespace = arguments.get("namespace", "HSCUSTOM")
            
            if not command:
                return [types.TextContent(
                    type="text",
                    text="❌ Error: 'command' parameter is required"
                )]
            
            logger.info(f"Executing direct command: {command} in namespace {namespace}")
            
            # Use the new direct execution method - NO session creation needed!
            direct_result = call_iris_sync(
                "SessionMCP.Core.Session",
                "ExecuteCommandDirect",
                command, namespace
            )
            
            # Parse and format response
            result_data = json.loads(direct_result)
            
            if result_data.get('status') == 'success':
                response_text = "⚡ **DIRECT EXECUTION SUCCESSFUL** ⚡\n\n"
                response_text += f"**Command**: {command}\n"
                response_text += f"**Namespace**: {result_data.get('namespace', 'unknown')}\n"
                response_text += f"**Execution Time**: {result_data.get('executionTimeMs', 0)}ms\n"
                response_text += f"**Mode**: {result_data.get('mode', 'direct')}\n"
                
                if result_data.get('output'):
                    response_text += f"\n**Output**:\n{result_data.get('output')}\n"
                
                response_text += "\n✅ **Success**: Command executed without session management overhead"
                
                return [types.TextContent(type="text", text=response_text)]
            else:
                error_msg = result_data.get('errorMessage', 'Unknown error')
                return [types.TextContent(
                    type="text",
                    text=f"❌ Direct execution failed: {error_msg}"
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
    logger.info(f"IRIS Configuration: {IRIS_CONFIG['hostname']}:{IRIS_CONFIG['port']}/{IRIS_CONFIG['namespace']} (user: {IRIS_CONFIG['username']})")
    
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
