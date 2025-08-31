@echo off
echo Restarting IRIS Execute MCP Server...
echo.

REM Kill any existing Python processes that might be running the MCP server
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo Starting MCP server...
start /B C:\iris-execute-mcp\venv\Scripts\python.exe C:\iris-execute-mcp\iris_execute_mcp.py

echo.
echo MCP server should now be running.
echo Please restart VS Code to reconnect Cline to the MCP server.
pause
