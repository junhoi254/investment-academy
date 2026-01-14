from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    phone: str
    name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_approved: bool
    expiry_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class StaffCreate(BaseModel):
    phone: str
    name: str
    password: str

class PasswordChange(BaseModel):
    new_password: str

class ExpiryUpdate(BaseModel):
    expiry_date: Optional[datetime]

# Room Schemas
class RoomCreate(BaseModel):
    name: str
    room_type: str
    is_free: bool = False
    description: Optional[str] = None
    price: Optional[int] = None

class RoomResponse(BaseModel):
    id: int
    name: str
    room_type: str
    is_free: bool
    description: Optional[str]
    price: Optional[int]
    online_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

# Message Schemas
class MessageCreate(BaseModel):
    room_id: int
    content: str
    message_type: str = "text"

class MessageResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    user_name: Optional[str]
    user_role: Optional[str]
    content: str
    message_type: str
    created_at: datetime

    class Config:
        from_attributes = True

# MT4 Schema
class MT4Position(BaseModel):
    symbol: str
    type: str  # BUY or SELL
    lots: float
    open_price: float
    sl: float
    tp: float
    open_time: str