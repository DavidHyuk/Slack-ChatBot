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

`.env` 파일 내용 (Bon Appétit Samsung SRA 예시):
```env
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=C12345678
TARGET_URL=https://sra.cafebonappetit.com/cafe/{date}/
```

`{date}` 는 기본으로 **America/Los_Angeles**(캘리포니아 등 US 서부) 달력의 오늘을 `YYYY-MM-DD` 로 넣습니다. 다른 타임존이면 `.env`에 `MENU_DATE_TZ=Asia/Seoul` 처럼 [IANA 이름](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)을 지정하세요.

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
   - `TARGET_URL`: 예) `https://sra.cafebonappetit.com/cafe/{date}/` — `{date}` 가 저장소 기본 타임존(`MENU_DATE_TZ`, 워크플로에서 `America/Los_Angeles`) 기준 오늘로 바뀝니다. 고정 URL만 쓰는 사이트면 `{date}` 없이 넣으면 됩니다.
3. **일 1회(프로덕션)**: `daily-menu.yml`은 기본으로 매일 **UTC 15:05** 한 번(`5 15 * * *`) 실행됩니다(Pacific 기준 대략 오전 8시 전후는 일광절약제에 따라 달라짐). **로컬 시각으로 보내기를 막는 로직은 없습니다** — GitHub 스케줄이 얼마나 밀려도 그 실행에서 곧바로 스크랩 후 Slack으로 보냅니다. 겨울(PST)에도 로컬 8시에 가깝게 맞추려면 워크플로의 `cron`을 `5 16 * * *` 등으로 조정하세요(여름에는 한 시간쯤 늦어질 수 있음). **Run workflow** 수동 실행도 동일하게 전송합니다.
4. **짧은 간격(스케줄 연속 테스트)**: GitHub는 **스케줄 트리거를 최소 5분 간격**만 허용합니다(`* * * * *` 같은 매분 cron은 [공식 문서](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#onschedule)상 지원되지 않습니다). `menu-bot-frequent-schedule.yml`의 **`*/5 * * * *`** 는 **UTC 기준 5분 격자마다 “돌릴 수 있는” 상한**이지, 실행이 **정확히 5분마다 이어지는 것을 보장하지는 않습니다**. Actions 부하가 크면 [스케줄이 수십 분~그 이상 밀리는 것](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule)이 흔해서, 목록에 간격이 들쭉날쭉해 보일 수 있습니다. **스케줄은 기본 브랜치(보통 `main`)에 있는 워크플로만** 돌아가고, **fork 레포**는 스케줄이 꺼져 있는 경우가 많습니다. 정확한 시각에 맞추려면 외부 cron + [repository_dispatch](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#repository_dispatch) 또는 `workflow_dispatch` API 호출을 검토하세요.
5. 한 번만 검증할 때는 Actions 탭에서 해당 워크플로의 **Run workflow**가 가장 예측 가능합니다.

## 🔧 커스터마이징 (스크래핑 로직 변경)

기본 제공되는 `scraper.py`는 예제 HTML 구조를 기반으로 작성되었습니다.
실제 사용하시는 카페테리아 사이트의 DOM 구조에 맞게 `scraper.py` 내부의 BeautifulSoup 셀렉터(`soup.find(...)`)를 수정하여 사용하세요.

## 📝 릴리즈 및 개발 히스토리
- [개발 버전 히스토리 문서](docs/development-history.md)를 참고하세요.
