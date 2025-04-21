# GitHub Actions Workflows

This directory contains GitHub Actions workflows for building, testing, and publishing the TradePilot Script Engine package.

## Workflows

### 1. Build and Test (`build-and-test.yml`)

This workflow runs automatically on:
- Pushes to the main/master branch
- Pull requests to the main/master branch
- Manual triggering

It performs the following steps:
- Tests the package on multiple Python versions (3.8, 3.9, 3.10, 3.11)
- Builds the package
- Checks the package for PyPI compatibility
- Uploads the built package as an artifact

### 2. Build Package (`build.yml`)

This workflow can be manually triggered and:
- Builds the package
- Checks the package for PyPI compatibility
- Uploads the built package as an artifact

### 3. Publish to PyPI (`publish.yml`)

This workflow runs automatically when:
- A new GitHub release is created
- Manual triggering

It performs the following steps:
- Builds the package
- Checks the package for PyPI compatibility
- Publishes to PyPI when triggered by a release
- Publishes to TestPyPI when manually triggered

## Required Secrets

To use these workflows, you need to set up the following secrets in your GitHub repository:

- `PYPI_API_TOKEN`: Your PyPI API token for publishing to PyPI
- `TEST_PYPI_API_TOKEN`: Your TestPyPI API token for publishing to TestPyPI (only needed if you want to test publishing)

## How to Use

### Testing and Building

The `build-and-test.yml` workflow runs automatically on pushes and pull requests. You don't need to do anything special.

### Publishing to PyPI

1. Update the version in `script_engine/version.py`
2. Create a new release on GitHub with a tag matching your version (e.g., `v0.1.0`)
3. The workflow will automatically build and publish to PyPI

### Publishing to TestPyPI

1. Go to the "Actions" tab in your GitHub repository
2. Select the "Publish to PyPI" workflow
3. Click "Run workflow"
4. The workflow will build and publish to TestPyPI
