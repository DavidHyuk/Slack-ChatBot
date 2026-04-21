import requests
from bs4 import BeautifulSoup
import logging
from typing import Any, Dict, List, Optional
import re

logger = logging.getLogger(__name__)

_WS_RE = re.compile(r"\s+")

def _clean_text(s: str) -> str:
    return _WS_RE.sub(" ", (s or "").strip())


_SIDES_HEADING = re.compile(r"^(?:SIDES?)\s*:\s*", re.IGNORECASE)


def _strip_redundant_sides_heading(s: str) -> str:
    """페이지 텍스트에 이미 붙은 SIDES:/SIDE: 라벨 제거 (_Sides:_ 와 중복 방지)."""
    t = _clean_text(s)
    while True:
        n = _SIDES_HEADING.sub("", t, count=1)
        if n == t:
            break
        t = _clean_text(n)
    return t


def _station_emoji(station: str) -> str:
    """스테이션 이름(예: @Soup)에 맞는 짧은 이모지. 매칭 없으면 기본값."""
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


def get_todays_menu(url: str) -> Optional[Dict[str, Any]]:
    """
    대상 카페테리아 URL에서 오늘의 메뉴와 사진 URL을 스크래핑합니다.
    Slack 가시성용으로 ``stations``(식당/스테이션별 항목 리스트)를 포함할 수 있습니다.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 'Lunch Specials' 탭 컨텐츠를 담고 있는 컨테이너 찾기
        lunch_specials_container = None
        for tab_content in soup.find_all('div', class_='c-tab__content'):
            # 내부의 'Lunch Specials'를 의미하는 특정 id나 구조인지 확인
            # 주어진 HTML에서는 <button>에 Lunch Specials가 적혀 있고, aria-controls로 tab-content를 가리킴.
            # 여기서는 편의상 모든 c-tab__content 내부에서 메뉴 아이템들을 수집합니다.
            if 'site-panel__daypart-tab-content' in tab_content.get('class', []):
                lunch_specials_container = tab_content
                break
                
        # 만약 못 찾으면 첫 번째 daypart-wrapper를 사용
        if not lunch_specials_container:
            lunch_specials_container = soup.find('div', class_='site-panel__daypart-wrapper')

        if not lunch_specials_container:
            logger.warning("메뉴 요소를 찾을 수 없습니다. (class='site-panel__daypart-wrapper')")
            return {
                "menu_text": "😢 Couldn't load today's menu.",
                "stations": [],
            }
            
        menu_items = []
        # 각 개별 메뉴 항목 찾기
        item_divs = lunch_specials_container.find_all('div', class_='site-panel__daypart-item-container')
        
        for item in item_divs:
            # 메뉴 제목
            title_btn = item.find('button', class_='site-panel__daypart-item-title')
            if not title_btn:
                continue
                
            # 불필요한 span(아이콘 등) 제거 후 텍스트만 추출
            for span in title_btn.find_all('span'):
                span.decompose()
            title_text = _clean_text(title_btn.get_text(" ", strip=True))
            
            # 메뉴 설명
            desc_div = item.find('div', class_='site-panel__daypart-item-description')
            desc_text = ""
            sides_text = ""
            if desc_div:
                # 불필요한 주석이나 빈 줄바꿈 등을 정리
                for tag in desc_div.find_all(['br', 'hr']):
                    tag.replace_with(' ')
                # 'SIDES:' 같은 부가 정보 영역이 있다면 조금 다듬기
                sides_div = desc_div.find('div', class_='site-panel__daypart-item-sides')
                if sides_div:
                    sides_text = _strip_redundant_sides_heading(
                        sides_div.get_text(separator=" ", strip=True)
                    )
                    sides_div.extract()
                    base_desc = _clean_text(desc_div.get_text(separator=" ", strip=True))
                    desc_text = base_desc
                else:
                    desc_text = _clean_text(desc_div.get_text(separator=" ", strip=True))
            
            # 스테이션 이름 (예: @Korean, @Spice 등)
            station_div = item.find('div', class_='site-panel__daypart-item-station')
            station_text = _clean_text(station_div.get_text(" ", strip=True)) if station_div else ""

            menu_items.append(
                {
                    "title": title_text,
                    "station": station_text,
                    "desc": desc_text,
                    "sides": sides_text,
                }
            )

            
        if not menu_items:
            menu_text = "📭 No menu items today."
            stations: List[Dict[str, Any]] = []
        else:
            # 스테이션(식당)별로 묶기 — 순서 유지
            station_order: List[str] = []
            by_station: Dict[str, List[Dict[str, str]]] = {}
            for it in menu_items:
                st = it.get("station") or "Other"
                if st not in by_station:
                    by_station[st] = []
                    station_order.append(st)
                by_station[st].append(it)

            stations = []
            lines = []
            for st in station_order:
                raw_items = by_station[st]
                items_out: List[Dict[str, str]] = []
                icon = _station_emoji(st)
                lines.append(f"{icon} *{st}*")
                for it in raw_items:
                    title = it.get("title") or ""
                    desc = it.get("desc") or ""
                    sides = it.get("sides") or ""
                    items_out.append(
                        {"title": title, "desc": desc, "sides": sides}
                    )
                    if desc and sides:
                        lines.append(f"  • *{title}* — {desc}")
                        lines.append(f"    🥗 _Sides:_ {sides}")
                    elif desc:
                        lines.append(f"  • *{title}* — {desc}")
                    elif sides:
                        lines.append(f"  • *{title}*")
                        lines.append(f"    🥗 _Sides:_ {sides}")
                    else:
                        lines.append(f"  • *{title}*")
                lines.append("")
                stations.append({"station": st, "items": items_out})

            menu_text = "\n".join(lines).strip()

        # 해당 사이트는 목록에 직접 이미지 URL이 없음. Slack image 블록은 공개 HTTPS에서
        # Slack 서버가 직접 다운로드 가능한 URL만 허용되므로, 플레이스홀더 외부 URL은 넣지 않음.
        return {
            "menu_text": menu_text,
            "stations": stations,
        }
        
    except requests.RequestException as e:
        logger.error(f"URL 요청 중 에러 발생: {e}")
        return None
    except Exception as e:
        logger.error(f"스크래핑 중 예상치 못한 에러 발생: {e}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_url = "http://example-cafeteria.com"
    result = get_todays_menu(test_url)
    print(f"Scraped Result: {result}")

