import pytest
from smartdocs.chunking import split_text


def test_empty_text_returns_no_chunks():
    assert split_text("   ") == []


def test_long_text_is_split():
    text = "A" * 4500
    chunks = split_text(text, chunk_size=1000, overlap=100)
    assert len(chunks) > 1
    assert all(chunks)


def test_invalid_overlap_is_rejected():
    with pytest.raises(ValueError):
        split_text("hello", chunk_size=10, overlap=10)
