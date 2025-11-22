import os
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from strands.session.repository_session_manager import RepositorySessionManager
from strands import Agent
from opensearch_session_manager import OpenSearchSessionRepository

# Opensearch domain configuration
cluster_url = os.getenv('OPENSEARCH_URL')
username = os.getenv('OPENSEARCH_USERNAME')
password = os.getenv('OPENSEARCH_PASSWORD')

# Memory and session configuration
memory_container_name = os.getenv('MEMORY_CONTAINER_NAME', 'strands_short_term')
memory_container_description = os.getenv('MEMORY_CONTAINER_DESCRIPTION', 'OpenSearch Strands demo memory container')
session_id = os.getenv('SESSION_ID', 'demo_short_term_session')

repo = OpenSearchSessionRepository(cluster_url, username, password,
                                   memory_container_name=memory_container_name,
                                   memory_container_description=memory_container_description)
session_manager = RepositorySessionManager(session_id=session_id, session_repository=repo)

agent = Agent(
    session_manager=session_manager,
    system_prompt="You are a helpful assistant.",
    # ... other args like tools, model, etc.
)

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