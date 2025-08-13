#!/usr/bin/env python3
"""
Example usage of the requirements-cleaner tool
"""

import subprocess
import sys
import os

def main():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to our requirements cleaner script
    cleaner_script = os.path.join(script_dir, "requirements_cleaner.py")
    
    # Example 1: Basic usage
    print("Example 1: Basic usage")
    print("Running: python requirements_cleaner.py --dry-run")
    subprocess.run([sys.executable, cleaner_script, "--dry-run"])
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Exclude specific packages
    print("Example 2: Exclude specific packages")
    print("Running: python requirements_cleaner.py -e pip setuptools wheel --dry-run")
    subprocess.run([sys.executable, cleaner_script, "-e", "pip", "setuptools", "wheel", "--dry-run"])
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Specify output file
    print("Example 3: Specify output file")
    print("Running: python requirements_cleaner.py -o my_requirements.txt --dry-run")
    subprocess.run([sys.executable, cleaner_script, "-o", "my_requirements.txt", "--dry-run"])
    
    print("\n" + "="*50 + "\n")
    
    # Example 4: Scan imports in a directory
    print("Example 4: Scan imports in a directory")
    test_project_dir = os.path.join(script_dir, "test_project")
    print(f"Running: python requirements_cleaner.py --scan-imports -d {test_project_dir} --dry-run")
    subprocess.run([sys.executable, cleaner_script, "--scan-imports", "-d", test_project_dir, "--dry-run"])

if __name__ == "__main__":
    main()