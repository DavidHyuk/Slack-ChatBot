import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _station_emoji(station: str) -> str:
    s = (station or "").lower()
    if "soup" in s:
        return "🥣"
    if "korean" in s:
        return "🍚"
    if "sushi" in s:
        return "🍣"
    if "blue plate" in s:
        return "🍽️"
    if "spice" in s:
        return "🌮"
    if "fire" in s:
        return "🌶️"
    if "grill" in s or "bbq" in s:
        return "🔥"
    if "salad" in s:
        return "🥗"
    if "dessert" in s or "sweet" in s:
        return "🍰"
    if "beverage" in s or "drink" in s:
        return "🥤"
    return "📍"


def _station_display_name(station: str) -> str:
    """@Soup → Soup (Slack 헤더/강조용 표시 이름)."""
    s = (station or "").strip()
    if s.startswith("@"):
        s = s[1:].strip()
    return s or "Other"


def _format_station_mrkdwn(station_key: str, items: List[Dict[str, str]]) -> str:
    icon = _station_emoji(station_key)
    name = _station_display_name(station_key)
    lines = [f"{icon} *{name}*", ""]
    for it in items:
        title = it.get("title") or ""
        desc = (it.get("desc") or "").strip()
        sides = (it.get("sides") or "").strip()
        if desc and sides:
            lines.append(f"• *{title}* — {desc}")
            lines.append(f"  🥗 _Sides:_ {sides}")
        elif desc:
            lines.append(f"• *{title}* — {desc}")
        elif sides:
            lines.append(f"• *{title}*")
            lines.append(f"  🥗 _Sides:_ {sides}")
        else:
            lines.append(f"• *{title}*")
    return "\n".join(lines).strip()


class SlackBot:
    def __init__(self, token: str, channel_id: str):
        """
        Slack API 클라이언트와 채널 ID 초기화
        """
        self.client = WebClient(token=token)
        self.channel_id = channel_id

    def build_menu_blocks(self, menu_data: Dict[str, Any]) -> list:
        """
        메뉴 텍스트와 이미지 URL을 Slack Block Kit 형식으로 변환합니다.
        ``stations``가 있으면 식당(스테이션)마다 ``divider`` + ``section``으로 나눕니다.
        """
        menu_text = menu_data.get("menu_text", "Unable to load today's menu.")
        image_url = menu_data.get("image_url")
        stations: Optional[List[Dict[str, Any]]] = menu_data.get("stations")

        blocks: List[Dict[str, Any]] = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🍽️ Today's cafeteria menu",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "✨ *Enjoy your lunch today!*",
                },
            },
        ]

        if image_url:
            blocks.append(
                {
                    "type": "image",
                    "image_url": image_url,
                    "alt_text": "Today's menu photo",
                }
            )

        if stations:
            for block in stations:
                station_key = str(block.get("station") or "Other")
                items = block.get("items") or []
                if not items:
                    continue
                blocks.append({"type": "divider"})
                body = _format_station_mrkdwn(station_key, items)
                blocks.append(
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": body},
                    }
                )
        else:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": menu_text,
                    },
                }
            )

        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🤖 Sent automatically by the bot.",
                    }
                ],
            }
        )

        return blocks

    def _slack_error_detail_text(self, response: Dict[str, Any]) -> str:
        parts = []
        errs = response.get("errors")
        if isinstance(errs, list):
            parts.extend(errs)
        elif errs:
            parts.append(str(errs))
        meta = response.get("response_metadata") or {}
        msgs = meta.get("messages")
        if isinstance(msgs, list):
            parts.extend(msgs)
        elif msgs:
            parts.append(str(msgs))
        return " ".join(parts).lower()

    def send_menu_message(self, menu_data: Dict[str, Any]) -> bool:
        """
        Slack 채널에 Block Kit 메시지를 전송합니다.
        image_url을 Slack 서버가 가져오지 못하면 invalid_blocks가 나므로, 이미지 없이 한 번 더 시도합니다.
        """
        blocks = self.build_menu_blocks(menu_data)
        fallback_text = "Today's cafeteria menu is here!"

        try:
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=blocks,
                text=fallback_text,
            )
            logger.info(f"Message posted successfully: {response['ts']}")
            return True
        except SlackApiError as e:
            resp = e.response
            error_code = resp.get("error")
            detail = self._slack_error_detail_text(resp)
            image_fail = (
                error_code == "invalid_blocks"
                and bool(menu_data.get("image_url"))
                and "downloading image failed" in detail
            )
            if image_fail:
                logger.warning(
                    "Slack could not fetch image_url; retrying without the image block."
                )
                retry_blocks = self.build_menu_blocks({**menu_data, "image_url": None})
                try:
                    response = self.client.chat_postMessage(
                        channel=self.channel_id,
                        blocks=retry_blocks,
                        text=fallback_text,
                    )
                    logger.info(f"Message posted successfully (no image): {response['ts']}")
                    return True
                except SlackApiError as e2:
                    logger.error(f"Slack API error: {e2.response.get('error')}")
                    return False

            logger.error(f"Slack API error: {error_code}")
            return False

if __name__ == "__main__":
    # 간단한 테스트
    logging.basicConfig(level=logging.INFO)
    dummy_token = os.environ.get("SLACK_BOT_TOKEN", "xoxb-dummy")
    dummy_channel = os.environ.get("SLACK_CHANNEL_ID", "C_DUMMY")
    
    bot = SlackBot(dummy_token, dummy_channel)
    test_data = {
        "menu_text": "현미밥, 김치찌개, 계란말이",
        "image_url": "https://images.unsplash.com/photo-1547592166-23ac45744acd?q=80&w=800&auto=format&fit=crop"
    }
    
    # 실제 토큰 없이는 에러가 발생하므로 주석 처리
    # bot.send_menu_message(test_data)
    print("Block Kit JSON:", bot.build_menu_blocks(test_data))
