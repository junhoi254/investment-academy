from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

# ==================== User Schemas ====================

class UserCreate(BaseModel):
    phone: str
    password: str
    name: str
    
    @validator('phone')
    def phone_must_be_valid(cls, v):
        # 숫자와 -만 허용
        cleaned = v.replace("-", "")
        if not cleaned.isdigit():
            raise ValueError('전화번호는 숫자만 입력 가능합니다')
        if len(cleaned) not in [10, 11]:
            raise ValueError('올바른 전화번호 형식이 아닙니다')
        return v
    
    @validator('password')
    def password_must_be_valid(cls, v):
        if len(v) < 4:
            raise ValueError('비밀번호는 최소 4자 이상이어야 합니다')
        return v

class StaffCreate(BaseModel):
    phone: str
    password: str
    name: str

class UserResponse(BaseModel):
    id: int
    phone: str
    name: str
    role: str
    is_approved: bool
    expiry_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    new_password: str
    
    @validator('new_password')
    def password_must_be_valid(cls, v):
        if len(v) < 4:
            raise ValueError('비밀번호는 최소 4자 이상이어야 합니다')
        return v

class ExpiryUpdate(BaseModel):
    expiry_date: Optional[datetime]

# ==================== Room Schemas ====================

class RoomCreate(BaseModel):
    name: str
    room_type: str  # notice, stock, futures, crypto
    is_free: bool = False
    description: Optional[str] = None

class RoomResponse(BaseModel):
    id: int
    name: str
    room_type: str
    is_free: bool
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== Message Schemas ====================

class MessageCreate(BaseModel):
    content: str
    message_type: str = "text"

class MessageResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    content: str
    message_type: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== MT4 Schemas ====================

class MT4Position(BaseModel):
    symbol: str
    type: str  # BUY or SELL
    lots: float
    open_price: float
    sl: float  # stop loss
    tp: float  # take profit
    open_time: str
    
    class Config:
        from_attributes = True

# ==================== News Schemas ====================

class NewsResponse(BaseModel):
    id: int
    category: str
    title: str
    url: str
    source: Optional[str]
    published_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
