# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md (if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
2025-04-02 04:45:20 - Log of updates made will be appended as footnotes to the end of this file.

*

## Project Goal

*   To implement a Python-based backtesting engine with a custom scripting system inspired by TradingView's Pine Script v5, allowing users to define, validate, and execute custom trading strategies and indicators.

## Key Features

*   **Strategy Scripts:** Define trading logic (`setup()`, `process(bar)`), use `strategy` namespace, restricted `input` usage.
*   **Indicator Scripts:** Reusable logic/TA, single `export`, no `strategy` calls, optional `chart.plot`.
*   **Scripting API Namespaces:** `ta`, `input`, `chart`, `color`, `strategy`.
*   **Script Validation:** Differentiate script types, enforce constraints (input usage, exports, strategy calls).
*   **Indicator Import:** Support `const indicator = import 'my_indicator_script'` syntax.
*   **Runtime:** Manage `setup()`/`process()` execution, inject inputs.
*   **Target:** Python 3.10+, modular, testable design.

## Overall Architecture

*
[2025-04-02 04:49:40] - Updated Project Goal and Key Features based on initial project description.