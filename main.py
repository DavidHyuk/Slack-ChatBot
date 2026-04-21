import os
import sys
import logging
import json
import time
from dotenv import load_dotenv
from scraper import get_todays_menu
from slack_bot import SlackBot

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG, # DEBUG 레벨로 변경하여 HTML 확인
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # 환경 변수 로드 (.env 파일이 있다면 로드됨)
    load_dotenv()
    
    # 환경 변수 확인
    target_url = os.environ.get("TARGET_URL")
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    slack_channel = os.environ.get("SLACK_CHANNEL_ID")
    
    if not target_url:
        logger.error("TARGET_URL 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)
        
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
