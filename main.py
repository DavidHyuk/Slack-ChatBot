import os
import sys
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from scraper import get_todays_menu
from slack_bot import SlackBot

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG, # DEBUG 레벨로 변경하여 HTML 확인
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _menu_date_tz_name() -> str:
    return os.environ.get(
        "MENU_DATE_TZ",
        os.environ.get("MENU_NOTIFY_TZ", "America/Los_Angeles"),
    )


def resolve_target_url(raw: str) -> str:
    """If TARGET_URL contains ``{date}``, substitute YYYY-MM-DD in MENU_DATE_TZ."""
    if "{date}" in raw:
        d = datetime.now(ZoneInfo(_menu_date_tz_name())).date().isoformat()
        return raw.replace("{date}", d)
    return raw


def should_skip_outside_notify_window() -> bool:
    """
    When ENFORCE_LOCAL_NOTIFY_WINDOW is set, skip unless local clock hour
    matches MENU_NOTIFY_HOUR (used with two UTC crons for DST-safe 8am PT).
    """
    flag = os.environ.get("ENFORCE_LOCAL_NOTIFY_WINDOW", "").strip().lower()
    if flag not in ("1", "true", "yes"):
        return False
    # Actions 수동 실행은 언제든 전체 플로우 실행
    if os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch":
        return False
    tz_name = os.environ.get("MENU_NOTIFY_TZ", "America/Los_Angeles")
    try:
        hour_target = int(os.environ.get("MENU_NOTIFY_HOUR", "8"))
    except ValueError:
        hour_target = 8
    now = datetime.now(ZoneInfo(tz_name))
    return now.hour != hour_target


def main():
    # 환경 변수 로드 (.env 파일이 있다면 로드됨)
    load_dotenv()

    if should_skip_outside_notify_window():
        tz = os.environ.get("MENU_NOTIFY_TZ", "America/Los_Angeles")
        hr = os.environ.get("MENU_NOTIFY_HOUR", "8")
        logger.info(
            "로컬 알림 시간이 아니어서 건너뜁니다 (timezone=%s, 대상 시각=%s시).",
            tz,
            hr,
        )
        sys.exit(0)

    # 환경 변수 확인
    raw_url = os.environ.get("TARGET_URL")
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    slack_channel = os.environ.get("SLACK_CHANNEL_ID")

    if not raw_url:
        logger.error("TARGET_URL 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)

    target_url = resolve_target_url(raw_url.strip())
    logger.info("요청 URL: %s", target_url)

    if not slack_token or not slack_channel:
        logger.error("SLACK_BOT_TOKEN 또는 SLACK_CHANNEL_ID 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)

    logger.info("카페테리아 메뉴 스크래핑을 시작합니다...")
    menu_data = get_todays_menu(target_url)
    
    if not menu_data:
        logger.error("메뉴 정보를 가져오는데 실패했습니다.")
        # 실패 메시지를 Slack으로 보내는 로직을 추가할 수도 있습니다.
        sys.exit(1)
        
    logger.info(f"성공적으로 메뉴 정보를 가져왔습니다. 텍스트 길이: {len(menu_data.get('menu_text', ''))}")
    
    # 디버깅을 위해 메뉴 텍스트를 파일로 저장
    try:
        with open("debug_menu_output.txt", "w", encoding="utf-8") as f:
            f.write(menu_data.get('menu_text', ''))
        logger.info("메뉴 텍스트를 debug_menu_output.txt 파일에 저장했습니다.")
    except Exception as e:
        logger.error(f"메뉴 텍스트 파일 저장 실패: {e}")
        
    # Slack 전송
    logger.info(f"Slack 채널({slack_channel})로 메시지를 전송합니다...")
    bot = SlackBot(token=slack_token, channel_id=slack_channel)
    success = bot.send_menu_message(menu_data)
    
    if success:
        logger.info("Slack 메시지 전송이 완료되었습니다.")
        sys.exit(0)
    else:
        logger.error("Slack 메시지 전송에 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()
