# Design Plan: Script Engine Redesign (Exec + Shared Context - v4)

**Goal:** Unify script execution using `exec`, manage state via a shared context merged into the execution scope, and have the `RuntimeEnvironment` call the script-defined `setup` and `process` functions transparently within that persistent context.

**Core Mechanism:**

1.  **Persistent State:** `RuntimeEnvironment` holds state in `self.shared_context`.
2.  **Execution:**
    *   Temporary `env` created (copy of `shared_context` + namespaces + inputs + `current_bar`).
    *   `exec(script.source, env)` defines functions and initial state in `env`.
3.  **Context Update:** `RuntimeEnvironment` copies relevant items (state vars, `setup`/`process` functions) from `env` back to `self.shared_context`. Injected items are excluded.
4.  **Transparent Function Calls:** `RuntimeEnvironment` calls `self.shared_context['setup']()` (first run) and `self.shared_context['process'](current_bar)` (every run). These functions execute using `self.shared_context` as their effective global scope.

**Detailed Plan:**

**Phase 1: Refactor `RuntimeEnvironment` (`script_engine/runtime.py`)**

1.  **Add Shared Context &amp; Setup Tracking:**
    *   `self.shared_context: Dict[str, Any] = {}`
    *   `self.setup_executed: Set[str] = set()` (Tracks script IDs).
2.  **Modify `_create_execution_environment`:** Merges `shared_context`, namespaces, `import`.
    ```python
    def _create_execution_environment(self) -> Dict[str, Any]:
        """Prepare the base execution environment with shared context and namespaces."""
        env = self.shared_context.copy() # Start with current shared state
        env.update(self.registered_namespaces)
        env["import"] = self._import_indicator
        return env
    ```
3.  **Unify `execute_script`:**
    *   Determine `script_id` and `is_first_run`.
    *   Get base `env` from `_create_execution_environment()`.
    *   Prepare script inputs and `current_bar`.
    *   Inject per-execution data into `env`: `current_bar`, inputs.
    *   Execute the script source: `exec(script.source, env)`.
    *   Update `self.shared_context`: Extract relevant variables (state, functions) from `env` back into `self.shared_context`, excluding injected items.
        ```python
        # After exec(script.source, env)
        keys_to_exclude = set(self.registered_namespaces.keys()) | {'import', 'current_bar'} | set(script_inputs.keys())
        for key, value in env.items():
            if key not in keys_to_exclude:
                self.shared_context[key] = value # Update or add to shared context
        ```
    *   Call `setup` (if first run, strategy, and exists in `self.shared_context`): `self.shared_context['setup']()`. Mark setup executed.
    *   Call `process` (if strategy and exists in `self.shared_context`): `self.shared_context['process'](current_bar_transformed)`.
    *   Return Indicator Result: `result = self.shared_context.get('export', None)`.

**Phase 2: Simplify `Script` Classes (`script_engine/script.py`)**

*   Remove `StrategyScript`, `IndicatorScript`.
*   Make `Script` a concrete class holding `source` and `metadata`.
*   Keep `ScriptMetadata` dataclass.

**Phase 3: Adapt `ScriptParser` (`script_engine/parser.py`)**

*   Validation checks for *definitions* of `setup`/`process`/`export` using AST.
*   `_create_script` instantiates the simplified `Script` class.

**Phase 4: Define and Document Script Conventions**

*   **State:** Accessed directly (`my_var = 1`). Variables persist. Be mindful of name clashes. Use `global` keyword inside functions to modify state variables defined at the top level.
*   **Strategy:** *Must* define top-level functions `setup()` and `process(bar)`. Do *not* call them explicitly.
*   **Indicator:** *Must* assign output to a top-level variable `export`.
*   **Inputs:** Accessed directly (`length = input_length`).
*   **Bar Data:** Passed as an argument to `process(bar)`. Can also be accessed via `current_bar` if needed in the main script body or `setup`.
*   **Namespaces:** Accessed directly (`ta.sma(...)`).

**Phase 5: Update Engine and Tests**

*   Update `engine.py` loop to manage `RuntimeEnvironment` and call `execute_script`.
*   Update all relevant tests (`test_script.py`, `test_runtime.py`, `test_parser.py`).