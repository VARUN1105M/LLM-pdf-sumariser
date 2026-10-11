import pytest
from src.knowledge.ingestion import KnowledgeBase
from src.knowledge.retriever import LennyRetriever

def test_knowledge_base_indexing():
    kb = KnowledgeBase()
    count = kb.build_index(force_reload=True)
    assert count > 0, "KnowledgeBase should extract chunks from transcripts"
    assert len(kb.chunks) == count
    assert kb.is_indexed is True

def test_retrieval_relevance_shreyas():
    kb = KnowledgeBase()
    kb.build_index()
    retriever = LennyRetriever(kb)

    # Query specifically about Shreyas Doshi's framework
    query = "Explain Shreyas Doshi LGP framework and Leverage vs Growth"
    context, citations = retriever.retrieve_grounded_context(query, top_k=3)

    assert len(citations) > 0, "Should return citations for relevant query"
    assert any("Shreyas" in c["guest"] for c in citations), "Shreyas Doshi should be identified as top citation"
    assert "Leverage" in context

def test_retrieval_relevance_brian_chesky():
    kb = KnowledgeBase()
    kb.build_index()
    retriever = LennyRetriever(kb)

    query = "Brian Chesky founder mode and delegation at Airbnb"
    context, citations = retriever.retrieve_grounded_context(query, top_k=3)

    assert len(citations) > 0
    assert any("Brian Chesky" in c["guest"] for c in citations)
    assert "Founder Mode" in context or "Airbnb" in context

def test_empty_retrieval_behavior():
    kb = KnowledgeBase()
    kb.build_index()
    retriever = LennyRetriever(kb)

    query = "Quantum electrodynamics and nuclear propulsion mechanics"
    context, citations = retriever.retrieve_grounded_context(query, top_k=3)
    # The retriever should handle unrelated queries gracefully
    assert isinstance(context, str)
    assert isinstance(citations, list)
