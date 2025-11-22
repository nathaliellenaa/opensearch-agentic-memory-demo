import os
from datetime import datetime
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from opensearch_checkpoint_saver import OpenSearchSaver

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Opensearch domain configuration
cluster_url = os.getenv('OPENSEARCH_URL')
username = os.getenv('OPENSEARCH_USERNAME')
password = os.getenv('OPENSEARCH_PASSWORD')
verify_ssl = os.getenv("OPENSEARCH_VERIFY_SSL", "false").lower() == "true"

# Memory configuration
memory_container_name = os.getenv('MEMORY_CONTAINER_NAME', 'langgraph_short_term')

# AWS Bedrock configuration
bedrock_model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
aws_region = os.getenv("AWS_REGION", "us-east-1")

def create_chatbot(checkpointer):
    """Create a minimal chatbot with checkpoint support."""
    
    model = ChatBedrock(
        model_id=bedrock_model_id,
        region_name=aws_region,
        model_kwargs={"temperature": 0.7, "max_tokens": 1024}
    )
    
    def chat_node(state: MessagesState):
        return {"messages": [model.invoke(state["messages"])]}
    
    graph = StateGraph(MessagesState)
    graph.add_node("chat", chat_node)
    graph.add_edge(START, "chat")
    graph.add_edge("chat", END)
    
    return graph.compile(checkpointer=checkpointer)


def send_message(app, thread_id: str, message: str):
    """Send a message and return the response."""
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke({"messages": [HumanMessage(content=message)]}, config)
    return result["messages"][-1].content


def get_message_count(app, thread_id: str) -> int:
    """Get the number of messages in the conversation."""
    config = {"configurable": {"thread_id": thread_id}}
    state = app.get_state(config)
    if state and state.values:
        return len(state.values.get("messages", []))
    return 0

def setup_opensearch_checkpointer(container_name: str, index_prefix: str) -> OpenSearchSaver:
    """Setup OpenSearch checkpoint saver.

    Args:
        container_name: Name for the memory container

    Returns:
        Configured OpenSearchSaver instance
    """
    auth = (username, password)

    # Try to create container (will fail if already exists, which is fine)
    try:
        container_id = OpenSearchSaver.create_memory_container(
            base_url=cluster_url,
            name=container_name,
            description="Checkpoint storage for Bedrock Claude chatbot",
            configuration={
                "index_prefix": index_prefix,
                "disable_history": False,
                "disable_session": False,
                "use_system_index": False,
            },
            auth=auth,
            verify_ssl=verify_ssl,
        )
        print(f"✅ Created memory container: {container_id}")
    except Exception as e:
        raise e

    # Create and return checkpointer
    checkpointer = OpenSearchSaver(
        base_url=cluster_url,
        memory_container_id=container_id,
        auth=auth,
        verify_ssl=verify_ssl,
    )

    return checkpointer

if __name__ == "__main__":
    """Create a new conversation session."""
    #1. Setup OpenSearch checkpointer
    print("\n1. Setting up OpenSearch checkpointer...")
    container_name = memory_container_name
    index_prefix = memory_container_name
    checkpointer = setup_opensearch_checkpointer(container_name, index_prefix)
    
    #2. Create chatbot
    print("\n2. Creating chatbot...")
    app = create_chatbot(checkpointer)
    print("✅ Chatbot ready\n")
    
    #3. Start interactive session
    thread_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print("LangGraph Interactive Demo")
    print("Type 'q' or 'quit' to end the conversation\n")
    
    while True:
        question = input("👤 You: ").strip()
        
        if question.lower() in ['q', 'quit']:
            print("🤖 Assistant: Goodbye!")
            
            # Show session summary
            msg_count = get_message_count(app, thread_id)
            print("\n" + "=" * 70)
            print(f"\n📊 Session Summary:")
            print(f"Thread ID: {thread_id}")
            print(f"Total messages: {msg_count}")
            print(f"Session ended: {datetime.now()}")
            break
        
        if not question:
            continue
        
        response = send_message(app, thread_id, question)
        print(f"🤖 Assistant: {response}")
        print()