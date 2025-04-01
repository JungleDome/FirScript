# TradePilot-ScriptEngine Design Plan

**Date:** 2025-04-02

## 1. Overview

This document outlines the design for the Python-based script engine for TradePilot, inspired by Pine Script v5. The engine will parse, validate, and execute two types of scripts: Strategy and Indicator, supporting custom imports and configurable inputs.

## 2. Core Requirements (from `productContext.md`)

*   **Strategy Scripts:** Define trading logic (`setup()`, `process(bar)`), use `strategy` namespace, restricted `input` usage.
*   **Indicator Scripts:** Reusable logic/TA, single `export`, no `strategy` calls, optional `chart.plot`.
*   **Scripting API Namespaces:** `ta`, `input`, `chart`, `color`, `strategy`.
*   **Script Validation:** Differentiate script types, enforce constraints.
*   **Indicator Import:** Support `const indicator = import 'my_indicator_script'` syntax.
*   **Runtime:** Manage `setup()`/`process()` execution, inject inputs.
*   **Target:** Python 3.10+, modular, testable design.

## 3. Analysis of Existing Code (`script_engine/`)

*   **`parser.py`:** Uses `ast` for parsing, basic type detection (strategy calls vs. `export`), metadata extraction (standard imports, inputs), and validation (required functions, input in `process`, single export). Lacks custom import syntax handling.
*   **`runtime.py`:** Sets up execution environment with placeholder namespaces and an `import` function. Executes strategies (`setup`/`process`) and indicators (`exec`, retrieves `export`). Indicator import relies on a pre-filled dict.
*   **`script.py`:** Defines `ScriptType`, `ScriptMetadata`, and `Script` ABC with placeholders.

## 4. Identified Gaps & Refinements Needed

1.  **Custom Import Syntax:** Parser needs to recognize `const name = import 'path'`.
2.  **Indicator Import Logic:** Runtime needs robust mechanism (load, parse, execute, cache, inject).
3.  **Concrete Script Classes:** Need `StrategyScript` and `IndicatorScript` inheriting from `Script`.
4.  **Namespace Implementation:** Placeholder functions need real logic interacting with backtester state.
5.  **Input Injection:** Clear mechanism for resolving `input.*` calls against user overrides and defaults.
6.  **Parser/Script Interaction:** Refine roles for clarity.

## 5. Proposed Design

### 5.1. Parser Enhancements (`parser.py`)

*   Modify AST traversal (`_extract_metadata` or new step) to detect `Assign` nodes where the `value` is a `Call` to a function named `import` with a string literal argument (the path). Store these as `custom_imports` in `ScriptMetadata`.
*   Update `_create_script` to instantiate `StrategyScript(ast, metadata)` or `IndicatorScript(ast, metadata)`.

### 5.2. Concrete Script Classes (`script.py`)

*   **`StrategyScript(Script)`:**
    *   Initialize by parsing the AST to find `setup` and `process` `FunctionDef` nodes. Store references to these (or compiled code objects).
    *   Implement `setup(**kwargs)` and `process(bar)` methods that execute the stored functions within the appropriate runtime environment.
*   **`IndicatorScript(Script)`:**
    *   Initialize with its AST and metadata.
    *   Implement the `@property def export(self) -> Any:` method. When accessed, it should trigger the execution of the indicator's code (likely using `exec` with its AST and the correct runtime environment) and return the value assigned to the `export` variable within that execution context.

### 5.3. Runtime Enhancements (`runtime.py`)

*   **Input Handling:**
    *   `execute_script(script, **kwargs)`: Store `kwargs` (user input overrides) within the `RuntimeEnvironment` instance, perhaps in a dedicated `self.input_overrides` dictionary.
    *   `_create_input_namespace()`: The returned functions (e.g., `input.int`) should:
        1.  Accept the input `name` and `default` value (and other params like `min`, `max`).
        2.  Check `self.input_overrides` for `name`. If found, return the override value (potentially validating type/constraints).
        3.  If not found, return the `default` value.
*   **`_import_indicator(name: str)` Implementation:**
    *   Argument `name` corresponds to the path from the `import 'path'` statement.
    *   Check `self.imported_indicators` cache using `name` as the key. Return if found.
    *   If not cached:
        *   Resolve the `name` to an actual file path (relative to the importing script or a defined library path).
        *   Read the indicator script source code.
        *   Create a `ScriptParser` instance.
        *   Parse the source: `indicator_script = parser.parse(indicator_source)`.
        *   Validate `indicator_script.metadata.type == ScriptType.INDICATOR`.
        *   Recursively call `self.execute_script(indicator_script, **self.input_overrides)` to get the export value. *Note: Consider if indicators need their own separate input overrides.*
        *   Store the returned value in `self.imported_indicators[name]`.
        *   Return the value.
*   **Namespace Implementation:**
    *   The `_create_X_namespace` methods should accept a reference to the backtesting engine's context/state.
    *   Implement the actual logic (e.g., `ta.ema` accesses historical data from the context, `strategy.long` interacts with the order execution module).

### 5.4. Execution Flow

*   **Strategy:** `execute_script` -> `_create_execution_environment` (inject namespaces, resolved imports via `_import_indicator`) -> Call `StrategyScript.setup()` -> Return `StrategyScript.process` method.
*   **Indicator:** `execute_script` -> `_create_execution_environment` -> Access `IndicatorScript.export` property, which triggers execution -> Return value.

### 5.5. Input Types Clarification

*   **`input.*`:** Static configuration, defined in script, potentially overridden by user at start of backtest, constant during run. Resolved by `input` namespace functions checking overrides then defaults.
*   **`bar`:** Dynamic market data stream, passed sequentially to `StrategyScript.process()` by the backtester. Used by `process` logic and `ta` functions. `ta` functions access historical series data via the context passed into the `RuntimeEnvironment`.

## 6. Visualization

*   **Parsing Flow:**
    ```mermaid
    graph TD
        A[Source Code] --> B{ScriptParser.parse};
        B --> C{ast.parse};
        C --> D{Determine Type};
        D --> E{Validate Constraints};
        E --> F{Extract Metadata (incl. Custom Imports)};
        F --> G{Create Concrete Script Object};
        G -- Strategy --> H[StrategyScript(ast, meta)];
        G -- Indicator --> I[IndicatorScript(ast, meta)];
    ```
*   **Indicator Import Runtime Flow:**
    ```mermaid
    graph TD
        Imp[Importing Script Needs 'ind'] --> Call{runtime._import_indicator('ind_path')};
        Call --> Cache{Check Cache['ind_path']};
        Cache -- Found --> Ret[Return Cached Value];
        Cache -- Not Found --> Load{Load/Parse 'ind_path'};
        Load --> ExecInd{runtime.execute_script(IndicatorScript)};
        ExecInd --> ExportVal[Get Export Value];
        ExportVal --> StoreCache{Store in Cache};
        StoreCache --> Ret;
    ```

## 7. Next Steps

1.  Review this design plan.
2.  Switch to `code` mode for implementation based on this plan.