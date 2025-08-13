#!/usr/bin/env python3
"""
A minimal tool to clean and generate requirements.txt from pip freeze output.
Optionally scans Python files to identify actually used dependencies.
"""

import subprocess
import sys
import argparse
import os
import ast
from typing import List, Set, Dict
from pathlib import Path


def get_pip_freeze_output() -> List[str]:
    """Get the output of pip freeze command."""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"Error running pip freeze: {e}", file=sys.stderr)
        return []


def scan_imports(directory: str) -> Set[str]:
    """Scan Python files in directory and extract imported package names."""
    imported_packages = set()
    
    # Standard library modules to exclude
    stdlib_modules = {
        'os', 'sys', 'json', 're', 'datetime', 'collections', 'itertools',
        'functools', 'typing', 'pathlib', 'subprocess', 'argparse', 'ast',
        'math', 'random', 'time', 'urllib', 'http', 'base64', 'hashlib',
        'logging', 'threading', 'multiprocessing', 'asyncio', 'unittest',
        'contextlib', 'dataclasses', 'enum', 'copy', 'pickle', 'csv',
        'xml', 'html', 'sqlite3', 'tempfile', 'glob', 'fnmatch', 'shutil',
        'zipfile', 'tarfile', 'gzip', 'bz2', 'lzma', 'platform', 'getpass',
        'locale', 'gettext', 'calendar', 'queue', 'heapq', 'bisect',
        'array', 'struct', 'binascii', ' mmap', 'select', 'socket',
        'ssl', 'ftplib', 'smtplib', 'poplib', 'imaplib', 'telnetlib',
        'uuid', 'hmac', 'secrets', 'statistics', 'decimal', 'fractions',
        'numbers', 'cmath', 'operator', 'string', 'textwrap', 'difflib'
    }
    
    # Walk through directory
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse the Python file
                    tree = ast.parse(content)
                    
                    # Extract imports
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                module_name = alias.name.split('.')[0]  # Get top-level package
                                if module_name not in stdlib_modules:
                                    imported_packages.add(module_name.lower())
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:  # Make sure module is not None
                                module_name = node.module.split('.')[0]  # Get top-level package
                                if module_name not in stdlib_modules:
                                    imported_packages.add(module_name.lower())
                except Exception as e:
                    print(f"Warning: Could not parse {file_path}: {e}")
    
    return imported_packages


def filter_dependencies(dependencies: List[str], exclude: Set[str] = None, 
                       used_packages: Set[str] = None) -> List[str]:
    """Filter out unwanted dependencies."""
    if exclude is None:
        exclude = set()
    
    if used_packages is not None:
        # If we have used packages info, only include those
        filtered = []
        for dep in dependencies:
            if dep.strip() == '':
                continue
                
            # Extract package name (before == or @)
            package_name = dep.split('==')[0].split('>=')[0].split('<=')[0].split('@')[0].strip()
            
            # Check if package should be excluded or not used
            if (package_name.lower() not in {name.lower() for name in exclude} and 
                package_name.lower() in used_packages):
                filtered.append(dep)
        return filtered
    else:
        # Original filtering logic
        filtered = []
        for dep in dependencies:
            if dep.strip() == '':
                continue
                
            # Extract package name (before == or @)
            package_name = dep.split('==')[0].split('>=')[0].split('<=')[0].split('@')[0].strip()
            
            if package_name.lower() not in {name.lower() for name in exclude}:
                filtered.append(dep)
        
        return filtered


def write_requirements(dependencies: List[str], output_file: str = 'requirements.txt') -> None:
    """Write dependencies to requirements.txt file."""
    try:
        with open(output_file, 'w') as f:
            for dep in dependencies:
                f.write(f"{dep}\n")
        print(f"Successfully wrote {len(dependencies)} dependencies to {output_file}")
    except IOError as e:
        print(f"Error writing to {output_file}: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description='Clean and generate requirements.txt from pip freeze')
    parser.add_argument('-o', '--output', default='requirements.txt', 
                       help='Output file name (default: requirements.txt)')
    parser.add_argument('-e', '--exclude', nargs='*', default=[], 
                       help='Packages to exclude (e.g., -e numpy pandas)')
    parser.add_argument('-d', '--directory', default='.', 
                       help='Directory to scan for imports (default: current directory)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be written without actually writing')
    parser.add_argument('--scan-imports', action='store_true',
                       help='Scan Python files to identify actually used dependencies')
    
    args = parser.parse_args()
    
    # Get pip freeze output
    dependencies = get_pip_freeze_output()
    
    if not dependencies or (len(dependencies) == 1 and dependencies[0] == ''):
        print("No dependencies found.")
        return
    
    # Scan imports if requested
    used_packages = None
    if args.scan_imports:
        print(f"Scanning imports in directory: {args.directory}")
        used_packages = scan_imports(args.directory)
        print(f"Found {len(used_packages)} unique imported packages")
    
    # Filter dependencies
    filtered_deps = filter_dependencies(dependencies, set(args.exclude), used_packages)
    
    # Show results
    action = "used" if args.scan_imports else "filtered"
    print(f"Found {len(dependencies)} dependencies, {len(filtered_deps)} after {action}")
    
    if args.dry_run:
        print(f"\n{action.capitalize()} dependencies:")
        for dep in filtered_deps:
            print(f"  {dep}")
        return
    
    # Write to file
    write_requirements(filtered_deps, args.output)


if __name__ == '__main__':
    main()