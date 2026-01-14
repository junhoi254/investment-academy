from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base

class UserRole(str, enum.Enum):
    admin = "admin"
    staff = "staff"
    member = "member"

class RoomType(str, enum.Enum):
    notice = "notice"
    stock = "stock"
    futures = "futures"
    crypto = "crypto"

class MessageType(str, enum.Enum):
    text = "text"
    signal = "signal"
    image = "image"
    file = "file"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(50), nullable=False)
    role = Column(String(20), default="member")  # admin, staff, member
    is_approved = Column(Boolean, default=False)
    expiry_date = Column(DateTime, nullable=True)  # 회원 기간
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = relationship("Message", back_populates="user")

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    room_type = Column(String(20), nullable=False)  # notice, stock, futures, crypto
    is_free = Column(Boolean, default=False)  # 무료방 여부
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = relationship("Message", back_populates="room")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, signal, image, file, emoji
    file_url = Column(String(500), nullable=True)  # 파일/이미지 URL
    file_name = Column(String(255), nullable=True)  # 원본 파일명
    created_at = Column(DateTime, default=datetime.utcnow)
    
    room = relationship("Room", back_populates="messages")
    user = relationship("User", back_populates="messages")

class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(20), nullable=False)  # stock, futures, crypto
    title = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    source = Column(String(100), nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
