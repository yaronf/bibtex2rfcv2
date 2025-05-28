# BibTeX to RFC v2

A modern Python tool for converting BibTeX citations into RFC-compliant XML references.

## Overview

This tool converts BibTeX entries into XML references that can be used in Internet Drafts and RFCs. It is a modernized version of the original [bibtex2rfc](https://github.com/yaronf/bibtex2rfc) project, with improved features and maintainability.

## Features

- Converts BibTeX entries to RFC-compliant XML format
- Supports all standard BibTeX entry types
- Maintains compatibility with xml2rfc v3 format
- Handles UTF-8 encoding properly
- Supports both file input and stdin/stdout operations
- Modern Python practices and dependencies
- Comprehensive test coverage
- Type hints throughout the codebase

## Requirements

- Python 3.8 or higher
- Modern Python packaging tools (pip, poetry, etc.)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/bibtex2rfcv2.git
cd bibtex2rfcv2

# Install in development mode
pip install -e ".[dev]"
```

## Usage

```bash
# Convert a BibTeX file to RFC XML
bibtex2rfc input.bib output.xml

# Convert from stdin to stdout
cat input.bib | bibtex2rfc > output.xml
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy src/bibtex2rfcv2

# Format code
black src/bibtex2rfcv2 tests
isort src/bibtex2rfcv2 tests

# Run linter
flake8 src/bibtex2rfcv2 tests
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 