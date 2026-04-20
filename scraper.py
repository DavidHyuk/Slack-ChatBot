import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def get_todays_menu(url: str) -> Optional[Dict[str, str]]:
    """
    대상 카페테리아 URL에서 오늘의 메뉴와 사진 URL을 스크래핑합니다.
    (실제 카페테리아 사이트 HTML 구조에 맞게 수정이 필요합니다.)
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 예시 HTML 구조 가정:
        # <div class="daily-menu">
        #   <h2>오늘의 메뉴</h2>
        #   <p class="menu-text">백미밥, 김치찌개, 돈육불고기, 계란말이, 깍두기</p>
        #   <img class="menu-image" src="/images/menu/20260420.jpg" alt="메뉴 이미지" />
        # </div>
        
        # 실제 DOM 요소 셀렉터로 수정하세요.
        menu_div = soup.find('div', class_='daily-menu')
        
        if not menu_div:
            logger.warning("메뉴 요소를 찾을 수 없습니다. (class='daily-menu')")
            # 스크래핑 테스트/예외 처리를 위한 더미 데이터 반환 (실제 환경에서는 None 반환 고려)
            return {
                "menu_text": "현미밥\n소고기 미역국\n제육볶음\n계란말이\n배추김치\n그린샐러드",
                "image_url": "https://images.unsplash.com/photo-1547592166-23ac45744acd?q=80&w=800&auto=format&fit=crop"
            }
            
        menu_text_elem = menu_div.find('p', class_='menu-text')
        menu_image_elem = menu_div.find('img', class_='menu-image')
        
        menu_text = menu_text_elem.get_text(strip=True) if menu_text_elem else "메뉴 텍스트를 찾을 수 없습니다."
        image_url = menu_image_elem.get('src') if menu_image_elem else None
        
        # 상대 경로인 경우 절대 경로로 변환 (필요시)
        if image_url and image_url.startswith('/'):
            from urllib.parse import urljoin
            image_url = urljoin(url, image_url)
            
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
