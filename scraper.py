import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def get_todays_menu(url: str) -> Optional[Dict[str, str]]:
    """
    대상 카페테리아 URL에서 오늘의 메뉴와 사진 URL을 스크래핑합니다.
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
                "menu_text": "오늘의 메뉴를 불러올 수 없습니다.",
                "image_url": "https://images.unsplash.com/photo-1547592166-23ac45744acd?q=80&w=800&auto=format&fit=crop"
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
            title_text = title_btn.get_text(strip=True)
            
            # 메뉴 설명
            desc_div = item.find('div', class_='site-panel__daypart-item-description')
            desc_text = ""
            if desc_div:
                # 불필요한 주석이나 빈 줄바꿈 등을 정리
                for tag in desc_div.find_all(['br', 'hr']):
                    tag.replace_with(' ')
                # 'SIDES:' 같은 부가 정보 영역이 있다면 조금 다듬기
                sides_div = desc_div.find('div', class_='site-panel__daypart-item-sides')
                if sides_div:
                    sides_text = sides_div.get_text(separator=' ', strip=True)
                    sides_div.extract()
                    base_desc = desc_div.get_text(separator=' ', strip=True)
                    desc_text = f"{base_desc} [{sides_text}]"
                else:
                    desc_text = desc_div.get_text(separator=' ', strip=True)
            
            # 스테이션 이름 (예: @Korean, @Spice 등)
            station_div = item.find('div', class_='site-panel__daypart-item-station')
            station_text = station_div.get_text(strip=True) if station_div else ""
            
            # 텍스트 조립
            if desc_text:
                menu_str = f"• *{title_text}* {station_text}\n  └ {desc_text}"
            else:
                menu_str = f"• *{title_text}* {station_text}"
                
            menu_items.append(menu_str)

            
        if not menu_items:
            menu_text = "메뉴 항목이 없습니다."
        else:
            menu_text = "\n\n".join(menu_items)
            
        # 해당 사이트는 개별 음식 사진이 목록에 노출되지 않으므로 고정 이미지나 None 사용
        image_url = "https://images.unsplash.com/photo-1498837167922-41c46b66c07a?q=80&w=800&auto=format&fit=crop"
        
        return {
            "menu_text": menu_text,
            "image_url": image_url
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

