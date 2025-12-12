import requests
from typing import List
from .config import settings


class EmbeddingService:
    def __init__(self):
        self.base_url = settings.OLLAMA_URL.rstrip("/")
        self.model = settings.APP_EMBEDDING_MODEL

    def embed(self, text: str) -> List[float]:
        url = f"{self.base_url}/api/embeddings"
        payload = {
            "model": self.model,
            "prompt": text,
        }
        try:
            resp = requests.post(url, json=payload, timeout=120)
        except Exception as e:
            raise RuntimeError(f"Error calling Ollama embeddings: {e}") from e

        if not resp.ok:
            # In chi tiết lỗi từ Ollama
            raise RuntimeError(
                f"Ollama embedding failed. "
                f"Status: {resp.status_code}, Body: {resp.text}"
            )

        data = resp.json()
        if "embedding" not in data:
            raise RuntimeError(f"Unexpected Ollama response: {data}")
        return data["embedding"]


embedding_service = EmbeddingService()