from app.workers.ingestion_worker import simple_chunk


def test_simple_chunk_splits_text():
    text = "abcdefghij"  # length 10
    chunks = simple_chunk(text, max_chars=4)

    # Expect: ["abcd", "efgh", "ij"]
    assert chunks == ["abcd", "efgh", "ij"]
