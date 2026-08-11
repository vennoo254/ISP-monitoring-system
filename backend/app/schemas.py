from pydantic import BaseModel

class TargetCreate(BaseModel):
    name: str | None = None
    address: str

class TargetOut(BaseModel):
    id: int
    name: str | None = None
    address: str

    class Config:
        orm_mode = True
