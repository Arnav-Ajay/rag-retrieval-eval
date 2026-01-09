# app.py → glue + debug prints
import os
import argparse
from llm import get_llm_response
from ingest import load_pdf, chunk_texts
from retriever import create_vector_store, retrieve_similar_documents
import csv


# Export chunks to CSV for debugging
def export_chunks_csv(all_chunks, output_path):

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

# Retrieval evaluation
def run_retrieval_evaluation(args, vector_store, inspect_k=50):
    import pandas as pd
    print("Running retrieval evaluation...\n")

    questions_df = pd.read_csv(args.questions_csv)
    evaluation_results = []

    for _, row in questions_df.iterrows():
        question_id = row["question_id"]
        question_text = row["question_text"]
        gold_chunk_id = int(row["gold_chunk_id"])
        gold_doc_id = row["gold_doc_id"]
        results = retrieve_similar_documents(vector_store, question_text, top_k=inspect_k)
        
        retrieved_chunk_ids = [chunk_id for chunk_id, doc_id, chunk_text, score in results]
        retrieved_chunk_ids_str = "|".join(map(str, retrieved_chunk_ids))

        evaluation_results.append({
            "question_id": question_id,
            "question": question_text,
            "gold_chunk_id": gold_chunk_id,
            "gold_doc_id": gold_doc_id,
            "retrieved_chunk_ids": retrieved_chunk_ids_str,
            "rank_of_first_relevant": "",
            "retrieved_in_top_k": "",
            "notes": ""
        })

    # Save evaluation results to CSV
    eval_output_path = args.eval_output
    pd.DataFrame(evaluation_results).to_csv(eval_output_path, index=False)    
    print(f"Retrieval evaluation results saved to {eval_output_path}\n")

def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf-dir", default=r"data/input_pdfs/") # Path to directory containing PDFs
    parser.add_argument("--query", default="Is the status for architectural decision case study final and locked?") # Query for retrieval
    
    parser.add_argument("--export-chunks", action="store_true") # Export chunks to CSV for debugging
    parser.add_argument("--corpus-diag", action="store_true") # Print corpus diagnostics
    parser.add_argument("--run-retrieval-eval", action="store_true") # Run retrieval evaluation
    
    
    parser.add_argument("--chunks-csv", default=r"data/chunks_and_questions/chunks_output.csv") # Path to questions csv
    parser.add_argument("--questions-csv", default=r"data/chunks_and_questions/question_input.csv") # Path to questions csv
    parser.add_argument("--eval-output", default=r"data/results_and_summaries/questions_retrieval_results.csv") # output to eval results
    
    args = parser.parse_args()
    pdf_path = args.pdf_dir
    query = args.query
    all_chunks = {}
    global_chunk_id = 0
    corpus_diagnostics = {}
    
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
                    print("⚠️ Chunk limit reached. Document truncated for control-system execution.\n")
                    break
    
    # Export chunks to CSV for debugging
    if args.export_chunks and args.chunks_csv:
        print("\n")
        export_chunks_csv(all_chunks, args.chunks_csv)

    # Corpus diagnostics
    if args.corpus_diag:
        print("\nCorpus Diagnostics:\n")

        for doc, chunk_count in corpus_diagnostics.items():
            print(f"Document: {doc} | Chunks: {chunk_count}")
            
        print(f"\nTotal chunks across corpus: {len(all_chunks)}\n")
        print("Chunk ID → Document ID mapping:")
        for chunk_id, chunk_info in all_chunks.items():
            print(f"Chunk ID: {chunk_id} | Document ID: {chunk_info['doc_id']}")
        
        print("\nCorpus Diagnostics Complete.\n")

    vector_store = create_vector_store(all_chunks)

    # Retrieval evaluation placeholder
    if args.run_retrieval_eval:
        run_retrieval_evaluation(args, vector_store)
        return

    top_k = 4
    results = retrieve_similar_documents(vector_store, query, top_k=top_k)
    print(f"Top {top_k} similar chunks retrieved:")
    context = ""

    for chunk_id, doc_id, chunk_text, score in results:
        print(f"Chunk {chunk_id} | doc={doc_id} | similarity={score:.4f}")
        context += f"\n[Chunk {chunk_id} | Source: {doc_id}]\n{chunk_text}"

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
