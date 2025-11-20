import os
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from strands.session.repository_session_manager import RepositorySessionManager
from strands import Agent
from opensearch_session_manager import OpenSearchSessionRepository

cluster_url = os.getenv('OPENSEARCH_DOMAIN_URL')
username = os.getenv('OPENSEARCH_USERNAME')
password = os.getenv('OPENSEARCH_PASSWORD')
memory_container_name = os.getenv('MEMORY_CONTAINER_NAME', 'demo_memory_container')
memory_container_description = os.getenv('MEMORY_CONTAINER_DESCRIPTION', 'OpenSearch Strands demo memory container')
session_id = os.getenv('SESSION_ID', 'demo_session')

repo = OpenSearchSessionRepository(cluster_url, username, password,
                                   memory_container_name=memory_container_name,
                                   memory_container_description=memory_container_description)
session_manager = RepositorySessionManager(session_id=session_id, session_repository=repo)

agent = Agent(
    session_manager=session_manager,
    system_prompt="You are a helpful assistant.",
    # ... other args like tools, model, etc.
)

question1 = "How are you? My name is Bob, I like swimming."
print(f"------------------ question 1: {question1}")
resp = agent(question1)

question2 = "Do you know my name?"
print(f"\n\n------------------ question 2: {question2}")
resp = agent("Do you know my name?")