from openai import OpenAI
import os

def create_vector_store(client: OpenAI, store_name: str) -> dict:
    """Create a new vector store."""
    try:
        vector_store = client.vector_stores.create(name=store_name)
        details = {
            "id": vector_store.id,
            "name": vector_store.name,
            "created_at": vector_store.created_at,
            "file_counts": vector_store.file_counts.completed
        }
        print("Vector store created:", details)
        return details
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return {}

def upload_file(client: OpenAI, file_path: str, vector_store_id: str) -> dict:
    """Upload a file to a vector store."""
    file_name = os.path.basename(file_path)
    try:
        file_response = client.files.create(file=open(file_path, 'rb'), purpose="assistants")
        attach_response = client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_response.id
        )
        return {"file": file_name, "status": "success"}
    except Exception as e:
        print(f"Error with {file_name}: {str(e)}")
        return {"file": file_name, "status": "failed", "error": str(e)}

if __name__ == "__main__":
    # Example usage
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Create a vector store
    store = create_vector_store(client, "ACME Shop Product Knowledge Base")
    
    # Upload a file to the vector store
    if store:
        result = upload_file(client, "voice_agents_knowledge/acme_product_catalogue.pdf", store["id"])
        print("Upload result:", result) 