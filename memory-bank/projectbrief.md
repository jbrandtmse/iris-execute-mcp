# IRIS Execute MCP Server - Project Brief

## Project Vision
Create a Model Context Protocol (MCP) server that enables AI agents to execute ObjectScript commands directly in InterSystems IRIS instances through a simplified, reliable interface focused on command execution without session management complexity.

## Core Requirements

### Primary Goal
Bridge AI agents (like Claude/Cline) with InterSystems IRIS systems through standardized MCP protocol, enabling:
- Direct ObjectScript command execution
- Multiple namespace support
- Security privilege validation
- Extensible architecture for additional tools

### Architecture Overview
**Simplified Two-Tier Design:**
1. **IRIS Backend** (ObjectScript class in `src/ExecuteMCP/Core/Command.cls`)
   - Direct command execution without session state
   - Security privilege validation
   - Namespace switching and restoration
   - Native API connectivity interface

2. **MCP Client** (Python application `iris_execute_mcp.py`)
   - IRIS Native API connectivity
   - JSON-RPC 2.0 protocol implementation
   - Single focused tool definition
   - STDIO transport mode

### Key Technical Decisions
- **Communication**: IRIS Native API (not WebSocket) for direct connectivity
- **Client Language**: Python (minimal setup burden)
- **Scope**: Single direct execution tool (no session management)
- **Expansion Strategy**: Foundation for multiple focused MCP tools (`execute_method`, `set_global`, `read_global`)
- **Class Location**: `src/ExecuteMCP/` with organized structure

## Implementation Philosophy

### Simplification Focus
**Direct Execution Model:**
- No session state management
- No global storage operations
- No timeout-prone session lifecycle
- Immediate command execution with security validation

### Reliability Priority
**Proven Patterns:**
- Synchronous IRIS calls (no async timeout issues)
- Security privilege checks before execution
- Namespace isolation and restoration
- Structured JSON error responses

## Success Criteria
1. AI agents can execute ObjectScript commands on IRIS reliably
2. Sub-second response times for command execution
3. Secure authentication and privilege validation
4. Minimal client setup requirements
5. Extensible foundation for additional MCP tools
6. Zero session management complexity

## Project Scope

### Current Scope
- **In Scope**: Direct ObjectScript command execution, security validation, namespace support
- **Foundation For**: Multi-tool architecture (`execute_command`, `execute_method`, `set_global`, `read_global`)

### Eliminated Scope  
- **Removed**: Session management, session persistence, diagnostic tools
- **Simplified**: Complex I/O redirection, global storage operations
- **Out of Scope**: IRIS installation, container management, GUI development

## Architecture Benefits

### Performance Excellence
- **Command Execution**: 0ms for simple commands
- **No Session Overhead**: Eliminates global storage operations
- **Direct API**: Native IRIS connectivity without abstraction layers
- **Immediate Response**: No session creation or validation delays

### Reliability Improvements
- **Timeout Elimination**: No session management timeouts
- **Simplified Error Handling**: Clear, actionable error messages
- **Security Compliance**: Proper IRIS privilege validation
- **Connection Stability**: Proven synchronous IRIS call pattern

### Future-Ready Foundation
- **Multi-Tool Ready**: Clean architecture for `execute_method`, `set_global`, `read_global`
- **Extension Pattern**: Established pattern for additional MCP tools
- **Proven Connectivity**: Reliable IRIS Native API integration
- **Documentation Complete**: Comprehensive guides for development and deployment

## Key References
- InterSystems IRIS Native API documentation
- Model Context Protocol specification
- Proven ObjectScript security patterns
- Direct execution performance benchmarks
