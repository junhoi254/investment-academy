#!/bin/bash

# AWS EC2 배포 스크립트
# 사용법: ./deploy-aws.sh

echo "🚀 AWS EC2 배포 시작..."

# 색상 코드
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 환경 변수 확인
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}❌ backend/.env 파일이 없습니다!${NC}"
    echo "backend/.env 파일을 생성하고 다음 변수를 설정하세요:"
    echo "  SECRET_KEY=your-secret-key"
    echo "  DATABASE_URL=sqlite:///./trading_chat.db"
    echo "  MT4_API_KEY=your-mt4-api-key"
    exit 1
fi

# 1. Backend 배포
echo -e "\n${YELLOW}📡 Backend 배포...${NC}"
cd backend

# 가상환경 생성 (없으면)
if [ ! -d "venv" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv venv
fi

# 패키지 설치
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# PM2로 실행
echo "Backend 서버 재시작..."
pm2 delete trading-chat-backend 2>/dev/null || true
pm2 start "gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000" --name trading-chat-backend
pm2 save

cd ..

# 2. Frontend 배포
echo -e "\n${YELLOW}🌐 Frontend 빌드...${NC}"
cd frontend

# 패키지 설치
if [ ! -d "node_modules" ]; then
    echo "패키지 설치 중..."
    npm install
fi

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo ".env 파일 생성 중..."
    cat > .env << EOF
REACT_APP_API_URL=https://your-domain.com
REACT_APP_WS_URL=wss://your-domain.com
EOF
    echo -e "${YELLOW}⚠️  .env 파일을 수정하여 도메인을 설정하세요!${NC}"
fi

# 프로덕션 빌드
echo "프로덕션 빌드 중..."
npm run build

cd ..

# 3. Nginx 설정
echo -e "\n${YELLOW}⚙️  Nginx 설정...${NC}"

# Nginx 설정 파일 생성
sudo tee /etc/nginx/sites-available/trading-chat > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        root /home/ubuntu/trading-chat/frontend/build;
        try_files $uri /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Nginx 설정 활성화
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/trading-chat /etc/nginx/sites-enabled/

# Nginx 설정 테스트
if sudo nginx -t; then
    echo -e "${GREEN}✅ Nginx 설정 성공${NC}"
    sudo systemctl restart nginx
    echo -e "${GREEN}✅ Nginx 재시작 완료${NC}"
else
    echo -e "${RED}❌ Nginx 설정 오류${NC}"
    exit 1
fi

# 4. 방화벽 설정 (UFW)
echo -e "\n${YELLOW}🔒 방화벽 설정...${NC}"
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 5. PM2 자동 시작 설정
echo -e "\n${YELLOW}⚡ PM2 자동 시작 설정...${NC}"
pm2 startup | tail -1 | sudo bash
pm2 save

# 배포 완료
echo -e "\n${GREEN}✨ 배포 완료!${NC}"
echo -e "\n📌 다음 단계:"
echo "1. 도메인을 서버 IP로 연결하세요"
echo "2. HTTPS 설정: sudo certbot --nginx -d your-domain.com"
echo "3. frontend/.env 파일에서 도메인 수정"
echo "4. 관리자 계정으로 로그인: 010-0000-0000 / admin1234"
echo ""
echo -e "${GREEN}🎉 축하합니다! 리딩방 시스템이 성공적으로 배포되었습니다!${NC}"
