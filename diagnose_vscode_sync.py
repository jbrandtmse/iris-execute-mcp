#!/usr/bin/env python3
"""
Diagnose VS Code ObjectScript extension sync behavior
"""

import os
import json

def main():
    """Diagnose VS Code sync issues"""
    
    print("=" * 80)
    print("VS Code ObjectScript Extension Sync Diagnosis")
    print("=" * 80)
    
    # Check filesystem for classes
    packages_to_check = [
        "ExecuteMCP.Core",
        "ExecuteMCP.Test", 
        "TestDiscovery"
    ]
    
    print("\nFile System Check:")
    print("-" * 40)
    
    for package in packages_to_check:
        package_path = package.replace(".", "/")
        src_path = f"src/{package_path}"
        
        if os.path.exists(src_path):
            files = [f for f in os.listdir(src_path) if f.endswith('.cls')]
            print(f"\n{package} Package:")
            print(f"  Directory: {src_path}")
            print(f"  Files: {files}")
        else:
            print(f"\n{package} Package:")
            print(f"  Directory {src_path} does not exist")
    
    # Check VS Code workspace settings
    workspace_files = [
        "iris-execute-mcp.code-workspace",
        ".vscode/settings.json"
    ]
    
    print("\n" + "=" * 80)
    print("VS Code Configuration:")
    print("=" * 80)
    
    for ws_file in workspace_files:
        if os.path.exists(ws_file):
            print(f"\n{ws_file}:")
            print("-" * 40)
            try:
                with open(ws_file, 'r') as f:
                    config = json.load(f)
                    
                    # Look for ObjectScript extension settings
                    if "settings" in config:
                        settings = config["settings"]
                    else:
                        settings = config
                    
                    # Check relevant settings
                    relevant_keys = [
                        "objectscript.conn",
                        "objectscript.export",
                        "objectscript.importOnSave",
                        "objectscript.autoCompile",
                        "objectscript.compileOnSave"
                    ]
                    
                    for key in relevant_keys:
                        if key in settings:
                            value = settings[key]
                            # Truncate long values
                            if isinstance(value, dict):
                                print(f"  {key}: <dict with {len(value)} keys>")
                            elif isinstance(value, list):
                                print(f"  {key}: <list with {len(value)} items>")
                            else:
                                print(f"  {key}: {value}")
                    
                    # Check if there are folder-specific settings
                    if "folders" in config:
                        print(f"\nWorkspace has {len(config['folders'])} folders configured")
                        for i, folder in enumerate(config["folders"]):
                            if "name" in folder:
                                print(f"  Folder {i+1}: {folder['name']}")
                            
            except Exception as e:
                print(f"  Error reading: {e}")
        else:
            print(f"\n{ws_file}: Not found")
    
    # Check C:\temp for test files (where %UnitTest.Manager looks)
    print("\n" + "=" * 80)
    print("Test Discovery Paths (C:\\temp):")
    print("=" * 80)
    
    test_dirs = [
        "C:\\temp\\ExecuteMCP\\Test",
        "C:\\temp\\TestDiscovery"
    ]
    
    for test_dir in test_dirs:
        print(f"\n{test_dir}:")
        if os.path.exists(test_dir):
            files = os.listdir(test_dir)
            if files:
                for f in files:
                    file_path = os.path.join(test_dir, f)
                    size = os.path.getsize(file_path)
                    print(f"  - {f} ({size} bytes)")
            else:
                print("  (empty)")
        else:
            print("  (does not exist)")
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary:")
    print("=" * 80)
    
    print("\nKey Findings:")
    print("1. TestDiscovery classes exist in src/ but not in IRIS")
    print("2. Only ExecuteMCP.Test.SampleUnitTest exists in IRIS (3 test methods)")
    print("3. VS Code's auto-sync may not be working for new files")
    print("4. Test discovery uses C:\\temp directory for loading test files")
    
    print("\nRecommendations:")
    print("1. Copy TestDiscovery files to C:\\temp\\TestDiscovery\\ for discovery")
    print("2. Use /load qualifier to load from filesystem during test run")
    print("3. Or manually import classes to IRIS using Studio or other method")

if __name__ == "__main__":
    main()
