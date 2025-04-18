.. FirScript documentation master file, created by
   sphinx-quickstart on Sat Apr 19 01:01:29 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

FirScript
========================

A modular scripting engine designed for algo trading. Write PineScript-like python code to define strategies, indicators, and libraries — then plug them into a clean, scriptable engine that does the orchestration for you.

.. image:: https://img.shields.io/pypi/v/firscript
   :alt: PyPI

.. image:: https://img.shields.io/github/license/JungleDome/FirScript
   :alt: License

Features
--------

* ✅ Write strategy logic as regular Python scripts
* ⚙️ Parse, register, and run strategies dynamically
* 🧹 Bring your own data, namespaces, and post-processors
* 🛠️ Easily embed into larger trading and backtesting systems or apps
* 🧪 Perfect for research, prototyping, and integration into custom trading platforms

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting_started/installation
   getting_started/quickstart
   getting_started/examples

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/scripting_conventions
   user_guide/namespaces
   user_guide/strategies
   user_guide/indicators
   user_guide/libraries

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/engine
   api/script
   api/parser
   api/execution_context
   api/importer
   api/namespace_registry
   api/namespaces
   api/exceptions

