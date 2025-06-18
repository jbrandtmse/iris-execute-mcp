#!/usr/bin/env python3
"""
IRIS Session MCP Server - Debug Version
Minimal version to isolate timeout issues
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

# IRIS connection configuration
IRIS_CONFIG = {
    'hostname': os.getenv('IRIS_HOSTNAME', 'localhost'),
    'port': int(os.getenv('IRIS_PORT', '1972')),
    'namespace': os.getenv('IRIS_NAMESPACE', 'HSCUSTOM'),
    'username': os.getenv('IRIS_USERNAME', '_SYSTEM'),
    'password': os.getenv('IRIS_PASSWORD', '_SYSTEM')
}

logging.basicConfig(level=logging.INFO, stream=sys.stderr, 
                   format='DEBUG:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

app = Server("iris-session-mcp-debug")

def simple_iris_test():
    """Minimal IRIS connectivity test"""
    try:
        if not IRIS_AVAILABLE:
            return "❌ IRIS not available"
        
        logger.info("Testing IRIS connectivity...")
        conn = iris.connect(
            IRIS_CONFIG['hostname'], 
            IRIS_CONFIG['port'], 
            IRIS_CONFIG['namespace'], 
            IRIS_CONFIG['username'], 
            IRIS_CONFIG['password']
        )
        iris_obj = iris.createIRIS(conn)
        result = iris_obj.classMethodString("%SYSTEM.Version", "GetVersion")
        conn.close()
        logger.info(f"IRIS test result: {result}")
        return f"✅ IRIS OK: {result}"
        
    except Exception as e:
        logger.error(f"IRIS test failed: {e}")
        return f"❌ IRIS Error: {str(e)}"

@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available tools."""
    logger.info("list_tools called")
    return [
        types.Tool(
            name="test_iris",
            description="Test IRIS connectivity",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="simple_command",
            description="Execute a simple test command",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_msg": {
                        "type": "string",
                        "description": "Test message",
                        "default": "Hello"
                    }
                },
                "required": []
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[types.TextContent]:
    """Handle tool calls."""
    logger.info(f"call_tool: name={name}, args={arguments}")
    
    try:
        if name == "test_iris":
            result = simple_iris_test()
            return [types.TextContent(type="text", text=result)]
        
        elif name == "simple_command":
            test_msg = arguments.get("test_msg", "Hello")
            logger.info(f"Processing simple command: {test_msg}")
            
            # Simple response without IRIS interaction
            response = f"✅ Simple command processed: {test_msg}"
            return [types.TextContent(type="text", text=response)]
        
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
    logger.info("Starting IRIS Session MCP Debug Server")
    logger.info(f"IRIS Config: {IRIS_CONFIG['hostname']}:{IRIS_CONFIG['port']}/{IRIS_CONFIG['namespace']}")
    
    # Quick IRIS test
    test_result = simple_iris_test()
    logger.info(f"Startup IRIS test: {test_result}")
    
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
