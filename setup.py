import os
from setuptools import setup, find_packages

# Read the contents of README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
with open("requirements.txt", encoding="utf-8") as f:
    requirements = [line.strip() for line in f.readlines() if line.strip()]

# Import version
about = {}
with open(os.path.join("script_engine", "version.py"), encoding="utf-8") as f:
    exec(f.read(), about)

setup(
    name="firscript",
    version=about["__version__"],
    description="A Python-based backtesting engine with a custom scripting system inspired by TradingView's Pine Script",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="JungleDome",
    author_email="",  # Replace with your email
    url="https://github.com/JungleDome/FirScript",  # Replace with your repo URL
    packages=find_packages(exclude=["tests*", "examples*"]),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="trading, backtesting, finance, technical analysis, pinescript",
    python_requires=">=3.8",
    project_urls={
        "Documentation": "https://github.com/JungleDome/FirScript",  # Replace with docs URL
        "Source": "https://github.com/JungleDome/FirScript",  # Replace with your repo URL
        "Tracker": "https://github.com/JungleDome/FirScript/issues",  # Replace with your issues URL
    },
)
