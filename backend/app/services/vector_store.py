import os
import json
import logging
import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import joblib

logger = logging.getLogger("app.services.vector_store")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
KB_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "knowledge_base"))
DOCS_PATH = os.path.join(KB_DIR, "career_documents.json")
INDEX_PATH = os.path.join(KB_DIR, "faiss_index.bin")
CHUNKS_PATH = os.path.join(KB_DIR, "chunks_metadata.json")
PIPELINE_PATH = os.path.join(KB_DIR, "embedding_pipeline.joblib")

VECTOR_DIMENSION = 128


class CareerVectorStore:
    """
    Lightweight, high-performance local vector store using FAISS (IndexFlatIP)
    and normalized dense continuous embeddings.
    Provides fast, deterministic semantic retrieval for the Career RAG Assistant.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CareerVectorStore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.index: Optional[faiss.IndexFlatIP] = None
        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.svd: Optional[TruncatedSVD] = None
        self.load_or_build()
        self._initialized = True

    def _chunk_document(self, doc: Dict[str, Any], max_words: int = 120, overlap: int = 25) -> List[Dict[str, Any]]:
        """Splits document content into overlapping semantic chunks."""
        words = doc["content"].split()
        if len(words) <= max_words:
            return [{
                "chunk_id": f"{doc['id']}_c0",
                "doc_id": doc["id"],
                "title": doc["title"],
                "category": doc["category"],
                "tags": doc.get("tags", []),
                "text": doc["content"],
                "word_count": len(words)
            }]

        chunks = []
        start = 0
        chunk_idx = 0
        while start < len(words):
            end = min(start + max_words, len(words))
            chunk_text = " ".join(words[start:end])
            chunks.append({
                "chunk_id": f"{doc['id']}_c{chunk_idx}",
                "doc_id": doc["id"],
                "title": doc["title"],
                "category": doc["category"],
                "tags": doc.get("tags", []),
                "text": chunk_text,
                "word_count": end - start
            })
            if end == len(words):
                break
            start += max_words - overlap
            chunk_idx += 1

        return chunks

    def build_index_from_documents(self):
        """Processes knowledge base JSON documents, creates embeddings, and builds FAISS index."""
        logger.info(f"Building career knowledge base vector index from {DOCS_PATH}...")
        if not os.path.exists(DOCS_PATH):
            raise FileNotFoundError(f"Career documents file not found at {DOCS_PATH}")

        with open(DOCS_PATH, "r", encoding="utf-8") as f:
            raw_docs = json.load(f)

        all_chunks = []
        for doc in raw_docs:
            all_chunks.extend(self._chunk_document(doc))

        self.chunks = all_chunks
        texts_for_embedding = [
            f"{c['title']}. Category: {c['category']}. Tags: {' '.join(c['tags'])}. Content: {c['text']}"
            for c in self.chunks
        ]

        # Fit TF-IDF with word and character n-grams to capture technical jargon
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_features=2500,
            token_pattern=r"(?u)\b\w[\w\.\+#-]+\b"
        )
        tfidf_matrix = self.vectorizer.fit_transform(texts_for_embedding)

        # Reduce dimensionality to dense continuous semantic vectors
        n_components = min(VECTOR_DIMENSION, tfidf_matrix.shape[1] - 1, tfidf_matrix.shape[0] - 1)
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        dense_vectors = self.svd.fit_transform(tfidf_matrix)

        # If dimension < VECTOR_DIMENSION, zero-pad to match fixed VECTOR_DIMENSION
        if dense_vectors.shape[1] < VECTOR_DIMENSION:
            padding = np.zeros((dense_vectors.shape[0], VECTOR_DIMENSION - dense_vectors.shape[1]), dtype=np.float32)
            dense_vectors = np.hstack([dense_vectors, padding])

        # L2-normalize vectors so Inner Product equals Cosine Similarity
        dense_vectors = dense_vectors.astype(np.float32)
        faiss.normalize_L2(dense_vectors)

        # Construct FAISS IndexFlatIP (Cosine Similarity)
        self.index = faiss.IndexFlatIP(VECTOR_DIMENSION)
        self.index.add(dense_vectors)

        # Persist index, metadata, and pipeline artifacts
        os.makedirs(KB_DIR, exist_ok=True)
        faiss.write_index(self.index, INDEX_PATH)
        with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, indent=2)

        joblib.dump({"vectorizer": self.vectorizer, "svd": self.svd}, PIPELINE_PATH)
        logger.info(f"Successfully indexed {len(self.chunks)} chunks into FAISS (dim={VECTOR_DIMENSION}).")

    def load_or_build(self):
        """Loads cached FAISS index & metadata, or triggers build if absent."""
        if (
            os.path.exists(INDEX_PATH)
            and os.path.exists(CHUNKS_PATH)
            and os.path.exists(PIPELINE_PATH)
        ):
            try:
                self.index = faiss.read_index(INDEX_PATH)
                with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
                pipeline = joblib.load(PIPELINE_PATH)
                self.vectorizer = pipeline["vectorizer"]
                self.svd = pipeline["svd"]
                logger.info(f"Loaded existing FAISS index with {len(self.chunks)} chunks.")
                return
            except Exception as e:
                logger.warning(f"Error loading cached FAISS index: {e}. Rebuilding index...")

        self.build_index_from_documents()

    def _embed_query(self, query: str) -> np.ndarray:
        """Transforms a user text query into an L2-normalized dense vector."""
        if not self.vectorizer or not self.svd:
            self.load_or_build()

        tfidf = self.vectorizer.transform([query])
        dense = self.svd.transform(tfidf)

        if dense.shape[1] < VECTOR_DIMENSION:
            padding = np.zeros((1, VECTOR_DIMENSION - dense.shape[1]), dtype=np.float32)
            dense = np.hstack([dense, padding])

        dense = dense.astype(np.float32)
        faiss.normalize_L2(dense)
        return dense

    def search(
        self,
        query: str,
        top_k: int = 4,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top-k relevant knowledge base chunks matching the query.
        Returns chunk content, title, category, tags, and similarity score.
        """
        if not self.index or len(self.chunks) == 0:
            self.load_or_build()

        query_vec = self._embed_query(query)
        # Search extra candidates if category filtering is requested
        search_k = min(top_k * 3 if category else top_k, len(self.chunks))

        scores, indices = self.index.search(query_vec, search_k)
        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            chunk = self.chunks[idx]
            if category and chunk["category"].lower() != category.lower():
                continue

            # Normalized cosine similarity score
            sim_score = max(0.0, min(1.0, float(score)))
            results.append({
                "chunk_id": chunk["chunk_id"],
                "doc_id": chunk["doc_id"],
                "title": chunk["title"],
                "category": chunk["category"],
                "tags": chunk.get("tags", []),
                "content": chunk["text"],
                "similarity_score": round(sim_score, 4)
            })

            if len(results) >= top_k:
                break

        return results


# Global singleton instance
vector_store = CareerVectorStore()
