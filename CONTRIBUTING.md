# Contributing to FirScript

Thank you for your interest in contributing to FirScript! This document provides guidelines and workflows for contributing to the project.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Local Development Workflow](#local-development-workflow)
- [Testing](#testing)
- [Building the Package](#building-the-package)
- [Documentation](#documentation)
- [GitHub Workflow](#github-workflow)
- [Release Process](#release-process)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)

## Development Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/JungleDome/FirScript.git
   cd FirScript
   ```

2. **Install project dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install development dependencies**:
   ```bash
   pip install pytest build twine black isort flake8 sphinx sphinx-autodoc-typehints myst-parser
   ```
   - `pytest` for running tests
   - `build` for building the package
   - `twine` for checking and uploading packages to PyPI
   - `black` and `isort` for code formatting
   - `flake8` for linting
   - `sphinx` and related packages for documentation

## Local Development Workflow

The typical development workflow is:

1. Branch out from `main` for your feature or bugfix (e.g., `feature/my-feature`)
2. Make your changes
3. Run tests to ensure your changes don't break existing functionality
4. Format your code with black and isort
5. Build and check the package locally
6. Submit a pull request

## Testing

Run tests using pytest:
```bash
pytest
```

The test configuration is defined in `pyproject.toml` under `[tool.pytest.ini_options]`:
- Tests are located in the `tests` directory
- Test files follow the pattern `test_*.py`
- Test cases follow the pattern `test_When_Condition_Expect_Result`

To run specific tests:
```bash
pytest tests/test_specific_file.py
pytest tests/test_specific_file.py::test_specific_function
```

## Building the Package

Build the package using the Python build module:
```bash
python -m build
```

This creates distribution packages in the `dist/` directory.

Check if the built package is compatible with PyPI:
```bash
twine check dist/*
```

## Documentation

Build the documentation locally:
```bash
cd docs
make html
```

Or on Windows:
```bash
cd docs
make.bat html
```

The built documentation will be available in `docs/build/html/`.

Additionally, the documentation will be automatically built and hosted on [ReadTheDocs](https://firscript.readthedocs.io/) once the code is merged into the main branch.

## Release Process

To publish a new version:

1. Update the version in `firscript/version.py`
2. Create a new release on GitHub with a tag matching your version (e.g., `v0.1.0`)
3. GitHub Actions will automatically build and publish to PyPI

For testing the publishing process:
1. Go to the "Actions" tab in your GitHub repository
2. Select the "Publish to PyPI" workflow
3. Click "Run workflow"
4. The workflow will build and publish to TestPyPI

## Code Style

This project uses:
- **Black** for code formatting with a line length of 88 characters
- **isort** for import sorting (with Black compatibility)
- **flake8** for linting

Configuration for these tools is in `pyproject.toml`.

Format your code before submitting a pull request:
```bash
black .
isort .
flake8
```

## Pull Request Process

1. Ensure your code follows the project's style guidelines
2. Update documentation if necessary
3. Add or update tests as appropriate
4. Ensure all tests pass
5. Submit your pull request with a clear description of the changes and any relevant issue numbers

Thank you for contributing to FirScript!
