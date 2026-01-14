# 📱 투자학당 모바일 앱 만들기

## 📋 목차
1. [준비 사항](#준비-사항)
2. [Android 앱 만들기](#android-앱-만들기)
3. [iOS 앱 만들기](#ios-앱-만들기)
4. [Play Store 배포](#play-store-배포)
5. [App Store 배포](#app-store-배포)

---

## 🛠️ 준비 사항

### 공통 요구사항
- ✅ Node.js 16 이상
- ✅ npm 또는 yarn
- ✅ 투자학당 프로젝트

### Android 앱용
- ✅ **Android Studio** (무료)
- ✅ **JDK 11 이상**
- ✅ Windows / Mac / Linux 모두 가능

### iOS 앱용
- ✅ **Xcode** (무료)
- ✅ **macOS 필수** (맥북, 맥미니 등)
- ✅ Apple Developer 계정 ($99/년, 배포 시에만 필요)

---

## 🤖 Android 앱 만들기

### 1단계: Android Studio 설치

1. **다운로드**
   - https://developer.android.com/studio
   - Windows / Mac / Linux 버전 다운로드

2. **설치**
   - 기본 설정으로 설치
   - Android SDK 자동 설치됨

3. **환경 변수 설정 (Windows)**
   ```
   ANDROID_HOME=C:\Users\YourName\AppData\Local\Android\Sdk
   PATH에 추가: %ANDROID_HOME%\platform-tools
   ```

4. **환경 변수 설정 (Mac/Linux)**
   ```bash
   # ~/.bash_profile 또는 ~/.zshrc에 추가
   export ANDROID_HOME=$HOME/Library/Android/sdk
   export PATH=$PATH:$ANDROID_HOME/platform-tools
   ```

### 2단계: Capacitor 설정

```bash
cd investment-academy/frontend

# Capacitor 설치
npm install @capacitor/core @capacitor/cli
npm install @capacitor/android

# Capacitor 초기화
npx cap init

# 입력 정보:
# App name: 투자학당
# App package ID: com.investmentacademy.app
# (엔터 계속 입력)
```

### 3단계: 빌드 설정

```bash
# .env 파일 수정
cat > .env << EOF
# 실제 서버 주소로 변경!
REACT_APP_API_URL=https://your-backend-url.com
REACT_APP_WS_URL=wss://your-backend-url.com
EOF

# 프로덕션 빌드
npm run build

# Android 프로젝트 생성
npx cap add android

# 빌드 동기화
npx cap sync android
```

### 4단계: Android Studio에서 열기

```bash
# Android Studio 자동 실행
npx cap open android
```

또는 Android Studio에서:
- File → Open
- `investment-academy/frontend/android` 폴더 선택

### 5단계: 앱 아이콘 설정

1. **아이콘 준비**
   - 1024x1024 PNG 이미지 준비 (훈장님 로고)
   - https://icon.kitchen 에서 자동 생성 가능

2. **Android Studio에서**
   - `app` 우클릭
   - New → Image Asset
   - Foreground Layer → 이미지 선택
   - Background Layer → 색상 선택 (#667eea)
   - Next → Finish

### 6단계: 앱 정보 수정

**android/app/src/main/res/values/strings.xml**
```xml
<resources>
    <string name="app_name">투자학당</string>
    <string name="title_activity_main">투자학당</string>
    <string name="package_name">com.investmentacademy.app</string>
    <string name="custom_url_scheme">com.investmentacademy.app</string>
</resources>
```

**android/app/build.gradle**
```gradle
android {
    compileSdkVersion 33
    
    defaultConfig {
        applicationId "com.investmentacademy.app"
        minSdkVersion 22
        targetSdkVersion 33
        versionCode 1
        versionName "1.0.0"
    }
}
```

### 7단계: 테스트 (실제 기기)

1. **개발자 옵션 활성화**
   - 안드로이드 폰 설정 → 휴대전화 정보
   - 빌드 번호 7번 탭

2. **USB 디버깅 활성화**
   - 설정 → 개발자 옵션
   - USB 디버깅 ON

3. **USB 연결**
   - 폰을 컴퓨터에 연결
   - USB 디버깅 허용

4. **Android Studio에서**
   - 상단 기기 선택 (Your Phone)
   - Run 버튼 (▶️) 클릭
   - 앱이 자동으로 설치되고 실행됨!

### 8단계: APK 파일 생성 (배포용)

```bash
# Android Studio에서
Build → Build Bundle(s) / APK(s) → Build APK(s)

# 또는 명령어로
cd android
./gradlew assembleRelease

# 생성된 APK 위치
android/app/build/outputs/apk/release/app-release-unsigned.apk
```

### 9단계: APK 서명 (배포용)

1. **키 생성**
```bash
# Windows
keytool -genkey -v -keystore investment-academy.keystore -alias investment-academy -keyalg RSA -keysize 2048 -validity 10000

# Mac/Linux
keytool -genkey -v -keystore ~/investment-academy.keystore -alias investment-academy -keyalg RSA -keysize 2048 -validity 10000
```

2. **정보 입력**
```
비밀번호 입력: (안전하게 보관!)
이름: 투자학당
조직: Investment Academy
도시: Seoul
국가: KR
```

3. **build.gradle 수정**

**android/app/build.gradle**
```gradle
android {
    ...
    signingConfigs {
        release {
            storeFile file('../../investment-academy.keystore')
            storePassword 'your-password'
            keyAlias 'investment-academy'
            keyPassword 'your-password'
        }
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

4. **서명된 APK 생성**
```bash
cd android
./gradlew assembleRelease

# 생성 위치
android/app/build/outputs/apk/release/app-release.apk
```

### 10단계: 완료! 🎉
- `app-release.apk` 파일을 폰에 설치
- 카카오톡으로 공유 가능
- 또는 Google Drive에 업로드

---

## 🍎 iOS 앱 만들기

### ⚠️ 주의사항
- **맥(macOS)에서만 가능합니다**
- Windows에서는 iOS 앱 개발 불가

### 1단계: Xcode 설치

1. **App Store에서 설치**
   - App Store 열기
   - "Xcode" 검색
   - 설치 (무료, 약 12GB)

2. **Command Line Tools 설치**
```bash
xcode-select --install
```

### 2단계: CocoaPods 설치

```bash
# CocoaPods 설치 (iOS 패키지 관리자)
sudo gem install cocoapods

# 설치 확인
pod --version
```

### 3단계: Capacitor 설정

```bash
cd investment-academy/frontend

# iOS Capacitor 설치
npm install @capacitor/ios

# iOS 프로젝트 생성
npx cap add ios

# 동기화
npx cap sync ios

# 의존성 설치
cd ios/App
pod install
cd ../..
```

### 4단계: Xcode에서 열기

```bash
# Xcode 자동 실행
npx cap open ios
```

또는 Xcode에서:
- File → Open
- `investment-academy/frontend/ios/App/App.xcworkspace` 선택

### 5단계: 앱 아이콘 설정

1. **아이콘 준비**
   - 1024x1024 PNG (훈장님 로고)
   - https://appicon.co 에서 자동 생성

2. **Xcode에서**
   - Assets.xcassets 클릭
   - AppIcon 우클릭 → Import
   - 생성된 아이콘 세트 선택

### 6단계: 앱 정보 수정

**Xcode에서:**
1. Project Navigator → App
2. General 탭
   ```
   Display Name: 투자학당
   Bundle Identifier: com.investmentacademy.app
   Version: 1.0.0
   Build: 1
   ```

3. Info 탭
   ```
   Bundle name: 투자학당
   Bundle display name: 투자학당
   ```

### 7단계: 시뮬레이터 테스트

1. **시뮬레이터 선택**
   - 상단 기기 선택 → iPhone 14 Pro (또는 원하는 기기)

2. **실행**
   - 재생 버튼(▶️) 클릭
   - 시뮬레이터 자동 실행
   - 앱 자동 설치 및 실행

### 8단계: 실제 iPhone 테스트

1. **Apple ID 로그인**
   - Xcode → Preferences → Accounts
   - Apple ID 추가

2. **개발 팀 설정**
   - Project → Signing & Capabilities
   - Team → Your Apple ID 선택
   - "Automatically manage signing" 체크

3. **iPhone 연결**
   - Lightning 케이블로 연결
   - iPhone에서 "이 컴퓨터 신뢰" 탭

4. **실행**
   - 상단 기기 선택 → Your iPhone
   - 재생 버튼 클릭

5. **iPhone 설정**
   - 설정 → 일반 → VPN 및 기기 관리
   - 개발자 앱 → 신뢰

### 9단계: Archive (배포용)

1. **Generic iOS Device 선택**
   - 상단 기기 → Any iOS Device (arm64)

2. **Archive 생성**
   - Product → Archive
   - 5-10분 소요

3. **완료!**
   - Window → Organizer → Archives
   - 생성된 Archive 확인

---

## 🏪 Play Store 배포 (Android)

### 1단계: Google Play Console 가입

1. **가입**
   - https://play.google.com/console
   - Google 계정 필요
   - **등록비: $25 (1회, 평생)**
   - 신용카드 결제

### 2단계: 앱 등록

1. **새 앱 만들기**
   ```
   앱 이름: 투자학당
   기본 언어: 한국어
   앱/게임: 앱
   무료/유료: 무료
   ```

2. **앱 카테고리**
   ```
   카테고리: 재무
   태그: 투자, 주식, 리딩방
   ```

### 3단계: 스토어 등록정보

1. **짧은 설명** (80자)
   ```
   일타훈장님의 실시간 트레이딩 리딩방
   ```

2. **전체 설명** (4000자)
   ```
   🎓 투자학당 - 일타훈장님과 함께하는 트레이딩

   ✨ 주요 기능
   • 실시간 리딩 시그널
   • 주식/해외선물/코인 분석
   • 전문가 매매 전략 공유
   • MT4 자동 시그널
   
   📊 제공 서비스
   • 무료 공지방 - 누구나 확인 가능
   • 프리미엄 리딩방 - 회원 전용
   • 차트 분석 공유
   • 투자 전략 문서
   
   👨‍🏫 일타훈장님
   10년 이상 트레이딩 경력의 전문가가
   직접 시그널을 제공합니다.
   ```

3. **스크린샷** (최소 2장)
   - 앱 실행 화면 캡처
   - 1080 x 1920 또는 1080 x 2340
   - 채팅방 화면, 로그인 화면 등

4. **아이콘**
   - 512 x 512 PNG
   - 32비트 PNG (알파 채널)

### 4단계: AAB 파일 업로드

1. **AAB 생성**
```bash
cd android
./gradlew bundleRelease

# 생성 위치
android/app/build/outputs/bundle/release/app-release.aab
```

2. **Play Console에 업로드**
   - 프로덕션 → 새 버전 만들기
   - AAB 파일 업로드
   - 버전 이름: 1.0.0
   - 버전 코드: 1

### 5단계: 콘텐츠 등급

1. **설문 작성**
   - 재무 앱
   - 투자 정보 제공
   - 도박 요소 없음

2. **등급 받기**
   - 한국: 전체 이용가
   - 미국: Everyone

### 6단계: 개인정보 보호

1. **개인정보처리방침 URL**
   - 웹사이트나 GitHub에 게시
   - 예: https://your-site.com/privacy

2. **권한 설명**
   - 인터넷: 채팅 통신
   - 저장소: 파일 다운로드

### 7단계: 검토 제출

1. **검토 요청**
   - 모든 항목 완료 확인
   - "검토 제출" 클릭

2. **대기**
   - 보통 1-3일 소요
   - 이메일로 결과 통지

### 8단계: 승인 및 배포! 🎉
- 승인 시 자동으로 Play Store 배포
- https://play.google.com/store/apps 에서 검색 가능

---

## 🍏 App Store 배포 (iOS)

### 1단계: Apple Developer 가입

1. **가입**
   - https://developer.apple.com
   - Apple ID 필요
   - **연회비: $99 (매년)**
   - 신용카드 결제

### 2단계: App Store Connect

1. **접속**
   - https://appstoreconnect.apple.com
   - 개발자 계정으로 로그인

2. **새 앱 등록**
   ```
   이름: 투자학당
   기본 언어: 한국어
   번들 ID: com.investmentacademy.app
   SKU: investment-academy-001
   ```

### 3단계: 앱 정보 입력

1. **기본 정보**
   ```
   카테고리: 재무
   부카테고리: 투자
   연령 등급: 4+
   ```

2. **설명**
   - 짧은 설명 (30자)
   - 전체 설명 (4000자)
   - Play Store와 동일하게 작성

3. **키워드**
   ```
   투자,주식,리딩,트레이딩,시그널,차트,분석
   ```

4. **스크린샷**
   - iPhone 6.7" (필수)
   - iPhone 6.5" (필수)
   - iPad Pro 12.9" (선택)

### 4단계: Xcode에서 Archive

1. **버전 확인**
   - Version: 1.0.0
   - Build: 1

2. **Archive**
   - Product → Archive
   - Archive 완료 대기

3. **Validate**
   - Archive → Validate App
   - 문제 없으면 통과

4. **Upload**
   - Distribute App → App Store Connect
   - Upload 클릭
   - 10-20분 소요

### 5단계: 심사 제출

1. **빌드 선택**
   - App Store Connect
   - 업로드된 빌드 선택

2. **Export Compliance**
   ```
   암호화 사용 여부: 아니오
   (HTTPS는 제외)
   ```

3. **검토 정보**
   ```
   데모 계정:
   - 전화번호: 010-0000-0000
   - 비밀번호: admin1234
   
   참고사항: 
   관리자 계정으로 로그인 후
   모든 기능 확인 가능합니다.
   ```

4. **심사 제출**
   - "제출" 클릭
   - 보통 1-7일 소요

### 6단계: 승인 및 출시! 🎉
- 승인 시 App Store 배포
- https://apps.apple.com 에서 검색 가능

---

## 🔄 앱 업데이트 방법

### Android 업데이트

```bash
# 1. 코드 수정
cd investment-academy/frontend

# 2. 버전 업데이트
# android/app/build.gradle
versionCode 2  # 1씩 증가
versionName "1.0.1"  # 버전 표시

# 3. 빌드
npm run build
npx cap sync android

# 4. AAB 생성
cd android
./gradlew bundleRelease

# 5. Play Console 업로드
프로덕션 → 새 버전 만들기 → AAB 업로드
```

### iOS 업데이트

```bash
# 1. 코드 수정
cd investment-academy/frontend

# 2. Xcode에서 버전 업데이트
Version: 1.0.1
Build: 2

# 3. 빌드
npm run build
npx cap sync ios

# 4. Archive & Upload
Product → Archive → Distribute
```

---

## 📊 배포 체크리스트

### Android
- [ ] APK/AAB 서명 완료
- [ ] 버전 코드 증가
- [ ] 스크린샷 준비 (최소 2장)
- [ ] 아이콘 512x512
- [ ] 개인정보처리방침 URL
- [ ] 앱 설명 작성
- [ ] 콘텐츠 등급 받기

### iOS
- [ ] Apple Developer 등록 ($99)
- [ ] 번들 ID 설정
- [ ] 스크린샷 준비 (iPhone + iPad)
- [ ] 아이콘 1024x1024
- [ ] 개인정보처리방침 URL
- [ ] 앱 설명 작성
- [ ] 데모 계정 정보
- [ ] Export Compliance

---

## 💡 꿀팁

### 1. 테스트 배포 (베타 테스트)

**Android - Internal Testing**
```
Play Console → 테스트 → 내부 테스트
→ 이메일로 테스터 초대
→ 즉시 테스트 가능
```

**iOS - TestFlight**
```
App Store Connect → TestFlight
→ 자동 베타 테스트 가능
→ 이메일로 테스터 초대
```

### 2. 앱 크기 줄이기

```bash
# Android
android/app/build.gradle에 추가:
android {
    buildTypes {
        release {
            shrinkResources true
            minifyEnabled true
        }
    }
}

# iOS
Xcode → Build Settings
→ Optimization Level → Fastest, Smallest
```

### 3. 자동 업데이트

```javascript
// App.js에 추가
import { App as CapApp } from '@capacitor/app';

CapApp.addListener('appStateChange', ({ isActive }) => {
  if (isActive) {
    // 서버에서 최신 버전 확인
    checkForUpdate();
  }
});
```

---

## 🐛 문제 해결

### Q: Gradle 빌드 실패
```bash
# 권한 오류 시
chmod +x android/gradlew

# 캐시 삭제
cd android
./gradlew clean
```

### Q: iOS 빌드 실패
```bash
# Pod 재설치
cd ios/App
pod deintegrate
pod install
```

### Q: 서명 오류
- Android: keystore 비밀번호 확인
- iOS: Provisioning Profile 확인

---

## 🎉 완성!

축하합니다! 투자학당 앱이 완성되었습니다!

### 다음 단계
1. 스토어 등록
2. 사용자 피드백 수집
3. 정기 업데이트

**문의사항은 GitHub Issues로!**
