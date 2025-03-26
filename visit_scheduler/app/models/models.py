from pydantic import BaseModel

class InsertModel(BaseModel): # TODO change to real model, this is just a placeholder
    name: str
    age: int


class SearchModel(BaseModel): # TODO change to real model, this is just a placeholder
    query: str
    page: int = 1
    per_page: int = 10