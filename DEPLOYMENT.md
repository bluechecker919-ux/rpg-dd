# 배포 가이드

## 로컬 테스트

### 1. 기본 테스트
```bash
cd fantasy-rpg-bot
python main.py
```

### 2. 디스�ords에서 테스트
1. 봇이 온라인 상태인지 확인
2. `!도움말` 명령어로 기본 기능 테스트
3. `!캐릭터생성 테스트 전사`로 캐릭터 생성 테스트
4. `!내정보`로 캐릭터 정보 확인
5. `!전투시작`으로 전투 시스템 테스트
6. `!상점`과 `!인벤토리`로 아이템 시스템 테스트

## 클라우드 배포

### Heroku 배포

#### 1. Heroku 계정 및 CLI 설치
- [Heroku](https://www.heroku.com/) 계정 생성
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) 설치

#### 2. Procfile 생성
```bash
echo "worker: python main.py" > Procfile
```

#### 3. Heroku 앱 생성
```bash
heroku create your-bot-name
```

#### 4. 환경 변수 설정
```bash
heroku config:set DISCORD_TOKEN=your_bot_token_here
```

#### 5. Git 배포
```bash
git init
git add .
git commit -m "Initial commit"
heroku git:remote -a your-bot-name
git push heroku master
```

#### 6. 워커 스케일링
```bash
heroku ps:scale worker=1
```

### Replit 배포

#### 1. Replit 프로젝트 생성
- [Replit](https://replit.com/)에서 새 Python 프로젝트 생성
- 모든 파일 업로드

#### 2. Secrets 설정
- `.env` 파일 생성
- `DISCORD_TOKEN=your_bot_token_here` 추가

#### 3. 실행
- Replit의 "Run" 버튼 클릭

### Railway 배포

#### 1. Railway 계정 및 프로젝트 생성
- [Railway](https://railway.app/) 계정 생성
- 새 프로젝트 생성

#### 2. GitHub 연결
- 프로젝트를 GitHub에 푸시
- Railway에서 GitHub 리포지토리 연결

#### 3. 환경 변수 설정
- Railway 대시보드에서 `DISCORD_TOKEN` 환경 변수 추가

#### 4. 배포
- 자동으로 배포 시작

### Docker 배포

#### 1. Dockerfile 생성
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

#### 2. docker-compose.yml 생성
```yaml
version: '3.8'

services:
  bot:
    build: .
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}
    restart: unless-stopped
```

#### 3. Docker 실행
```bash
docker-compose up -d
```

## 모니터링 및 유지보수

### 로그 확인
```bash
# Heroku
heroku logs --tail

# Docker
docker-compose logs -f

# 일반
tail -f bot.log
```

### 재시작
```bash
# Heroku
heroku ps:restart

# Docker
docker-compose restart
```

### 업데이트
```bash
# 코드 변경 후
git add .
git commit -m "Update bot"
git push

# Heroku 자동 배포
# Docker
docker-compose up -d --build
```

## 보안 권장사항

1. **토큰 보호**: 절대 토큰을 공개 리포지토리에 커밋하지 마세요
2. **환경 변수 사용**: 항상 환경 변수로 토큰을 관리하세요
3. **권한 최소화**: 봇에 필요한 최소 권한만 부여하세요
4. **정기 업데이트**: 주기적으로 패키지를 업데이트하세요
5. **백업**: data.json을 정기적으로 백업하세요

## 문제 해결

### Heroku 배포 문제
- Worker 타입 사용 (web 타입은 웹 앱용)
- buildpack이 Python으로 설정되어 있는지 확인
- 디스코드 봇 권한이 올바른지 확인

### 메모리 문제
- Heroku: `heroku config:set HEROKU_RAM=512`
- 데이터베이스 크기 모니터링
- 정기적인 데이터 정리

### 연결 끊김
- Heartbeat 메커니즘 구현
- 자동 재시작 설정
- 로그를 통한 원인 분석

## 성능 최적화

1. **데이터베이스**: SQLite로 마이그레이션 고려 (대규모용)
2. **캐싱**: 자주 사용되는 데이터 캐싱
3. **비동기 처리**: 무거운 작업 비동기 처리
4. **로드 밸런싱**: 여러 인스턴스 운영 (대규모용)

이 가이드를 따라하면 성공적으로 봇을 배포할 수 있습니다!