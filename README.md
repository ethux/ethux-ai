# ETHUX-AI

**Agentic Python Framework for LLM Integration**

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

## Introduction

ETHUX-AI aims to improve the way LLMs interact with tools and create workflows, by allowing them to write their actions and workflows in Python.

By encapsulating multiple functionalities within Python pip-packages or modules, ETHUX-AI enables LLMs to perform tasks using a more natural and expressive approach.

In this README, we'll provide a more grounded and humble explanation of ETHUX-AI and its capabilities.

## How It Works

Each Python module in the `modules` directory encapsulates specific functionalities that LLMs can use to perform tasks. The system:

1. Retrieves relevant modules based on conversation context
2. Allows the LLM to select appropriate functions
3. Enables the LLM to write and execute Python workflows

Example workflow written by the LLM with comments:

```python
# Import the necessary modules
from search import Google
from vm_interactor import Hetzner
from code_writer import agent

def workflow():
    try:
        # Create a Google search object and perform a search
        search = Google()
        results = search.search("ETHUX-AI")
        print(f"Search results: {results}")

        # Initialize the code writer agent
        agent = agent()

        # Generate a list of commands to install ethux-ai based on the search results
        list_of_installation_commands = agent.write_code(results)

        # Create a Hetzner virtual machine object
        vm = Hetzner()

        # Create a new virtual machine using the provided name
        creation = vm.create_vm("ethux-ai-vm")
        print(f"Creation status: {creation}")

        # Initialize an empty list to store results
        list_of_results = []

        # Execute each command on the virtual machine and store the results
        for command in list_of_installation_commands:
            result = vm.execute_command(command)
            list_of_results.append(result)

        # Return the search results
        return results
    except Exception as e:
        print(f"Error: {e}")
        return None
```

5. This workflow should be dry-runned and linted to ensure it is correct, and can be executed without any issues.
6. Based on the execution result a retry is possible or inform the user the process has failed.

As you can see, this enables the LLM to write its own process within code, instead of pre-defining functions and flows.
See each module as n8n modules, but then in code, with the possebility for the LLM to wr

### ETHUX-AI enables LLMs to:

✔ Build multi-step workflows with error handling

✔ Maintain state across executions within a continuous process

✔ Nest agents in hierarchical structures for complex problem-solving

✔ Combine pre-built packages with custom logic for optimal solutions

✔ Reduce LLM inference calls through efficient workflow composition

## Getting Started

To start using ETHUX-AI, follow these steps:

1. Clone the repository:
```
git clone https://github.com/ethux/ethux-ai.git
cd ethux-ai
```

2. Copy the example environment variables and fill in your API keys and other vars

Note: Right now it works only with the Mistral API and models, for other API providers you have to change some of the code.
  
   Use: `cp .example.env .env`.

   Do this within the root directory of this project and the executor directory.

   Depending on the modules you are using update the .env file with the required API keys and vars.


4. Start the docker-compose stack:
```
sudo docker-compose up --build
```

4. Access the ETHUX-AI API at `http://localhost:8000`

### Optional:

5. Install OpenWebUI and connect to the ETHUX-AI API to interact with the ETHUX-AI API using a web interface:

```
sudo docker compose -f docker-compose.openwebui.yaml up -d
```

## Next steps

- [ ] Check the modules directory for available functions and add your own
- [ ] Update the modules.json file with your own modules (required for now, will be automated with docstrings etc. soon)
- [ ] Fill the .env file with your API keys if needed

## Contributing

We welcome contributions to the ETHUX-AI framework! Whether you're interested in adding new capabilities, improving documentation, or sharing use cases.

## License

ETHUX-AI is available under the [AGPL-3.0 License](LICENSE). See the LICENSE file for more details.
