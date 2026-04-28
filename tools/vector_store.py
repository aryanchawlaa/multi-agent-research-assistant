import uuid
import os
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = "research_papers"
EMBEDDING_MODEL  = "all-MiniLM-L6-v2"
VECTOR_SIZE      = 384


class VectorMemory:
    """Qdrant-backed semantic memory — works with both local Docker and Qdrant Cloud."""

    def __init__(self):
        qdrant_url     = os.getenv("QDRANT_URL", "http://localhost:6333")
        qdrant_api_key = os.getenv("QDRANT_API_KEY", "").strip()

        # If an API key is set → Qdrant Cloud, else → local Docker
        if qdrant_api_key:
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            print(f"[VectorMemory] Connected to Qdrant Cloud: {qdrant_url}")
        else:
            self.client = QdrantClient(url=qdrant_url)
            print(f"[VectorMemory] Connected to local Qdrant: {qdrant_url}")

        self.encoder = SentenceTransformer(EMBEDDING_MODEL)
        self._ensure_collection()

    def _ensure_collection(self):
        existing = [c.name for c in self.client.get_collections().collections]
        if COLLECTION_NAME not in existing:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            print(f"[VectorMemory] Created collection: {COLLECTION_NAME}")

    def store(self, text: str, metadata: Dict[str, Any]) -> str:
        vector   = self.encoder.encode(text).tolist()
        point_id = str(uuid.uuid4())
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[PointStruct(
                id=point_id,
                vector=vector,
                payload={"text": text, **metadata},
            )],
        )
        return point_id

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        vector  = self.encoder.encode(query).tolist()
        results = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector,
            limit=top_k,
        )
        return [{"score": round(r.score, 4), **r.payload} for r in results]

    def clear(self):
        self.client.delete_collection(COLLECTION_NAME)
        self._ensure_collection()
