from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import logging
import time
import asyncio
from typing import List, Dict, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime
from services.code_agent.code_executor import execute_code
from services.module_resolver import find_relevant_modules
from services.llm_client import stream_text_from_llm, get_text_from_llm
from services.code_agent.code_generator import generate_code

router = APIRouter()
logger = logging.getLogger(__name__)

# Models
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.5
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    user: Optional[str] = None

class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: Optional[str] = None

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Dict[str, int]

class DeltaMessage(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None

class StreamChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[str] = None

class ChatCompletionChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[StreamChoice]

# The main chat completions endpoint
@router.post("/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    """
    Create a chat completion with code execution capabilities.
    """
    #start_time = time.time()
    request_id = f"chatcmpl-{uuid.uuid4()}"

    if request.stream:
        return StreamingResponse(
            stream_chat_completion(request, request_id, is_code_request=True),
            media_type="text/event-stream"
        )
    # For non-streaming requests
    try:
        # Find relevant modules for the task
        user_query = request.messages[-1].content
        relevant_modules = await find_relevant_modules(user_query)

        # Generate code with retry mechanism
        max_retries = 2
        attempt = 0
        code = None
        error_message = None

        while attempt <= max_retries:
            try:
                code = await generate_code(
                    messages=request.messages,
                    relevant_modules=relevant_modules,
                    temperature=request.temperature
                )
                break
            except Exception as e:
                error_message = str(e)
                logger.warning(f"Code generation attempt {attempt + 1} failed: {error_message}")
                attempt += 1
                if attempt > max_retries:
                    raise Exception("Code generation failed after multiple attempts.")
                else:
                    await asyncio.sleep(1)  # Wait for a second before retrying

        logger.info(code)
        # Execute the generated code
        execution_result = await execute_code(code)
        # Modify the system message to include instructions about the execution result
        system_message = "You are a helpful AI Agent Orchestrator."
        system_message += f"The user asked: '{user_query}'. Answer this question within the context of the chat."
        system_message += f"The Python AI Agent wrote and executed Python code that produced this result: '{execution_result}'. "
        system_message += "Use the execution result to answers the users question within the context."
        if error_message:
            system_message += f" The previous attempt to generate code failed with the following error: '{error_message}'. Please correct the code and try again."

        # Create new messages with the modified system message
        new_messages = [
            Message(role="system", content=system_message)
        ]
        # Add all user messages
        for msg in request.messages:
            if msg.role == "user":
                new_messages.append(msg)
        # Get final response from the LLM API
        response_content = await get_text_from_llm(
            messages=new_messages,
            model="mistral-large-latest",
            temperature=request.temperature
        )
        # Format the response
        return ChatCompletionResponse(
            id=request_id,
            created=int(time.time()),
            model=request.model,
            choices=[
                Choice(
                    index=0,
                    message=Message(role="assistant", content=response_content),
                    finish_reason="stop"
                )
            ],
            usage={
                "prompt_tokens": 0,  # Need to implement token usage
                "completion_tokens": 0,
                "total_tokens": 0
            }
        )
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def stream_chat_completion(request: ChatCompletionRequest, request_id: str, is_code_request: bool):
    """
    Stream the chat completion response.
    """
    start_time = time.time()  # Log the start time
    created = int(time.time())
    try:
        # Find relevant modules
        user_query = request.messages[-1].content
        relevant_modules = await find_relevant_modules(user_query)

        # Generate code with retry mechanism
        max_retries = 2
        attempt = 0
        code = None
        error_message = None

        while attempt <= max_retries:
            try:
                code = await generate_code(
                    messages=request.messages,
                    relevant_modules=relevant_modules,
                    temperature=0.3
                )
                break
            except Exception as e:
                error_message = str(e)
                logger.warning(f"Code generation attempt {attempt + 1} failed: {error_message}")
                attempt += 1
                if attempt > max_retries:
                    raise Exception("Code generation failed after multiple attempts.")
                else:
                    await asyncio.sleep(1)  # Wait for a second before retrying

        # Log the generated code for debugging
        logger.info(f"Generated code: {code[:100]}...")

        # Execute code silently
        execution_result = await execute_code(code)

        current_time = datetime.now().strftime("%Y-%m-%d")

        # This is probably a bad way to do this, it needs to be more straight forward for the LLM what it retrieves.
        system_message = "You are a helpful AI Agent, you can provide real-time information and execute tools."
        system_message += f"The current date and time is {current_time}. "
        system_message += f"You have retrieved the following information:'{execution_result}'. "
        system_message += "Use the retrieved information to answer the user's question."
        system_message += "Always use nice markdown formatting for a clear and concrete answer."
        if error_message:
            system_message += f" The previous attempt to generate code failed with the following error: '{error_message}'. Please correct the code and try again."

        new_messages = [
            Message(role="system", content=system_message)
        ]

        # Add all user messages
        for msg in request.messages:
                new_messages.append(msg)

        # Stream the final explanation from the LLM API
        logging.info(f"Streaming final explanation from LLM API {new_messages}")
        async for chunk_text in stream_text_from_llm(
            messages=new_messages,
            model="mistral-large-latest",
            temperature=0.4
        ):
            chunk = ChatCompletionChunk(
                id=request_id,
                created=created,
                model=request.model,
                choices=[
                    StreamChoice(
                        index=0,
                        delta=DeltaMessage(content=chunk_text),
                        finish_reason=None
                    )
                ]
            )
            yield f"data: {json.dumps(chunk.model_dump())}\n\n"
    except Exception as e:
        logger.error(f"Error in streaming: {str(e)}")
        error_message = f"Error: {str(e)}"
        chunk = ChatCompletionChunk(
            id=request_id,
            created=created,
            model=request.model,
            choices=[
                StreamChoice(
                    index=0,
                    delta=DeltaMessage(content=error_message),
                    finish_reason='error'
                )
            ]
        )
        yield f"data: {json.dumps(chunk.model_dump())}\n\n"
        yield "data: [DONE]\n\n"
    finally:
        end_time = time.time()  # Log the end time
        total_time = end_time - start_time
        logger.info(f"Total execution time for request {request_id}: {total_time:.2f} seconds")