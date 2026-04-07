import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
embedding_fn=SentenceTransformerEmbeddingFunction(model_name="sentence-transformers/all-MiniLM-L6-v2")
client=chromadb.PersistentClient(path="./chroma_db")
dsa_collection=client.get_or_create_collection(name="dsa_problems",embedding_function=embedding_fn,metadata={"hnsw:space":"cosine"})
math_collection=client.get_or_create_collection(name="math_prereqs",embedding_function=embedding_fn)
