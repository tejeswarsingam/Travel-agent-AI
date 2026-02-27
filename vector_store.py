import chromadb
from chromadb.utils import embedding_functions
import os

# Use Gemini or local embeddings
emb_fn = embedding_functions.GoogleGenerativeAiEmbeddingFunction()
client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_or_create_collection(name="user_trips", embedding_function=emb_fn)

def save_trip_to_vector(trip_id, text_content, metadata):
    collection.add(
        documents=[text_content],
        metadatas=[metadata],
        ids=[str(trip_id)]
    )

def search_similar_trips(query):
    return collection.query(query_texts=[query], n_results=3)