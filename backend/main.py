from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
import bcrypt
from pydantic import BaseModel
import json
import os
import uuid
from pathlib import Path

from database import get_db, engine
import models
import schemas

# 업로드 폴더 생성
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="투자학당 - Investment Academy")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 업로드된 파일 서빙
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# JWT 설정
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# WebSocket 연결 관리자
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
        self.user_connections: dict = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_id: int):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
        self.user_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, room_id: str, user_id: int):
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def send_message(self, message: dict, room_id: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()

# 유틸리티 함수
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def format_phone_number(phone: str) -> str:
    phone = phone.replace("-", "")
    if len(phone) == 11:
        return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
    elif len(phone) == 10:
        return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
    return phone

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_approved:
        raise HTTPException(status_code=403, detail="관리자 승인 대기 중입니다")
    
    if user.role == "member" and user.expiry_date:
        if user.expiry_date < datetime.utcnow():
            raise HTTPException(status_code=403, detail="회원 기간이 만료되었습니다")
    
    return user

async def get_current_user_optional(token: Optional[str] = None, db: Session = Depends(get_db)):
    """선택적 인증 - 토큰이 없어도 None 반환"""
    if not token:
        return None
    try:
        return await get_current_user(token, db)
    except:
        return None

async def get_admin_user(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
    return current_user

# ==================== 인증 API ====================

@app.post("/api/register", response_model=schemas.UserResponse)
async def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    phone = format_phone_number(user_data.phone)
    existing_user = db.query(models.User).filter(models.User.phone == phone).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 등록된 전화번호입니다")
    
    hashed_password = get_password_hash(user_data.password)
    new_user = models.User(
        phone=phone,
        password=hashed_password,
        name=user_data.name,
        role="member",
        is_approved=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    phone = format_phone_number(form_data.username)
    user = db.query(models.User).filter(models.User.phone == phone).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="전화번호 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_approved:
        raise HTTPException(status_code=403, detail="관리자 승인 대기 중입니다")
    
    if user.role == "member" and user.expiry_date:
        if user.expiry_date < datetime.utcnow():
            raise HTTPException(status_code=403, detail="회원 기간이 만료되었습니다")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "phone": user.phone,
            "name": user.name,
            "role": user.role
        }
    }

@app.get("/api/me", response_model=schemas.UserResponse)
async def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# 추가: 프론트엔드 호환성을 위한 엔드포인트
@app.get("/api/users/me", response_model=schemas.UserResponse)
async def get_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# ==================== 채팅방 API ====================

@app.get("/api/rooms/free", response_model=List[schemas.RoomResponse])
async def get_free_rooms(db: Session = Depends(get_db)):
    rooms = db.query(models.Room).filter(models.Room.is_free == True).all()
    return rooms

@app.get("/api/rooms", response_model=List[schemas.RoomResponse])
async def get_all_rooms(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """전체 채팅방 목록 (로그인 필요)"""
    rooms = db.query(models.Room).all()
    return rooms

@app.get("/api/rooms/{room_id}", response_model=schemas.RoomResponse)
async def get_room(
    room_id: int,
    db: Session = Depends(get_db)
):
    """특정 채팅방 정보"""
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다")
    return room

@app.post("/api/rooms", response_model=schemas.RoomResponse)
async def create_room(
    room_data: schemas.RoomCreate,
    admin: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    new_room = models.Room(**room_data.dict())
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room

# ==================== 메시지 API ====================

@app.get("/api/messages/{room_id}", response_model=List[schemas.MessageResponse])
async def get_messages(
    room_id: int,
    db: Session = Depends(get_db)
):
    """채팅방 메시지 조회 (로그인 불필요)"""
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다")
    
    messages = db.query(models.Message).filter(
        models.Message.room_id == room_id
    ).order_by(models.Message.created_at.asc()).limit(100).all()
    
    return messages

@app.post("/api/messages")
async def create_message(
    message_data: schemas.MessageCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """메시지 전송"""
    room = db.query(models.Room).filter(models.Room.id == message_data.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다")
    
    # 무료방인 경우 관리자만 전송 가능
    if room.is_free:
        if current_user.role not in ["admin", "sub_admin"]:
            raise HTTPException(status_code=403, detail="관리자와 서브관리자만 메시지를 보낼 수 있습니다")
    
    # 메시지 저장
    message = models.Message(
        room_id=message_data.room_id,
        user_id=current_user.id,
        content=message_data.content,
        message_type=message_data.message_type or "text"
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # WebSocket으로 전송
    await manager.send_message({
        "id": message.id,
        "room_id": message.room_id,
        "user_id": current_user.id,
        "user_name": current_user.name,
        "user_role": current_user.role,
        "content": message.content,
        "message_type": message.message_type,
        "created_at": message.created_at.isoformat()
    }, str(message_data.room_id))
    
    return {"message": "전송되었습니다", "id": message.id}

# ==================== WebSocket ====================

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    room_id: int,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """WebSocket 연결 (로그인 선택사항)"""
    user = None
    user_id = None
    
    # 토큰이 있으면 사용자 인증
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            user = db.query(models.User).filter(models.User.id == user_id).first()
        except:
            pass
    
    # 채팅방 확인
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        await websocket.close(code=1008)
        return
    
    await manager.connect(websocket, str(room_id), user_id or 0)
    
    # 접속 알림
    if user:
        await manager.send_message({
            "type": "system",
            "message": f"{user.name}님이 입장하셨습니다.",
            "timestamp": datetime.utcnow().isoformat()
        }, str(room_id))
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, str(room_id), user_id or 0)
        if user:
            await manager.send_message({
                "type": "system",
                "message": f"{user.name}님이 퇴장하셨습니다.",
                "timestamp": datetime.utcnow().isoformat()
            }, str(room_id))

# ==================== 초기 데이터 생성 ====================

@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    
    # 관리자 계정 생성
    admin = db.query(models.User).filter(models.User.phone == "010-0000-0000").first()
    if not admin:
        admin = models.User(
            phone="010-0000-0000",
            password=get_password_hash("admin1234"),
            name="일타훈장님",
            role="admin",
            is_approved=True
        )
        db.add(admin)
        db.commit()
    
    # 기본 채팅방 생성
    rooms = db.query(models.Room).all()
    if not rooms:
        default_rooms = [
            models.Room(name="무료 공지방", room_type="notice", is_free=True, description="누구나 볼 수 있는 공지방"),
            models.Room(name="주식 리딩방", room_type="stock", is_free=False, description="주식 매매 시그널"),
            models.Room(name="해외선물 리딩방", room_type="futures", is_free=False, description="해외선물 매매 시그널"),
            models.Room(name="코인선물 리딩방", room_type="crypto", is_free=False, description="코인선물 매매 시그널"),
        ]
        db.add_all(default_rooms)
        db.commit()
    
    print("✅ 서버 시작 완료!")
    print("📌 관리자 계정: 010-0000-0000 / admin1234")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)