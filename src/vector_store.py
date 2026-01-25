import faiss
import numpy as np
import json
from pathlib import Path
from typing import List, Tuple

class VectorStore:
    def __init__(self, dimension: int, index_path: str = "embeddings/vector.index"):
        self.dimension = dimension
        self.index_path = index_path
        self.chunks_path = index_path.replace('.index', '_chunks.json')
        self.index = None
        self.chunks = []
    
    def create_index(self):
        """Create a new FAISS index"""
        self.index = faiss.IndexFlatL2(self.dimension)
        print(f"Created new FAISS index with dimension {self.dimension}")
    
    def add_embeddings(self, embeddings: np.ndarray, chunks: List[str]):
        """Add embeddings and their corresponding chunks"""
        if self.index is None:
            self.create_index()
        
        self.index.add(embeddings.astype('float32'))
        self.chunks.extend(chunks)
        print(f"Added {len(chunks)} chunks to index. Total: {len(self.chunks)}")
    
    def search(self, query_embedding: np.ndarray, k: int = 3) -> Tuple[List[str], List[float]]:
        """Search for top-k similar chunks"""
        if self.index is None or self.index.ntotal == 0:
            return [], []
        
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(
            query_embedding.astype('float32'), k
        )
        
        results = [self.chunks[i] for i in indices[0]]
        scores = distances[0].tolist()
        
        return results, scores
    
    def save(self):
        """Save index and chunks to disk"""
        Path(self.index_path).parent.mkdir(parents=True, exist_ok=True)
        
        faiss.write_index(self.index, self.index_path)
        
        with open(self.chunks_path, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        
        print(f"Saved index to {self.index_path}")
    
    def load(self):
        """Load index and chunks from disk"""
        if Path(self.index_path).exists():
            self.index = faiss.read_index(self.index_path)
            
            with open(self.chunks_path, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
            
            print(f"Loaded index with {len(self.chunks)} chunks")
            return True
        return False