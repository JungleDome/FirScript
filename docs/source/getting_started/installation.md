# Installation

## Requirements

FirScript requires Python 3.8 or higher and the following dependencies:

- numpy
- pandas
- pytest (for running tests)

## Installing from PyPI

The easiest way to install FirScript is via pip:

```bash
pip install firscript
```

## Installing from Source

You can also install from source for the latest development version:

```bash
git clone https://github.com/JungleDome/FirScript.git
cd FirScript
pip install -e .
```

## Verifying Installation

To verify that the installation was successful, you can run:

```python
import firscript
print(firscript.__version__)
```

This should print the current version of the FirScript.
