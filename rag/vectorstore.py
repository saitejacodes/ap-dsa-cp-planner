import os
import chromadb
from dotenv import load_dotenv
load_dotenv()
from chromadb.utils.embedding_functions import GoogleGenerativeAiEmbeddingFunction

embedding_fn=GoogleGenerativeAiEmbeddingFunction(api_key=os.environ.get("GEMINI_API_KEY"),task_type="RETRIEVAL_DOCUMENT")
client=chromadb.PersistentClient(path="./chroma_db")
dsa_collection=client.get_or_create_collection(name="dsa_problems",embedding_function=embedding_fn,metadata={"hnsw:space":"cosine"})
math_collection=client.get_or_create_collection(name="math_prereqs",embedding_function=embedding_fn)
