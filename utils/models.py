from enum import Enum
from pydantic import BaseModel
from typing import Optional, Union, List, Literal

class Action(str, Enum):
    create = "create"
    read = "read"
    update = "update"
    delete = "delete"
    filters = "filter"
    sort = "sort"
    replicate = "replicate"
    stats = "stats"

class Operator(str, Enum):
    eq = "="
    lt = "<"
    lte = "<="
    gt = ">"
    gte = ">="
    neq = "!="
    like = "LIKE"

class Product(BaseModel):
	name: str
	category: Optional[Literal["Furniture", "Electronics", "Clothing", "Books", "Toys", "Kitchen"]]
	color: str
	quantity: int
	price: float
	
class DBCommand(BaseModel):
    action: Action
    row: Optional[Union[int, List]] = None
    field: Optional[str] = None
    value: Optional[Union[str, float, Product]] = None
    operator: Optional[Operator] = None
    message: Optional[str] = "I just complted you will. Anything else."

class Status(BaseModel):
	status: Literal["clear", "unclear"]
	#message: str
