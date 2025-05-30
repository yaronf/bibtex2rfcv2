# Troubleshooting Guide

## Installation Issues

### Python Version
**Problem**: Installation fails with Python version error
**Solution**: Ensure you have Python 3.8 or higher:
```bash
python --version
```

### Permission Errors
**Problem**: `pip install` fails with permission errors
**Solution**: Use one of these approaches:
```bash
# Install for current user only
pip install --user bibtex2rfcv2

# Use sudo (not recommended)
sudo pip install bibtex2rfcv2

# Use virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate
pip install bibtex2rfcv2
```

### Missing Dependencies
**Problem**: Installation fails due to missing dependencies
**Solution**: Update pip and try again:
```bash
pip install --upgrade pip
pip install bibtex2rfcv2
```

## Usage Issues

### Command Not Found
**Problem**: `bibtex2rfcv2` command not found
**Solution**: 
1. Verify installation:
```bash
pip list | grep bibtex2rfcv2
```
2. Check PATH:
```bash
echo $PATH
```
3. Reinstall if needed:
```bash
pip uninstall bibtex2rfcv2
pip install bibtex2rfcv2
```

### File Access
**Problem**: Cannot read/write files
**Solution**:
1. Check file permissions:
```bash
ls -l input.bib output.xml
```
2. Check directory permissions:
```bash
ls -ld .
```
3. Use absolute paths if needed:
```bash
bibtex2rfcv2 convert /full/path/to/input.bib /full/path/to/output.xml
```

### BibTeX Parsing Errors

#### Missing Required Fields
**Problem**: Error about missing required fields
**Solution**: Ensure your BibTeX entry has all required fields:
```bibtex
@article{example,
  author = {Author Name},  # Required
  title = {Title},         # Required
  journal = {Journal},     # Required for articles
  year = {2023}           # Required
}
```

#### Invalid Field Format
**Problem**: Error about invalid field format
**Solution**: Check field formatting:
- Use curly braces `{}` or quotes `""` for values
- Escape special characters
- Use proper BibTeX syntax

#### Encoding Issues
**Problem**: Unicode/encoding errors
**Solution**:
1. Ensure files are UTF-8 encoded
2. Use proper Unicode characters
3. Check file encoding:
```bash
file -i input.bib
```

### XML Generation Issues

#### Invalid XML
**Problem**: Generated XML is invalid
**Solution**:
1. Check BibTeX entry format
2. Verify all required fields
3. Use `--no-progress` for verbose output:
```bash
bibtex2rfcv2 convert --no-progress input.bib output.xml
```

#### Missing References
**Problem**: Some references are missing from output
**Solution**:
1. Check BibTeX syntax
2. Verify entry types are supported
3. Check for parsing errors in output

## Performance Issues

### Slow Processing
**Problem**: Tool runs slowly with large files
**Solution**:
1. Use `--no-progress` to disable progress bar
2. Process files in smaller batches
3. Use stdin/stdout for piping:
```bash
cat large.bib | bibtex2rfcv2 convert - output.xml
```

### Memory Usage
**Problem**: High memory usage with large files
**Solution**:
1. Process files in smaller batches
2. Use streaming input/output
3. Monitor memory usage:
```bash
top -p $(pgrep -f bibtex2rfcv2)
```

## Development Issues

### Test Failures
**Problem**: Tests are failing
**Solution**:
1. Check test environment:
```bash
python -m pytest --version
```
2. Run specific test:
```bash
python -m pytest tests/test_specific.py -v
```
3. Check test data:
```bash
ls -l tests/data/
```

### Type Checking Errors
**Problem**: mypy reports type errors
**Solution**:
1. Check type hints
2. Update type stubs
3. Run mypy with verbose output:
```bash
mypy src/bibtex2rfcv2 --verbose
```

### Code Style Issues
**Problem**: black/isort/flake8 report issues
**Solution**:
1. Format code:
```bash
black src/bibtex2rfcv2 tests
isort src/bibtex2rfcv2 tests
```
2. Fix linting issues:
```bash
flake8 src/bibtex2rfcv2 tests
```

## Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/yourusername/bibtex2rfcv2/issues)
2. Search existing issues
3. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Relevant error messages 