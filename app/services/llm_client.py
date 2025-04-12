from typing import List, Dict, Any, Optional, AsyncIterable
from pydantic import BaseModel
import httpx
import logging
import json
import os

logger = logging.getLogger(__name__)

LLM_API_KEY = os.getenv("MISTRAL_API_KEY", "")
LLM_API_URL = "https://api.mistral.ai/v1"

class Message(BaseModel):
    role: str
    content: str

async def _make_request(payload: Dict[str, Any], headers: Dict[str, str], url: str) -> httpx.Response:
    """
    Make an asynchronous HTTP POST request to the specified URL.

    Args:
        payload (Dict[str, Any]): The JSON payload to send in the request.
        headers (Dict[str, str]): The headers to include in the request.
        url (str): The URL to send the request to.

    Returns:
        httpx.Response: The response from the server.

    Raises:
        ValueError: If the response status code is not 200.
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(url, headers=headers, json=payload, timeout=120.0)
        if response.status_code != 200:
            logger.error(f"LLM API error: {response.status_code} - {response.text}")
            raise ValueError(f"LLM API error: {response.status_code} - {response.text}")
        return response

def stream_text_from_llm(
    messages: List[Message],
    model: str = "mistral-large-latest",
    temperature: float = 0.5
) -> AsyncIterable[str]:
    """
    Stream text from any compatible OpenAI API in real-time.

    This function returns an asynchronous generator that yields text chunks as they are received from the API.

    Args:
        messages (List[Message]): A list of message objects containing the conversation history.
        model (str, optional): The model to use for generating the response. Defaults to "mistral-large-latest".
        temperature (float, optional): The sampling temperature to use. Defaults to 0.5.

    Returns:
        AsyncIterable[str]: An asynchronous generator that yields text chunks.

    Raises:
        ValueError: If the LLM_API_KEY environment variable is not set.
    """
    # Initalize LLM Generator
    async def generator():
        if not LLM_API_KEY:
            raise ValueError("LLM_API_KEY environment variable is not set")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}"
        }

        llm_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        payload = {
            "model": model,
            "messages": llm_messages,
            "temperature": temperature,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{LLM_API_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120.0
            ) as response:
                if response.status_code != 200:
                    error_detail = await response.aread()
                    logger.error(f"LLM API error: {response.status_code} - {error_detail}")
                    raise ValueError(f"LLM API error: {response.status_code} - {error_detail}")

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        if line.strip() == "data: [DONE]":
                            continue

                        try:
                            json_str = line[6:].strip()
                            if not json_str:
                                continue

                            data = json.loads(json_str)
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse LLM API response: {line} - Error: {str(e)}")

    return generator()

async def get_text_from_llm(
    messages: List[Message],
    model: str = "mistral-large-latest",
    temperature: float = 0.2,
    response_format: Optional[Dict[str, Any]] = None
) -> str:
    """
    Get a complete text response from any compatible OpenAI API.

    This function sends a request to the compatible OpenAI API API and returns the complete response as a string.

    Args:
        messages (List[Message]): A list of message objects containing the conversation history.
        model (str, optional): The model to use for generating the response. Defaults to "mistral-large-latest".
        temperature (float, optional): The sampling temperature to use. Defaults to 0.2.
        response_format (Optional[Dict[str, Any]], optional): The desired response format. Defaults to None.

    Returns:
        str: The complete text response from the API.

    Raises:
        ValueError: If the LLM_API_KEY environment variable is not set.
    """
    if not LLM_API_KEY:
        raise ValueError("LLM_API_KEY environment variable is not set")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}"
    }

    llm_messages = [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]

    payload = {
        "model": model,
        "messages": llm_messages,
        "temperature": temperature,
        "stream": False
    }

    if response_format:
        payload["response_format"] = response_format

    response = await _make_request(payload, headers, f"{LLM_API_URL}/chat/completions")

    data = response.json()
    if response_format:
        return data
    else:
        return data["choices"][0]["message"]["content"]