from pydantic import BaseModel, Field
from typing import Optional, Literal, List


class Message(BaseModel):
    content: str = Field(default='')


class Query(BaseModel):
    message: Message
    userId: str


class WecomAppClient(BaseModel):
    company_id: Optional[str] = Field(None, max_length=100, description="企业ID")
    client_app_token: Optional[str] = Field(None, max_length=100, description="客户端token")
    client_aes_key: Optional[str] = Field(None, max_length=100, description="客户端加解密key")


class WecomCustomerMessage(BaseModel):
    msgid: str
    open_kfid: str
    external_userid: str
    send_time: int
    origin: int
    msgtype: str
    text: Optional[dict] = Field({})


class WecomCustomerData(BaseModel):
    errcode: int = 0
    errmsg: str = "ok"
    next_cursor: str = ""
    has_more: int = 0
    msg_list: list[WecomCustomerMessage] = []


class CacheSignal(BaseModel):
    userId: int


class Conversation(BaseModel):
    Q2A: list = Field(default=[])
    limit: int = 5


class QA(BaseModel):
    Q: str = Field(default='')
    A: str = Field(default='')
