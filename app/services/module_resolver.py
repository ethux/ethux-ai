import os
import logging
from typing import List, Dict, Any
import json
import aiofiles

logger = logging.getLogger(__name__)

# Load environment variables
MODULES_DB_PATH = os.getenv("MODULES_DB_PATH", "/docs/modules.json")

# Ensure data directory exists
os.makedirs(os.path.dirname(MODULES_DB_PATH), exist_ok=True)

async def find_relevant_modules(query: str) -> List[Dict[str, Any]]:
    """
    Find modules relevant to the user's query.

    Args:
        query: The user's query

    Returns:
        A list of all modules with their documentation
    """
    # Load the modules database
    async with aiofiles.open(MODULES_DB_PATH, 'r') as f:
        content = await f.read()
        modules = json.loads(content)

    logger.info(f"Returning all modules for query: {query}")
    return modules