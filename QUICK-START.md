# ⚡ 투자학당 빠른 시작 가이드

## 🎯 3단계로 시작하기

### 1️⃣ 로컬에서 테스트 (5분)
```bash
# 다운로드 & 압축 해제
tar -xzf investment-academy.tar.gz
cd investment-academy

# 자동 실행
chmod +x start.sh
./start.sh
```
✅ http://localhost:3000 접속  
✅ 로그인: 010-0000-0000 / admin1234

---

### 2️⃣ 무료 서버 배포 (10분)
**가장 쉬운 방법: Railway**

```bash
# GitHub 업로드
git init
git add .
git commit -m "투자학당"
git push

# Railway.app 접속
1. GitHub 연동
2. 저장소 선택
3. 자동 배포 ✨
```
✅ 5분 후 실제 URL 받음  
✅ 전세계 어디서나 접속 가능

📖 상세 가이드: [SERVER-DEPLOY-GUIDE.md](SERVER-DEPLOY-GUIDE.md)

---

### 3️⃣ 모바일 앱 만들기 (30분)

**Android 앱**
```bash
# Capacitor 설치
cd frontend
npm install @capacitor/android
npx cap add android

# Android Studio 열기
npx cap open android

# Run 버튼 클릭!
```
✅ APK 파일 생성  
✅ 폰에 설치 가능

**iOS 앱** (Mac만 가능)
```bash
# Capacitor 설치
npm install @capacitor/ios
npx cap add ios

# Xcode 열기
npx cap open ios

# Run 버튼 클릭!
```
✅ 시뮬레이터에서 테스트  
✅ iPhone에 설치 가능

📖 상세 가이드: [APP-BUILD-GUIDE.md](APP-BUILD-GUIDE.md)

---

## 📚 전체 문서

| 문서 | 설명 | 난이도 |
|------|------|--------|
| [README.md](README.md) | 프로젝트 개요 | ⭐ |
| [INSTALL.md](INSTALL.md) | 설치 가이드 | ⭐ |
| [SERVER-DEPLOY-GUIDE.md](SERVER-DEPLOY-GUIDE.md) | 서버 배포 | ⭐⭐ |
| [APP-BUILD-GUIDE.md](APP-BUILD-GUIDE.md) | 앱 빌드 | ⭐⭐⭐ |
| [CHANGELOG.md](CHANGELOG.md) | 변경 사항 | ⭐ |

---

## 🆘 도움이 필요하신가요?

### 서버 배포 추천
- **초보자**: Railway (5분, 완전 무료)
- **중급자**: Render (안정적)
- **고급자**: AWS EC2 (완전 제어)

### 앱 배포 추천
- **Android만**: Android Studio만 설치
- **iOS만**: Mac + Xcode 필요
- **둘 다**: Mac에서 모두 가능

---

## ⚙️ 기본 설정

### 관리자 계정
```
전화번호: 010-0000-0000
비밀번호: admin1234
```

### 서브관리자 생성
1. 관리자로 로그인
2. 관리자 페이지
3. 서브관리자 관리 → 생성

### 채팅방 생성
1. 관리자 페이지
2. 채팅방 관리
3. 새 채팅방 추가

---

## 🎓 일타훈장님 시작하기

### 첫 리딩 시작
1. ✅ 서버 배포
2. ✅ 서브관리자 계정 생성
3. ✅ 회원 가입 승인
4. ✅ 리딩 시그널 공유
5. ✅ 파일/이미지 업로드
6. ✅ MT4 연동 (선택)

### 회원 관리
```
무료 회원 → 관리자 승인 → 활성화
유료 회원 → 기간 설정 → 만료 관리
서브관리자 → 직접 생성 → 채팅 권한
```

---

## 💡 자주 묻는 질문

**Q: 완전 무료인가요?**
→ 네! Railway는 완전 무료입니다 (월 $5 크레딧)

**Q: 코딩을 몰라도 되나요?**
→ 네! 스크립트 실행만 하면 됩니다

**Q: Windows에서 iOS 앱 만들 수 있나요?**
→ 아니요, iOS는 Mac만 가능합니다

**Q: 몇 명까지 사용 가능한가요?**
→ Railway: ~50명, AWS: 제한 없음

**Q: 도메인이 필요한가요?**
→ 아니요, 자동으로 URL 제공됩니다

---

## 🚀 시작하세요!

```bash
# 지금 바로 시작
./start.sh

# 브라우저 자동 실행
# http://localhost:3000
```

**투자학당과 함께 성공적인 리딩방 운영하세요!** 🎓

---

**개발**: 투자학당 팀  
**관리**: 일타훈장님 👨‍🏫  
**버전**: 2.1.0
