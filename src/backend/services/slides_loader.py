import importlib
import inspect
from typing import Any, Dict


class SlidesLoader:
    """Load and inspect slide functions from template modules"""

    def load_template_functions(self, template_id: str) -> Dict[str, Any]:
        """
        Load slide functions from a template module.

        Args:
            template_id: Template identifier (e.g., 'k2g4h1x9')

        Returns:
            Dictionary of function names to function info
        """
        try:
            # Dynamic import of template module
            module = importlib.import_module(f"src.backend.templates.{template_id}")

            functions = {}

            # Get functions listed in __all__
            for func_name in getattr(module, "__all__", []):
                func = getattr(module, func_name)

                functions[func_name] = {
                    "function": func,
                    "docstring": inspect.getdoc(func) or "",
                    "signature": str(inspect.signature(func)),
                    "args_info": self._parse_function_args(func),
                }

            return functions

        except ImportError as e:
            raise ImportError(f"Cannot load template '{template_id}': {e}")

    def _parse_function_args(self, func) -> Dict[str, str]:
        """Parse function arguments from docstring"""
        doc = inspect.getdoc(func) or ""
        args_info = {}

        lines = doc.split("\n")
        in_args_section = False

        for line in lines:
            line = line.strip()

            if line == "Args:":
                in_args_section = True
                continue
            elif line.startswith("Returns:") or line.startswith("Raises:"):
                in_args_section = False
                continue

            if in_args_section and ":" in line:
                arg_name = line.split(":")[0].strip()
                arg_desc = ":".join(line.split(":")[1:]).strip()
                args_info[arg_name] = arg_desc

        return args_info

    def create_function_catalog(self, template_id: str) -> str:
        """
        Create a formatted catalog of functions for LLM consumption.

        Args:
            template_id: Template identifier

        Returns:
            Formatted string containing function documentation
        """
        functions = self.load_template_functions(template_id)
        catalog_parts = []

        for func_name, info in functions.items():
            # Extract purpose from docstring first line
            doc_lines = info["docstring"].split("\n")
            purpose = doc_lines[0].strip() if doc_lines else "No description"

            func_doc = f"""Function: {func_name}
Purpose: {purpose}
Signature: {info['signature']}

Arguments:"""

            for arg_name, arg_desc in info["args_info"].items():
                func_doc += f"\n  - {arg_name}: {arg_desc}"

            catalog_parts.append(func_doc)

        return "\n\n" + "=" * 50 + "\n\n".join(catalog_parts)

    def get_function_by_name(self, template_id: str, function_name: str):
        """Get specific function by name"""
        functions = self.load_template_functions(template_id)
        return functions.get(function_name, {}).get("function")

    def list_available_functions(self, template_id: str) -> list:
        """List all available function names for a template"""
        functions = self.load_template_functions(template_id)
        return list(functions.keys())
