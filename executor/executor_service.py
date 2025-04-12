import os
import sys
import subprocess
import tempfile
import traceback
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class CodeExecution(BaseModel):
    code: str
    execution_id: str
    timeout: int = 120

@app.post("/execute")
async def execute_code(execution: CodeExecution):
    """Execute Python code and return the result."""
    try:
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write(execution.code)
            code_file = f.name
        
        # Execute the code with timeout
        result = subprocess.run(
            [sys.executable, code_file],
            capture_output=True,
            text=True,
            timeout=execution.timeout
        )
        
        # Clean up the temporary file
        os.unlink(code_file)
        
        # Return the result
        return {
            "execution_id": execution.execution_id,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "success": result.returncode == 0
        }
    
    except subprocess.TimeoutExpired:
        return {
            "execution_id": execution.execution_id,
            "stdout": "",
            "stderr": f"Execution timed out after {execution.timeout} seconds",
            "returncode": -1,
            "success": False
        }
    
    except Exception as e:
        return {
            "execution_id": execution.execution_id,
            "stdout": "",
            "stderr": f"Error executing code: {str(e)}\n{traceback.format_exc()}",
            "returncode": -1,
            "success": False
        }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "executor_id": os.environ.get("EXECUTOR_ID", "unknown")}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)