#!/usr/bin/env python3
"""
Minimal MCP Server Test
Creates the simplest possible working MCP server to isolate protocol issues.
"""

import asyncio
import logging
import sys
from typing import Any, Dict, List, Sequence

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Simple stderr logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr, 
                   format='INFO:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Create server
app = Server("minimal-test-mcp")

@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available MCP tools."""
    logger.info("list_tools called")
    return [
        types.Tool(
            name="hello_world",
            description="Returns a simple hello world message",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name to greet",
                        "default": "World"
                    }
                },
                "required": []
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[types.TextContent]:
    """Handle MCP tool calls."""
    logger.info(f"call_tool: name={name}, args={arguments}")
    
    if name == "hello_world":
        name_arg = arguments.get("name", "World")
        return [types.TextContent(
            type="text",
            text=f"Hello, {name_arg}! This is a minimal MCP server test."
        )]
    else:
        return [types.TextContent(
            type="text", 
            text=f"❌ Unknown tool: {name}"
        )]

async def main():
    """Main entry point."""
    logger.info("Starting Minimal MCP Server")
    
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
