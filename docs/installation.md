# Installation Guide

## Requirements
- Python 3.10 or higher
- pip (Python package installer)

## Basic Installation
```bash
pip install bibtex2rfcv2
```

## Development Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/bibtex2rfcv2.git
cd bibtex2rfcv2

# Install in development mode with all dependencies
pip install -e ".[dev]"
```

## Verifying Installation
```bash
# Check the version
bibtex2rfc --version

# Try a simple conversion
echo '@article{test, title="Test", author="Author"}' | bibtex2rfc > test.xml
```

## Troubleshooting
If you encounter any issues during installation:

1. Ensure you have Python 3.10 or higher:
   ```bash
   python --version
   ```

2. Update pip to the latest version:
   ```bash
   pip install --upgrade pip
   ```

3. If you encounter permission errors, try:
   ```bash
   pip install --user bibtex2rfcv2
   ``` 