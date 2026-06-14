from pydantic import BaseModel


class KnowledgeComponentItem(BaseModel):
    code: str
    name: str
    description: str
    exerciseCount: int


class KnowledgeComponentDetail(KnowledgeComponentItem):
    exerciseIds: list[str]


class KnowledgeComponentListResponse(BaseModel):
    items: list[KnowledgeComponentItem]
    total: int
