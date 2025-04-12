import ast

def extract_docstrings(code):
    """
    Extract docstrings from the given code.

    Args:
        code (str): The code to extract docstrings from.

    Returns:
        dict: A dictionary containing the extracted docstrings.
    """
    tree = ast.parse(code)
    docstrings = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
            docstring = ast.get_docstring(node)
            if docstring:
                docstrings[node.name] = docstring

    return docstrings