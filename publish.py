#!/usr/bin/env python
"""
Script to build and publish the package to PyPI.
Usage:
    python publish.py
"""
import os
import subprocess
import sys

def run_command(command):
    """Run a shell command and print its output."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=True)
    return result.returncode

def main():
    """Main function to build and publish the package."""
    # Clean up previous builds
    if os.path.exists("dist"):
        run_command("rm -rf dist")
    if os.path.exists("build"):
        run_command("rm -rf build")
    if os.path.exists("tradepilot_script_engine.egg-info"):
        run_command("rm -rf tradepilot_script_engine.egg-info")

    # Install build dependencies
    run_command("pip install --upgrade pip")
    run_command("pip install --upgrade setuptools wheel twine")

    # Build the package
    run_command("python setup.py sdist bdist_wheel")

    # Check the package
    run_command("twine check dist/*")

    # Upload to PyPI
    if input("Upload to PyPI? (y/n): ").lower() == "y":
        run_command("twine upload dist/*")
        print("Package uploaded to PyPI!")
    else:
        print("Package not uploaded to PyPI.")

if __name__ == "__main__":
    main()
