#!/usr/bin/env python3
"""
MCP Connection Diagnostic Tool
Tests all aspects of the MCP server setup and provides solutions
"""

import json
import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check environment variables"""
    print("=" * 50)
    print("ENVIRONMENT CHECK")
    print("=" * 50)
    
    env_vars = [
        "IRIS_HOSTNAME",
        "IRIS_PORT", 
        "IRIS_NAMESPACE",
        "IRIS_USERNAME",
        "IRIS_PASSWORD"
    ]
    
    for var in env_vars:
        val = os.getenv(var)
        if val:
            # Mask password
            if "PASSWORD" in var:
                print(f"✓ {var}: ****** (set)")
            else:
                print(f"✓ {var}: {val}")
        else:
            print(f"✗ {var}: NOT SET")

def check_python_packages():
    """Check required Python packages"""
    print("\n" + "=" * 50)
    print("PYTHON PACKAGE CHECK")
    print("=" * 50)
    
    packages = ["fastmcp", "iris"]
    
    for package in packages:
        try:
            __import__(package)
            print(f"✓ {package}: installed")
        except ImportError:
            print(f"✗ {package}: NOT INSTALLED")

def check_iris_connection():
    """Test IRIS connection"""
    print("\n" + "=" * 50)
    print("IRIS CONNECTION CHECK")
    print("=" * 50)
    
    try:
        import iris
        
        hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
        port = int(os.getenv('IRIS_PORT', '1972'))
        namespace = os.getenv('IRIS_NAMESPACE', 'HSCUSTOM')
        username = os.getenv('IRIS_USERNAME', '_SYSTEM')
        password = os.getenv('IRIS_PASSWORD', '_SYSTEM')
        
        print(f"Connecting to {hostname}:{port}/{namespace}...")
        
        conn = iris.connect(hostname, port, namespace, username, password)
        iris_obj = iris.createIRIS(conn)
        
        # Test basic command
        result = iris_obj.classMethodString("ExecuteMCP.Core.Command", "GetSystemInfo")
        parsed = json.loads(result)
        
        if parsed.get("status") == "success":
            print("✓ IRIS connection successful")
            print(f"  Version: {parsed.get('irisVersion', 'unknown')}")
        else:
            print(f"✗ IRIS connection failed: {parsed.get('error')}")
        
        conn.close()
        
    except ImportError:
        print("✗ iris package not installed")
        print("  Fix: pip install intersystems-irispython")
    except Exception as e:
        print(f"✗ IRIS connection failed: {str(e)}")
        print("  Check your IRIS instance is running and credentials are correct")

def test_mcp_server():
    """Test MCP server startup"""
    print("\n" + "=" * 50)
    print("MCP SERVER TEST")
    print("=" * 50)
    
    script_path = Path("C:/iris-execute-mcp/iris_execute_mcp.py")
    venv_python = Path("C:/iris-execute-mcp/venv/Scripts/python.exe")
    
    if not script_path.exists():
        print(f"✗ MCP script not found: {script_path}")
        return
    
    if not venv_python.exists():
        print(f"✗ Virtual environment not found: {venv_python}")
        return
    
    print("Testing MCP server startup...")
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env.update({
            'IRIS_HOSTNAME': os.getenv('IRIS_HOSTNAME', 'localhost'),
            'IRIS_PORT': os.getenv('IRIS_PORT', '1972'),
            'IRIS_NAMESPACE': os.getenv('IRIS_NAMESPACE', 'HSCUSTOM'),
            'IRIS_USERNAME': os.getenv('IRIS_USERNAME', '_SYSTEM'),
            'IRIS_PASSWORD': os.getenv('IRIS_PASSWORD', '_SYSTEM')
        })
        
        # Try to start the server
        process = subprocess.Popen(
            [str(venv_python), str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        # Wait a moment for startup
        import time
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✓ MCP server started successfully")
            print("  Terminating test server...")
            process.terminate()
            process.wait(timeout=5)
        else:
            # Process ended, check for errors
            stdout, stderr = process.communicate()
            print("✗ MCP server failed to start")
            if stderr:
                print(f"  Error: {stderr[:500]}")
        
    except Exception as e:
        print(f"✗ Failed to test MCP server: {str(e)}")

def check_cline_config():
    """Check Cline MCP configuration"""
    print("\n" + "=" * 50)
    print("CLINE CONFIGURATION CHECK")
    print("=" * 50)
    
    config_path = Path("C:/iris-execute-mcp/MCP_CONFIG.json")
    
    if not config_path.exists():
        print(f"✗ MCP configuration not found: {config_path}")
        return
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if "cline.mcp.servers" in config:
            servers = config["cline.mcp.servers"]
            if "iris-execute-mcp" in servers:
                server_config = servers["iris-execute-mcp"]
                print("✓ Cline MCP configuration found")
                print(f"  Command: {server_config.get('command')}")
                print(f"  Args: {server_config.get('args')}")
                print(f"  Transport: {server_config.get('transportType')}")
                print(f"  Disabled: {server_config.get('disabled', False)}")
                
                # Check if paths exist
                cmd_path = Path(server_config.get('command', ''))
                if not cmd_path.exists():
                    print(f"  ✗ Command path does not exist: {cmd_path}")
                
                if server_config.get('args'):
                    script_path = Path(server_config['args'][0])
                    if not script_path.exists():
                        print(f"  ✗ Script path does not exist: {script_path}")
            else:
                print("✗ iris-execute-mcp not found in configuration")
        else:
            print("✗ Invalid configuration format")
            
    except Exception as e:
        print(f"✗ Failed to read configuration: {str(e)}")

def provide_solutions():
    """Provide solutions for common issues"""
    print("\n" + "=" * 50)
    print("TROUBLESHOOTING STEPS")
    print("=" * 50)
    
    print("""
1. If MCP server works but Cline shows "Connection closed":
   - Close VS Code completely
   - Reopen VS Code and the project
   - Cline should reconnect automatically

2. If that doesn't work:
   - Open VS Code Command Palette (Ctrl+Shift+P)
   - Search for "Cline: Reset MCP Connections"
   - Or disable/enable the Cline extension

3. Manual restart:
   - Run: .\\restart_mcp.bat
   - Then restart VS Code

4. Check VS Code settings:
   - File > Preferences > Settings
   - Search for "cline.mcp"
   - Ensure configuration matches MCP_CONFIG.json

5. If still having issues:
   - Check Windows Defender/Antivirus isn't blocking Python
   - Ensure no other Python processes are using the same ports
   - Try running VS Code as Administrator
""")

if __name__ == "__main__":
    print("\nIRIS EXECUTE MCP DIAGNOSTIC TOOL")
    print("=" * 50)
    
    # Set environment variables if not set
    if not os.getenv('IRIS_HOSTNAME'):
        os.environ['IRIS_HOSTNAME'] = 'localhost'
    if not os.getenv('IRIS_PORT'):
        os.environ['IRIS_PORT'] = '1972'
    if not os.getenv('IRIS_NAMESPACE'):
        os.environ['IRIS_NAMESPACE'] = 'HSCUSTOM'
    if not os.getenv('IRIS_USERNAME'):
        os.environ['IRIS_USERNAME'] = '_SYSTEM'
    if not os.getenv('IRIS_PASSWORD'):
        os.environ['IRIS_PASSWORD'] = '_SYSTEM'
    
    check_environment()
    check_python_packages()
    check_iris_connection()
    test_mcp_server()
    check_cline_config()
    provide_solutions()
    
    print("\n" + "=" * 50)
    print("Diagnostic complete!")
    print("=" * 50)
