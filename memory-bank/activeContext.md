# Active Context

## Current Work: Tool Refactoring Complete ✅

Successfully refactored iris-execute-mcp from 10 tools to 8 production-ready tools by consolidating unit testing functionality and removing deprecated async pattern.

### Key Achievements (January 9, 2025)
1. **Renamed tool** - `run_custom_testrunner` → `execute_unit_tests`
2. **Removed deprecated tools** - `queue_unit_tests` and `poll_unit_tests` removed
3. **Backend cleanup** - ExecuteMCP.Core.UnitTestQueue marked as deprecated
4. **Documentation updated** - README.md and User Manual reflect 8-tool structure

### Tool Consolidation Summary
- **Previous**: 10 tools (including experimental async unit testing)
- **Current**: 8 production-ready tools
- **Benefit**: Cleaner API, better maintainability, single reliable unit testing tool

### Current Tool Inventory (8 Production Tools)
1. **execute_command** - Direct ObjectScript command execution
2. **get_global** - Read IRIS global values
3. **set_global** - Write IRIS global values
4. **get_system_info** - IRIS system connectivity test
5. **execute_classmethod** - Execute ObjectScript class methods with output parameters
6. **execute_unit_tests** - Run unit tests using custom TestRunner
7. **compile_objectscript_class** - Compile individual ObjectScript classes
8. **compile_objectscript_package** - Compile entire ObjectScript packages

## Custom TestRunner Architecture

### Technical Solution
- **Problem**: %UnitTest.Manager designed for terminal, not concurrent MCP access
- **Solution**: ExecuteMCP.TestRunner package with custom implementation
- **Components**:
  - Discovery.cls - SQL-based test discovery bypassing file system
  - Manager.cls - Process-local singleton with ^||TestRunnerManager storage
  - TestCase.cls - Base class providing Manager property initialization
  - Executor.cls - Test execution with timeout handling
  - Wrapper.cls - MCP-safe wrapper methods for test execution

### Key Features
- Bypasses VS Code filesystem sync issues
- Process-local globals ensure Manager isolation
- SQL discovery provides reliable test class detection
- Auto-prefix feature for flexible test specification

## Next Steps
1. Monitor production usage of consolidated 8-tool structure
2. Consider future expansion for additional MCP capabilities
3. Potential Native API alternatives investigation

## Important Patterns and Preferences

### Unit Testing in VS Code
- Always use `execute_unit_tests` tool for test execution
- TestRunner automatically bypasses VS Code sync issues
- Process-local globals (^||) ensure thread-safe operation

### MCP Tool Development
- Be aware of Native API parameter marshaling limitations
- Create wrapper methods when parameter passing is problematic
- Test thoroughly with actual MCP integration

### Architecture Decisions
- Deprecated WorkMgr async pattern in favor of synchronous TestRunner
- Consolidated from 10 to 8 tools for production clarity
- Custom TestRunner provides superior VS Code integration

## Learnings and Project Insights

### VS Code Integration Challenges
- File system sync delays cause "class not found" errors
- Solution: SQL-based discovery of compiled classes
- TestRunner architecture bypasses all sync issues

### Manager Singleton Pattern
- %UnitTest.Manager designed for terminal use, not concurrent access
- Process-local globals provide perfect isolation
- Custom TestCase base class ensures Manager availability

### Tool Consolidation Benefits
- Reduced complexity from 10 to 8 tools
- Single unit testing tool with superior architecture
- Cleaner API surface for MCP clients
- Better maintainability and documentation

## Environment Status
- IRIS running and accessible
- MCP server (iris-execute-mcp) connected and functional
- All 8 production tools available and tested
- Version 3.0.0 ready for production deployment
