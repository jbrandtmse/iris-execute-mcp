# Product Context - IRIS Terminal MCP Server

## Why This Project Exists

### The Problem
AI agents and developers need programmatic access to InterSystems IRIS terminal functionality, but current solutions require:
- Complex WebTerminal integration
- CSP application development
- Manual session management
- Custom protocol development

### The Solution
A standardized MCP server that provides terminal-like IRIS access through:
- Industry-standard Model Context Protocol
- Direct Native API connectivity
- AI-agent friendly tool definitions
- Session persistence and state management

## User Experience Goals

### Primary Users
1. **AI Agents** (Claude, GPT-4, etc.)
   - Execute IRIS commands through natural language
   - Explore databases and applications
   - Perform administrative tasks
   - Debug and troubleshoot systems

2. **Developers** integrating AI with IRIS
   - Rapid prototyping and testing
   - Automated script execution
   - System monitoring and analysis
   - Educational and training scenarios

### Core User Journeys

**Journey 1: AI Database Exploration**
1. Agent connects to IRIS via MCP server
2. Executes "show me available namespaces"
3. Explores specific namespace structure
4. Queries sample data
5. Provides insights and recommendations

**Journey 2: System Administration**
1. Agent receives monitoring request
2. Checks system status via IRIS commands
3. Analyzes performance metrics
4. Identifies issues and suggests solutions
5. Executes corrective commands

**Journey 3: Development Assistance**
1. Developer asks for help with ObjectScript
2. Agent executes test code snippets
3. Demonstrates proper syntax and patterns
4. Provides real-time feedback and suggestions

## Key Value Propositions

### For AI Agents
- **Native IRIS Access**: Direct terminal functionality without custom integration
- **Session Persistence**: Maintain context across multiple interactions
- **Standardized Interface**: Consistent MCP protocol across different IRIS instances
- **Error Handling**: Graceful error management with meaningful feedback

### For Developers
- **Rapid Integration**: Minimal setup to connect AI tools with IRIS
- **Educational Value**: Learn IRIS through AI-assisted exploration
- **Automation Potential**: Script complex administrative tasks
- **Production Ready**: Secure authentication and session management

### For Organizations
- **Knowledge Transfer**: AI can help document and explain IRIS systems
- **Operational Efficiency**: Automate routine administrative tasks
- **Training Enhancement**: Interactive learning experiences for new IRIS developers
- **System Insights**: AI-powered analysis of database structure and performance

## User Experience Principles

### Simplicity
- Minimal client setup requirements
- Clear, intuitive tool interfaces
- Predictable behavior matching IRIS Terminal

### Reliability
- Robust error handling and recovery
- Consistent session state management
- Graceful handling of network issues

### Security
- IRIS native authentication integration
- Secure credential management
- Audit trail for executed commands

### Extensibility
- Modular tool architecture
- Easy addition of new capabilities
- Configurable behavior for different use cases

## Success Metrics

### Technical Metrics
- Command execution success rate > 99%
- Session persistence across interactions
- Response time < 2 seconds for typical commands
- Error recovery rate > 95%

### User Experience Metrics
- Setup time < 5 minutes for new users
- Learning curve for AI integration < 1 hour
- User satisfaction with output accuracy
- Adoption rate across development teams

## Competitive Landscape

### Current Alternatives
- **WebTerminal**: Browser-based but requires web application setup
- **IRIS Terminal**: Direct access but not AI-agent accessible
- **Custom REST APIs**: Require significant development effort
- **Database Connectors**: Limited to SQL, miss ObjectScript capabilities

### Our Differentiation
- **AI-First Design**: Built specifically for agent interaction
- **Protocol Standardization**: Uses industry-standard MCP
- **Full Terminal Emulation**: Complete IRIS functionality access
- **Zero Custom Development**: Works out-of-the-box with MCP clients
