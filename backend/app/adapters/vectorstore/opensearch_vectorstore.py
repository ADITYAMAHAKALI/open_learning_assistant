# app/adapters/vectorstore/opensearch_vectorstore.py
from typing import List, Dict, Any
from opensearchpy import OpenSearch


class OpenSearchVectorStore:
    def __init__(self, client: OpenSearch, index_name: str) -> None:
        self.client = client
        self.index_name = index_name
        self._ensure_index()

    def _ensure_index(self) -> None:
        if self.client.indices.exists(self.index_name):
            return

        body = {
            "settings": {
                "index": {
                    "knn": True,
                    "knn.algo_param.ef_search": 100,
                }
            },
            "mappings": {
                "properties": {
                    "material_id": {"type": "integer"},
                    "topic_id": {"type": "integer"},
                    "chunk_id": {"type": "keyword"},
                    "content": {"type": "text"},
                    "page": {"type": "integer"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": 1536,  # set to your embedding size
                    },
                }
            },
        }
        self.client.indices.create(index=self.index_name, body=body)

    def index_chunk(
        self,
        material_id: int,
        topic_id: int | None,
        chunk_id: str,
        content: str,
        embedding: list[float],
        page: int | None = None,
    ) -> None:
        doc = {
            "material_id": material_id,
            "topic_id": topic_id,
            "chunk_id": chunk_id,
            "content": content,
            "page": page,
            "embedding": embedding,
        }
        self.client.index(index=self.index_name, id=chunk_id, body=doc)

    def search(
        self,
        query: str,
        material_id: int,
        topic_id: int | None,
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Very simple BM25-style text search over `content`
        filtered by material_id (and optionally topic_id).

        This avoids the NotImplementedError and gives you something usable
        until you wire up real vector embeddings.
        """
        must_clauses: list[Dict[str, Any]] = [
            {"match": {"content": query}},
        ]

        filter_clauses: list[Dict[str, Any]] = [
            {"term": {"material_id": material_id}},
        ]

        if topic_id is not None:
            filter_clauses.append({"term": {"topic_id": topic_id}})

        body = {
            "size": k,
            "query": {
                "bool": {
                    "must": must_clauses,
                    "filter": filter_clauses,
                }
            },
        }

        resp = self.client.search(index=self.index_name, body=body)
        hits = resp.get("hits", {}).get("hits", [])
        results: List[Dict[str, Any]] = []

        for h in hits:
            source = h.get("_source", {}) or {}
            # propagate score & id just in case you want it later
            source["_score"] = h.get("_score")
            source["_id"] = h.get("_id")
            results.append(source)

        return results
