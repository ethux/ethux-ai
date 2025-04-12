import requests
import json
import os

class CodeGenerator:
    """
    A class to generate code using a chat completions API.

    Attributes:
        api_key (str): The API key for the chat completions API.
        api_endpoint (str): The endpoint URL for the chat completions API.
    """

    def __init__(self):
        """
        Initialize the CodeGenerator.

        Loads the API key and endpoint from environment variables.
        """
        self.api_key = os.getenv('CHAT_COMPLETIONS_API_KEY')
        self.api_endpoint = os.getenv('CHAT_COMPLETIONS_API_ENDPOINT')
        if not self.api_key or not self.api_endpoint:
            raise ValueError("CHAT_COMPLETIONS_API_KEY and CHAT_COMPLETIONS_API_ENDPOINT environment variables must be set.")

    def generate_code(self, file_names, goals, contexts):
        """
        Generate code using the chat completions API.

        Args:
            file_names (list of str): The names of the files to be generated.
            goals (list of str): The goals or purposes of the code.
            contexts (list of str): The contexts for the code generation.
            other_modules_contexts (list of str): The contexts of other modules.

        Returns:
            list of str: The generated codes.
        """
        generated_codes = []

        file_names = file_names if file_names else "Not defined"
        goals = goals if goals else "Not defined"
        contexts = contexts if contexts else "Not defined"

        for file_name, goal, context in zip(file_names, goals, contexts):
            prompt = (
                f"Generate the code for the file named '{file_name}' with the goal: '{goal}'.\n"
                f"Context: {context}\n"
                f"Include detailed docstrings for all functions and classes.\n"
            )

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': 'codestral-latest',
                'messages': [
                    {'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': prompt}
                ]
            }

            response = requests.post(self.api_endpoint, headers=headers, data=json.dumps(data))
            response.raise_for_status()

            generated_code = response.json()['choices'][0]['message']['content']
            generated_codes.append(generated_code)

        return generated_codes