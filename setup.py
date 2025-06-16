from setuptools import setup, find_packages

setup(
    name="iris-session-mcp",
    version="1.0.0",
    description="IRIS Session MCP Server - Execute ObjectScript commands via MCP protocol",
    author="IRIS Session MCP Team",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "intersystems-iris>=3.2.0",
        "mcp>=0.4.0", 
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "iris-session-mcp=iris_session_mcp:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
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
