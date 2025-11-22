import os
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from strands import Agent
from opensearch_memory_tool import OpenSearchMemoryToolProvider

# Opensearch domain configuration
cluster_url = os.getenv('OPENSEARCH_URL')
username = os.getenv('OPENSEARCH_USERNAME')
password = os.getenv('OPENSEARCH_PASSWORD')

# Model configuration
embedding_model_id = os.getenv('EMBEDDING_MODEL_ID')
llm_id = os.getenv('LLM_MODEL_ID')

# Memory and session configuration
memory_container_name = os.getenv('MEMORY_CONTAINER_NAME', 'strands_long_term')
session_id = os.getenv('SESSION_ID', 'demo_long_term_session')
user_id = os.getenv('USER_ID', 'demo_user')
agent_id = os.getenv('AGENT_ID', 'demo_agent')

# Initialize the tool provider
provider = OpenSearchMemoryToolProvider(
    cluster_url=cluster_url,
    username=username,
    password=password,
    memory_container_name=memory_container_name,
    session_id=session_id,
    agent_id=agent_id,
    user_id=user_id,
    embedding_model_id=embedding_model_id,
    llm_id=llm_id
)

agent = Agent(tools=provider.tools)

print(f"OpenSearch Agentic Memory Demo - Session: {session_id}")
print("Type 'q' or 'quit' to end the conversation\n")

while True:
    question = input("👤 You: ").strip()
    
    print(f"🤖 Assistant: ", end='') 
    
    if question.lower() in ['q', 'quit']:
        print("Goodbye!")
        break
    
    if not question:
        continue
    
    response = agent(question)
    print("\n")