#!/bin/bash

# 리딩방 채팅 시스템 실행 스크립트

echo "🚀 리딩방 채팅 시스템 시작..."

# Backend 시작
echo "📡 Backend 서버 시작..."
cd backend

# 가상환경 활성화
if [ ! -d "venv" ]; then
    echo "⚙️  가상환경 생성 중..."
    python3 -m venv venv
fi

source venv/bin/activate

# 패키지 설치
if [ ! -f "venv/installed" ]; then
    echo "📦 패키지 설치 중..."
    pip install -r requirements.txt
    touch venv/installed
fi

# Backend 서버 백그라운드 실행
python main.py &
BACKEND_PID=$!
echo "✅ Backend 서버 시작됨 (PID: $BACKEND_PID)"

cd ..

# Frontend 시작
echo "🌐 Frontend 서버 시작..."
cd frontend

# 패키지 설치
if [ ! -d "node_modules" ]; then
    echo "📦 패키지 설치 중..."
    npm install
fi

# .env 파일 생성
if [ ! -f ".env" ]; then
    echo "⚙️  .env 파일 생성..."
    cp .env.example .env
fi

# Frontend 서버 실행
npm start &
FRONTEND_PID=$!
echo "✅ Frontend 서버 시작됨 (PID: $FRONTEND_PID)"

echo ""
echo "✨ 모든 서버가 시작되었습니다!"
echo ""
echo "📌 접속 주소:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API 문서: http://localhost:8000/docs"
echo ""
echo "🔑 관리자 계정:"
echo "   전화번호: 010-0000-0000"
echo "   비밀번호: admin1234"
echo ""
echo "⚠️  종료하려면 Ctrl+C를 누르세요"

# 종료 처리
trap "echo ''; echo '🛑 서버 종료 중...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT

# 대기
wait
