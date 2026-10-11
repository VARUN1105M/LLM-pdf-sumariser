import logging
from typing import List, Dict, Any, Tuple
from src.knowledge.ingestion import KnowledgeBase
from src.config import settings

logger = logging.getLogger("lenny_assistant.retriever")

class LennyRetriever:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

    def retrieve_grounded_context(self, query: str, top_k: int = 4) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Retrieves top relevant transcript chunks and formats them into:
        1. Context string for the LLM
        2. Clean citation metadata payload for UI rendering
        """
        results = self.kb.search(query, top_k=top_k)
        
        if not results:
            return "No directly relevant transcript excerpts found in Lenny's Knowledge Base.", []

        context_lines = []
        citations = []

        for i, res in enumerate(results, 1):
            guest = res["guest"]
            title = res["title"]
            ts = res.get("timestamp_hint", "")
            ep = f"Ep #{res['episode_number']}" if res.get("episode_number") else ""
            url = res.get("url", "")
            text = res["text"]

            context_lines.append(
                f"[Source {i}: {guest} ({title}, {ep} {ts})]\n{text}\n"
            )

            citations.append({
                "source_index": i,
                "chunk_id": res["chunk_id"],
                "guest": guest,
                "guest_role": res.get("guest_role", ""),
                "title": title,
                "episode": ep,
                "timestamp": ts,
                "url": url,
                "snippet": text[:200] + ("..." if len(text) > 200 else "")
            })

        formatted_context = "\n---\n".join(context_lines)
        return formatted_context, citations
