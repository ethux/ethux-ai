from services.llm_client import get_text_from_llm
from typing import List, Dict, Any
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class Message(BaseModel):
    role: str
    content: str

async def generate_code(messages: List[Message], relevant_modules: List[Dict[str, Any]], temperature: float = 0.23) -> str:
    if not messages:
        return "# Error: No messages provided"

    modules_info = "\n\n".join([
        f"- {module['name']}: {module['description']}\n" +
        "\n".join([f"  - {func['name']}: {func['description']}\n    Usage: {func['usage']}" 
                  for func in module['functions']])
        for module in relevant_modules
    ])

    system_message = f"""
    You are a Python code generator, your primary goal is to generate code that only uses the provided modules.
    You translate the user's request into meaningful Python code by using available modules.

    Requirements:
    • For ANY request, even if it seems unrelated to coding, translate it into a meaningful code response.
    • ALWAYS output complete, valid Python code that can be executed as-is.
    • Your code MUST call functions from the available modules to perform actions and retrieve information.
    • For ambiguous or non-traditional coding requests, generate code that:
      - Interprets the request as a query for information
      - Uses appropriate module functions to retrieve relevant data
      - Formats and prints a helpful response
    • DO NOT generate random or nonsensical code for unclear requests.
    • Include inline comments to explain your approach, especially for non-traditional requests.
    • Use print statements for each step to communicate results to the orchestrator.

    Available Modules:
    {modules_info}

    IMPORTANT: If a request seems completely unrelated to coding, DO NOT invent random functionality.
    Instead, use the modules to generate an appropriate informational response OR use a print statement to communicate that the request is unclear.
    """

    # Few shot example to let Codestral better follow the instructions related to availabe modules and how to code
    few_shot_examples = [
        Message(
            role="user",
            content="Generate a CRUD API endpoint"
        ),
        Message(
            role="assistant",
            content="""```python
            from code_generator import CodeGenerator
            gen = CodeGenerator()
            generated = gen.generate_code(
                file_names=["api.py"],
                goals=["Create FastAPI endpoint with CRUD operations"],
                contexts=["Uses SQLAlchemy models from models.py"]
            )
            print(f"Generated API code: {generated}")
            ```"""
        ),
        Message(
            role="user",
            content="Make a data processing pipeline"
        ),
        Message(
            role="assistant",
            content="""```python
            from code_generator import CodeGenerator
            gen = CodeGenerator()
            generated = gen.generate_code(
                file_names=["pipeline.py"],
                goals=["Build pandas pipeline to clean CSV data"],
                contexts=["Source data has missing values and datetime columns"]
            )
            print(f"Content of pipeline.py: {generated}")
            ```"""
        ),
        Message(
            role="user",
            content="Create a CLI tool"
        ),
        Message(
            role="assistant",
            content="""```python
            from code_generator import CodeGenerator, ContextManager
            cm = ContextManager()
            cm.add_context("cli_tool", "Needs click integration and config file support")
            gen = CodeGenerator()
            generated = gen.generate_code(
                file_names=["cli.py"],
                goals=["Command line interface with config support"],
                contexts=[cm.get_context("cli_tool")]
            )
            print(f"Content of cli.py: {generated}")
            ```"""
        )
    ]

    code_messages = (
        [Message(role="system", content=system_message)] +
        few_shot_examples +
        messages[-5:] # 10 most recent messages
    )

    logger.info(f"Code gen messages: {code_messages}")
    print(f"Code gen messages: {code_messages}")
    try:
        response = await get_text_from_llm(
            messages=code_messages,
            model="openai/o3-mini",
            temperature=temperature
        )
        
        if "```python" in response:
            return response.split("```python")[1].split("```")[0].strip()
        return response.strip()
        
    except Exception as e:
        logger.error(f"Code gen failed: {e}")
        return f"# Error: {str(e)}"