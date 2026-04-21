# Cafeteria SlackBot 🍽️

매일 아침 사내 카페테리아의 오늘의 메뉴와 사진을 스크래핑하여 Slack 채널에 자동으로 공지해주는 봇입니다. GitHub Actions를 사용하여 서버 없이 무료로 스케줄링하여 동작합니다.

## ✨ 기능

- 지정된 카페테리아 웹사이트에서 오늘의 메뉴 텍스트와 사진 자동 추출 (로그인 불필요)
- 추출된 정보를 보기 좋은 Slack Block Kit 포맷으로 가공하여 전송
- GitHub Actions를 통한 매일 지정 시간 자동 실행 (Cron 스케줄링)

## 🚀 로컬 환경 실행 가이드

### 1. 요구 사항
- Python 3.12 이상
- [Slack Workspace](#-slack-app-설정-가이드) (Bot Token 생성 가능 권한 필요)

### 2. 설치 방법
저장소를 클론하고 의존성 패키지를 설치합니다.
```bash
git clone <repository-url>
cd Slack-ChatBot
pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 아래 항목들을 채워 넣습니다.
```bash
cp .env.example .env
```

`.env` 파일 내용:
```env
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=C12345678
TARGET_URL=http://your-cafeteria-url.com
```

### 4. 실행
```bash
python main.py
```

## 🤖 Slack App 설정 가이드

Slack 봇을 사용하려면 먼저 Slack App을 생성하고 토큰을 발급받아야 합니다.

1. [Slack API: Applications](https://api.slack.com/apps) 페이지로 이동합니다.
2. **Create New App** -> **From scratch** 를 선택하고, App 이름과 설치할 워크스페이스를 선택합니다.
3. 좌측 메뉴의 **OAuth & Permissions** 로 이동합니다.
4. **Scopes** -> **Bot Token Scopes** 에 다음 권한을 추가합니다.
   - `chat:write`: 메시지 전송 권한
5. 위쪽의 **Install to Workspace** 버튼을 눌러 워크스페이스에 앱을 설치합니다.
6. 생성된 **Bot User OAuth Token** (보통 `xoxb-` 로 시작)을 복사하여 `.env` 파일 또는 GitHub Secrets의 `SLACK_BOT_TOKEN` 값으로 사용합니다.
7. 메시지를 받을 Slack 채널에 앱을 초대합니다. (채널에서 `/invite @App이름` 입력)

## ⚙️ GitHub Actions 자동화 설정 (Secrets)

매일 정해진 시간에 자동으로 봇을 실행하려면 GitHub Repository에 Secrets를 설정해야 합니다.

1. GitHub Repository의 **Settings** -> **Secrets and variables** -> **Actions** 로 이동합니다.
2. **New repository secret** 버튼을 눌러 아래 세 가지 환경 변수를 등록합니다.
   - `SLACK_BOT_TOKEN`: 발급받은 Slack Bot Token
   - `SLACK_CHANNEL_ID`: 메시지를 전송할 채널 ID (예: C0123456789)
   - `TARGET_URL`: 스크래핑 대상 메뉴 웹사이트 URL
3. **일 1회(프로덕션)**: `.github/workflows/daily-menu.yml`의 `cron`이 기본으로 매일 KST 오전 11시(UTC 02:00)에 실행되도록 되어 있습니다. 시간을 바꾸려면 해당 파일의 `cron`만 수정하면 됩니다.
4. **1분마다(스케줄 연속 테스트)**: `.github/workflows/menu-bot-frequent-schedule.yml` 상단 `on:` 블록에 있는 `schedule` / `cron` 주석을 해제한 뒤 커밋하면 GitHub가 매 분 워크플로를 실행합니다. 테스트가 끝나면 같은 부분을 다시 주석 처리해 불필요한 실행과 Slack 알림을 막으세요. 이 워크플로는 **Run workflow** 수동 실행도 항상 사용할 수 있습니다.
5. GitHub 쪽 부하로 스케줄이 몇 분 밀릴 수 있습니다. 한 번만 검증할 때는 Actions 탭에서 해당 워크플로의 **Run workflow**를 쓰는 편이 가장 확실합니다.

## 🔧 커스터마이징 (스크래핑 로직 변경)

기본 제공되는 `scraper.py`는 예제 HTML 구조를 기반으로 작성되었습니다.
실제 사용하시는 카페테리아 사이트의 DOM 구조에 맞게 `scraper.py` 내부의 BeautifulSoup 셀렉터(`soup.find(...)`)를 수정하여 사용하세요.

## 📝 릴리즈 및 개발 히스토리
- [개발 버전 히스토리 문서](docs/development-history.md)를 참고하세요.
