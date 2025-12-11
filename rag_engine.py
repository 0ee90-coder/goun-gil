"""
🎯 종로구 관광 코스 추천 시스템 RAG Engine (최적화 버전)
- 벡터스토어 중복 제거
- RAG 검색 다양성 보장 (MMR)
- TSP 경로 최적화
- Content 기반 추천
- Streamlit 완벽 호환
"""

import json
import os
import math
import re
from itertools import permutations
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# 환경 변수 로드
load_dotenv()


class TourRecommendationEngine:
    """관광 코스 추천 엔진"""
    
    def __init__(self):
        """초기화"""
        # API 키 확인 (Streamlit secrets 우선, 환경 변수 fallback)
        try:
            import streamlit as st
            api_key = st.secrets.get("OPENAI_API_KEY")
        except:
            api_key = None
        
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY가 설정되지 않았습니다. "
                ".env 파일 또는 .streamlit/secrets.toml에 API 키를 추가하세요."
            )
        
        # LLM 설정
        self.llm = ChatOpenAI(model="gpt-5.1", temperature=0.7, api_key=api_key)
        self.rerank_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=api_key)
        
        # 상수
        self.WALK_SPEED_NORMAL = 4.0
        self.WALK_SPEED_SLOW = 2.5
        
        # 데이터 저장
        self.integrated_data = None
        self.vectorstore = None
        
        print("✅ RAG Engine 초기화 완료!")
    
    
    def load_json_with_dedup(self, tour_path: str, cafe_path: str, restaurant_path: str) -> Dict:
        """JSON 로드 + 중복 제거"""
        def load_and_dedup(path, category_name):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 제목 기준 중복 제거
            seen = set()
            unique_data = []
            duplicates = 0
            
            for item in data:
                title = item.get('title', '')
                if title and title not in seen:
                    seen.add(title)
                    unique_data.append(item)
                else:
                    duplicates += 1
            
            print(f"  {category_name}: {len(data)}개 → {len(unique_data)}개 (중복 {duplicates}개 제거)")
            return unique_data
        
        print("\n📖 데이터 로드 중...")
        tour_data = load_and_dedup(tour_path, "관광지")
        cafe_data = load_and_dedup(cafe_path, "카페")
        restaurant_data = load_and_dedup(restaurant_path, "음식점")
        
        integrated = {
            'tour': {item['title']: item for item in tour_data},
            'cafe': {item['title']: item for item in cafe_data},
            'restaurant': {item['title']: item for item in restaurant_data}
        }
        
        print(f"\n✅ 총 {len(tour_data) + len(cafe_data) + len(restaurant_data)}개 장소 로드 완료!\n")
        self.integrated_data = integrated
        return integrated
    
    
    def setup_vectorstore(self) -> Chroma:
        """벡터스토어 생성 (메모리에만 저장)"""
        if not self.integrated_data:
            raise ValueError("먼저 load_json_with_dedup()를 실행하세요!")
        
        print("\n" + "="*60)
        print("📚 벡터스토어 설정")
        print("="*60)
        
        print("📝 문서 생성 중...")
        documents = []
        
        for category_key, category_name in [('tour', '관광지'), ('cafe', '카페'), ('restaurant', '음식점')]:
            for title, data in self.integrated_data[category_key].items():
                content = data.get('content', '')
                if content:
                    # facilities를 문자열로 변환
                    facilities = data.get('facilities', '')
                    if isinstance(facilities, list):
                        facilities = ', '.join(facilities)
                    
                    # 좌표 안전하게 추출
                    lat = self._extract_coordinate(data, 'latitude')
                    lng = self._extract_coordinate(data, 'longitude')
                    
                    doc = Document(
                        page_content=content,
                        metadata={
                            'title': title,
                            'category': category_name,
                            'address': data.get('address', ''),
                            'content': content,
                            'facilities': facilities,
                            'latitude': lat,
                            'longitude': lng
                        }
                    )
                    documents.append(doc)
        
        print(f"📝 총 {len(documents)}개 문서 생성")
        
        # 벡터스토어 생성 (메모리만 사용)
        print("🔄 벡터 임베딩 중... (시간이 걸릴 수 있습니다)")
        
        # Chroma 클라이언트 설정 (메모리 전용)
        import chromadb
        
        # EphemeralClient 사용 (메모리 전용, 테이블 오류 방지)
        chroma_client = chromadb.EphemeralClient()

        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            client=chroma_client,
            collection_name="goun_gil_collection"
        )
        
        print("✅ 벡터스토어 생성 완료!")
        return self.vectorstore
    
    
    @staticmethod
    def _extract_coordinate(data: Dict, coord_type: str) -> float:
        """좌표 안전하게 추출 (1_map.py와 동일한 로직)"""
        # 1. coordinates 객체에서 찾기
        if 'coordinates' in data:
            coords = data['coordinates']
            value = coords.get(coord_type)
            if value:
                try:
                    return float(value)
                except (ValueError, TypeError):
                    pass
        
        # 2. 최상위 레벨에서 찾기
        value = data.get(coord_type)
        if value:
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
        
        # 3. mapx/mapy fallback
        if coord_type == 'longitude':
            value = data.get('mapx')
        elif coord_type == 'latitude':
            value = data.get('mapy')
        
        if value:
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
        
        return 0.0
    
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """두 좌표 간 거리 계산 (km)"""
        R = 6371
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    
    def openai_rerank(self, query: str, documents: List, top_k: int = 10) -> List:
        """OpenAI 기반 Reranker"""
        if len(documents) == 0:
            return []
        
        if len(documents) <= top_k:
            return documents
        
        doc_list = "\n".join([
            f"{i+1}. {doc.metadata.get('title', 'Unknown')}: {doc.metadata.get('content', '')[:100]}"
            for i, doc in enumerate(documents)
        ])
        
        prompt = f"""
쿼리: {query}

문서 목록:
{doc_list}

관련성이 높은 순서대로 상위 {top_k}개의 번호만 쉼표로 구분하여 출력하세요.
예: 3,1,5,2,7,4,9,6,8,10
"""
        
        try:
            response = self.rerank_llm.invoke(prompt)
            indices = [int(x.strip())-1 for x in response.content.strip().split(',')]
            reranked = [documents[i] for i in indices if 0 <= i < len(documents)]
            return reranked[:top_k]
        except Exception as e:
            print(f"⚠️ Reranker 오류: {e}")
            return documents[:top_k]
    
    
    def search_places(self, user_type: str, trip_purpose: str, category: str, 
                     region: Optional[str] = None, top_k: int = 10) -> List[Dict]:
        """장소 검색 + 중복 제거 + 다양성 보장 + 지역 필터링"""
        if not self.vectorstore:
            raise ValueError("먼저 setup_vectorstore()를 실행하세요!")
        
        if isinstance(trip_purpose, list):
            trip_purpose = " ".join(trip_purpose)
        
        query = f"{user_type}에게 적합한 {trip_purpose} 분위기의 {category}. 접근성이 좋고 시설이 잘 갖춰진 곳."
        
        # 지역 필터 추가
        search_kwargs = {
            "k": 50,
            "fetch_k": 100,
            "lambda_mult": 0.7,
            "filter": {"category": category}
        }
        
        retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs=search_kwargs
        )
        
        candidates = retriever.invoke(query)
        
        # 지역 필터링 (region이 지정된 경우)
        if region:
            filtered_candidates = [
                doc for doc in candidates 
                if region in doc.metadata.get('address', '')
            ]
            if filtered_candidates:
                candidates = filtered_candidates
                print(f"  {category}: {region} 필터 적용 → {len(candidates)}개")
        
        print(f"  {category}: MMR로 {len(candidates)}개 검색")
        
        # Reranker로 정렬
        reranked = self.openai_rerank(query, candidates, top_k=top_k * 2)
        print(f"  {category}: Reranker로 {len(reranked)}개 정렬")
        
        # 중복 제거
        seen_titles = set()
        unique_results = []
        
        for doc in reranked:
            title = doc.metadata.get('title', '')
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_results.append(doc.metadata)
                if len(unique_results) >= top_k:
                    break
        
        print(f"  {category}: 중복 제거 후 {len(unique_results)}개 최종 선택\n")
        return unique_results
    
    
    def create_courses(self, user_type: str, trip_purpose: List[str], 
                      region: Optional[str] = None) -> List[Dict]:
        """LLM으로 코스 생성 (Streamlit 호환 버전)"""
        print(f"\n{'='*60}")
        print(f"🎯 {user_type} - {' '.join(trip_purpose)} 분위기")
        if region:
            print(f"📍 지역: {region}")
        print(f"{'='*60}\n")
        
        print("🔍 장소 검색 중...")
        tour_list = self.search_places(user_type, trip_purpose, "관광지", region, 10)
        cafe_list = self.search_places(user_type, trip_purpose, "카페", region, 10)
        restaurant_list = self.search_places(user_type, trip_purpose, "음식점", region, 10)
        
        print(f"✅ 총 {len(tour_list) + len(cafe_list) + len(restaurant_list)}개 장소 검색 완료\n")
        
        # 원본 데이터에서 전체 정보 가져오기
        def get_full_data(place_name, category_key):
            """장소 이름으로 전체 데이터 가져오기"""
            full_data = self.integrated_data[category_key].get(place_name)
            if not full_data:
                print(f"⚠️ 경고: {category_key}에서 '{place_name}'을 찾을 수 없습니다.")
                return None
            return full_data
        
        # LLM으로 코스 생성
        llm_output, data_dict = self._create_courses_llm(user_type, trip_purpose, 
                                                         tour_list, cafe_list, restaurant_list)
        
        # 파싱
        courses = self.parse_llm_result(llm_output, data_dict)
        
        if len(courses) == 0:
            print("⚠️ 파싱 실패!")
            return []
        
        # TSP 최적화
        optimized_courses = self.optimize_all_courses(courses, data_dict)
        
        # RAG 설명 생성
        print("\n" + "="*60)
        print("📝 RAG 설명 생성")
        print("="*60)
        
        courses_with_explanation = []
        
        for course in optimized_courses:
            try:
                explained = self.generate_course_explanation(course, data_dict, user_type)
                
                # ⭐ 카테고리별로 장소 찾기 + optimized_order 생성
                tour_place = None
                cafe_place = None
                restaurant_place = None
                optimized_order = []  # 최적화된 순서 저장
                
                # places의 구조 확인
                for place in course['places']:
                    # place가 딕셔너리인지 확인
                    if isinstance(place, dict):
                        place_name = place['name']
                        category = place['category']
                    else:
                        # place가 문자열이면 data_dict에서 찾기
                        print(f"⚠️ place가 문자열입니다: {place}")
                        place_name = place
                        # data_dict에서 카테고리 찾기
                        if place_name in data_dict['tour']:
                            category = 'tour'
                        elif place_name in data_dict['cafe']:
                            category = 'cafe'
                        elif place_name in data_dict['restaurant']:
                            category = 'restaurant'
                        else:
                            print(f"⚠️ '{place_name}'의 카테고리를 찾을 수 없습니다.")
                            continue
                    
                    # optimized_order에 순서대로 추가
                    optimized_order.append(category)
                    
                    # 카테고리에 따라 데이터 가져오기
                    if category == 'tour':
                        tour_place = get_full_data(place_name, 'tour')
                    elif category == 'cafe':
                        cafe_place = get_full_data(place_name, 'cafe')
                    elif category == 'restaurant':
                        restaurant_place = get_full_data(place_name, 'restaurant')
                
                # 3개 장소가 모두 있는지 확인
                if not tour_place or not cafe_place or not restaurant_place:
                    print(f"⚠️ 코스 {course['course_id']}: 장소 정보 누락")
                    print(f"  - 관광지: {'✓' if tour_place else '✗'}")
                    print(f"  - 카페: {'✓' if cafe_place else '✗'}")
                    print(f"  - 음식점: {'✓' if restaurant_place else '✗'}")
                    continue
                
                # Streamlit 호환 형식으로 변환
                streamlit_course = {
                    'course_id': course['course_id'],
                    'title': explained['title'],
                    'explanation': explained['explanation'],
                    'tour': tour_place,
                    'cafe': cafe_place,
                    'restaurant': restaurant_place,
                    'optimized_order': optimized_order  # ⭐ TSP 순서 추가
                }
                
                courses_with_explanation.append(streamlit_course)
                print(f"✔ 코스 {course['course_id']} 완료")
                
            except Exception as e:
                print(f"⚠️ 코스 처리 중 오류: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n✅ 총 {len(courses_with_explanation)}개 코스 생성 완료!\n")
        return courses_with_explanation
    
    
    def _create_courses_llm(self, user_type: str, trip_purpose: List[str], 
                           tour_list, cafe_list, restaurant_list) -> Tuple[str, Dict]:
        """LLM으로 코스 생성 (내부 메서드)"""
        def format_places(places):
            return "\n".join([f"- {p['title']}" for p in places])
        
        prompt = f"""
당신은 종로구 여행 전문가예요. {user_type}를 위한 3개 코스를 추천해주세요.

사용자: {user_type}
테마: {' '.join(trip_purpose)}

[관광지 후보]
{format_places(tour_list)}

[카페 후보]
{format_places(cafe_list)}

[음식점 후보]
{format_places(restaurant_list)}

🚨 필수 규칙:
1. 각 코스는 관광지 1개 + 카페 1개 + 음식점 1개 (총 3개 장소)
2. ⚠️⚠️⚠️ 9개 장소 모두 사용, 중복 절대 금지! ⚠️⚠️⚠️
3. 가까운 장소끼리 묶기
4. 장소 이름을 정확히 복사

⚠️⚠️⚠️ 출력 형식을 정확히 지켜주세요! ⚠️⚠️⚠️

## 코스 1: [구체적이고 매력적인 제목을 대괄호 안에 작성]
[관광지] 국립현대미술관 서울관
[카페] 사랑 고궁박물관 카페
[음식점] 재동순두부

## 코스 2: [구체적이고 매력적인 제목을 대괄호 안에 작성]
[관광지] 국립민속박물관
[카페] 설레는마중
[음식점] 종로진낙지

## 코스 3: [구체적이고 매력적인 제목을 대괄호 안에 작성]
[관광지] 청와대사랑채
[카페] 더스키
[음식점] 흥남부두

⚠️ 반드시:
- 제목은 [대괄호] 안에 작성
- [관광지], [카페], [음식점] 표기 정확히 사용
- 다른 설명 추가하지 말고 위 형식만 출력
"""
        
        print("🤖 LLM 코스 생성 중...\n")
        response = self.llm.invoke(prompt)
        
        data_dict = {
            'tour': {item['title']: item for item in tour_list},
            'cafe': {item['title']: item for item in cafe_list},
            'restaurant': {item['title']: item for item in restaurant_list}
        }
        
        return response.content, data_dict
    
    
    def parse_llm_result(self, llm_output: str, data_dict: Dict) -> List[Dict]:
        """LLM 출력 파싱 + 중복 체크"""
        print("\n" + "="*60)
        print("📋 LLM 출력 파싱")
        print("="*60)
        
        courses = []
        course_blocks = re.split(r'##\s*코스\s*(\d+):', llm_output)
        
        # 중복 체크용
        used_places = set()
        
        for i in range(1, len(course_blocks), 2):
            course_id = int(course_blocks[i])
            content = course_blocks[i + 1]
            
            # 제목 추출
            title_match = re.search(r'\[(.+?)\]', content)
            title = title_match.group(1) if title_match else f"코스 {course_id}"
            
            # 장소 추출
            places = []
            place_pattern = r'\[(관광지|카페|음식점|식당)\]\s*(.+?)(?:\n|$)'
            place_matches = re.findall(place_pattern, content)
            
            for category, name in place_matches:
                name = name.strip()
                
                if '관광' in category:
                    category_key = 'tour'
                elif '카페' in category:
                    category_key = 'cafe'
                elif '음식' in category or '식당' in category:
                    category_key = 'restaurant'
                else:
                    continue
                
                # 중복 체크
                place_id = f"{category_key}:{name}"
                
                if place_id in used_places:
                    print(f"⚠️ 중복 발견: {name}")
                    
                    # 교체 시도
                    available_places = [
                        p for p in data_dict[category_key].keys()
                        if f"{category_key}:{p}" not in used_places
                    ]
                    
                    if available_places:
                        name = available_places[0]
                        place_id = f"{category_key}:{name}"
                        print(f"   ✅ 교체: {name}")
                
                used_places.add(place_id)
                places.append({'category': category_key, 'name': name})
            
            if len(places) >= 3:
                courses.append({
                    'course_id': course_id,
                    'title': title,
                    'places': places[:3]
                })
                
                print(f"\n✅ 코스 {course_id}: {title}")
                for p in places[:3]:
                    print(f"  [{p['category']}] {p['name']}")
        
        return courses
    
    
    def optimize_route(self, places: List[Dict], data_dict: Dict) -> List[Dict]:
        """TSP 최적화"""
        def get_coords(category: str, name: str):
            place = data_dict[category].get(name)
            if not place:
                raise ValueError(f"{category}에서 '{name}'을(를) 찾을 수 없습니다.")
            return place['latitude'], place['longitude']
        
        all_orders = list(permutations(places))
        best_order = None
        min_distance = float('inf')
        
        for order in all_orders:
            coords = [get_coords(p['category'], p['name']) for p in order]
            
            total_distance = 0
            for i in range(len(coords) - 1):
                lat1, lon1 = coords[i]
                lat2, lon2 = coords[i + 1]
                total_distance += self.haversine_distance(lat1, lon1, lat2, lon2)
            
            if total_distance < min_distance:
                min_distance = total_distance
                best_order = list(order)
        
        return best_order
    
    
    def optimize_all_courses(self, courses: List[Dict], data_dict: Dict) -> List[Dict]:
        """모든 코스 최적화"""
        print("\n" + "="*60)
        print("🚀 경로 최적화 (TSP)")
        print("="*60)
        
        optimized_courses = []
        
        for course in courses:
            # optimize_route는 places 리스트를 재정렬해서 반환
            best_order = self.optimize_route(course['places'], data_dict)
            
            # ⭐ best_order가 딕셔너리 형태를 유지하도록 보장
            optimized_courses.append({
                'course_id': course['course_id'],
                'title': course['title'],
                'places': best_order  # 이미 [{'category': '...', 'name': '...'}, ...] 형태
            })
            
            # 순서 출력
            category_names = {'tour': '관광지', 'cafe': '카페', 'restaurant': '음식점'}
            order_str = " → ".join([category_names.get(p['category'], '?') for p in best_order])
            print(f"✔ 코스 {course['course_id']}: {order_str}")
        
        return optimized_courses
    
    
    def generate_course_explanation(self, course: Dict, data_dict: Dict, user_type: str) -> Dict:
        """RAG로 코스 설명 생성 (Content 기반)"""
        
        # 각 장소의 content 가져오기
        places_info = []
        for place in course['places']:
            place_data = data_dict[place['category']].get(place['name'])
            if place_data:
                places_info.append({
                    'name': place_data['title'],
                    'content': place_data.get('content', '')
                })
        
        places_summary = "\n\n".join([
            f"[{p['name']}]\n{p['content']}"
            for p in places_info
        ])
        
        prompt = f"""
당신은 종로구 여행 전문가입니다. {user_type}를 위한 하루 코스를 소개해주세요.

방문 장소:
{places_summary}

아래 형식으로 출력하세요:

### 코스 제목
경복궁에서 즐기는 예술과 맛의 여행

**이 코스의 장점**
1. 문화유산 감상 후 여유로운 휴식
2. 도보 이동 가능한 최적의 동선
3. 전통과 현대의 조화로운 경험

규칙:
- 장점은 반드시 3개
- 각 장점은 10-18자의 짧은 명사형 문구
- "1. ", "2. ", "3. " 형식 사용
- 장소명을 직접 쓰지 말 것
- ~합니다, ~있습니다 같은 문장형 금지
- 구체적인 편의시설(휠체어, 화장실 등) 언급 금지

좋은 예:
1. 역사적 건축물과 자연의 조화
2. 가까운 거리의 편리한 동선
3. 다양한 문화 체험 기회

나쁜 예:
1. 아이들과 함께 자연 속 놀이를 즐길 수 있습니다 (너무 김)
2. 휠체어 접근이 용이합니다 (편의시설 언급)
"""
        
        response = self.llm.invoke(prompt)
        content = response.content
        
        # 🔍 디버깅: GPT 응답 출력
        print("\n" + "="*80)
        print(f"🔍 [디버깅] 코스 {course['course_id']} GPT 원본 응답:")
        print("="*80)
        print(content)
        print("="*80 + "\n")
        
        # 제목 추출
        title_match = re.search(r'###\s*코스\s*제목.*?\n\s*(.+?)(?=\n|$)', content, re.DOTALL)
        if title_match:
            generated_title = title_match.group(1).strip()
            # 대괄호 제거
            generated_title = re.sub(r'^\[(.+?)\]$', r'\1', generated_title)
            
            # "코스 제목", "추천 이유" 같은 메타 텍스트 제거
            generated_title = re.sub(r'^(코스\s*제목|추천\s*이유)\s*[:\-]?\s*', '', generated_title)
            
            # 제목이 비어있거나 메타 텍스트면 기본값
            if not generated_title or generated_title in ["추천 이유", "코스 제목"]:
                generated_title = course.get('title', f"코스 {course['course_id']}")
        else:
            generated_title = course.get('title', f"코스 {course['course_id']}")
        
        print(f"📌 추출된 제목: {generated_title}\n")
        
        # 장점 추출 - 개선된 정규식
        advantages_match = re.search(r'\*\*이\s*코스의\s*장점\*\*\s*\n(.+?)(?=\n\n|###|$)', content, re.DOTALL)
        if advantages_match:
            advantages_text = advantages_match.group(1).strip()
            print(f"✅ 장점 추출 성공 (정규식 매칭)")
            print(f"📝 추출된 텍스트:\n{advantages_text}\n")
        else:
            # fallback
            advantages_text = "1. 접근성이 우수한 편리한 위치.\n2. 다양한 볼거리와 즐길거리.\n3. 쾌적하고 안전한 환경."
            print(f"⚠️ 장점 추출 실패 - fallback 사용")
        
        explanation = "**이 코스의 장점**\n" + advantages_text
        
        print(f"📌 최종 장점:\n{explanation}\n")
        print("="*80 + "\n")
        
        return {
            'course_id': course['course_id'],
            'title': generated_title,
            'places': course['places'],
            'explanation': explanation
        }


# Streamlit 호환성을 위한 별칭
CourseRecommender = TourRecommendationEngine


# 사용 예시
if __name__ == "__main__":
    # 엔진 초기화
    engine = TourRecommendationEngine()
    
    # 데이터 로드
    engine.load_json_with_dedup(
        './tour_final.json',
        './cafe_final.json',
        './restaurant_final.json'
    )
    
    # 벡터스토어 설정
    engine.setup_vectorstore()
    
    # 코스 생성
    result = engine.create_courses(
        user_type="보행약자",
        trip_purpose=["전시", "예술"],
        region="종로구"
    )
    
    # 결과 출력
    for course in result:
        print(f"\n{'='*60}")
        print(f"🎯 코스 {course['course_id']}: {course['title']}")
        print(f"{'='*60}\n")
        print(f"📍 관광지: {course['tour']['title']}")
        print(f"☕ 카페: {course['cafe']['title']}")
        print(f"🍽️ 음식점: {course['restaurant']['title']}")
        print(f"\n{course['explanation']}\n")
