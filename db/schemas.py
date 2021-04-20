from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class outPutShortURL(BaseModel):
    base_url : str
    short : str
    counter : int
    created : datetime

class createShortURL(BaseModel):
    base_url: str = Field(..., min_length=10, regex="^(https:\/\/[a-z,A-Z,0-9,\-,_,.]+\.[a-z,A-Z]{2,4}[А-Я,а-я,a-z,A-Z,0-9,\-,_,\/,=,?,&]*|[a-z,A-Z,0-9,\-,_,.]+\.[a-z,A-Z]{2,4}[А-Я,а-я,a-z,A-Z,0-9,\-,_,\/,=,?,&]*)$")

class updateShortURL(BaseModel):
    counter: int = Field(..., ge=0)