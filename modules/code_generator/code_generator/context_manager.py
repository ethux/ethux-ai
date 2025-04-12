import os

class ContextManager:
    """
    A class to manage the context for code generation.

    Attributes:
        context (dict): A dictionary to store the context of different modules.
    """

    def __init__(self):
        """
        Initialize the ContextManager.
        """
        self.context = {}

    def add_context(self, module_name, context):
        """
        Add context for a module.

        Args:
            module_name (str): The name of the module.
            context (str): The context for the module.
        """
        self.context[module_name] = context

    def get_context(self, module_name):
        """
        Get the context for a module.

        Args:
            module_name (str): The name of the module.

        Returns:
            str: The context for the module.
        """
        return self.context.get(module_name, "")

    def get_all_contexts(self):
        """
        Get the context for all modules.

        Returns:
            str: The context for all modules.
        """
        return "\n".join(self.context.values())