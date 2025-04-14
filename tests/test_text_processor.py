import pytest
from legal_summarizer.utils.text_processors import TextProcessor

@pytest.fixture
def text_processor():
    return TextProcessor()

def test_clean_text(text_processor):
    text = "This is a test.\n\nMultiple lines.\tTabs and spaces."
    cleaned = text_processor.clean_text(text)
    assert "\n\n" not in cleaned
    assert "\t" not in cleaned

def test_smart_chunk_text(text_processor):
    text = "This is a sentence. This is another sentence. And one more."
    chunks = text_processor.smart_chunk_text(text, max_length=20)
    assert len(chunks) > 1
    assert all(len(chunk) <= 20 for chunk in chunks)

def test_extract_key_phrases(text_processor):
    text = "The court ruled in favor of the plaintiff. The defendant appealed the decision."
    phrases = text_processor.extract_key_phrases(text, top_n=2)
    assert len(phrases) == 2
    assert all(isinstance(phrase, str) for phrase in phrases)

def test_normalize_dates(text_processor):
    dates = [
        "January 1, 2023",
        "01/01/2023",
        "2023-01-01"
    ]
    normalized = [text_processor.normalize_dates(date) for date in dates]
    assert all(norm == "2023-01-01" for norm in normalized)

def test_extract_entities(text_processor):
    text = "The case was filed on January 1, 2023 by John Doe v. Jane Smith."
    entities = text_processor.extract_entities(text)
    assert "date" in entities
    assert "person" in entities
    assert len(entities["date"]) > 0
    assert len(entities["person"]) > 0 