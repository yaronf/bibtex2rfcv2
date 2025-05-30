# Development Guide

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yaronf/bibtex2rfcv2.git
cd bibtex2rfcv2
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

## Project Structure

```
bibtex2rfcv2/
├── src/
│   └── bibtex2rfcv2/
│       ├── __init__.py
│       ├── cli.py
│       ├── converter.py
│       ├── parser.py
│       ├── errors.py
│       └── constants.py
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_converter.py
│   ├── test_parser.py
│   └── data/
│       └── *.bibtex
├── docs/
│   ├── index.md
│   ├── installation.md
│   ├── usage.md
│   ├── api.md
│   └── development.md
├── pyproject.toml
└── README.md
```

## Running Tests

1. Run all tests:
```bash
pytest
```

2. Run tests with coverage:
```bash
pytest --cov=src
```

3. Run specific test categories:
```bash
# Unit tests
pytest tests/test_*.py

# CLI tests
pytest tests/test_cli.py

# Parser tests
pytest tests/test_parser.py
```

## Code Quality Tools

1. Type checking:
```bash
mypy src/bibtex2rfcv2
```

2. Code formatting:
```bash
# Format code
black src/bibtex2rfcv2 tests

# Sort imports
isort src/bibtex2rfcv2 tests
```

3. Linting:
```bash
flake8 src/bibtex2rfcv2 tests
```

## Adding New Features

1. Create a new branch:
```bash
git checkout -b feature/new-feature
```

2. Make your changes
3. Add tests for new functionality
4. Run all tests and quality checks
5. Update documentation
6. Submit a pull request

## Testing Guidelines

1. Unit Tests:
   - Test individual functions and methods
   - Mock external dependencies
   - Use pytest fixtures for common setup

2. Integration Tests:
   - Test component interactions
   - Use real file I/O
   - Test error conditions

3. CLI Tests:
   - Test all command options
   - Test stdin/stdout handling
   - Test error messages

## Documentation Guidelines

1. Code Documentation:
   - Use docstrings for all public functions
   - Include type hints
   - Document exceptions

2. API Documentation:
   - Keep docs/api.md up to date
   - Include examples
   - Document all parameters

3. User Documentation:
   - Keep docs/usage.md up to date
   - Include common use cases
   - Document all features

## Release Process

1. Update version in pyproject.toml
2. Update CHANGELOG.md
3. Run all tests
4. Build package:
```bash
python -m build
```

5. Upload to PyPI:
```bash
twine upload dist/*
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions small and focused
- Use meaningful variable names
- Add comments for complex logic 