from pydantic import BaseModel, Field
from typing import Optional,List
from datetime import datetime

class UserInsert(BaseModel):
    username: str
    password: str=Field(min_length=6,max_length=30)

    class Config:
        from_attributes=True

class RoleInsert(BaseModel):
    name: str
    created_at: Optional[str] = None

    class Config:
        from_attributes=True

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    updated_at: datetime
    # role: str

    class Config:
        from_attributes=True

class RoleResponse(BaseModel):
    name: str
    created_at: str

    class Config:
        from_attributes=True

class UpdateUser(BaseModel):
    username: Optional[str]
    password: Optional[str]
    roles: Optional[List[str]]

    class Config:
        from_attributes=True