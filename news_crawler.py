import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class NewsCrawler:
    def __init__(self):
        self.client_id = os.getenv("NAVER_CLIENT_ID")
        self.client_secret = os.getenv("NAVER_CLIENT_SECRET")
        self.base_url = "https://openapi.naver.com/v1/search/news.json"

    def fetch_news(self, query, display=20):
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        params = {
            "query": query,
            "display": display,
            "sort": "sim"
        }
        
        response = requests.get(self.base_url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            print(f"Error fetching news for {query}: {response.status_code}")
            return []

    def get_daily_reports(self):
        from email.utils import parsedate_to_datetime
        from datetime import timezone
        
        now = datetime.now(timezone.utc)
        # 2,000건 이상의 방대한 데이터를 확보하기 위한 키워드 대폭 확장
        categories = {
            "정치 핵심 (필수 분석)": [
                "한동훈", "이재명", "국민의힘", "더불어민주당", "대통령실", "정국 주도권", "정계 개편", "제명", "사법 리스크",
                "국방", "외교", "안보 이슈", "대통령 지지율", "비상계엄", "탄핵", "조기 대선", "개혁신당", "조국혁신당",
                "여당 내분", "야당 공세", "국회 마비", "정치 개혁", "민생 입법"
            ],
            "국제 정세 및 글로벌 소식 (필수 반영)": [
                "트럼프", "시진핑", "푸틴", "김정은", "세계 정상", "일본 총리", "국제 정세", "외교부", "백악관", "해외 지도자 인사", "국제 분쟁"
            ],
            "정치 지역 및 정세": [
                "수도권 민심", "영남 정치", "호남 민심", "충청 캐스팅보트", "정치권 여론조사", "보수 결집", "진보 재편",
                "한동훈 행보", "이재명 재판", "장동혁", "김건희 여사", "특검법", "거부권 정국"
            ],
            "문화체육관광위원회 (상임위 정책)": [
                "문화체육관광부", "문체부 광주 이전", "지방 이전", "K-컬처 콘텐츠", "관광 산업", "스포츠", "국회 문체위",
                "문학계 소식", "게임 산업 규제", "예술인 지원", "체육회 개혁"
            ],
            "사회 및 민생": [
                "민생 경제", "물가", "금리 인상", "부동산 시장", "전세 사기", "사회 현안",
                "노동 개혁", "교육 비전", "저출산 대책", "연금 개혁"
            ],
            "청년 및 장애인 (집중 트래킹)": [
                "청년 정책", "청년 취업", "청년 주거", "청년 면접", "청년 수당", "고립 은둔 청년",
                "장애인 복지", "장애인 권익", "특수 교육", "장애인 고용", "이동권 보장", "장애인 인권",
                "교통약자", "발달장애", "지역사회 자립", "장애인 정책"
            ]
        }
        all_news = {}
        
        for cat, kws in categories.items():
            cat_items = []
            display_count = 100 if "정치" in cat else 50 
            
            # 카테고리에 따른 시간 필터 설정 (청년/장애인은 14일, 나머지는 24시간)
            hours_limit = 14 * 24 if "청년 및 장애인" in cat else 24
            
            for kw in kws:
                news_items = self.fetch_news(kw, display=display_count)
                for item in news_items:
                    pub_date_str = item.get("pubDate")
                    if pub_date_str:
                        try:
                            pub_date = parsedate_to_datetime(pub_date_str)
                            if now - pub_date > timedelta(hours=hours_limit):
                                continue
                        except:
                            pass
                            
                    cat_items.append({
                        "title": item.get("title", ""),
                        "description": item.get("description", ""),
                        "link": item.get("originallink", item.get("link", ""))
                    })
            all_news[cat] = cat_items
            
        return all_news

if __name__ == "__main__":
    crawler = NewsCrawler()
    results = crawler.get_daily_reports()
    for kw, items in results.items():
        print(f"Keyword: {kw}, Found: {len(items)} items")
