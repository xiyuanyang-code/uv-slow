"""
A minimal tool to clean and generate requirements.txt from pip list output.
Scans Python files to identify actually used dependencies by default.
"""

import subprocess
import sys
import argparse
import os
import ast
import json
from typing import List, Set, Dict

# --- ANSI Escape Codes for colored output ---
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"


class RequirementsGenerator:
    """
    A tool to generate a requirements.txt file by scanning pip installed packages
    and optionally filtering them based on code imports.
    """

    def __init__(self, directory: str, output: str, exclude: List[str]):
        self.directory = directory
        self.output_file = output
        self.exclude_packages = {pkg.lower() for pkg in exclude}
        self.all_dependencies: List[Dict[str, str]] = []
        self.used_packages: Set[str] = set()

    def get_python_version(self) -> str:
        return sys.version

    def get_installed_packages(self) -> None:
        """
        Retrieves a list of all installed packages using pip.
        Stores the result in self.all_dependencies.
        """
        try:
            print(f"{BOLD}Fetching installed packages via `pip list`...{RESET}")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True,
            )
            self.all_dependencies = json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"{RED}Error running pip list: {e}{RESET}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"{RED}Error parsing pip list output: {e}{RESET}", file=sys.stderr)
            sys.exit(1)

    def _get_stdlib_modules(self) -> Set[str]:
        """Returns a set of common Python standard library modules to be ignored."""
        return {
            "os",
            "sys",
            "json",
            "re",
            "datetime",
            "collections",
            "itertools",
            "functools",
            "typing",
            "pathlib",
            "subprocess",
            "argparse",
            "ast",
            "math",
            "random",
            "time",
            "urllib",
            "http",
            "base64",
            "hashlib",
            "logging",
            "threading",
            "multiprocessing",
            "asyncio",
            "unittest",
            "contextlib",
            "dataclasses",
            "enum",
            "copy",
            "pickle",
            "csv",
            "xml",
            "html",
            "sqlite3",
            "tempfile",
            "glob",
            "fnmatch",
            "shutil",
            "zipfile",
            "tarfile",
            "gzip",
            "bz2",
            "lzma",
            "platform",
            "getpass",
            "locale",
            "gettext",
            "calendar",
            "queue",
            "heapq",
            "bisect",
            "array",
            "struct",
            "binascii",
            "mmap",
            "select",
            "socket",
            "ssl",
            "ftplib",
            "smtplib",
            "poplib",
            "imaplib",
            "telnetlib",
            "uuid",
            "hmac",
            "secrets",
            "statistics",
            "decimal",
            "fractions",
            "numbers",
            "cmath",
            "operator",
            "string",
            "textwrap",
            "difflib",
        }

    def scan_for_imports(self) -> None:
        """
        Scans the project directory for Python files and extracts top-level
        imported package names, storing them in self.used_packages.
        """
        print(f"{BOLD}Scanning imports in directory: {self.directory}...{RESET}")
        imported_modules = set()
        stdlib_modules = self._get_stdlib_modules()

        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            tree = ast.parse(f.read(), filename=file_path)

                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                module_name = node.names[0].name
                                top_level = module_name.split(".")[0]
                                if top_level not in stdlib_modules:
                                    imported_modules.add(top_level.lower())
                            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                                if node.module:
                                    top_level = node.module.split(".")[0]
                                    if top_level not in stdlib_modules:
                                        imported_modules.add(top_level.lower())
                    except Exception as e:
                        print(
                            f"{YELLOW}{BOLD}Warning: Could not parse {file_path}: {e}{RESET}",
                            file=sys.stderr,
                        )
        self.used_packages = imported_modules

    def filter_dependencies(self) -> List[Dict[str, str]]:
        """
        Filters the list of installed dependencies based on excluded packages
        and the list of used packages from code scans.
        """
        filtered_deps = []
        all_installed_lower = {dep["name"].lower() for dep in self.all_dependencies}

        # Check for unknown imports
        unknown_imports = self.used_packages - all_installed_lower
        if unknown_imports:
            print(
                f"{YELLOW}{BOLD}Warning: Found {len(unknown_imports)} package(s) in code but not installed:{RESET}"
            )
            for pkg in sorted(unknown_imports):
                print(f"  - {pkg}")

        for dep in self.all_dependencies:
            dep_name_lower = dep["name"].lower()
            if dep_name_lower in self.exclude_packages:
                continue

            if self.used_packages and dep_name_lower not in self.used_packages:
                continue

            filtered_deps.append(dep)

        return filtered_deps

    def confirm_overwrite(self) -> bool:
        """Checks if the output file exists and prompts for overwrite confirmation."""
        if os.path.exists(self.output_file) and os.path.getsize(self.output_file) > 0:
            print(
                f"{YELLOW}{BOLD}Warning: Output file '{self.output_file}' already exists and is not empty.{RESET}"
            )
            while True:
                response = input("Do you want to overwrite it? (y/n): ").strip().lower()
                if response in {"y", "yes"}:
                    return True
                if response in {"n", "no"}:
                    return False
                print("Please enter 'y' for yes or 'n' for no.")
        return True

    def write_requirements(self, dependencies: List[Dict[str, str]]) -> None:
        """Writes the final list of dependencies to the output file."""
        try:
            with open(self.output_file, "w") as f:
                # write some comments and the Python version
                self.version = self.get_python_version()
                f.write(f"# Python Version {self.version} is recommended\n")
                f.write(f"# Several Dependencies: \n")
                for dep in dependencies:
                    f.write(f"{dep['name']}=={dep['version']}\n")
            print(
                f"{GREEN}Successfully wrote {len(dependencies)} dependencies to {self.output_file}{RESET}"
            )
        except IOError as e:
            print(
                f"{RED}Error writing to {self.output_file}: {e}{RESET}", file=sys.stderr
            )
            sys.exit(1)

    def run(self, dry_run: bool, scan_imports: bool):
        """Orchestrates the entire process of generating the requirements file."""
        self.get_installed_packages()
        if not self.all_dependencies:
            print(f"{YELLOW}No dependencies found from `pip list` output.{RESET}")
            return

        if scan_imports:
            self.scan_for_imports()
            print(
                f"{GREEN}Found {len(self.used_packages)} unique imported packages.{RESET}"
            )

        filtered_dependencies = self.filter_dependencies()

        action_msg = "used" if scan_imports else "filtered"
        print(
            f"\nFound {len(self.all_dependencies)} dependencies. "
            f"{len(filtered_dependencies)} after {action_msg}."
        )

        if dry_run:
            print(
                f"\n{BOLD}Dry Run: The following dependencies would be written to '{self.output_file}':{RESET}"
            )
            for dep in filtered_dependencies:
                print(f"  {dep['name']}=={dep['version']}")
            return

        if not self.confirm_overwrite():
            print("Operation cancelled by user.")
            return

        self.write_requirements(filtered_dependencies)


def main():
    """Main entry point for the command-line script."""
    parser = argparse.ArgumentParser(
        description="Clean and generate requirements.txt from pip list."
    )
    parser.add_argument(
        "-o", "--output", default="requirements.txt", help="Output file name."
    )
    parser.add_argument(
        "-e", "--exclude", nargs="*", default=[], help="Packages to exclude."
    )
    parser.add_argument(
        "-d", "--directory", default=".", help="Directory to scan for imports."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be written without writing.",
    )
    parser.add_argument(
        "--scan-imports",
        action="store_true",
        default=True,
        help="Scan Python files for imports.",
    )
    parser.add_argument(
        "--no-scan-imports",
        action="store_false",
        dest="scan_imports",
        help="Disable scanning.",
    )

    args = parser.parse_args()

    generator = RequirementsGenerator(args.directory, args.output, args.exclude)
    generator.run(args.dry_run, args.scan_imports)


if __name__ == "__main__":
    main()
