from pydantic import BaseModel


class EmailMessageResponse(BaseModel):
    message: str


class ReturnStatusEmailRequest(BaseModel):
    status: str
    message: str | None = None