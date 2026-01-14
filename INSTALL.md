# 🚀 빠른 설치 가이드

## 1️⃣ 로컬 개발 환경

### 필수 요구사항
- Python 3.9 이상
- Node.js 16 이상
- npm 또는 yarn

### 설치 및 실행

```bash
# 1. 프로젝트 클론
git clone https://github.com/your-repo/trading-chat.git
cd trading-chat

# 2. 실행 스크립트에 권한 부여
chmod +x start.sh

# 3. 스크립트 실행 (자동으로 백엔드/프론트엔드 시작)
./start.sh
```

또는 수동으로:

```bash
# Backend 실행
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# 새 터미널에서 Frontend 실행
cd frontend
npm install
npm start
```

### 접속

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

### 기본 관리자 계정

- **전화번호**: 010-0000-0000
- **비밀번호**: admin1234

## 2️⃣ Docker로 실행

```bash
# Docker Compose로 전체 시스템 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 종료
docker-compose down
```

## 3️⃣ 모바일 앱 빌드

### iOS (Mac만 가능)

```bash
cd frontend
npm install @capacitor/ios
npm run build
npx cap add ios
npx cap sync
npx cap open ios
```

Xcode에서 빌드 및 실행

### Android

```bash
cd frontend
npm install @capacitor/android
npm run build
npx cap add android
npx cap sync
npx cap open android
```

Android Studio에서 빌드 및 실행

## 4️⃣ AWS 배포

### EC2 설정

```bash
# EC2 SSH 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# 프로젝트 클론
git clone https://github.com/your-repo/trading-chat.git
cd trading-chat

# Backend 설정
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# PM2로 Backend 실행
pm2 start "gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000" --name trading-chat-backend

# Frontend 빌드
cd ../frontend
npm install
npm run build

# Nginx 설정
sudo cp nginx.conf /etc/nginx/sites-available/trading-chat
sudo ln -s /etc/nginx/sites-available/trading-chat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 환경 변수 설정

```bash
# backend/.env
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///./trading_chat.db
MT4_API_KEY=your-mt4-api-key
```

## 5️⃣ MT4 연동

1. MT4 Expert Advisors 폴더에 `TradingChatSender.mq4` 복사
2. MT4 재시작
3. EA 설정:
   - API_URL: `https://your-domain.com/api/mt4/position`
   - API_KEY: 백엔드에 설정한 키
4. 차트에 EA 적용

## 🔧 문제 해결

### Backend가 실행되지 않을 때
```bash
# 포트 8000 확인
lsof -i :8000
# 프로세스 종료
kill -9 [PID]
```

### Frontend가 실행되지 않을 때
```bash
# node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install
```

### Database 초기화
```bash
# SQLite 사용 시
rm backend/trading_chat.db
# 서버 재시작하면 자동으로 재생성됨
```

## 📞 지원

문제가 발생하면 GitHub Issues에 등록해주세요.

## 🎉 축하합니다!

설치가 완료되었습니다. 이제 리딩방 채팅 시스템을 사용하실 수 있습니다!
