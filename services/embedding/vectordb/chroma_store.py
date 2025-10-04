from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
import uuid

class ChromaStore:
    def __init__(self, db_path="./chromadb"):
        # Ensure the directory exists
        import os
        os.makedirs(db_path, exist_ok=True)
        
        self.client = PersistentClient(path=db_path)
        self.embedder = SentenceTransformer("BAAI/bge-base-en-v1.5", trust_remote_code=True)
        
        # Get the embedding dimension from the model
        embedding_dimension = self.embedder.get_sentence_embedding_dimension()
        print(f"BGE model embedding dimension: {embedding_dimension}")
        
        # Force delete existing collection to avoid dimension conflicts
        try:
            self.client.delete_collection("walnut-embeddings")
            print("Deleted existing collection to avoid dimension conflicts")
        except:
            pass  # Collection doesn't exist, which is fine
        
        # Create collection with correct embedding dimension
        self.collection = self.client.get_or_create_collection(
            name="walnut-embeddings",
            metadata={"hnsw:space": "cosine"}
        )
        print(f"Created collection with dimension: {embedding_dimension}")

    def add_texts(self, texts: list[str], metadatas: list[dict] = None) -> list[str]:
        embeddings = self.embedder.encode(texts).tolist()
        ids = [str(uuid.uuid4()) for _ in texts]
        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas if metadatas else [{} for _ in texts]
        )
        return ids

    def search(self, query: str, k: int = 5):
        embedding = self.embedder.encode([query]).tolist()[0]
        return self.collection.query(query_embeddings=[embedding], n_results=k)