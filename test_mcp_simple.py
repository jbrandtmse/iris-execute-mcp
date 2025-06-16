#!/usr/bin/env python3
"""
Simple MCP Server Test - Just echo back to test communication
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Sequence

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Configure logging to stderr so it doesn't interfere with MCP protocol
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Initialize the server
app = Server("test-mcp")

@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available MCP tools."""
    return [
        types.Tool(
            name="echo",
            description="Echo back the input message",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to echo back"
                    }
                },
                "required": ["message"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[types.TextContent]:
    """Handle MCP tool calls."""
    if name == "echo":
        message = arguments.get("message", "No message provided")
        return [types.TextContent(
            type="text",
            text=f"Echo: {message}"
        )]
    else:
        return [types.TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Simple Test MCP Server")
    
    try:
        # Start the stdio server
        async with stdio_server() as streams:
            await app.run(
                streams[0], streams[1], app.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
