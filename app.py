# app.py → glue + debug prints

import os
from llm import get_llm_response
from ingest import load_pdf, chunk_texts
from retriever import create_vector_store, retrieve_similar_documents

def export_chunks_csv(all_chunks, output_path="data/chunks_debug.csv"):
    import csv

    with open(output_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['chunk_id', 'doc_id', 'text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for chunk_id, chunk_info in all_chunks.items():
            writer.writerow({
                'chunk_id': chunk_id,
                'doc_id': chunk_info['doc_id'],
                'text': chunk_info['text']
            })

    print(f"Chunks exported to {output_path}")

def main():

    query = "What is the architecture described in the documents?"

    all_chunks = {}
    global_chunk_id = 0
    corpus_diagnostics = {}

    pdf_path = r"data/"

    for filename in os.listdir(pdf_path):
        if filename.endswith(".pdf"):
            pdf_text = load_pdf(os.path.join(pdf_path, filename))
            chunks = chunk_texts(pdf_text)
            corpus_diagnostics[filename] = len(chunks)
            for _, chunk_text in chunks.items():
                # Preserve document boundary via prefix (no new data structures)
                all_chunks[global_chunk_id] = {
                    "doc_id": filename,
                    "text": chunk_text
                }

                global_chunk_id += 1

                if global_chunk_id >= 1000:
                    print("⚠️ Chunk limit reached. Document truncated for control-system execution.")
                    break

    print("Corpus Diagnostics:")
    for doc, chunk_count in corpus_diagnostics.items():
        print(f"Document: {doc} | Chunks: {chunk_count}")
        
    print(f"Total chunks across corpus: {len(all_chunks)}")
    print("Chunk ID → Document ID mapping:")
    for chunk_id, chunk_info in all_chunks.items():
        print(f"Chunk ID: {chunk_id} | Document ID: {chunk_info['doc_id']}")

    export_chunks_csv(all_chunks)
    print("Exported chunks to CSV for debugging.")
    print("\nCorpus Diagnostics Complete.")

    vector_store = create_vector_store(all_chunks)

    top_k = 4
    results = retrieve_similar_documents(vector_store, query, top_k=top_k)
    print(f"Top {top_k} similar chunks retrieved:")
    context = ""

    for chunk_id, doc_id, chunk_text, score in results:
        print(f"Chunk {chunk_id} | doc={doc_id} | similarity={score:.4f}")
        context += f"\n[Chunk {chunk_id} | Source: {doc_id}]\n{chunk_text}\n"

    prompt = f"""
You are answering a question using ONLY the information provided below.

If the information is insufficient, respond exactly with:
"I don’t have enough information in the provided documents."

--- CONTEXT ---
{context}
--- END CONTEXT ---

Question:
{query}
"""

    response = get_llm_response(prompt)
    print("LLM Response:")
    print(response)


if __name__ == "__main__":
    main()
