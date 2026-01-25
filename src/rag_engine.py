import subprocess
import json
from typing import List, Optional

class RAGEngine:
    def __init__(self, pdf_processor, embedder, vector_store, model_name: str = "mistral"):
        self.pdf_processor = pdf_processor
        self.embedder = embedder
        self.vector_store = vector_store
        self.model_name = model_name
    
    def index_pdfs(self, pdf_directory: str):
        """Process and index all PDFs"""
        # Process PDFs
        results = self.pdf_processor.process_directory(pdf_directory)
        
        # Collect all chunks
        all_chunks = []
        for pdf_name, data in results.items():
            all_chunks.extend(data['chunks'])
        
        if not all_chunks:
            print("No chunks to index!")
            return
        
        # Generate embeddings
        embeddings = self.embedder.embed_texts(all_chunks)
        
        # Add to vector store
        self.vector_store.add_embeddings(embeddings, all_chunks)
        
        # Save index
        self.vector_store.save()
        
        print(f"\nIndexing complete!")
        print(f"Total chunks: {len(all_chunks)}")
    
    def query(self, question: str, top_k: int = 3) -> dict:
        """Query the RAG system"""
        # Generate query embedding
        query_embedding = self.embedder.embed_query(question)
        
        # Retrieve relevant chunks
        contexts, scores = self.vector_store.search(query_embedding, k=top_k)
        
        if not contexts:
            return {
                'answer': 'No relevant information found.',
                'contexts': [],
                'scores': []
            }
        
        # Build prompt
        context_text = "\n\n".join([f"[{i+1}] {ctx}" for i, ctx in enumerate(contexts)])
        
        prompt = f"""You are a helpful research assistant. Answer the question based ONLY on the provided context from research papers.

Context:
{context_text}

Question: {question}

Instructions:
- Answer based solely on the context above
- If the context doesn't contain enough information, say so
- Be concise but comprehensive
- Cite which context section(s) you used

Answer:"""
        
        # Call Ollama
        answer = self._call_ollama(prompt)
        
        return {
            'answer': answer,
            'contexts': contexts,
            'scores': scores
        }
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama LLM"""
        try:
            result = subprocess.run(
                ['ollama', 'run', self.model_name],
                input=prompt.encode('utf-8'),
                capture_output=True,
                timeout=60
            )
            return result.stdout.decode('utf-8').strip()
        except Exception as e:
            return f"Error calling Ollama: {e}"