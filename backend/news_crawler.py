import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict

async def crawl_news(category: str, limit: int = 10) -> List[Dict]:
    """
    뉴스 크롤링
    category: stock, futures, crypto
    """
    news_list = []
    
    if category == "stock":
        # 네이버 금융 뉴스
        news_list = await crawl_naver_finance(limit)
    elif category == "futures":
        # 해외선물 뉴스 (인베스팅닷컴)
        news_list = await crawl_investing_futures(limit)
    elif category == "crypto":
        # 코인 뉴스 (업비트, 코인데스크)
        news_list = await crawl_crypto_news(limit)
    
    return news_list

async def crawl_naver_finance(limit: int = 10) -> List[Dict]:
    """네이버 금융 뉴스 크롤링"""
    url = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                news_list = []
                articles = soup.select('.newsList .articleSubject')[:limit]
                
                for article in articles:
                    title = article.get_text(strip=True)
                    link = "https://finance.naver.com" + article.get('href', '')
                    
                    news_list.append({
                        'title': title,
                        'url': link,
                        'source': '네이버 금융',
                        'published_at': datetime.utcnow().isoformat(),
                        'category': 'stock'
                    })
                
                return news_list
    except Exception as e:
        print(f"네이버 금융 크롤링 오류: {e}")
        return []

async def crawl_investing_futures(limit: int = 10) -> List[Dict]:
    """해외선물 뉴스 크롤링 (Investing.com)"""
    # 인베스팅닷컴은 크롤링 방지가 있어서 RSS 피드 사용 권장
    url = "https://kr.investing.com/news/commodities-news"
    
    try:
        # 실제 구현 시 RSS 피드나 API 사용 권장
        news_list = [
            {
                'title': '금 선물, 연준 발언 앞두고 약보합',
                'url': 'https://kr.investing.com/news/example1',
                'source': 'Investing.com',
                'published_at': datetime.utcnow().isoformat(),
                'category': 'futures'
            },
            {
                'title': '원유 선물 상승, OPEC+ 감산 연장 전망',
                'url': 'https://kr.investing.com/news/example2',
                'source': 'Investing.com',
                'published_at': datetime.utcnow().isoformat(),
                'category': 'futures'
            }
        ]
        return news_list[:limit]
    except Exception as e:
        print(f"해외선물 뉴스 크롤링 오류: {e}")
        return []

async def crawl_crypto_news(limit: int = 10) -> List[Dict]:
    """코인 뉴스 크롤링"""
    # CoinDesk Korea RSS 또는 업비트 공지사항
    url = "https://www.upbit.com/service_center/notice"
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            async with session.get(url, headers=headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                news_list = []
                # 업비트 공지사항 파싱 (실제 선택자는 사이트 구조에 따라 변경 필요)
                # 예시 데이터
                news_list = [
                    {
                        'title': '비트코인 급등, 기관 투자 증가',
                        'url': 'https://www.upbit.com/service_center/notice/1',
                        'source': '업비트',
                        'published_at': datetime.utcnow().isoformat(),
                        'category': 'crypto'
                    },
                    {
                        'title': '이더리움 2.0 업그레이드 임박',
                        'url': 'https://www.upbit.com/service_center/notice/2',
                        'source': '업비트',
                        'published_at': datetime.utcnow().isoformat(),
                        'category': 'crypto'
                    }
                ]
                
                return news_list[:limit]
    except Exception as e:
        print(f"코인 뉴스 크롤링 오류: {e}")
        # 오류 시 더미 데이터 반환
        return [
            {
                'title': '암호화폐 시장 동향',
                'url': '#',
                'source': '크립토뉴스',
                'published_at': datetime.utcnow().isoformat(),
                'category': 'crypto'
            }
        ]

# 뉴스 DB 저장 함수
async def save_news_to_db(news_list: List[Dict], db):
    """크롤링한 뉴스를 DB에 저장"""
    from models import News
    
    for news_data in news_list:
        # 중복 확인
        existing = db.query(News).filter(News.url == news_data['url']).first()
        if not existing:
            news = News(**news_data)
            db.add(news)
    
    db.commit()
