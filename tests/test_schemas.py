from smartdocs.schemas import AnswerResponse


def test_answer_schema_accepts_valid_response():
    result = AnswerResponse(answer="The document says so.", source_ids=["1"])
    assert result.answer
    assert result.source_ids == ["1"]


def test_answer_schema_defaults_to_no_sources():
    result = AnswerResponse(answer="Not found")
    assert result.source_ids == []
