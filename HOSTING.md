# 디스코드 봇 무료 호스팅 가이드

## 🚀 추천 호스팅 서비스

### 1. Replit (초보자 추천) ⭐⭐⭐⭐⭐

**가장 쉬운 방법!**

#### 단계별 가이드:

1. **Replit 계정 생성**
   - [replit.com](https://replit.com/) 방문
   - 가입 (Google/GitHub 계정 가능)

2. **새 프로젝트 생성**
   - "Create Repl" 클릭
   - "Python" 선택
   - 프로젝트 이름 입력 (예: fantasy-rpg-bot)

3. **파일 업로드**
   - 다음 파일들을 업로드:
     - `main.py`
     - `config.py`
     - `database.py`
     - `rpg_system.py`
     - `battle_system.py`
     - `item_system.py`
     - `commands.py`
     - `requirements.txt`
     - `Procfile`
     - `runtime.txt`

4. **환경 변수 설정**
   - 좌측 패널의 "Secrets" (키 아이콘) 클릭
   - "Add new secret" 클릭
   - Key: `DISCORD_TOKEN`
   - Value: (당신의 디스코드 봇 토큰)
   - "Add secret" 클릭

5. **봇 실행**
   - 상단의 "Run" 버튼 클릭
   - 콘솔에 연결 메시지가 나타나면 성공!

6. **24시간 실행 (Keep Alive)**
   - 무료 플랜은 비활성화 시 종료됨
   - `uptimerobot.com`으로 핑 보내기
   - 또는 Replit Hacker 플랜 구독 ($7/월)

### 2. Heroku (안정성 추천) ⭐⭐⭐⭐

#### 전제 조건:
- Heroku 계정
- Heroku CLI 설치
- Git 설치

#### 단계별 가이드:

1. **Heroku CLI 설치**
   ```bash
   # Windows
   # https://devcenter.heroku.com/articles/heroku-cli

   # 설치 후 로그인
   heroku login
   ```

2. **Git 초기화**
   ```bash
   cd fantasy-rpg-bot
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **Heroku 앱 생성**
   ```bash
   heroku create your-bot-name
   ```

4. **환경 변수 설정**
   ```bash
   heroku config:set DISCORD_TOKEN=your_actual_token_here
   ```

5. **배포**
   ```bash
   git push heroku master
   ```

6. **Worker 스케일링**
   ```bash
   heroku ps:scale worker=1
   ```

7. **로그 확인**
   ```bash
   heroku logs --tail
   ```

### 3. Railway (현대적 선택) ⭐⭐⭐⭐

#### 단계별 가이드:

1. **Railway 계정 생성**
   - [railway.app](https://railway.app/) 방문
   - GitHub 계정으로 가입

2. **프로젝트 생성**
   - "New Project" 클릭
   - "Deploy from GitHub repo" 선택

3. **GitHub 연동**
   - 프로젝트를 GitHub에 푸시
   - Railway에서 리포지토리 선택

4. **환경 변수 설정**
   - Railway 대시보드
   - "Variables" 탭
   - `DISCORD_TOKEN` 추가

5. **자동 배포**
   - 푸시할 때마다 자동 배포

### 4. Render (좋은 무료 티어) ⭐⭐⭐⭐

#### 단계별 가이드:

1. **Render 계정 생성**
   - [render.com](https://render.com/) 방문
   - 가입

2. **New Web Service**
   - "New +" 버튼
   - "Web Service" 선택

3. **GitHub 연동**
   - 리포지토리 연결
   - 브랜치 선택 (main)

4. **설정**
   - Name: fantasy-rpg-bot
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`

5. **환경 변수**
   - `DISCORD_TOKEN` 추가

6. **배포**
   - "Create Web Service" 클릭

## 🛠️ 필수 파일 확인

프로젝트에 다음 파일들이 있는지 확인하세요:

- ✅ `main.py` - 메인 봇 파일
- ✅ `config.py` - 설정 파일
- ✅ `requirements.txt` - 패키지 목록
- ✅ `Procfile` - Heroku용 (이 경우에는 worker)
- ✅ `runtime.txt` - Python 버전 지정
- ✅ `.env.example` - 환경 변수 예시

## 📱 24시간 유지 방법

### 무료 방법:

1. **UptimeRobot**
   - [uptimerobot.com](https://uptimerobot.com/) 가입
   - 봇 URL 추가 (Ping)
   - 5분마다 핑 전송

2. **서로 핑**
   - 다른 사람의 봇과 서로 핑
   - 일정 시간마다 요청 전송

### 유료 방법:

1. **Replit Hacker** - $7/월
2. **Heroku Eco** - $5/월
3. **Railway Pro** - $5/월

## 🔧 문제 해결

### Heroku 문제:
```bash
# 로그 확인
heroku logs --tail

# 재시작
heroku ps:restart

# 재배포
git push heroku master
```

### Replit 문제:
- Secrets가 올바른지 확인
- requirements.txt가 있는지 확인
- Python 버전 호환성 확인

### 일반 문제:
- 토큰이 올바른지 확인
- 디스코드 봇 권한 확인
- 인터넷 연결 확인

## 🎯 추천 설정

**초보자:** Replit (가장 쉬움)
**안정성:** Heroku (가장 신뢰성 높음)
**무료:** Render (좋은 무료 티어)
**현대적:** Railway (좋은 UI)

## 📞 도움말

문제가 있으면:
- 각 플랫폼의 문서 확인
- 디스코드 개발 커뮤니티
- Stack Overflow

성공적인 호스팅을 빕니다! 🚀