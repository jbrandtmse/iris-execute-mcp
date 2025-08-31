from setuptools import setup, find_packages

setup(
    name="iris-execute-mcp",
    version="2.0.0",
    description="IRIS Execute MCP Server - Execute ObjectScript commands via FastMCP protocol with I/O capture",
    author="IRIS Execute MCP Team",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "intersystems-iris>=3.2.0",
        "fastmcp>=0.4.0", 
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "iris-execute-mcp=iris_execute_fastmcp:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License", 
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
