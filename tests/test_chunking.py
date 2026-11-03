from app.utils.chunking import split_text


def test_split_text():
    chunks = split_text("one two three four five six seven eight nine ten", chunk_size=20, overlap=5)
    assert chunks
    assert all(c.text for c in chunks)


def test_empty_text():
    assert split_text("   ") == []
