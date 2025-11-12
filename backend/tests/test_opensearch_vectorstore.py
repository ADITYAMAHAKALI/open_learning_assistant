from app.adapters.vectorstore.opensearch_vectorstore import OpenSearchVectorStore


class FakeIndicesClient:
    def __init__(self):
        self.created = {}
        self.exists_called_with = []

    def exists(self, index):
        self.exists_called_with.append(index)
        return index in self.created

    def create(self, index, body):
        self.created[index] = body


class FakeOpenSearch:
    def __init__(self):
        self.indices = FakeIndicesClient()
        self.indexed_docs = {}

    def index(self, index, id, body):
        self.indexed_docs[id] = {"index": index, "body": body}

    def search(self, index, body):
        hits = []
        for doc_id, meta in self.indexed_docs.items():
            source = meta["body"]
            hits.append(
                {
                    "_id": doc_id,
                    "_score": 1.0,
                    "_source": source,
                }
            )
        return {"hits": {"hits": hits}}


def test_opensearch_vectorstore_creates_index_and_searches():
    client = FakeOpenSearch()
    store = OpenSearchVectorStore(client=client, index_name="test_index")

    assert "test_index" in client.indices.created

    store.index_chunk(
        material_id=1,
        topic_id=None,
        chunk_id="chunk1",
        content="This is about linear algebra",
        embedding=[0.1, 0.2, 0.3],
        page=1,
    )

    results = store.search(
        query="linear algebra",
        material_id=1,
        topic_id=None,
        k=5,
    )
    assert len(results) == 1
    assert results[0]["content"] == "This is about linear algebra"
    assert results[0]["chunk_id"] == "chunk1"
