## Design Plan: Backtesting Script Engine (Revision 4)

This plan outlines the architecture and key components for the Python-based backtesting script engine, inspired by Pine Script v5, incorporating the final adjustment.

**1. Core Components:**

*   **`ScriptEngine` (`script_engine/engine.py` - New File):** A high-level facade class providing a simplified interface for common use cases. It initializes and coordinates `ScriptParser` and `RuntimeEnvironment` with default settings.
*   **`ScriptParser` (`script_engine/parser.py`):** Responsible for parsing script source code (`ast`), validation, metadata extraction, type identification, and creating `Script` objects. (Exported for direct use).
*   **`RuntimeEnvironment` (`script_engine/runtime.py`):** Manages the execution context, including loading/importing scripts, injecting namespaces, handling inputs, executing script logic, and managing dynamic namespace registration. (Exported for direct use).
*   **`Script` Classes (`script_engine/script.py`):** `Script` (ABC), `StrategyScript`, `IndicatorScript`.
*   **`ScriptMetadata` (`script_engine/script.py`):** Dataclass for script metadata.
*   **Custom Exceptions (`script_engine/exceptions.py` - New File):** Hierarchy for clear error reporting (`ScriptEngineError`, `ScriptParsingError`, `ScriptRuntimeError`, etc.).

**2. Parser Enhancements (`ScriptParser`):**

*   Detailed Error Reporting (file/line/col).
*   Improved `import` Handling (syntax detection, metadata storage).
*   Circular Dependency Check (raise `CircularImportError`).
*   Robust `input` Extraction (global scope & `setup` function).
*   Validation (no `input.*` in `process`).

**3. Runtime Enhancements (`RuntimeEnvironment`):**

*   **Dynamic Namespace Registration:**
    *   Add method: `register_namespace(self, name: str, namespace_instance: Any)`. This is the **only** way to add or override namespaces. It updates `self.registered_namespaces`. If a namespace with the same `name` already exists (either default or previously registered), it will be overridden.
    *   `_create_execution_environment` injects default namespaces *and* namespaces from `self.registered_namespaces` into the script's `env`. Registered namespaces take precedence over defaults with the same name.
*   **Indicator Import Implementation (`_import_indicator`):** (Handles loading, parsing, execution, error handling; no caching).
*   **Input Override Handling:** (Via `inputs_override: Dict[str, Any]` passed to `setup`).
*   **Accessing Inputs in `process`:** (`setup` manages state).
*   **Bar Data:** The engine accepts a **Pandas DataFrame** containing historical bar data. The `RuntimeEnvironment` iterates through this DataFrame. The `process` function receives the current bar's data (e.g., as a `pd.Series` or dict). Namespaces (like `ta`) need access to the historical portion of the DataFrame and column mapping.
*   **Namespace Injection:** Injects defaults + registered namespaces.

**4. Namespace Design:**

*   **Interfaces:** Define abstract base classes or protocols.
*   **Extensibility:**
    *   **Solely via `RuntimeEnvironment.register_namespace()`**. Constructor injection for namespaces is *not* supported.
*   **Default Implementations:** (`ta`, `input`, `chart`, `color` defaults; `strategy` placeholder).
*   **Default Engine (`ScriptEngine`):** Pre-configured with default namespaces. Users must call `engine.register_namespace()` *after* initialization to customize.

**5. Error Handling (`script_engine/exceptions.py`):**

*   Base `ScriptEngineError`, specific subclasses with detailed info.

**6. High-Level Usage (`ScriptEngine`):**

*   **Initialization:** `engine = ScriptEngine()` (uses defaults).
*   **Customization & Execution (Example):**
    ```python
    engine = ScriptEngine() # Initialize with defaults

    # MANDATORY: Register custom/override namespaces AFTER initialization
    engine.register_namespace("ta", MyCustomTALib()) # Override default 'ta'
    engine.register_namespace("my_utils", MyUtilityNamespace()) # Add new namespace

    script_source = "..."
    bars_data = pd.DataFrame(...) # DataFrame with timestamp, open, high, low, close, volume columns
    # Optional column name mapping
    column_mapping = {"open": "O", "high": "H", "low": "L", "close": "C", "volume": "V", "timestamp": "T"}
    input_overrides = {"ema_length": 20, "rsi_period": 14}

    results = engine.run_strategy(
        script_source=script_source,
        bars_df=bars_data,
        inputs_override=input_overrides,
        column_mapping=column_mapping # Optional
    )
    ```

**7. Data Flow Diagram (Mermaid - Updated Extensibility):**

```mermaid
graph TD
    subgraph User Interaction
        U_Source[Script Source Code]
        U_Bars[Bar Data (pd.DataFrame)]
        U_ColMap[Optional Column Mapping (Dict)]
        U_Overrides[Input Overrides (Dict)]
        U_RegNS[Dynamic Namespace Registration Calls]
    end

    SE[ScriptEngine]

    subgraph Core Components
        P[ScriptParser]
        R[RuntimeEnvironment]
        SC[Script Classes (Strategy/Indicator)]
        SM[ScriptMetadata]
        EX[Custom Exceptions]
        NS_Default[Default Namespaces (ta, input, ...)]
        NS_Custom[Registered Namespaces]
    end

    U_Source --> SE;
    U_Bars --> SE;
    U_ColMap --> SE;
    U_Overrides --> SE;

    SE -- Initializes --> P;
    SE -- Initializes --> R; # R starts with NS_Default
    U_RegNS -- Calls register_namespace --> SE -- Updates --> R; # R updates NS_Custom

    P -- Parses --> U_Source;
    P -- Creates --> SC;
    P -- Extracts --> SM;
    P -- Raises --> EX;

    R -- Executes --> SC;
    R -- Uses --> SM;
    R -- Uses --> NS_Default;
    R -- Uses --> NS_Custom; # Registered overrides defaults
    R -- Manages Imports --> P; # For indicators
    R -- Receives Bar DataFrame, Col Map & Input Dict --> SE;
    R -- Raises --> EX;

    SE -- Returns --> Results[Backtest Results / State];

    style EX fill:#f9f,stroke:#333,stroke-width:2px;
```

**8. Extensibility & Export:**

*   Core components (`ScriptParser`, `RuntimeEnvironment`, `Script` classes, `Exceptions`) will be importable for advanced users to build custom workflows.

**9. Future Enhancements (To Note):**

*   Indicator result caching.
*   Full `strategy` namespace implementation.
*   Plotting integration.