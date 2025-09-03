#!/usr/bin/env python3
"""
Inspect the MCP server tool structure.
"""

import os
import sys

# Add the iris_execute_mcp module path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the MCP server module
import iris_execute_mcp

# Get the MCP server instance
server = iris_execute_mcp.mcp

print("Inspecting MCP Tool Manager Structure...")
print("=" * 60)

# Check what attributes the tool manager has
print("\nTool Manager attributes:")
for attr in dir(server._tool_manager):
    if not attr.startswith('__'):
        print(f"  - {attr}")

print("\nChecking _tools type:")
print(f"  Type: {type(server._tool_manager._tools)}")
print(f"  Content: {server._tool_manager._tools}")

# Check if there's a _handlers attribute or similar
if hasattr(server._tool_manager, '_handlers'):
    print("\n_handlers found:")
    print(f"  Type: {type(server._tool_manager._handlers)}")
    print(f"  Keys: {list(server._tool_manager._handlers.keys())}")

# Try to find where the actual tool functions are stored
print("\nLooking for tool functions...")
for attr_name in ['_handlers', '_tool_functions', '_tool_map', 'tools']:
    if hasattr(server._tool_manager, attr_name):
        attr = getattr(server._tool_manager, attr_name)
        print(f"\n{attr_name}:")
        print(f"  Type: {type(attr)}")
        if isinstance(attr, dict):
            print(f"  Keys: {list(attr.keys())[:5]}...")  # First 5 keys

print("\n" + "=" * 60)
