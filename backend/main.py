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
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 업로드된 파일 서빙
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# JWT 설정
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24시간

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# WebSocket 연결 관리자
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}  # room_id: [websocket connections]
        self.user_connections: dict = {}    # user_id: websocket

    async def connect(self, websocket: WebSocket, room_id: str, user_id: int):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
        self.user_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, room_id: str, user_id: int):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def send_message(self, message: dict, room_id: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_json(message)

    async def broadcast(self, message: dict):
        for connections in self.active_connections.values():
            for connection in connections:
                await connection.send_json(message)

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
    """전화번호 포맷팅 (자동으로 - 추가)"""
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
    
    # 계정 승인 확인
    if not user.is_approved:
        raise HTTPException(status_code=403, detail="관리자 승인 대기 중입니다")
    
    # 회원 기간 확인
    if user.role == "member" and user.expiry_date:
        if user.expiry_date < datetime.utcnow():
            raise HTTPException(status_code=403, detail="회원 기간이 만료되었습니다")
    
    return user

async def get_admin_user(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
    return current_user

# ==================== 인증 API ====================

@app.post("/api/register", response_model=schemas.UserResponse)
async def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """회원가입"""
    # 전화번호 포맷팅
    phone = format_phone_number(user_data.phone)
    
    # 중복 확인
    existing_user = db.query(models.User).filter(models.User.phone == phone).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 등록된 전화번호입니다")
    
    # 사용자 생성
    hashed_password = get_password_hash(user_data.password)
    new_user = models.User(
        phone=phone,
        password=hashed_password,
        name=user_data.name,
        role="member",
        is_approved=False  # 관리자 승인 필요
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post("/api/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """로그인"""
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
    
    # 회원 기간 확인
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
    """현재 사용자 정보"""
    return current_user

# ==================== 관리자 API ====================

@app.get("/api/admin/users", response_model=List[schemas.UserResponse])
async def get_all_users(
    admin: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """모든 사용자 조회"""
    users = db.query(models.User).all()
    return users

@app.put("/api/admin/users/{user_id}/approve")
async def approve_user(
    user_id: int,
    admin: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """회원 승인"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    user.is_approved = True
    db.commit()
    
    return {"message": "승인되었습니다"}

@app.put("/api/admin/users/{user_id}/password")
async def change_user_password(
    user_id: int,
    password_data: schemas.PasswordChange,
    admin: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """회원/직원 비밀번호 변경"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    user.password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "비밀번호가 변경되었습니다"}

@app.put("/api/admin/users/{user_id}/expiry")
async def update_user_expiry(
    user_id: int,
    expiry_data: schemas.ExpiryUpdate,
    admin: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """회원 기간 설정"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    user.expiry_date = expiry_data.expiry_date
    db.commit()
    
    return {"message": "회원 기간이 설정되었습니다"}

@app.post("/api/admin/staff", response_model=schemas.UserResponse)
async def create_staff(
    staff_data: schemas.StaffCreate,
    admin: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """직원 생성"""
    phone = format_phone_number(staff_data.phone)
    
    existing_user = db.query(models.User).filter(models.User.phone == phone).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 등록된 전화번호입니다")
    
    hashed_password = get_password_hash(staff_data.password)
    new_staff = models.User(
        phone=phone,
        password=hashed_password,
        name=staff_data.name,
        role="staff",
        is_approved=True
    )
    
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    
    return new_staff

@app.delete("/api/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """사용자 삭제"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    if user.role == "admin":
        raise HTTPException(status_code=403, detail="관리자는 삭제할 수 없습니다")
    
    db.delete(user)
    db.commit()
    
    return {"message": "사용자가 삭제되었습니다"}

# ==================== 채팅방 API ====================

@app.get("/api/rooms/free", response_model=List[schemas.RoomResponse])
async def get_free_rooms(db: Session = Depends(get_db)):
    """무료 채팅방 목록 (로그인 불필요)"""
    rooms = db.query(models.Room).filter(models.Room.is_free == True).all()
    return rooms

@app.get("/api/rooms/paid", response_model=List[schemas.RoomResponse])
async def get_paid_rooms(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """유료 채팅방 목록 (로그인 필요)"""
    rooms = db.query(models.Room).filter(models.Room.is_free == False).all()
    return rooms

@app.post("/api/rooms", response_model=schemas.RoomResponse)
async def create_room(
    room_data: schemas.RoomCreate,
    admin: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """채팅방 생성"""
    new_room = models.Room(**room_data.dict())
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room

@app.get("/api/rooms/{room_id}/messages", response_model=List[schemas.MessageResponse])
async def get_room_messages(
    room_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """채팅방 메시지 조회"""
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다")
    
    messages = db.query(models.Message).filter(
        models.Message.room_id == room_id
    ).order_by(models.Message.created_at.desc()).limit(100).all()
    
    return messages[::-1]  # 오래된 순서로

# ==================== 파일 업로드 API ====================

@app.post("/api/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
):
    """이미지 업로드"""
    # 파일 확장자 확인
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="지원하지 않는 이미지 형식입니다")
    
    # 파일 크기 제한 (5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="파일 크기는 5MB 이하여야 합니다")
    
    # 고유 파일명 생성
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # 파일 저장
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # URL 반환
    file_url = f"/uploads/{unique_filename}"
    
    return {
        "url": file_url,
        "filename": file.filename,
        "type": "image"
    }

@app.post("/api/upload/file")
async def upload_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
):
    """파일 업로드"""
    # 파일 확장자 확인
    allowed_extensions = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".zip"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다")
    
    # 파일 크기 제한 (10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="파일 크기는 10MB 이하여야 합니다")
    
    # 고유 파일명 생성
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # 파일 저장
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # URL 반환
    file_url = f"/uploads/{unique_filename}"
    
    return {
        "url": file_url,
        "filename": file.filename,
        "type": "file"
    }

# ==================== WebSocket ====================

@app.websocket("/ws/chat/{room_id}")
async def websocket_chat(websocket: WebSocket, room_id: int, token: str, db: Session = Depends(get_db)):
    """채팅 WebSocket"""
    try:
        # 토큰 검증
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user or not user.is_approved:
            await websocket.close(code=1008)
            return
        
        room = db.query(models.Room).filter(models.Room.id == room_id).first()
        if not room:
            await websocket.close(code=1008)
            return
        
        await manager.connect(websocket, str(room_id), user_id)
        
        # 접속 알림
        await manager.send_message({
            "type": "system",
            "message": f"{user.name}님이 입장하셨습니다.",
            "timestamp": datetime.utcnow().isoformat()
        }, str(room_id))
        
        while True:
            data = await websocket.receive_json()
            
            # 일반 회원은 메시지 전송 불가 (관리자/서브관리자/직원만 가능)
            if user.role == "member":
                await websocket.send_json({
                    "type": "error",
                    "message": "관리자와 직원만 메시지를 보낼 수 있습니다."
                })
                continue
            
            # 메시지 저장
            message = models.Message(
                room_id=room_id,
                user_id=user_id,
                content=data.get("message"),
                message_type=data.get("type", "text")
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            
            # 메시지 브로드캐스트
            await manager.send_message({
                "type": "message",
                "id": message.id,
                "user_id": user.id,
                "user_name": user.name,
                "user_role": user.role,
                "content": message.content,
                "message_type": message.message_type,
                "timestamp": message.created_at.isoformat()
            }, str(room_id))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, str(room_id), user_id)
        await manager.send_message({
            "type": "system",
            "message": f"{user.name}님이 퇴장하셨습니다.",
            "timestamp": datetime.utcnow().isoformat()
        }, str(room_id))
    except Exception as e:
        print(f"WebSocket error: {e}")

# ==================== MT4 연동 API ====================

@app.post("/api/mt4/position")
async def receive_mt4_position(
    position_data: schemas.MT4Position,
    api_key: str,  # MT4에서 보내는 API 키
    db: Session = Depends(get_db)
):
    """MT4 포지션 수신"""
    # API 키 검증 (실제 환경에서는 DB에 저장된 키와 비교)
    if api_key != "your-mt4-api-key":
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # 해외선물 채팅방 찾기
    room = db.query(models.Room).filter(
        models.Room.room_type == "futures"
    ).first()
    
    if not room:
        raise HTTPException(status_code=404, detail="해외선물 채팅방을 찾을 수 없습니다")
    
    # 메시지 생성
    message_content = f"""
🔔 포지션 알림

상품: {position_data.symbol}
타입: {"매수" if position_data.type == "BUY" else "매도"}
수량: {position_data.lots}
진입가: {position_data.open_price}
손절가: {position_data.sl}
목표가: {position_data.tp}
시간: {position_data.open_time}
    """.strip()
    
    # 시스템 메시지로 저장
    message = models.Message(
        room_id=room.id,
        user_id=1,  # 시스템 사용자
        content=message_content,
        message_type="signal"
    )
    db.add(message)
    db.commit()
    
    # WebSocket으로 전송
    await manager.send_message({
        "type": "signal",
        "content": message_content,
        "timestamp": datetime.utcnow().isoformat()
    }, str(room.id))
    
    return {"message": "포지션이 전송되었습니다"}

# ==================== 뉴스 크롤링 API ====================

@app.get("/api/news/{category}")
async def get_news(
    category: str,  # stock, futures, crypto
    current_user: models.User = Depends(get_current_user)
):
    """뉴스 크롤링"""
    from news_crawler import crawl_news
    
    try:
        news_list = await crawl_news(category)
        return {"news": news_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 초기 데이터 생성 ====================

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 기본 데이터 생성"""
    db = next(get_db())
    
    # 관리자 계정 생성 (없으면)
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
