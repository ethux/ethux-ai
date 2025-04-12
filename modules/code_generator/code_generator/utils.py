import os
from dotenv import load_dotenv

def load_env_variables(env_path='.env'):
    """
    Load environment variables from a .env file.

    Args:
        env_path (str): The path to the .env file. Defaults to '.env'.
    """
    load_dotenv(env_path)