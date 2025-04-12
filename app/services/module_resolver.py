import os
import logging
from typing import List, Dict, Any
import json
import aiofiles

logger = logging.getLogger(__name__)

# Load environment variables
MODULES_DB_PATH = os.getenv("MODULES_DB_PATH", "./docs/modules.json")

# Ensure data directory exists
os.makedirs(os.path.dirname(MODULES_DB_PATH), exist_ok=True)

# Create a default modules database if it doesn't exist
DEFAULT_MODULES = [
    {
        "name": "pandas",
        "description": "Data analysis and manipulation library",
        "functions": [
            {
                "name": "read_csv",
                "description": "Read a comma-separated values (csv) file into DataFrame",
                "usage": "df = pd.read_csv('filename.csv')"
            },
            {
                "name": "DataFrame",
                "description": "Two-dimensional, size-mutable, potentially heterogeneous tabular data",
                "usage": "df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})"
            }
        ]
    }
]

async def _initialize_modules_db():
    """Initialize the modules database with default values if it doesn't exist."""
    if not os.path.exists(MODULES_DB_PATH):
        async with aiofiles.open(MODULES_DB_PATH, 'w') as f:
            await f.write(json.dumps(DEFAULT_MODULES, indent=2))
        logger.info(f"Created default modules database at {MODULES_DB_PATH}")

async def find_relevant_modules(query: str) -> List[Dict[str, Any]]:
    """
    Find modules relevant to the user's query.

    Args:
        query: The user's query

    Returns:
        A list of relevant modules with their documentation
    """
    await _initialize_modules_db()

    # Load the modules database
    async with aiofiles.open(MODULES_DB_PATH, 'r') as f:
        content = await f.read()
        modules = json.loads(content)

    # Should be improved from keyword search to search using embeddings
    relevant_modules = []
    query_lower = query.lower()

    for module in modules:
        # Check if the module name or description matches the query
        if (module["name"].lower() in query_lower or
            module["description"].lower() in query_lower):
            relevant_modules.append(module)
            continue

        # Check if any function in the module matches the query
        for function in module["functions"]:
            if (function["name"].lower() in query_lower or
                function["description"].lower() in query_lower):
                relevant_modules.append(module)
                break

    # If no modules were found, return the default modules
    if not relevant_modules:
        logger.info(f"No specific modules found for query: {query}. Using all modules.")
        return modules

    logger.info(f"Found {len(relevant_modules)} relevant modules for query: {query}")
    return relevant_modules

async def add_module(module_data: Dict[str, Any]) -> bool:
    """
    Add a new module to the database.

    Args:
        module_data: The module data to add

    Returns:
        True if successful, False otherwise
    """
    await _initialize_modules_db()

    try:
        # Load the existing modules
        async with aiofiles.open(MODULES_DB_PATH, 'r') as f:
            content = await f.read()
            modules = json.loads(content)

        # Check if the module already exists
        for i, module in enumerate(modules):
            if module["name"] == module_data["name"]:
                # Update the existing module
                modules[i] = module_data
                break
        else:
            modules.append(module_data)

        # Save updated modules
        async with aiofiles.open(MODULES_DB_PATH, 'w') as f:
            await f.write(json.dumps(modules, indent=2))

        return True

    except Exception as e:
        logger.error(f"Error adding module: {str(e)}")
        return False