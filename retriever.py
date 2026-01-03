# retriever.py → embeddings + top-K
import numpy as np

# Function to embedd chunked text into vector
def get_embedding(chunk):
    # Dummy embedding function: convert each character to its ASCII value and create a fixed-size vector
    embedding_size = 128
    embedding = np.zeros(embedding_size)
    for i, char in enumerate(chunk):
        if i < embedding_size:
            embedding[i] = ord(char)
    return embedding

# Function to create a vector store from document chunks
def create_vector_store(chunks):
    vector_store = []
    for id, chunk_info in chunks.items():
        chunk_text = chunk_info["text"]
        doc_id = chunk_info["doc_id"]
        embedding = get_embedding(chunk_text)
        vector_store.append((id, doc_id, chunk_text, embedding))
    return vector_store


# Function to compute cosine similarity between two vectors
def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2.T)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

# store embeddings in a list
def retrieve_similar_documents(vector_store, query, top_k=4):
    query_embedding = get_embedding(query)
    similarities = []

    for chunk_id, doc_id, chunk_text, embedding in vector_store:
        sim = cosine_similarity(query_embedding, embedding)
        similarities.append((chunk_id, doc_id, chunk_text, sim))

    similarities.sort(key=lambda x: x[3], reverse=True)

    return similarities[:top_k]


