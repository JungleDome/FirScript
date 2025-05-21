from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Dict
import pandas as pd
from firscript.exceptions.base import ScriptEngineError
from firscript.importer import ScriptImporter
from firscript.namespace_registry import NamespaceRegistry
from firscript.script import Script


@dataclass
class EngineOutput:
    metadatas: Dict[str, Any]
    export: SimpleNamespace | None | Any
    result: Dict[str, Any]


class Engine:
    def __init__(self):
        self.initialized = False
        self.registry = NamespaceRegistry()
        self.importer = ScriptImporter(self.registry)

    def register_default_namespaces(self, inputs_override: dict[str, Any] = None, column_mapping: dict[str, str] = None):
        """Register default namespaces that is available in the scripts.

            Example: `engine.register_default_namespaces()` will register data, strategy, chart & etc namespace

            Then in script it can be used as `chart.plot(data.close)`, which will call the `plot` method inside `chart` namespace
        """
        self.registry.register_default_namespaces(
            inputs_override, column_mapping)

    def register_import_script_namespace(self, name: str = 'import_script'):
        """
            Register special script importer namespace.

            When called, this namespace will be available in the script through the specified `name`. Default: `import_script`

            This namespace will try to resolve and parse the script that is registered through `engine.register_scripts()`

            Example: In the script it calls `import_script('some library script.py')`. This will resolve the script '`some library script.py`' from the key or name of the script in `register_scripts()`.

            Throws `ScriptNotFoundError` during runtime when trying to resolve script that is not registered.
        """
        self.registry.register(name, self.importer.import_script)

    def register_scripts(self, main_script: str = '', import_scripts: dict[str, str] = {}, scripts: list[Script] = None):
        if scripts:
            for script in scripts:
                self.importer.add_script(script=script)
        elif main_script != '':
            self.importer.add_script('main', main_script, is_main=True)
            for name, script_str in import_scripts.items():
                self.importer.add_script(name, script_str)
        else:
            raise ScriptEngineError("Please define a script to execute.")

    def initialize(self, inputs_override: dict[str, Any] = None, column_mapping: dict[str, str] = None, main_script: str = '', import_scripts: dict[str, str] = {}, scripts: list[Script] = None):
        """
            Default method to initialize the engine. This will register the required namespace, script importer and runtime context.

            If you are registering your own custom namespace kindly refer to `initialize_context()`.
        """
        self.register_default_namespaces(inputs_override, column_mapping)
        self.register_import_script_namespace()
        self.register_scripts(main_script, import_scripts, scripts)
        self.initialize_context()

    def initialize_context(self):
        """
            Initialize the engine runtime context.

            This method is the manual method to initialize the engine. Use it when you want to customize the namespaces.

            Example:
            ```
            engine = Engine()
            engine.register_default_namespaces()
            engine.registry.register('myOwnNamespace', SomeNamespaceClassOrInstance)
            engine.register_scripts(myScript)
            engine.initialize_context() //<-- call this method at last before running the engine
            engine.run(data)
            ```
        """
        self.ctx = self.importer.build_main_script()
        self.ctx.run_setup()
        self.initialized = True

    def generate_output(self):
        """
            Generate outputs after the script has finish running.
        """
        return EngineOutput(
            metadatas=self.ctx.generate_metadatas(),
            export=self.ctx.get_export(),
            result=self.ctx.generate_outputs()
        )

    def run_step(self):
        """
            Run the script tick by tick.

            This method provide a way to manually update the engine or namespace data before running the script in the next tick.
        """
        if (self.initialized == False):
            raise ScriptEngineError(
                "Please call initialize() or initialize_context() to initialize the engine before running the script.")

        self.ctx.run_process()

    def run(self, data: pd.DataFrame):
        """
            Run the script using the data provided. This will update the data in `data` namespace incrementally until it is finish.

            If you prefer to update the data manually use `run_step()`
        """
        for i in range(len(data)):
            current_bar = data.iloc[i]  # Get current row as Series
            # Get all bars up to and including current row
            historical_bars = data.iloc[:i+1]

            if (self.ctx.namespaces.get('data') != None):
                self.ctx.namespaces.get('data').set_current_bar(current_bar)
                self.ctx.namespaces.get('data').set_all_bar(historical_bars)

            self.ctx.run_process()

        output = self.generate_output()
        return output.export if output.export else output.result, output.metadatas
