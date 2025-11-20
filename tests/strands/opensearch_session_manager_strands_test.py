from strands.session.repository_session_manager import RepositorySessionManager
from strands import Agent
from opensearch_session_manager import OpenSearchSessionRepository

cluster_url = "https://localhost:9200"
username = "admin"
password = "<PASSWORD>"

repo = OpenSearchSessionRepository(cluster_url, username, password,
                                   memory_container_name="ylwu_test1",
                                   memory_container_description="This is a test memory container")
session_manager = RepositorySessionManager(session_id="yaliang_test_sessoion1", session_repository=repo)

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
