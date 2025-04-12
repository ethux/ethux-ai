from services.code_agent.code_logger import log_code_execution
import asyncio
import tempfile
import os
import logging
import uuid
import shutil
import random
import httpx

logger = logging.getLogger(__name__)

# Get the number of executors
EXECUTOR_POOL_SIZE = int(os.getenv("EXECUTOR_POOL_SIZE", "3"))

# Get the list of installed modules from environment variable or use defaults
INSTALLED_MODULES = os.getenv("INSTALLED_MODULES", "pandas,numpy,matplotlib,requests").split(",")

async def execute_code(code: str, timeout: int = 120) -> str:
    """
    Execute Python code with a timeout and retry mechanism.

    Args:
        code: The Python code to execute
        timeout: Maximum execution time in seconds

    Returns:
        The execution output (stdout + stderr)
    """
    execution_id = str(uuid.uuid4())
    max_retries = 2
    attempt = 0

    while attempt <= max_retries:
        try:
            # Try to use the executor pool, on failover it will use the local environment
            return await _execute_in_pool(code, execution_id, timeout)
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            attempt += 1
            if attempt > max_retries:
                logger.error("All attempts failed. Falling back to local execution.")
                return await _execute_locally(code, execution_id, timeout)
            else:
                await asyncio.sleep(2)  # Wait before retrying

async def _execute_in_pool(code: str, execution_id: str, timeout: int) -> str:
    """Execute code in one of the executor containers from the pool."""
    try:
        # Select a random executor from the pool
        executor_id = random.randint(1, EXECUTOR_POOL_SIZE)
        executor_url = f"http://executor-{executor_id}:5000/execute"

        logger.info(f"Executing code in executor-{executor_id} with ID {execution_id}")

        # Send the code to the executor
        async with httpx.AsyncClient(timeout=timeout + 5) as client:
            response = await client.post(
                executor_url,
                json={
                    "code": code,
                    "execution_id": execution_id,
                    "timeout": timeout
                }
            )
            result = response.json()

            logging.info(f"Execution result: {result}")
            # Log the code execution result to the slitedb for debugging purposes
            await log_code_execution(code, result["stdout"], response.status_code, result["stderr"] )

            if response.status_code != 200:
                logger.error(f"Error from executor: {response.text}")
                raise Exception(f"Error executing code: {response.text}")

            if result["stderr"]:
                return f"Output:\n{result['stdout']}\n\nWarnings/Errors:\n{result['stderr']}"
            return result["stdout"]

    except httpx.RequestError as e:
        logger.error(f"Error connecting to executor: {str(e)}")
        raise Exception(f"Error connecting to code executor: {str(e)}")

    except Exception as e:
        logger.exception(f"Error executing code in pool: {str(e)}")
        raise Exception(f"Error executing code in pool: {str(e)}")

async def _execute_locally(code: str, execution_id: str, timeout: int) -> str:
    """
    Execute code locally in a subprocess (less secure but works as fallback).
    This is a fallback method when the executor pool is not available.
    """
    temp_dir = tempfile.mkdtemp(prefix=f"code_exec_{execution_id}_")

    try:
        # Write code to a temporary file
        code_file = os.path.join(temp_dir, "code.py")
        with open(code_file, "w") as f:
            f.write(code)

        # Execute the code in a subprocess
        logger.info(f"Executing code locally for execution {execution_id}")

        # Create a virtual environment for isolation
        venv_dir = os.path.join(temp_dir, "venv")

        # Create virtual environment
        proc = await asyncio.create_subprocess_shell(
            f"python -m venv {venv_dir}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()

        if proc.returncode != 0:
            return "Failed to create virtual environment for code execution."

        # Install required packages in the virtual environment
        pip_cmd = f"{venv_dir}/bin/pip" if os.name != 'nt' else f"{venv_dir}\\Scripts\\pip"

        # Install only safe modules
        safe_modules = [m for m in INSTALLED_MODULES if m.strip() in
                        ["pandas", "numpy", "matplotlib", "requests", "scikit-learn"]]

        if safe_modules:
            modules_str = " ".join(safe_modules)
            proc = await asyncio.create_subprocess_shell(
                f"{pip_cmd} install {modules_str}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()

        # Execute the code
        python_cmd = f"{venv_dir}/bin/python" if os.name != 'nt' else f"{venv_dir}\\Scripts\\python"

        proc = await asyncio.create_subprocess_exec(
            python_cmd, code_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            output = stdout.decode()
            error = stderr.decode()

            if error:
                return f"Output:\n{output}\n\nErrors:\n{error}"
            return output

        except asyncio.TimeoutError:
            proc.terminate()
            return f"Execution timed out after {timeout} seconds."

    except Exception as e:
        logger.exception(f"Error executing code locally: {str(e)}")
        return f"Error executing code: {str(e)}"

    finally:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")