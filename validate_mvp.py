#!/usr/bin/env python3
"""
IRIS Session MCP Server Validation Script
Test Python MCP client connectivity and functionality.
"""

import asyncio
import json
import logging
import subprocess
import sys
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MCPClientValidator:
    """Validate MCP client functionality."""
    
    def __init__(self):
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
        if message:
            logger.info(f"  {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    def test_python_dependencies(self) -> bool:
        """Test that required Python packages are available."""
        try:
            import iris
            self.log_test("IRIS Package Import", True, "intersystems-iris package available")
            iris_available = True
        except ImportError:
            self.log_test("IRIS Package Import", False, "intersystems-iris package not found")
            iris_available = False
        
        try:
            from mcp import types
            from mcp.server import Server
            self.log_test("MCP Package Import", True, "mcp package available")
            mcp_available = True
        except ImportError:
            self.log_test("MCP Package Import", False, "mcp package not found")
            mcp_available = False
        
        try:
            from pydantic import BaseModel
            self.log_test("Pydantic Package Import", True, "pydantic package available")
            pydantic_available = True
        except ImportError:
            self.log_test("Pydantic Package Import", False, "pydantic package not found")
            pydantic_available = False
        
        return iris_available and mcp_available and pydantic_available
    
    def test_mcp_server_structure(self) -> bool:
        """Test that MCP server can be instantiated."""
        try:
            from iris_session_mcp import IRISSessionMCPServer, app
            
            # Test server instantiation
            server = IRISSessionMCPServer()
            self.log_test("MCP Server Instantiation", True, "IRISSessionMCPServer created successfully")
            
            # Test configuration
            config = server.config
            expected_namespace = "HSCUSTOM"
            namespace_correct = config.namespace == expected_namespace
            self.log_test("Namespace Configuration", namespace_correct, 
                         f"Namespace: {config.namespace} (expected: {expected_namespace})")
            
            return True
            
        except Exception as e:
            self.log_test("MCP Server Instantiation", False, f"Error: {str(e)}")
            return False
    
    def test_iris_connectivity(self) -> bool:
        """Test IRIS connection."""
        try:
            from iris_session_mcp import IRISSessionMCPServer
            
            server = IRISSessionMCPServer()
            
            # Test connection
            connection = server.connect_to_iris()
            self.log_test("IRIS Connection", True, "Successfully connected to IRIS")
            
            # Test version query using correct API
            import iris
            iris_obj = iris.createIRIS(connection)
            version = iris_obj.classMethodString("%SYSTEM.Version", "GetVersion")
            self.log_test("IRIS Version Query", True, f"IRIS Version: {version}")
            
            # Disconnect
            server.disconnect_from_iris()
            self.log_test("IRIS Disconnection", True, "Successfully disconnected from IRIS")
            
            return True
            
        except Exception as e:
            self.log_test("IRIS Connection", False, f"Error: {str(e)}")
            return False
    
    async def test_session_creation(self) -> bool:
        """Test IRIS session creation."""
        try:
            from iris_session_mcp import IRISSessionMCPServer
            
            server = IRISSessionMCPServer()
            
            # Test session creation
            session_result = await server.call_iris_method(
                "SessionMCP.Core.Session",
                "CreateSession",
                ["HSCUSTOM", ""]
            )
            
            session_data = json.loads(session_result)
            
            if session_data.get('status') == 'success':
                session_id = session_data.get('sessionId')
                self.log_test("Session Creation", True, f"Created session: {session_id}")
                return True
            else:
                error_msg = session_data.get('errorMessage', 'Unknown error')
                self.log_test("Session Creation", False, f"Error: {error_msg}")
                return False
            
        except Exception as e:
            self.log_test("Session Creation", False, f"Error: {str(e)}")
            return False
    
    async def test_command_execution(self) -> bool:
        """Test command execution."""
        try:
            from iris_session_mcp import IRISSessionMCPServer
            
            server = IRISSessionMCPServer()
            
            # Test execute_command method
            result = await server.execute_command('WRITE "Hello World!"')
            
            if result and "content" in result:
                content = result["content"][0]
                text = content.text
                # Command is successful if we get the success indicator
                success = "✅ Command executed successfully" in text
                self.log_test("Command Execution", success, f"Result: {text[:100]}...")
                return success
            else:
                self.log_test("Command Execution", False, "Invalid response format")
                return False
            
        except Exception as e:
            self.log_test("Command Execution", False, f"Error: {str(e)}")
            return False
    
    async def test_mcp_tool_definition(self) -> bool:
        """Test MCP tool definition."""
        try:
            from iris_session_mcp import list_tools
            
            tools = await list_tools()
            
            if tools and len(tools) > 0:
                tool_names = [tool.name for tool in tools]
                has_execute_command = "execute_command" in tool_names
                self.log_test("MCP Tool Definition", has_execute_command, 
                             f"Tools available: {tool_names}")
                return has_execute_command
            else:
                self.log_test("MCP Tool Definition", False, "No tools found")
                return False
            
        except Exception as e:
            self.log_test("MCP Tool Definition", False, f"Error: {str(e)}")
            return False
    
    def print_summary(self):
        """Print validation summary."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print("\n" + "="*60)
        print("IRIS SESSION MCP VALIDATION SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! The Python MCP client is ready for deployment.")
        else:
            print("\n⚠️ Some tests failed. Please address the issues before deployment.")
            print("\nFailed tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("="*60)


async def main():
    """Main validation function."""
    print("IRIS Session MCP Server Validation")
    print("Testing Python MCP client with real IRIS connectivity")
    print("-" * 60)
    
    validator = MCPClientValidator()
    
    # Run validation tests
    validator.test_python_dependencies()
    validator.test_mcp_server_structure()
    validator.test_iris_connectivity()
    await validator.test_session_creation()
    await validator.test_command_execution()
    await validator.test_mcp_tool_definition()
    
    # Print results
    validator.print_summary()
    
    # Return appropriate exit code
    all_passed = all(result["success"] for result in validator.test_results)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())
