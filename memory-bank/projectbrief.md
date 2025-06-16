# IRIS Terminal MCP Server - Project Brief

## Project Vision
Create a Model Context Protocol (MCP) server that enables AI agents to interact with InterSystems IRIS instances through terminal-like command execution, replicating the functionality of IRIS Terminal and WebTerminal in a programmatic, AI-accessible interface.

## Core Requirements

### Primary Goal
Bridge AI agents (like Claude/Cline) with InterSystems IRIS systems through standardized MCP protocol, enabling:
- ObjectScript command execution
- SQL query processing
- Namespace exploration
- Session state management
- Administrative operations

### Architecture Overview
**Two-Tier Design:**
1. **IRIS Backend** (ObjectScript classes in `src/SessionMCP/`)
   - Session management and command execution
   - I/O redirection and output capture
   - Error handling and state persistence
   - Native API connectivity interface

2. **MCP Client** (Python application)
   - IRIS Native API connectivity
   - JSON-RPC 2.0 protocol implementation
   - Tool definitions and parameter validation
   - STDIO/HTTP transport modes

### Key Technical Decisions
- **Communication**: IRIS Native API (not WebSocket) for direct connectivity
- **Client Language**: Python (minimal setup burden)
- **Initial Scope**: Single command execution tool
- **Expansion Strategy**: Multiple MCP tools within same server
- **Class Location**: `src/SessionMCP/` with organized subfolders

## Implementation Phases

### Phase 1: Minimal Viable Product
- Single `execute_command` MCP tool
- Basic session handling
- STDIO transport mode
- Core error handling

### Phase 2: Enhanced Capabilities  
- `execute_sql` tool
- `get_namespace_info` tool
- HTTP transport mode
- Enhanced error reporting

### Phase 3: Full Terminal Emulation
- `manage_session` tool
- Interactive READ handling
- Multi-session support
- Production security features

## Success Criteria
1. AI agents can execute ObjectScript commands on IRIS
2. Session state persists across multiple commands
3. Output matches IRIS Terminal behavior exactly
4. Secure authentication and access control
5. Minimal client setup requirements
6. Extensible architecture for additional tools

## Project Scope Boundaries
- **In Scope**: Terminal command execution, session management, basic security
- **Future Scope**: Web application management, complex workflow automation
- **Out of Scope**: IRIS installation, container management, GUI development

## Key References
- InterSystems WebTerminal architecture patterns
- %Atelier.v7.TerminalAgent implementation
- %CSP.WebSocket communication patterns
- Model Context Protocol specification
- IRIS Native API documentation
