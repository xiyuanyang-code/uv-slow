# uv-slow

A minimal tool to clean and generate `requirements.txt` from `pip list` output.
Scans Python files to identify actually used dependencies by default.

## Features

- Scans current environment dependencies using `pip list`
- Filters out unwanted dependencies
- Generates a clean `requirements.txt` file
- Command-line interface with options
- Scans Python files by default to identify actually used packages
- Can be installed via pip

## Installation

```bash
pip install uvslow
```

## Usage

```bash
# Basic usage (scans current directory by default)
uvslow

# Specify output file
uvslow -o my_requirements.txt

# Exclude specific packages
uvslow -e numpy pandas

# Dry run to see what would be written
uvslow --dry-run

# Disable import scanning
uvslow --no-scan-imports

# Scan imports in specific directory
uvslow -d /path/to/project

# Combine options
uvslow -o requirements.txt -e setuptools pip --dry-run
```

## Development

To install in development mode:

```bash
pip install -e .
```

## Todo List

- Add more test cases
- Fix problems for something like: `Flask @ file:///croot/flask_1716545870149/work`
- Add import which are not included