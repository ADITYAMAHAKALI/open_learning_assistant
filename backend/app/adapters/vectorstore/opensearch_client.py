# app/adapters/vectorstore/opensearch_client.py
from opensearchpy import OpenSearch
from app.core.config import settings

def get_opensearch_client() -> OpenSearch:
    return OpenSearch(
        hosts=[settings.OPENSEARCH_HOST],
        http_auth=(settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD),
        use_ssl=False,  # adjust if you enable SSL
        verify_certs=False,
    )
