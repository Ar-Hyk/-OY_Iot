from decimal import Decimal
from typing import Union
from pydantic import BaseModel, Field


# 数据结构
class Data(BaseModel):
    t: int = Field(None, ge=10e9, le=10e10 - 1)
    key: str = ''
    value: Decimal = Field(None, max_digits=10, decimal_places=2)
    unit: Union[str, None]

    class Config:
        orm_mode = True
