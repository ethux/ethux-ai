from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.routes.models import router as models_router
from api.v1.routes.chat_completions import router as chat_completions_router
from api.v1.routes.get_execution_results import router as get_execution_results_router

import uvicorn
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Code Execution Backend")

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For prod, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(models_router, prefix="/v1", tags=["Models"])
app.include_router(chat_completions_router, prefix="/v1", tags=["Chat"])
app.include_router(get_execution_results_router, prefix="/v1", tags=["Execution Results"])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8008))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)