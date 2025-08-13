# Requirements Cleaner

A minimal tool to clean and generate `requirements.txt` from `pip freeze` output.
Optionally scans Python files to identify actually used dependencies.

>[!WARNING]
> To be Refactored.

## Features

- Scans current environment dependencies using `pip freeze`
- Filters out unwanted dependencies
- Generates a clean `requirements.txt` file
- Command-line interface with options
- Optional import scanning to identify actually used packages

## Usage

```bash
# Basic usage
python requirements_cleaner.py

# Specify output file
python requirements_cleaner.py -o my_requirements.txt

# Exclude specific packages
python requirements_cleaner.py -e numpy pandas

# Dry run to see what would be written
python requirements_cleaner.py --dry-run

# Scan imports in current directory and only include used packages
python requirements_cleaner.py --scan-imports

# Scan imports in specific directory
python requirements_cleaner.py --scan-imports -d /path/to/project

# Combine options
python requirements_cleaner.py -o requirements.txt -e setuptools pip --scan-imports --dry-run
```

## Todo List

- Make it packaged

- Add more test cases

- Fix problems for something like: `Flask @ file:///croot/flask_1716545870149/work`

- Update docs and rewrite README

- Add import which are not included