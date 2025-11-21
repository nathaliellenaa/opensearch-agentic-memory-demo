# OpenSearch Agentic Memory Demo

This repository demonstrates how to integrate OpenSearch's Agentic Memory capabilities with popular AI agent frameworks like Strands and LangGraph. The demo showcases persistent memory management for AI agents, enabling them to maintain context across sessions and conversations.

## Strands Agents (Short-term memory)

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Set environment variables

```bash
# OpenSearch domain configuration (required)
export OPENSEARCH_DOMAIN_URL=<your_opensearch_domain_endpoint>
export OPENSEARCH_USERNAME=<your_opensearch_domain_username>
export OPENSEARCH_PASSWORD=<your_opensearch_domain_password>

# Memory and session configuration (Optional)
export MEMORY_CONTAINER_NAME=<your_memory_container_name>               # Defaults to 'demo_short_term_memory'
export MEMORY_CONTAINER_DESCRIPTION=<your_memory_container_description> # Defaults to 'OpenSearch Strands demo memory container'
export SESSION_ID=<your_session_id>                                     # Defaults to 'demo_short_term_session'
```

3. Set AWS credentials to use Amazon Bedrock

```bash
export AWS_ACCESS_KEY_ID=<your_aws_access_key>
export AWS_SECRET_ACCESS_KEY=<your_aws_secret_key>
export AWS_SESSION_TOKEN=<your_aws_session_token>
```

4. Run the script

```bash
python strands/strands_short_term.py
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

## Strands Agents (Long-term memory)

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Set environment variables

```bash
# OpenSearch domain configuration (required)
export OPENSEARCH_DOMAIN_URL=<your_opensearch_domain_endpoint>
export OPENSEARCH_USERNAME=<your_opensearch_domain_username>
export OPENSEARCH_PASSWORD=<your_opensearch_domain_password>

# Model configuration (Optional - auto-created if not provided)
export EMBEDDING_MODEL_ID=<your_embedding_model_id>        # Defaults to Amazon Titan Embedding model
export LLM_MODEL_ID=<your_llm_model_id>                    # Default to Amazon Bedrock Claude model

# Memory and session configuration (Optional)
export MEMORY_CONTAINER_NAME=<your_memory_container_name>  # Defaults to 'demo_long_term_memory'
export SESSION_ID=<your_session_id>                        # Defaults to 'demo_long_term_session'
export USER_ID=<your_user_id>                              # Defaults to 'demo_user'
export AGENT_ID=<your_agent_id>                            # Defaults to 'demo_agent'

# Tool configuration (Optional)
export BYPASS_TOOL_CONSENT=<true/false>                    # Defaults to true
```

3. Set AWS credentials (required for automatic model creation)

```bash
export AWS_REGION=<your_aws_region>
export AWS_ACCESS_KEY_ID=<your_aws_access_key>
export AWS_SECRET_ACCESS_KEY=<your_aws_secret_key>
export AWS_SESSION_TOKEN=<your_aws_session_token>
```

> Note: AWS credentials are only required if you don't provide `EMBEDDING_MODEL_ID` or `LLM_MODEL_ID`. The system will automatically create Amazon Bedrock models using these credentials

4. Run the script

```bash
python strands/strands_long_term.py
```

The script creates an interactive chat session with long-term memory capabilities. Unlike short-term memory, this agent can remember information across different sessions and uses semantic search to retrieve relevant memories based on meaning.

- Enter your messages at the "You:" prompt
- Type `q` or `quit` to exit

**Example conversation:**
```
% python strands/strands_long_term.py
Created embedding model with id 'tqfkp5oB6Os6SYy-CA32'
Created LLM model with id 'uKfkp5oB6Os6SYy-CQ18'
Created memory container with id 'uqfkp5oB6Os6SYy-CQ2t'
OpenSearch Agentic Memory Demo - Session: demo_session0
Type 'q' or 'quit' to end the conversation

You: My name is Bob and I like swimming
I'll store this information about you in memory so I can remember it for future conversations.
Tool #1: opensearch_memory
╭─────────────────────────────────────── Add long-term memory for session demo_sesison0, agent demo_agent ────────────────────────────────────────╮
│ User's name is Bob and he likes swimming                                                                                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────────────────────── Memory Stored ─────────────────────────────────────────────────────────────╮
│ ✅ Memory stored successfully:                                                                                                          │
│ 🔑 Memory ID: xKfkp5oB6Os6SYy-Nw2Q                                                                                                      │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Nice to meet you, Bob! I've stored that information so I'll remember that your name is Bob and that you enjoy swimming. Is there anything specific about swimming you'd like to talk about, or anything else you'd like me to remember about you?
You: Do you know my name and hobby?
Let me search my memory to recall what I know about you.
Tool #2: opensearch_memory
╭──────────────────────────────────────────────────────────── Search Results ─────────────────────────────────────────────────────────────╮
│                              Long term memories                                                                                         │
│ ┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓                                                           │
│ ┃ Memory ID            ┃ Content                                            ┃                                                           │
│ ┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩                                                           │
│ │ xqfkp5oB6Os6SYy-QA3H │ Bob likes swimming.                                │                                                           │
│ └──────────────────────┴────────────────────────────────────────────────────┘                                                           │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Yes, I do! Based on my memory, your name is **Bob** and your hobby is **swimming**. I remembered this from our earlier conversation where you introduced yourself to me.
You: q
Goodbye!


# New session
% python strands/strands_long_term.py
Find memory container with id 'uqfkp5oB6Os6SYy-CQ2t' by name 'demo_memory_container'
OpenSearch Agentic Memory Demo - Session: demo_session1
Type 'q' or 'quit' to end the conversation

You: Now I don't like swimming any more, I like playing basketball now.
I'll store this updated preference for you, noting that you now like playing basketball instead of swimming.
Tool #1: opensearch_memory
╭─────────────────────────────────────── Add long-term memory for session demo_session1, agent demo_agent ────────────────────────────────────────╮
│ User no longer likes swimming and now prefers playing basketball                                                                        │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────────────────────── Memory Stored ─────────────────────────────────────────────────────────────╮
│ ✅ Memory stored successfully:                                                                                                          │
│ 🔑 Memory ID: yKflp5oB6Os6SYy-Iw0L                                                                                                      │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Perfect! I've stored your updated preference. Your memory now shows that you no longer like swimming and have switched to enjoying basketball instead. This information is saved and I'll remember it for future conversations.
You: Do you know my name and hobby?
Let me search through your stored memories to find information about your name and hobby.
Tool #2: opensearch_memory
╭──────────────────────────────────────────────────────────── Search Results ─────────────────────────────────────────────────────────────╮
│                              Long term memories                                                                                         │
│ ┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓                                                           │
│ ┃ Memory ID            ┃ Content                                            ┃                                                           │
│ ┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩                                                           │
│ │ yaflp5oB6Os6SYy-Mg0g │ Bob no longer likes swimming and now prefers       │                                                           │
│ │                      │ playing basketball.                                │                                                           │
│ └──────────────────────┴────────────────────────────────────────────────────┘                                                           │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Based on the search results, I can see that I have information about you! According to my memories:

**Your name:** Bob

**Your current hobby:** You now like playing basketball (you previously liked swimming but changed your preference)

So yes, I know that your name is Bob and your current hobby is playing basketball. I also remember that you used to like swimming but switched to preferring basketball instead.
You: q
Goodbye!
```
