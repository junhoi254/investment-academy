# 🚀 투자학당 무료 서버 배포 가이드

## 📋 목차
1. [Railway 배포 (가장 쉬움)](#railway-배포)
2. [Render 배포 (추천)](#render-배포)
3. [AWS EC2 배포 (12개월 무료)](#aws-ec2-배포)
4. [Oracle Cloud 배포 (평생 무료)](#oracle-cloud-배포)

---

## 🎯 Railway 배포 (가장 쉬움 - 5분 완료)

### 특징
- ✅ **완전 무료** (월 $5 크레딧)
- ✅ **자동 배포** (GitHub 연동)
- ✅ **SSL 자동** (HTTPS)
- ✅ **도메인 자동** 제공
- ⚠️ 제한: 월 500시간, 100GB 대역폭

### 1단계: GitHub에 코드 업로드

```bash
cd investment-academy

# Git 초기화
git init
git add .
git commit -m "투자학당 초기 배포"

# GitHub에 새 저장소 생성 후
git remote add origin https://github.com/your-username/investment-academy.git
git branch -M main
git push -u origin main
```

### 2단계: Railway 설정

1. **Railway 가입**
   - https://railway.app 접속
   - GitHub 계정으로 로그인

2. **새 프로젝트 생성**
   - "New Project" 클릭
   - "Deploy from GitHub repo" 선택
   - `investment-academy` 저장소 선택

3. **Backend 배포**
   - "Add Service" → "GitHub Repo"
   - Root directory: `backend`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   
4. **환경 변수 설정**
   ```
   SECRET_KEY=your-super-secret-key-change-this
   DATABASE_URL=sqlite:///./trading_chat.db
   MT4_API_KEY=your-mt4-api-key
   PORT=8000
   ```

5. **Frontend 배포**
   - "Add Service" → "GitHub Repo"
   - Root directory: `frontend`
   - Build command: `npm install && npm run build`
   - Start command: `npx serve -s build -l $PORT`

6. **환경 변수 설정 (Frontend)**
   ```
   REACT_APP_API_URL=https://your-backend-url.railway.app
   REACT_APP_WS_URL=wss://your-backend-url.railway.app
   ```

7. **도메인 확인**
   - Backend: `https://your-backend.railway.app`
   - Frontend: `https://your-frontend.railway.app`

### 3단계: 완료! ✅
- Frontend URL로 접속
- 관리자 로그인: 010-0000-0000 / admin1234

---

## 🌟 Render 배포 (추천 - 안정적)

### 특징
- ✅ **무료 티어** (750시간/월)
- ✅ **PostgreSQL 무료** (90일)
- ✅ **자동 SSL**
- ✅ **GitHub 자동 배포**
- ⚠️ 15분 미사용 시 슬립 모드

### 1단계: Render 가입
- https://render.com 접속
- GitHub 계정으로 가입

### 2단계: PostgreSQL 생성 (선택)

1. Dashboard → "New +" → "PostgreSQL"
2. Name: `investment-academy-db`
3. Database: `tradingchat`
4. User: `admin`
5. Region: `Singapore` (가장 가까움)
6. Plan: **Free**
7. Create Database

### 3단계: Backend 배포

1. **New Web Service**
   - "New +" → "Web Service"
   - GitHub 저장소 연결
   - Root Directory: `backend`
   
2. **설정**
   ```
   Name: investment-academy-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. **환경 변수**
   ```
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://user:pass@host/db (PostgreSQL 정보)
   MT4_API_KEY=your-api-key
   PYTHON_VERSION=3.11
   ```

4. **Create Web Service**

### 4단계: Frontend 배포

1. **New Static Site**
   - "New +" → "Static Site"
   - 같은 GitHub 저장소 선택
   - Root Directory: `frontend`

2. **설정**
   ```
   Name: investment-academy
   Build Command: npm install && npm run build
   Publish Directory: build
   ```

3. **환경 변수**
   ```
   REACT_APP_API_URL=https://investment-academy-backend.onrender.com
   REACT_APP_WS_URL=wss://investment-academy-backend.onrender.com
   ```

4. **Create Static Site**

### 5단계: 완료! ✅
- Frontend URL: `https://investment-academy.onrender.com`
- Backend URL: `https://investment-academy-backend.onrender.com`

---

## 🔥 AWS EC2 배포 (12개월 무료)

### 특징
- ✅ **12개월 무료** (t2.micro)
- ✅ **완전한 제어권**
- ✅ **높은 안정성**
- ⚠️ 설정 복잡

### 1단계: AWS 계정 생성
- https://aws.amazon.com/ko/free
- 신용카드 필요 (무료 범위 초과 시만 과금)

### 2단계: EC2 인스턴스 생성

1. **EC2 Console 접속**
   - AWS Console → EC2 → "인스턴스 시작"

2. **설정**
   ```
   이름: investment-academy
   AMI: Ubuntu Server 22.04 LTS
   인스턴스 유형: t2.micro (프리 티어)
   키 페어: 새로 생성 (다운로드 보관!)
   ```

3. **보안 그룹 설정**
   ```
   SSH (22): 내 IP
   HTTP (80): 0.0.0.0/0
   HTTPS (443): 0.0.0.0/0
   Custom TCP (8000): 0.0.0.0/0
   ```

4. **인스턴스 시작**

### 3단계: 서버 접속 및 설정

```bash
# SSH 접속 (Windows는 PuTTY 사용)
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@your-ec2-ip

# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Python 설치
sudo apt install python3-pip python3-venv -y

# Node.js 설치
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Nginx 설치
sudo apt install nginx -y

# Git 설치
sudo apt install git -y
```

### 4단계: 프로젝트 배포

```bash
# GitHub에서 클론
git clone https://github.com/your-username/investment-academy.git
cd investment-academy

# Backend 설정
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# .env 파일 생성
cat > .env << EOF
SECRET_KEY=your-super-secret-key
DATABASE_URL=sqlite:///./trading_chat.db
MT4_API_KEY=your-api-key
EOF

# Gunicorn 설치
pip install gunicorn

# Frontend 빌드
cd ../frontend
npm install
npm run build
```

### 5단계: 자동 실행 설정

```bash
# PM2 설치 (프로세스 관리자)
sudo npm install -g pm2

# Backend 실행
cd ~/investment-academy/backend
source venv/bin/activate
pm2 start "gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000" --name investment-academy

# 부팅 시 자동 시작
pm2 startup
pm2 save
```

### 6단계: Nginx 설정

```bash
# Nginx 설정 파일 생성
sudo nano /etc/nginx/sites-available/investment-academy
```

다음 내용 입력:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 또는 EC2 IP

    # Frontend
    location / {
        root /home/ubuntu/investment-academy/frontend/build;
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
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # 업로드 파일
    location /uploads {
        proxy_pass http://localhost:8000/uploads;
    }
}
```

저장 후:

```bash
# Nginx 설정 활성화
sudo ln -s /etc/nginx/sites-available/investment-academy /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Nginx 테스트 및 재시작
sudo nginx -t
sudo systemctl restart nginx
```

### 7단계: HTTPS 설정 (무료 SSL)

```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx -y

# SSL 인증서 발급 (도메인 필요)
sudo certbot --nginx -d your-domain.com

# 자동 갱신 설정
sudo certbot renew --dry-run
```

### 8단계: 완료! ✅
- `http://your-ec2-ip` 또는 `https://your-domain.com` 접속

---

## 💎 Oracle Cloud 배포 (평생 무료)

### 특징
- ✅ **평생 무료** (Always Free)
- ✅ **높은 성능** (ARM 기반 4 vCPU, 24GB RAM)
- ✅ **무제한 트래픽**
- ⚠️ 가입 복잡, 신용카드 필요

### 1단계: Oracle Cloud 가입
- https://www.oracle.com/kr/cloud/free
- 신용카드 인증 (과금 없음)

### 2단계: VM 인스턴스 생성

1. **인스턴스 만들기**
   ```
   이름: investment-academy
   이미지: Ubuntu 22.04
   Shape: VM.Standard.A1.Flex (Always Free)
   OCPU: 2 (무료 한도)
   메모리: 12GB (무료 한도)
   ```

2. **네트워킹**
   - VCN 자동 생성
   - 공용 IP 할당

3. **SSH 키 추가**
   - 새 키 페어 생성 및 다운로드

### 3단계: 방화벽 설정

```bash
# Oracle Cloud 콘솔에서
Networking → Virtual Cloud Networks → Subnet → Security List
Ingress Rules 추가:
- 80 (HTTP)
- 443 (HTTPS)
- 8000 (Backend)

# 서버 내부 방화벽
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
sudo netfilter-persistent save
```

### 4단계: AWS EC2와 동일하게 진행
- 3단계부터 동일하게 설정

---

## 🎯 자동 배포 스크립트

편리한 배포를 위한 스크립트를 제공했습니다:

```bash
chmod +x deploy-aws.sh
./deploy-aws.sh
```

---

## 📊 서비스 비교

| 서비스 | 난이도 | 무료 기간 | 성능 | 추천도 |
|--------|--------|----------|------|--------|
| **Railway** | ⭐ 쉬움 | 평생 (제한) | 중 | ⭐⭐⭐⭐⭐ 초보자 |
| **Render** | ⭐⭐ 보통 | 평생 (제한) | 중 | ⭐⭐⭐⭐ 중급자 |
| **AWS EC2** | ⭐⭐⭐ 어려움 | 12개월 | 높음 | ⭐⭐⭐⭐ 고급자 |
| **Oracle** | ⭐⭐⭐⭐ 복잡 | 평생 | 매우높음 | ⭐⭐⭐ 전문가 |

---

## 💡 추천 배포 전략

### 1. 처음 시작 (테스트)
→ **Railway** 사용
- 5분만에 배포
- 무료로 테스트
- 실사용자 10-20명까지 가능

### 2. 본격 운영 (소규모)
→ **Render** 사용
- PostgreSQL DB 포함
- 안정적 운영
- 사용자 50-100명

### 3. 대규모 운영
→ **AWS EC2** 또는 **Oracle Cloud**
- 완전한 제어권
- 높은 성능
- 사용자 500명 이상

---

## 🔧 배포 후 해야할 일

### 1. 보안 강화
```bash
# Backend .env 파일 수정
SECRET_KEY=매우-복잡한-랜덤-문자열-64자-이상
MT4_API_KEY=안전한-API-키
```

### 2. 도메인 연결 (선택)
- Namecheap, GoDaddy 등에서 도메인 구매
- DNS A 레코드를 서버 IP로 설정
- SSL 인증서 발급

### 3. 모니터링 설정
```bash
# PM2 모니터링
pm2 monit

# 로그 확인
pm2 logs investment-academy
```

### 4. 백업 설정
```bash
# 데이터베이스 백업
cp backend/trading_chat.db backup/trading_chat_$(date +%Y%m%d).db

# 업로드 파일 백업
tar -czf backup/uploads_$(date +%Y%m%d).tar.gz backend/uploads
```

---

## 📞 문제 해결

### Q: 배포 후 접속이 안 돼요
```bash
# Backend 상태 확인
pm2 status
pm2 logs investment-academy

# Nginx 상태 확인
sudo systemctl status nginx
sudo nginx -t

# 방화벽 확인
sudo ufw status
```

### Q: WebSocket 연결이 안 돼요
- Nginx WebSocket 설정 확인
- 방화벽 포트 8000 개방 확인
- Backend 로그 확인

### Q: 파일 업로드가 안 돼요
```bash
# uploads 폴더 권한 설정
cd backend
mkdir -p uploads
chmod 755 uploads
```

---

## 🎉 완료!

이제 투자학당이 인터넷에서 24시간 실행됩니다!

다음 단계: [모바일 앱 만들기](APP-BUILD-GUIDE.md)
