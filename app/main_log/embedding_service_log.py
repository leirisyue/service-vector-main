import requests
from typing import List
from .config import settings
from .logger import setup_logger

logger = setup_logger(__name__)


class EmbeddingService:
    def __init__(self):
        self.base_url = settings.OLLAMA_URL.rstrip("/")
        self.model = settings.APP_EMBEDDING_MODEL
        logger.info(f"EmbeddingService initialized with base_url={self.base_url}, model={self.model}")

    def embed(self, text: str) -> List[float]:
        url = f"{self.base_url}/api/embeddings"
        payload = {
            "model": self.model,
            "prompt": text,
        }
        logger.info(f"Calling Ollama embeddings at {url}")

        try:
            resp = requests.post(url, json=payload, timeout=120)
        except Exception as e:
            logger.exception("Error calling Ollama embeddings")
            raise RuntimeError(f"Error calling Ollama embeddings: {e}") from e

        if not resp.ok:
            logger.error(
                "Ollama embedding failed. Status=%s, Body=%s",
                resp.status_code,
                resp.text,
            )
            raise RuntimeError(
                f"Ollama embedding failed. "
                f"Status: {resp.status_code}, Body: {resp.text}"
            )

        data = resp.json()
        if "embedding" not in data:
            logger.error("Unexpected Ollama response: %s", data)
            raise RuntimeError(f"Unexpected Ollama response: {data}")

        logger.info("Embedding generated successfully, length=%d", len(data["embedding"]))
        return data["embedding"]


embedding_service = EmbeddingService()