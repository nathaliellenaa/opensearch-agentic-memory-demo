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

def create_simple_chatbot(checkpointer):
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

def resume_existing_thread(container_id: str, thread_id: str):
    """Resume an existing thread and allow interactive conversation."""
    
    print("=" * 70)
    print(f"RESUMING EXISTING THREAD: {thread_id}")
    print("=" * 70)
    
    # Setup (same as before)
    auth = (username, password)
    checkpointer = OpenSearchSaver(
        base_url=cluster_url,
        memory_container_id=container_id,
        auth=auth,
        verify_ssl=False
    )
    
    app = create_simple_chatbot(checkpointer)
    
    # Check existing messages
    msg_count = get_message_count(app, thread_id)
    print(f"\nMessages found: {msg_count}")
    
    if msg_count == 0:
        print("❌ No messages found. Thread may not exist.")
        return
    
    # Show conversation history
    config = {"configurable": {"thread_id": thread_id}}
    state = app.get_state(config)
    if state and state.values:
        messages = state.values.get("messages", [])
        print("\nConversation history:")
        for i, msg in enumerate(messages):
            role = "User" if msg.__class__.__name__ == "HumanMessage" else "AI"
            content = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
            print(f"  [{i+1}] {role}: {content}")
    
    # Continue interactive conversation
    print(f"\nContinuing conversation at {datetime.now()}")
    print("Type 'q' or 'quit' to end the conversation\n")

    while True:
        question = input("👤 You: ").strip()
        
        if question.lower() in ['q', 'quit']:
            print("🤖 Assistant: Goodbye!")
            
            # Show session summary
            final_msg_count = get_message_count(app, thread_id)
            print("\n" + "=" * 70)
            print(f"\n📊 Session Summary:")
            print(f"Thread ID: {thread_id}")
            print(f"Total messages: {final_msg_count}")
            print(f"Session ended: {datetime.now()}")
            break
        
        if not question:
            continue
        
        response = send_message(app, thread_id, question)
        print(f"🤖 Assistant: {response}")
        print()


if __name__ == "__main__":
    print("LangGraph Checkpoint Resume")
    container_id = input("Enter container ID: ").strip()
    thread_id = input("Enter thread ID: ").strip()
    print()
    
    if container_id and thread_id:
        resume_existing_thread(container_id, thread_id)
    else:
        print("❌ Both container ID and thread ID are required")
