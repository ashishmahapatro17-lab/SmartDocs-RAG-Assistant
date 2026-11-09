from pydantic import BaseModel, Field

class AnswerResponse(BaseModel):
    answer: str = Field(description="Answer based only on the supplied document context.")
    source_ids: list[str] = Field(default_factory=list, description="IDs of context passages that support the answer.")
