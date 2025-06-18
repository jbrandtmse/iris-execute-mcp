#!/usr/bin/env python3
"""
FastMCP Test Server
Testing MCP connectivity with the FastMCP library which may be more reliable.
"""

import asyncio
import logging
import sys

try:
    import iris
    IRIS_AVAILABLE = True
except ImportError:
    IRIS_AVAILABLE = False
    iris = None

from fastmcp import FastMCP

# Setup logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("iris-test-fastmcp")

@mcp.tool()
def hello_world(name: str = "World") -> str:
    """Say hello to someone."""
    return f"Hello, {name}! This is FastMCP working."

@mcp.tool()
def test_iris_simple() -> str:
    """Test basic IRIS connectivity."""
    if not IRIS_AVAILABLE:
        return "❌ IRIS not available - intersystems-irispython not installed"
    
    try:
        # Simple IRIS connectivity test
        conn = iris.connect('localhost', 1972, 'HSCUSTOM', '_SYSTEM', '_SYSTEM')
        iris_obj = iris.createIRIS(conn)
        result = iris_obj.classMethodString("ExecuteMCP.Core.Command", "GetSystemInfo")
        conn.close()
        return f"✅ IRIS connectivity successful: {result[:100]}..."
    except Exception as e:
        return f"❌ IRIS connection failed: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting FastMCP IRIS Test Server")
    mcp.run()
