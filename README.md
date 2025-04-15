# ETHUX-AI  
### Agentic Python Framework for LLM Integration  

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

## Introduction

ETHUX-AI tries to transforms how Large Language Models (LLMs) interact by embedding them natively within a Python execution environment. Unlike other AI frameworks that rely on isolated tool calls, ETHUX-AI enables LLMs to operate as active agents, capable of dynamic workflow composition, stateful problem-solving, and true computational agency.

While LLMs using Python as a native execution environment isn't new (as seen in code interpreters), ETHUX-AI's innovation lies in enabling LLMs to compose complex workflows using pre-defined functions tailored for LLMs and the broader Python ecosystem. This approach allows LLMs to create sophisticated solutions with error handling, state management, and multi-agent architectures.

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
