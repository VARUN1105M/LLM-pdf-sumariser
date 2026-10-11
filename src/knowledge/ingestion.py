import os
import re
import json
import logging
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.config import settings

logger = logging.getLogger("lenny_assistant.knowledge")

class TranscriptChunk:
    def __init__(
        self,
        chunk_id: str,
        transcript_id: str,
        title: str,
        guest: str,
        guest_role: str,
        url: str,
        episode_number: Optional[int],
        text: str,
        timestamp_hint: str = "",
        topics: Optional[List[str]] = None
    ):
        self.chunk_id = chunk_id
        self.transcript_id = transcript_id
        self.title = title
        self.guest = guest
        self.guest_role = guest_role
        self.url = url
        self.episode_number = episode_number
        self.text = text
        self.timestamp_hint = timestamp_hint
        self.topics = topics or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "transcript_id": self.transcript_id,
            "title": self.title,
            "guest": self.guest,
            "guest_role": self.guest_role,
            "url": self.url,
            "episode_number": self.episode_number,
            "text": self.text,
            "timestamp_hint": self.timestamp_hint,
            "topics": self.topics
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TranscriptChunk":
        return cls(
            chunk_id=data["chunk_id"],
            transcript_id=data["transcript_id"],
            title=data["title"],
            guest=data["guest"],
            guest_role=data.get("guest_role", ""),
            url=data.get("url", ""),
            episode_number=data.get("episode_number"),
            text=data["text"],
            timestamp_hint=data.get("timestamp_hint", ""),
            topics=data.get("topics", [])
        )

class KnowledgeBase:
    def __init__(self, transcripts_dir: Optional[Path] = None, cache_dir: Optional[Path] = None):
        self.transcripts_dir = transcripts_dir or settings.TRANSCRIPTS_DIR
        self.cache_dir = cache_dir or settings.EMBEDDINGS_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.chunks: List[TranscriptChunk] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.is_indexed: bool = False

    def chunk_text(self, text: str, chunk_size: int = 600, overlap: int = 100) -> List[tuple[str, str]]:
        """
        Splits text into chunks while preserving timestamp markers e.g. [00:02:10].
        Returns list of (chunk_text, first_timestamp_found).
        """
        # Split primarily by dialogue paragraphs / speaker turns
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        current_chunk = []
        current_length = 0
        current_timestamp = ""

        timestamp_regex = re.compile(r"\[\d{2}:\d{2}(?::\d{2})?\]")

        for p in paragraphs:
            p_len = len(p)
            match = timestamp_regex.search(p)
            if match and not current_timestamp:
                current_timestamp = match.group(0)

            if current_length + p_len > chunk_size and current_chunk:
                combined_text = "\n\n".join(current_chunk)
                chunks.append((combined_text, current_timestamp or "[00:00:00]"))
                
                # Keep some overlap if multiple paragraphs
                if len(current_chunk) > 1:
                    current_chunk = [current_chunk[-1], p]
                    current_length = len(current_chunk[0]) + p_len
                else:
                    current_chunk = [p]
                    current_length = p_len
                current_timestamp = match.group(0) if match else ""
            else:
                current_chunk.append(p)
                current_length += p_len

        if current_chunk:
            combined_text = "\n\n".join(current_chunk)
            chunks.append((combined_text, current_timestamp or "[00:00:00]"))

        return chunks

    def build_index(self, force_reload: bool = False) -> int:
        """
        Ingests all transcript files, chunks them, and builds vector index.
        """
        index_file = self.cache_dir / "index.pkl"
        if not force_reload and index_file.exists():
            try:
                with open(index_file, "rb") as f:
                    data = pickle.load(f)
                    self.chunks = [TranscriptChunk.from_dict(c) for c in data["chunks"]]
                    self.vectorizer = data["vectorizer"]
                    self.tfidf_matrix = data["tfidf_matrix"]
                    self.is_indexed = True
                    logger.info(f"Loaded existing index with {len(self.chunks)} chunks from {index_file}")
                    return len(self.chunks)
            except Exception as e:
                logger.warning(f"Failed to load cached index, rebuilding: {e}")

        self.chunks = []
        if not self.transcripts_dir.exists():
            logger.warning(f"Transcripts directory {self.transcripts_dir} does not exist.")
            return 0

        # Scan for .json files
        for file_path in self.transcripts_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                t_id = data.get("id", file_path.stem)
                title = data.get("title", "Untitled Episode")
                guest = data.get("guest", "Unknown Guest")
                guest_role = data.get("guest_role", "")
                url = data.get("url", "https://www.lennyspodcast.com")
                ep_num = data.get("episode_number")
                topics = data.get("topics", [])
                content = data.get("content", "")

                text_chunks = self.chunk_text(content, chunk_size=settings.CHUNK_SIZE, overlap=settings.CHUNK_OVERLAP)
                for idx, (chunk_str, ts) in enumerate(text_chunks):
                    chunk_obj = TranscriptChunk(
                        chunk_id=f"{t_id}_chk_{idx}",
                        transcript_id=t_id,
                        title=title,
                        guest=guest,
                        guest_role=guest_role,
                        url=url,
                        episode_number=ep_num,
                        text=chunk_str,
                        timestamp_hint=ts,
                        topics=topics
                    )
                    self.chunks.append(chunk_obj)
            except Exception as e:
                logger.error(f"Error parsing transcript {file_path}: {e}")

        if not self.chunks:
            logger.warning("No transcript chunks extracted.")
            return 0

        # Build TF-IDF vector matrix
        corpus = [c.text for c in self.chunks]
        self.vectorizer = TfidfVectorizer(
            stop_words="english", 
            ngram_range=(1, 2), 
            max_features=10000
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        self.is_indexed = True

        # Cache to disk
        try:
            with open(index_file, "wb") as f:
                pickle.dump({
                    "chunks": [c.to_dict() for c in self.chunks],
                    "vectorizer": self.vectorizer,
                    "tfidf_matrix": self.tfidf_matrix
                }, f)
            logger.info(f"Indexed and saved {len(self.chunks)} chunks to {index_file}")
        except Exception as e:
            logger.error(f"Failed to cache index to {index_file}: {e}")

        return len(self.chunks)

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Retrieves top_k relevant chunks with similarity scores.
        """
        if not self.is_indexed or not self.chunks or self.vectorizer is None:
            self.build_index()

        if not self.chunks or self.vectorizer is None or self.tfidf_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Get top indices
        top_indices = similarities.argsort()[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            # Only consider relevant chunks if score > 0.05
            if score > 0.02:
                chunk = self.chunks[idx]
                results.append({
                    "chunk_id": chunk.chunk_id,
                    "transcript_id": chunk.transcript_id,
                    "title": chunk.title,
                    "guest": chunk.guest,
                    "guest_role": chunk.guest_role,
                    "url": chunk.url,
                    "episode_number": chunk.episode_number,
                    "timestamp_hint": chunk.timestamp_hint,
                    "score": round(score, 4),
                    "text": chunk.text
                })

        return results
