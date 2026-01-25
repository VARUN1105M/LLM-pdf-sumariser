from src.pdf_processor import PDFProcessor
from src.embedder import EmbeddingGenerator
from src.vector_store import VectorStore
from src.rag_engine import RAGEngine

def main():
    # Initialize components
    pdf_processor = PDFProcessor(chunk_size=500, chunk_overlap=50)
    embedder = EmbeddingGenerator()
    vector_store = VectorStore(dimension=embedder.dimension)
    rag_engine = RAGEngine(pdf_processor, embedder, vector_store, model_name="mistral")
    
    # Try to load existing index
    if not vector_store.load():
        print("No existing index found. Indexing PDFs...")
        rag_engine.index_pdfs("data/pdfs")
    
    # Interactive query loop
    print("\nRAG System Ready! Ask questions (or 'quit' to exit)\n")
    
    while True:
        question = input("Question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        if not question:
            continue
        
        result = rag_engine.query(question)
        
        print(f"\nAnswer: {result['answer']}\n")
        print(f"Sources used: {len(result['contexts'])} chunks\n")

if __name__ == "__main__":
    main()