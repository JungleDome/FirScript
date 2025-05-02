# Decision Log

This file records architectural and implementation decisions using a list format.
2025-04-02 04:46:18 - Log of updates made.

*

[2025-04-09 09:57:10]
## Decision
* Enforce best practice: all mutable state variables must be initialized inside the `setup()` function.
* Discourage defining mutable state at the global script scope.
* Add runtime warnings if mutable state is detected outside `setup()`.

## Rationale
* Improves clarity and maintainability of user scripts.
* Avoids confusion about variable lifetimes and persistence.
* Less intrusive than strict parser validation; allows flexibility.

## Implementation Details
* Updated `docs/scripting_conventions.md` with explicit guidelines and examples.
* Modified example script `examples/simple_strategy.py` to follow this pattern.
* Plan to add runtime warnings in the script engine when global mutable state is detected.
* Did not implement strict parser enforcement to maintain flexibility.

## Decision

*

## Rationale

*

## Implementation Details

*   [2025-04-08 03:09:36]
    ## Decision
    * Finalized script engine core implementation
    * Established state management architecture
    * Standardized script conventions
    
    ## Rationale
    * Unified execution model works for both strategies/indicators
    * Shared context enables state persistence
    * Clear conventions improve maintainability
    
    ## Implementation
    * Uses Python's exec() with controlled environment
    * Context merging handles state persistence
    * Validation ensures script safety
    ---
    [2025-04-02 05:05:20] - Script Engine Parser & Runtime Design

    ## Decision
    *   Refine the existing Python AST-based parser and runtime for the custom scripting language.
    *   Implement support for custom indicator import syntax (`const x = import 'path'`).
    *   Introduce concrete `StrategyScript` and `IndicatorScript` classes.
    *   Define clear mechanisms for handling static `input.*` configuration (with user overrides) and dynamic `bar` data.
    *   Implement robust indicator import logic (parsing, execution, caching).
    *   Flesh out API namespace functions (`ta`, `input`, `strategy`, etc.) to interact with the backtesting engine state.

    ## Rationale
    *   Leverages existing code structure while addressing key missing features identified during analysis.
    *   Provides clear separation of concerns between parsing, script representation, and runtime execution.
    *   Ensures correct handling of different input types (static config vs. dynamic market data).
    *   Enables required script reusability via indicator imports.

    ## Implementation Details
    *   **Parser:** Modify AST traversal to detect `import` syntax, store in metadata. Instantiate concrete script classes.
    *   **Script Classes:** `StrategyScript` stores `setup`/`process` functions; `IndicatorScript` manages `export` value computation.
    *   **Runtime:** Enhance `_import_indicator` for file loading, parsing, execution, caching. Handle `input.*` overrides via `kwargs`. Pass backtesting context to namespaces (especially `ta`).
    *   **Namespaces:** Implement actual logic within placeholder functions, accessing backtester state as needed.