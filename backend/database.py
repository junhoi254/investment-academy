from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 데이터베이스 URL
# 개발 환경: SQLite
# 프로덕션 환경: PostgreSQL (AWS RDS)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./trading_chat.db"  # 기본값: SQLite
)

# PostgreSQL 예시 (AWS RDS 사용 시)
# DATABASE_URL = "postgresql://username:password@your-rds-endpoint:5432/dbname"

# SQLAlchemy 엔진 생성
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

# 세션 로컬 클래스
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스
Base = declarative_base()

# 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
