from enum import Enum
from pydantic import BaseModel
from typing import Optional, Union, List

class Action(str, Enum):
    create = "create"
    read = "read"
    update = "update"
    delete = "delete"
    filters = "filter"
    sort = "sort"
    replicate = "replicate"

class Operator(str, Enum):
    eq = "="
    lt = "<"
    lte = "<="
    gt = ">"
    gte = ">="
    neq = "!="
    like = "LIKE"

class DBCommand(BaseModel):
    action: Action
    row: Optional[Union[int, List]] = None
    field: Optional[str] = None
    value: Optional[Union[str, float]] = None
    operator: Optional[Operator] = None


