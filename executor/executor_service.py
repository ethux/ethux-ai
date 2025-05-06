import os
import sys
import subprocess
import traceback
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import autopep8

app = FastAPI()

class CodeExecution(BaseModel):
    code: str
    execution_id: str
    timeout: int = 120

@app.post("/execute")
async def execute_code(execution: CodeExecution):
    """Execute Python code and return the result."""
    try:
        # Format the code using autopep8
        formatted_code = autopep8.fix_code(execution.code)

        # Execute the formatted code with timeout using subprocess.Popen
        process = subprocess.Popen(
            [sys.executable, '-c', formatted_code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            stdout, stderr = process.communicate(timeout=execution.timeout)
            returncode = process.returncode
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            returncode = -1

        # Return the result
        return {
            "execution_id": execution.execution_id,
            "stdout": stdout,
            "stderr": stderr,
            "returncode": returncode,
            "success": returncode == 0
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