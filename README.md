# Cafeteria SlackBot 🍽️

매일 아침 사내 카페테리아의 오늘의 메뉴와 사진을 스크래핑하여 Slack 채널에 자동으로 공지해주는 봇입니다. 팀 데스크탑의 Linux cron으로 매일 지정 시간에 실행하며, GitHub Actions는 수동 실행/백업용으로 남아 있습니다.

## ✨ 기능

- 지정된 카페테리아 웹사이트에서 오늘의 메뉴 텍스트와 사진 자동 추출 (로그인 불필요)
- 추출된 정보를 보기 좋은 Slack Block Kit 포맷으로 가공하여 전송
- 로컬 Linux cron을 통한 매일 지정 시간 자동 실행 (GitHub Actions는 수동 실행 백업용)

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

## ⚙️ 자동 실행 스케줄링 (로컬 cron)

GitHub Actions의 `schedule` 트리거는 best-effort라 부하가 크면 몇 시간씩 밀리는 문제가 반복돼(`docs/dev-history.md` 0.3.10, 0.3.11 참고), 매일 자동 발송은 **팀 데스크탑의 Linux cron**으로 옮겼습니다.

1. `.env.example`을 복사해 `.env`를 만들고 `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`, `TARGET_URL`을 채웁니다.
2. `crontab -e`로 아래 줄을 등록합니다 (데스크탑 타임존이 `America/Los_Angeles`라 로컬 시각 08:07 = 목표 도착 창 08:00~09:00):
   ```cron
   7 8 * * 1-5 /path/to/Cafeteria-Slack-Bot/run_main.sh >> /path/to/Cafeteria-Slack-Bot/logs/cron.log 2>&1
   ```
3. `run_main.sh`는 `uv run --with-requirements requirements.txt python main.py`로 의존성을 캐시된 환경에 설치하고 실행합니다.
4. `daily-menu.yml`은 이제 `workflow_dispatch`만 남아 있는 수동 실행/백업용입니다. GitHub Secrets(`SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`, `TARGET_URL`)는 Actions 탭에서 필요할 때 그대로 사용할 수 있습니다.

## 🔧 커스터마이징 (스크래핑 로직 변경)

기본 제공되는 `scraper.py`는 예제 HTML 구조를 기반으로 작성되었습니다.
실제 사용하시는 카페테리아 사이트의 DOM 구조에 맞게 `scraper.py` 내부의 BeautifulSoup 셀렉터(`soup.find(...)`)를 수정하여 사용하세요.

## 📝 릴리즈 및 개발 히스토리
- [개발 버전 히스토리 문서](docs/dev-history.md)를 참고하세요.
