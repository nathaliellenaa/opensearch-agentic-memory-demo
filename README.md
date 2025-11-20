# OpenSearch Agentic Memory Demo

This repository demonstrates how to integrate OpenSearch's Agentic Memory capabilities with popular AI agent frameworks like Strands and LangGraph. The demo showcases persistent memory management for AI agents, enabling them to maintain context across sessions and conversations.

## Strands Agents (Short-term memory)

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Set environment variables

```bash
export OPENSEARCH_DOMAIN_URL=<your_opensearch_domain_endpoint>
export OPENSEARCH_USERNAME=<your_opensearch_domain_username>
export OPENSEARCH_PASSWORD=<your_opensearch_domain_password>

export MEMORY_CONTAINER_NAME=<your_memory_container_name>  # Optional, defaults to 'demo_memory_container'
export MEMORY_CONTAINER_DESCRIPTION=<your_memory_container_description> # Optional, defaults to 'OpenSearch Strands demo memory container'
export SESSION_ID=<your_session_id>  # Optional, defaults to 'demo_session'
```

3. Set AWS credentials to use Bedrock

```bash
# Option 1 - refresh AWS credentials
aws configure

# Option 2 - set env variables
export AWS_ACCESS_KEY_ID=<your_aws_access_key>
export AWS_SECRET_ACCESS_KEY=<your_aws_secret_key>
export AWS_SESSION_TOKEN=<your_aws_session_token>
```

4. Run the script

```bash
python strands/short_term/strands_short_term.py
```

The script creates an interactive chat session where you can converse with the AI agent. The agent maintains conversation history using OpenSearch's persistent memory.

- Enter your messages at the "You:" prompt
- Type `q` or `quit` to exit

**Example conversation:**
```
Created memory container with id 'Wac4o5oB6Os6SYy-CAwu'
OpenSearch Agentic Memory Demo - Session: demo_session
Type 'q' or 'quit' to end the conversation

You: Hello, my name is Bob and I enjoy swimming.
Assistant: Hi Bob! Nice to meet you. Swimming is a great exercise!

You: Do you remember my name?
Assistant: Yes, your name is Bob. You mentioned it when you introduced yourself.

You: q
Goodbye!
```