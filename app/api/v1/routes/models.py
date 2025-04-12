from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

router = APIRouter()

# Environment variables for API keys
LLM_API_KEY = os.getenv("MISTRAL_API_KEY", "")
CODESTRAL_API_KEY = os.getenv("CODESTRAL_API_KEY", "")

class ModelData(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str
    permission: List[Dict[str, Any]] = []
    root: Optional[str] = None
    parent: Optional[str] = None

class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[ModelData]

# Define available models
AVAILABLE_MODELS = [
    {
        "id": "ethux-ai",
        "object": "model",
        "created": int(datetime(2023, 1, 1).timestamp()),
        "owned_by": "ETHUX",
        "permission": [],
    },
    {
        "id": "ethux-ai-dev",
        "object": "model",
        "created": int(datetime(2023, 1, 1).timestamp()),
        "owned_by": "ETHUX",
        "permission": [],
    },
]

@router.get("/models", response_model=ModelsResponse)
async def list_models():
    """
    List available models compatible with the OpenAI format.
    """
    if not LLM_API_KEY:
        # Still return models but log a warning
        print("WARNING: LLM_API_KEY not set")
    
    return {
        "object": "list",
        "data": AVAILABLE_MODELS
    }