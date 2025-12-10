"""
고운길 서비스 - 5단계: 코스 상세 페이지
선택한 코스의 상세 정보와 지도를 보여주는 페이지
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import openrouteservice as ors
import os
from style import (
    apply_common_style,
    render_header,
    init_session_state,
    render_accessibility_toggle,
    show_help_modal
)

# ==================== 접근성 정보 처리 함수 ====================
def process_accessibility_info(facilities):
    """접근성 정보를 3단계 우선순위로 분류하고 처리"""
    if not facilities:
        return []
    
    if isinstance(facilities, str):
        facilities = [f.strip() for f in facilities.split(',')]
    
    # 키워드와 아이콘 매핑 (더 세분화)
    keyword_icon_map = {
        # 휠체어 관련 (세분화)
        '휠체어 전용 매표소': {'icon': '♿', 'keyword': '휠체어 매표소'},
        '휠체어 매표소': {'icon': '♿', 'keyword': '휠체어 매표소'},
        '휠체어 사용자 테이블': {'icon': '♿', 'keyword': '휠체어 테이블'},
        '휠체어 사용자 안내': {'icon': '♿', 'keyword': '휠체어 안내'},
        '휠체어 안내': {'icon': '♿', 'keyword': '휠체어 안내'},
        '휠체어 대여': {'icon': '♿', 'keyword': '휠체어 대여'},
        '휠체어': {'icon': '♿', 'keyword': '휠체어'},
        
        # 매표소
        '매표소': {'icon': '🎫', 'keyword': '매표소'},
        
        # 엘리베이터
        '엘리베이터': {'icon': '🛗', 'keyword': '엘리베이터'},
        '승강기': {'icon': '🛗', 'keyword': '엘리베이터'},
        
        # 주차장
        '주차장': {'icon': '🅿️', 'keyword': '주차장'},
        '주차': {'icon': '🅿️', 'keyword': '주차장'},
        
        # 화장실 (세분화) - 아이콘 구분
        '가족 화장실': {'icon': '👨‍👩‍👧', 'keyword': '가족 화장실'},
        '가족화장실': {'icon': '👨‍👩‍👧', 'keyword': '가족 화장실'},
        '장애인 화장실': {'icon': '🚻', 'keyword': '장애인 화장실'},
        '장애인화장실': {'icon': '🚻', 'keyword': '장애인 화장실'},
        '화장실': {'icon': '🚻', 'keyword': '화장실'},
        
        # 접근성 관련 (세분화)
        '진입로 접근': {'icon': '🚶', 'keyword': '진입로'},
        '진입로': {'icon': '🚶', 'keyword': '진입로'},
        '접근로': {'icon': '🚶', 'keyword': '접근로'},
        '시각장애인용 접근성': {'icon': '👁️', 'keyword': '시각장애인 접근성'},
        '접근성': {'icon': '🚶', 'keyword': '접근성'},
        '통로': {'icon': '🚶', 'keyword': '통로'},
        
        # 안내시설
        '안내시설': {'icon': '📢', 'keyword': '안내시설'},
        '안내': {'icon': '📢', 'keyword': '안내시설'},
        '점자': {'icon': '👆', 'keyword': '점자 안내'},
        
        # 편의시설
        '청각장애인용 편의시설': {'icon': '👂', 'keyword': '청각장애인 편의'},
        '시각장애인용 편의시설': {'icon': '👁️', 'keyword': '시각장애인 편의'},
        '편의시설': {'icon': '✨', 'keyword': '편의시설'},
        
        # 경사로/출입구
        '경사로': {'icon': '♿', 'keyword': '경사로'},
        '출입구': {'icon': '🚪', 'keyword': '출입구'},
        
        # 유아 관련
        '유아의자': {'icon': '🍼', 'keyword': '유아의자'},
        '수유실': {'icon': '🍼', 'keyword': '수유실'},
        '기저귀 교환대': {'icon': '👶', 'keyword': '기저귀 교환대'},
        '기저귀': {'icon': '👶', 'keyword': '기저귀 교환대'},
        '유아차 대여': {'icon': '🚼', 'keyword': '유아차 대여'},
        '유아차 보관소': {'icon': '🚼', 'keyword': '유아차 보관소'},
        '유아차': {'icon': '🚼', 'keyword': '유아차 보관소'},
    }
    
    # 키워드 정제 함수 (있음, 없음 제거)
    def clean_keyword(text):
        # 있음, 없음, 불가 등 상태 키워드 제거
        cleaned = text.replace(' 있음', '').replace(' 없음', '').replace(' 불가', '')
        cleaned = cleaned.replace('있음', '').replace('없음', '').replace('불가', '')
        return cleaned.strip()
    
    # 상태 분류 함수 (3단계) - 부정 키워드를 먼저 체크!
    def classify_status(text):
        # 2순위를 먼저: 부정 (주황) - "있으나 불편함" 같은 경우 대비
        if any(word in text for word in ['불편', '불편함', '어려움', '미흡']):
            return {'type': 'negative', 'status': '불편함', 'color': 'orange'}
        # 3순위: 없음 (회색)
        elif any(word in text for word in ['없음', '불가']):
            return {'type': 'none', 'status': '없음', 'color': 'gray'}
        # 1순위: 긍정 (초록)
        elif any(word in text for word in ['있음', '설치', '제공', '완비','좋음', '양호', '양호함', '용이', '용이함', '원활', '가능']):
            return {'type': 'positive', 'status': '있음', 'color': 'green'}
        # elif any(word in text for word in ['있음', '설치', '제공', '완비']):
        #     return {'type': 'positive', 'status': '가능', 'color': 'green'}
        else:
            # 키워드 없으면 긍정으로 간주
            return {'type': 'positive', 'status': '가능', 'color': 'green'}
    
    # 3개 리스트로 분류
    positive_items = []  # 초록
    negative_items = []  # 주황
    none_items = []      # 회색
    
    # 중복 체크용 (icon + keyword 조합)
    seen_items = set()
    
    for facility in facilities:
        facility = facility.strip()
        if not facility:
            continue
        
        # 키워드 매칭 (긴 키워드부터 확인 - 더 구체적인 매칭)
        found = False
        # 키워드를 길이 순으로 정렬 (긴 것부터)
        sorted_keywords = sorted(keyword_icon_map.items(), key=lambda x: len(x[0]), reverse=True)
        
        for key, value in sorted_keywords:
            if key in facility:
                classification = classify_status(facility)
                
                # 중복 체크 (icon + keyword 조합)
                item_signature = f"{value['icon']}_{value['keyword']}"
                if item_signature in seen_items:
                    found = True
                    break  # 이미 있으면 스킵
                
                seen_items.add(item_signature)
                
                item = {
                    'icon': value['icon'],
                    'keyword': value['keyword'],
                    'status': classification['status'],
                    'color': classification['color']
                }
                
                # 분류별로 저장
                if classification['type'] == 'positive':
                    positive_items.append(item)
                elif classification['type'] == 'negative':
                    negative_items.append(item)
                else:
                    none_items.append(item)
                
                found = True
                break
        
        # 매핑되지 않은 경우 기본값
        if not found:
            classification = classify_status(facility)
            # 키워드 정제
            cleaned_keyword = clean_keyword(facility[:15])
            
            # 중복 체크
            item_signature = f"✓_{cleaned_keyword}"
            if item_signature not in seen_items:
                seen_items.add(item_signature)
                
                item = {
                    'icon': '✓',
                    'keyword': cleaned_keyword,
                    'status': classification['status'],
                    'color': classification['color']
                }
                
                if classification['type'] == 'positive':
                    positive_items.append(item)
                elif classification['type'] == 'negative':
                    negative_items.append(item)
                else:
                    none_items.append(item)
    
    # 우선순위대로 합치기 (최대 6개)
    result = []
    
    # 1순위: 초록 (최대 6개까지)
    result.extend(positive_items[:6])
    
    # 2순위: 주황 (남은 자리만큼)
    remaining = 6 - len(result)
    if remaining > 0:
        result.extend(negative_items[:remaining])
    
    # 3순위: 회색 (남은 자리만큼)
    remaining = 6 - len(result)
    if remaining > 0:
        result.extend(none_items[:remaining])
    
    return result

def format_hours(hours_text):
    """이용시간 텍스트를 여러 줄로 포맷팅"""
    if not hours_text or hours_text == '이용시간 정보 없음':
        return hours_text
    
    # 리스트로 들어온 경우 처리
    if isinstance(hours_text, list):
        hours_text = ' '.join(str(item) for item in hours_text)
    
    # 문자열로 변환
    hours_text = str(hours_text)
    
    import re
    lines = []
    
    # 방법 1: "평일:", "토요일:", "주말:" 등 시간 키워드 찾기
    # 패턴: 키워드 + 콜론 + 시간
    pattern = r'([가-힣\d\-]+(?:월|일|평일|주말|주중|토요일|일요일|공휴일|요일))\s*[:：]\s*([^\n]*?)(?=\s+[가-힣\d\-]+(?:월|일|평일|주말|주중|토요일|일요일|공휴일|요일)\s*[:：]|$)'
    
    matches = re.findall(pattern, hours_text, re.DOTALL)
    
    if matches:
        for keyword, time_info in matches:
            keyword = keyword.strip()
            time_info = time_info.strip()
            # 불필요한 쉼표 제거
            time_info = time_info.rstrip(',').strip()
            if keyword and time_info:
                lines.append(f"{keyword}: {time_info}")
    
    # 방법 2: 패턴 매칭 실패시 쉼표로 분리
    if not lines:
        parts = hours_text.split(',')
        for part in parts:
            part = part.strip()
            if part and len(part) > 2:
                lines.append(part)
    
    return '<br>'.join(lines) if lines else hours_text



def format_price(price_text):
    """이용요금 텍스트를 여러 줄로 포맷팅"""
    if not price_text:
        return price_text
    
    import re
    
    # 리스트로 들어온 경우 처리
    if isinstance(price_text, list):
        price_text = ', '.join(str(item) for item in price_text)
    
    # 문자열로 변환
    price_text = str(price_text)
    
    lines = []
    
    # "이름: 1,000원" 또는 "이름 1,000원" 패턴 찾기
    # 한글/영문 + 숫자,원 조합
    pattern = r'([가-힣a-zA-Z\s\(\)]+?)\s*[:：]?\s*(\d{1,3}(?:,\d{3})*)\s*원'
    matches = re.findall(pattern, price_text)
    
    if matches:
        for name, price in matches:
            name = name.strip()
            if name and name not in ['-', '·', ',', ';']:
                lines.append(f"· {name}: {price}원")
    else:
        # 패턴 매칭 실패시 원본 반환
        return price_text
    
    return '<br>'.join(lines) if lines else price_text

# ==================== 페이지 설정 ====================
st.set_page_config(
    layout="wide",
    page_title="고운길 - 코스 상세",
    page_icon="🛣️"
)

# ==================== 초기화 ====================
init_session_state()
render_accessibility_toggle()

# 스타일 적용
st.markdown(
    apply_common_style(st.session_state["accessibility_mode"]),
    unsafe_allow_html=True
)

# ==================== 추가 스타일 ====================
st.markdown("""
<style>
/* ==================== 5_map.py 전용 스타일 (style.py 덮어쓰기) ==================== */

/* 이미지 회색 배경 제거 - 5_map.py에서만 적용 */
.stImage img {
    padding: 0 !important;
    background: transparent !important;
    border-radius: 8px !important;
    width: 100% !important;
    object-fit: cover !important;
}

/* 이미지 컨테이너 여백 제거 */
div[data-testid="stImage"] {
    padding: 0 !important;
    margin: 0 !important;
}

/* 이미지 컬럼 간격 최소화 */
div[data-testid="column"] {
    padding: 0 !important;
}

div[data-testid="stHorizontalBlock"] {
    gap: 4px !important;
}

div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
    gap: 4px !important;
}

/* ==================== 기존 스타일 ==================== */

/* Expander 스타일 커스터마이징 */
.streamlit-expanderHeader {
    font-size: 18px !important;
    font-weight: 700 !important;
    color: #212121 !important;
    background-color: #f8f9fa !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    border: 2px solid #e0e0e0 !important;
}

.streamlit-expanderHeader:hover {
    background-color: #e9ecef !important;
    border-color: #2196F3 !important;
}

/* Expander 화살표를 > 로 변경 */
.streamlit-expanderHeader svg {
    display: none !important;
}

.streamlit-expanderHeader::before {
    content: '›' !important;
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #666 !important;
    margin-right: 12px !important;
    transition: transform 0.2s !important;
    display: inline-block !important;
}

details[open] .streamlit-expanderHeader::before {
    transform: rotate(90deg) !important;
}

/* 코스 제목 */
.course-detail-title {
    font-size: 36px;
    font-weight: 800;
    color: #212121;
    margin-bottom: 16px;
    text-align: center;
}

/* 가게명 스타일 */
.place-name {
    font-size: 28px;
    font-weight: 700;
    color: #212121;
    margin-bottom: 20px;
    margin-top: 10px;
}

/* 거리 정보 */
.distance-info {
    text-align: center;
    font-size: 20px;
    color: #2E7D32;
    font-weight: 700;
    margin-bottom: 30px;
    padding: 12px;
    background: #E8F5E9;
    border-radius: 12px;
}

/* 지도 컨테이너 */
.map-container {
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    margin-bottom: 40px;
}

/* 장소 정보 카드 */
.place-info {
    background: transparent;
    padding: 16px 0px;
    border-radius: 0px;
    margin-top: 12px;
}

.place-info-row {
    display: flex;
    margin-bottom: 12px;
    font-size: 14px;
    padding-bottom: 12px;
    border-bottom: 1px solid #212121 !important;
}

.place-info-row:last-child {
    border-bottom: none !important;
    padding-bottom: 0;
    margin-bottom: 0;
}

.place-info-label {
    font-weight: 700;
    color: #666;
    min-width: 80px;
}

.place-info-value {
    color: #333;
    line-height: 1.6;
}

/* 접근성 정보 박스 */
.accessibility-box {
    background: #F1F8F4;
    border: 1px solid #C8E6C9;
    border-radius: 12px;
    padding: 16px;
    margin-top: 0px;
    margin-bottom: 16px;
}

/* 하늘색 외곽 컨테이너 */
.accessibility-outer-box {
    background: #E3F2FD;
    border: 2px solid #90CAF9;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    min-height: 400px;
}

.accessibility-box-title {
    font-size: 18px;
    font-weight: 700;
    color: #1976D2;
    margin-bottom: 16px;
}

/* 접근성 아이템 */
.accessibility-item {
    background: #E8F5E9;
    border: 2px solid #4CAF50;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
}

/* 접근성 아이템 - 주황색 (불편함) */
.accessibility-item-orange {
    background: #FFF3E0;
    border: 2px solid #FF9800;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
}

/* 접근성 아이템 - 회색 (없음) */
.accessibility-item-gray {
    background: #F5F5F5;
    border: 2px solid #9E9E9E;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.accessibility-icon {
    font-size: 28px;
    flex-shrink: 0;
}

.accessibility-content {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.accessibility-keyword {
    color: #2E7D32;
    font-size: 14px;
    font-weight: 600;
    line-height: 1.2;
    word-break: keep-all;
    white-space: normal;
}

/* 주황색 카드 텍스트 */
.accessibility-item-orange .accessibility-keyword {
    color: #E65100;
}

.accessibility-item-orange .accessibility-status {
    color: #FB8C00;
}

/* 회색 카드 텍스트 */
.accessibility-item-gray .accessibility-keyword {
    color: #616161;
}

.accessibility-item-gray .accessibility-status {
    color: #9E9E9E;
}

.accessibility-status {
    color: #66BB6A;
    font-size: 12px;
    font-weight: 500;
    line-height: 1.2;
    word-break: keep-all;
}


/* 리뷰 영역 */
.review-section {
    margin-top: 20px;
    padding: 0px;
    background: transparent;
    border-radius: 0px;
}

.review-title {
    font-size: 18px;
    font-weight: 700;
    color: #333;
    margin-bottom: 12px;
}

/* Expander 스타일 */
div[data-testid="stExpander"] {
    background: white;
    border: 2px solid #E0E0E0;
    border-radius: 12px;
    margin-bottom: 20px;
}

div[data-testid="stExpander"] summary {
    background: #F5F5F5 !important;
    padding: 16px !important;
    border-radius: 10px !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #212121 !important;
}

div[data-testid="stExpander"] summary:hover {
    background: #EEEEEE !important;
}

/* 소개 텍스트 */
.intro-section {
    margin-top: 16px;
    margin-bottom: 16px;
}

.intro-title {
    font-size: 16px;
    font-weight: 700;
    color: #333;
    margin-bottom: 8px;
}

.intro-content {
    font-size: 14px;
    color: #555;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ==================== 헤더 ====================
render_header(show_help_modal_callback=lambda: st.session_state.update({"show_help": True}))

# ==================== 도움말 모달 ====================
if st.session_state.get("show_help", False):
    show_help_modal()
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("✖️ 닫기", use_container_width=True, key="close_help"):
            st.session_state["show_help"] = False
            st.rerun()
    st.markdown("---")

# ==================== OpenRouteService API 키 ====================
try:
    ORS_API_KEY = st.secrets["OPENROUTESERVICE_API_KEY"]
except:
    ORS_API_KEY = os.getenv("OPENROUTESERVICE_API_KEY", "")

# ==================== 선택된 코스 확인 ====================
selected_course = st.session_state.get("selected_course")
course_idx = st.session_state.get("selected_course_idx", 1)

if not selected_course:
    st.error("⚠️ 선택된 코스가 없습니다.")
    col1, col2, col3 = st.columns([2, 2, 2])
    with col2:
        if st.button("🏠 코스 목록으로", use_container_width=True):
            st.switch_page("pages/4_rec.py")
    st.stop()

# ==================== 코스 제목 + 거리 ====================
# 거리 계산 먼저 수행
try:
    optimized_order = selected_course.get('optimized_order', ['tour', 'cafe', 'restaurant'])
    
    # 좌표 추출 함수
    def get_coords(place):
        lat = None
        lng = None
        
        if 'coordinates' in place:
            coords = place['coordinates']
            lat = coords.get('latitude')
            lng = coords.get('longitude')
        
        if not lat:
            lat = place.get('latitude') or place.get('mapy')
        if not lng:
            lng = place.get('longitude') or place.get('mapx')
        
        if lat and lng:
            return float(lat), float(lng)
        return None, None
    
    # 좌표 리스트 생성
    coords_list = []  # [(lat, lng), ...]
    coordinates_ors = []  # [[lng, lat], ...] ORS 형식
    
    for category in optimized_order:
        if category in selected_course:
            place = selected_course[category]
            lat, lng = get_coords(place)
            if lat and lng:
                coords_list.append((lat, lng))
                coordinates_ors.append([lng, lat])
    
    # ORS로 실제 도로 거리 계산
    total_distance = 0
    distance_text = "계산 중..."
    route_geometry = None
    
    if ORS_API_KEY and len(coordinates_ors) >= 2:
        try:
            client = ors.Client(key=ORS_API_KEY)
            
            # 경로 계산
            route = client.directions(
                coordinates=coordinates_ors,
                profile='foot-walking',
                format='geojson',
                validate=False
            )
            
            # 거리 정보 추출 (미터 단위)
            total_distance = route['features'][0]['properties']['segments'][0]['distance']
            distance_text = f"{total_distance / 1000:.1f}km"
            
            # 경로 지오메트리 저장
            route_geometry = route
            
        except Exception as e:
            # Haversine으로 fallback
            import math
            def haversine(lat1, lon1, lat2, lon2):
                R = 6371
                lat1_rad = math.radians(lat1)
                lat2_rad = math.radians(lat2)
                delta_lat = math.radians(lat2 - lat1)
                delta_lon = math.radians(lon2 - lon1)
                
                a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                
                return R * c
            
            total_distance = 0
            for i in range(len(coords_list) - 1):
                lat1, lng1 = coords_list[i]
                lat2, lng2 = coords_list[i + 1]
                total_distance += haversine(lat1, lng1, lat2, lng2)
            
            distance_text = f"{total_distance:.1f}km (직선)"
    
    elif len(coords_list) >= 2:
        # API 키 없을 때 Haversine 사용
        import math
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)
            
            a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            
            return R * c
        
        total_distance = 0
        for i in range(len(coords_list) - 1):
            lat1, lng1 = coords_list[i]
            lat2, lng2 = coords_list[i + 1]
            total_distance += haversine(lat1, lng1, lat2, lng2)
        
        distance_text = f"{total_distance:.1f}km (직선)"

except Exception as e:
    distance_text = "계산 중..."

# 제목 먼저 표시
st.markdown(f'''
<div style="
    text-align: center;
    margin-bottom: 20px;
">
    <div style="
        font-size: 36px; 
        font-weight: 800; 
        color: #212121;
    ">
        {selected_course.get("title", "코스 상세")}
    </div>
</div>
''', unsafe_allow_html=True)

# 거리 카드를 제목 아래 중앙에 배치
st.markdown(f'''
<div style="
    display: flex;
    justify-content: center;
    margin-bottom: 30px;
">
    <div style="
        font-size: 18px;
        color: #2E7D32;
        font-weight: 700;
        padding: 10px 20px;
        background: #E8F5E9;
        border-radius: 12px;
        white-space: nowrap;
    ">
        🚶 총 거리: {distance_text}
    </div>
</div>
''', unsafe_allow_html=True)

# ==================== 지도 ====================
st.markdown('<div class="map-container">', unsafe_allow_html=True)

try:
    if len(coords_list) >= 2:
        # 지도 중심 좌표 계산
        center_lat = sum([c[0] for c in coords_list]) / len(coords_list)
        center_lng = sum([c[1] for c in coords_list]) / len(coords_list)
        
        # Folium 지도 생성
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=14,
            tiles="OpenStreetMap"
        )
        
        # ORS 경로가 있으면 그리기
        if route_geometry:
            folium.GeoJson(
                route_geometry,
                name='route',
                style_function=lambda x: {
                    'color': '#2196F3',
                    'weight': 5,
                    'opacity': 0.8
                }
            ).add_to(m)
        else:
            # ORS 경로 없으면 직선으로 연결
            folium.PolyLine(
                locations=coords_list,
                color='#2196F3',
                weight=4,
                opacity=0.7
            ).add_to(m)
        
        # 마커 추가
        category_names = {'tour': '관광지', 'cafe': '카페', 'restaurant': '음식점'}
        colors = {'tour': 'blue', 'cafe': 'green', 'restaurant': 'red'}
        
        for idx, category in enumerate(optimized_order, 1):
            if category in selected_course:
                place = selected_course[category]
                lat, lng = get_coords(place)
                
                if lat and lng:
                    # 이미지 URL
                    img_url = (place.get('thumbnail_url') or 
                              place.get('firstimage') or 
                              'https://via.placeholder.com/300x200?text=No+Image')
                    
                    # 팝업 HTML
                    popup_html = f"""
                    <div style="font-family: Arial; width: 280px;">
                        <img src="{img_url}" style="width: 100%; height: 180px; object-fit: cover; border-radius: 8px; margin-bottom: 8px;">
                        <b style="font-size: 16px;">{idx}. {place.get('title', '장소명')}</b><br>
                        <small style="color: #666;">{category_names.get(category, '장소')}</small>
                    </div>
                    """
                    
                    folium.Marker(
                        location=[lat, lng],
                        popup=folium.Popup(popup_html, max_width=320),
                        tooltip=f"{idx}. {category_names.get(category, '장소')}",
                        icon=folium.Icon(color=colors.get(category, 'gray'), icon='info-sign')
                    ).add_to(m)
        
        # 지도 표시 (returned_objects=[] 로 무한 리렌더링 방지)
        st_folium(m, width=None, height=500, returned_objects=[])
    else:
        st.warning("⚠️ 표시할 수 있는 장소 좌표가 부족합니다.")

except Exception as e:
    st.error("⚠️ 지도를 불러올 수 없습니다.")

st.markdown('</div>', unsafe_allow_html=True)

# ==================== 상세 코스 ====================
st.markdown("""
<div style="
    background: #f5f5f5;
    padding: 16px 24px;
    border-radius: 12px;
    margin: 40px 0 20px 0;
">
    <div style="
        font-size: 18px;
        font-weight: 700;
        color: #666;
    ">각 코스에 대한 상세정보를 제공합니다.</div>
</div>
""", unsafe_allow_html=True)

# 장소 순서대로 표시
category_names = {'tour': '관광지', 'cafe': '카페', 'restaurant': '음식점'}
category_icons = {'tour': '🏛️', 'cafe': '☕', 'restaurant': '🍽️'}

for idx, category in enumerate(optimized_order, 1):
    if category not in selected_course:
        continue
    
    place = selected_course[category]
    place_title = place.get('title', '장소명')
    
    # 토글 형식으로 표시 - 기본으로 접혀있음
    with st.expander(f"{idx}번째 장소 - {category_icons.get(category, '📍')} {place_title}", expanded=False):
        
        # ===== 상단: 이미지(왼쪽) + 접근성 정보 + 리뷰(오른쪽) =====
        top_left, top_right = st.columns([6, 4])
        
        with top_left:
            # 이미지 3개
            thumbnail = place.get('thumbnail_url') or place.get('firstimage') or 'https://via.placeholder.com/500x500?text=No+Image'
            image_2 = place.get('image_2') or 'https://via.placeholder.com/200x245?text=No+Image'
            image_3 = place.get('image_3') or 'https://via.placeholder.com/200x245?text=No+Image'
            
            img_col1, img_col2 = st.columns([5, 2])
            with img_col1:
                st.markdown(f'''
                    <img src="{thumbnail}" style="width:100%; height:300px; object-fit:cover; border-radius:8px;">
                ''', unsafe_allow_html=True)
            with img_col2:
                st.markdown(f'''
                    <img src="{image_2}" style="width:100%; height:145px; object-fit:cover; border-radius:8px; margin-bottom:10px;">
                ''', unsafe_allow_html=True)
                st.markdown(f'''
                    <img src="{image_3}" style="width:100%; height:145px; object-fit:cover; border-radius:8px;">
                ''', unsafe_allow_html=True)
            
            # ===== 이미지 바로 아래: 운영 정보 카드 =====
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            
            # 데이터 추출
            address = place.get('address', '주소 정보 없음')
            phone = place.get('tel', place.get('phone', ''))
            hours = place.get('operating_hours', place.get('hours', ''))
            price = place.get('price', place.get('이용요금', ''))
            content = place.get('content', place.get('overview', ''))
            
            # 시간 포맷팅
            if hours and hours != '이용시간 정보 없음':
                formatted_hours = format_hours(hours)
            else:
                formatted_hours = ''
            
            # 가격 포맷팅
            if price:
                formatted_price = format_price(price)
            else:
                formatted_price = ''
            
            # 소개 내용 처리
            if content:
                if len(content) > 200:
                    import re
                    match = re.search(r'[.!?]\s', content[180:280])
                    if match:
                        cut_point = 180 + match.end()
                        display_content = content[:cut_point].strip()
                    else:
                        display_content = content[:200].rsplit(' ', 1)[0] + "..."
                else:
                    display_content = content
            else:
                display_content = ''
            
            # 완전한 HTML을 한 번에 생성
            card_html = '<div style="background: #E3F2FD; border: 2px solid #90CAF9; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">'
            
            # 주소
            card_html += '<div style="display: flex; align-items: center; margin-bottom: 14px;">'
            card_html += '<div style="font-size: 16px; font-weight: 700; color: #1A237E; min-width: 110px;">📍 주소</div>'
            card_html += f'<div style="font-size: 15px; color: #424242; line-height: 1.6;">{address}</div>'
            card_html += '</div>'
            
            # 전화번호
            if phone and phone != '전화번호 없음':
                card_html += '<div style="display: flex; align-items: center; margin-bottom: 14px;">'
                card_html += '<div style="font-size: 16px; font-weight: 700; color: #1A237E; min-width: 110px;">📞 전화번호</div>'
                card_html += f'<div style="font-size: 15px; color: #424242; line-height: 1.6;">{phone}</div>'
                card_html += '</div>'
            
            # 운영시간
            if formatted_hours:
                card_html += '<div style="display: flex; align-items: center; margin-bottom: 14px;">'
                card_html += '<div style="font-size: 16px; font-weight: 700; color: #1A237E; min-width: 110px;">🕐 운영시간</div>'
                card_html += f'<div style="font-size: 15px; color: #424242; line-height: 1.6;">{formatted_hours}</div>'
                card_html += '</div>'
            
            # 이용요금
            if formatted_price:
                card_html += '<div style="display: flex; align-items: center; margin-bottom: 14px;">'
                card_html += '<div style="font-size: 16px; font-weight: 700; color: #1A237E; min-width: 110px;">💰 이용요금</div>'
                card_html += f'<div style="font-size: 15px; color: #424242; line-height: 1.6;">{formatted_price}</div>'
                card_html += '</div>'
            
            # 소개 (구분선 제거)
            if display_content:
                card_html += '<div style="margin-top: 16px;">'
                card_html += '<div style="font-size: 16px; font-weight: 700; color: #1976D2; margin-bottom: 12px;">📝 소개</div>'
                card_html += f'<div style="font-size: 14px; color: #424242; line-height: 1.7;">{display_content}</div>'
                card_html += '</div>'
            
            card_html += '</div>'
            
            # 한 번에 렌더링
            st.markdown(card_html, unsafe_allow_html=True)
        
        with top_right:
            # 접근성 정보 - 2x3 그리드
            facilities = place.get('facilities', [])
            processed_facilities = process_accessibility_info(facilities)
            
            st.markdown('''
                <div style="font-size: 18px; font-weight: 700; color: #1976D2; margin-bottom: 16px;">♿ 접근성 정보</div>
            ''', unsafe_allow_html=True)
            
            # 6개 항목 준비 (부족하면 "정보 없음"으로 채우기)
            facility_items = []
            for i in range(6):
                if i < len(processed_facilities):
                    facility_items.append(processed_facilities[i])
                else:
                    facility_items.append({
                        'icon': 'ℹ️',
                        'keyword': '정보 없음',
                        'status': '없음',
                        'color': 'gray'
                    })
            
            # 2x3 그리드로 표시
            for row in range(3):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    facility = facility_items[row * 2]
                    color = facility.get('color', 'green')
                    
                    # 색상별 CSS 클래스
                    if color == 'green':
                        item_class = 'accessibility-item'
                    elif color == 'orange':
                        item_class = 'accessibility-item-orange'
                    else:  # gray
                        item_class = 'accessibility-item-gray'
                    
                    st.markdown(f'''
                        <div class="{item_class}">
                            <div class="accessibility-icon">{facility['icon']}</div>
                            <div class="accessibility-content">
                                <div class="accessibility-keyword">{facility['keyword']}</div>
                                <div class="accessibility-status">{facility['status']}</div>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
                
                with col_b:
                    facility = facility_items[row * 2 + 1]
                    color = facility.get('color', 'green')
                    
                    # 색상별 CSS 클래스
                    if color == 'green':
                        item_class = 'accessibility-item'
                    elif color == 'orange':
                        item_class = 'accessibility-item-orange'
                    else:  # gray
                        item_class = 'accessibility-item-gray'
                    
                    st.markdown(f'''
                        <div class="{item_class}">
                            <div class="accessibility-icon">{facility['icon']}</div>
                            <div class="accessibility-content">
                                <div class="accessibility-keyword">{facility['keyword']}</div>
                                <div class="accessibility-status">{facility['status']}</div>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
            
            # 접근성 정보와 2x2 그리드 사이 여백 (왼쪽 운영정보 카드 시작점과 맞추기)
            st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
            
            # ===== 정보 카드 섹션 (2x2 그리드) =====
            # 정보 카드 옵션 (4개)
            info_cards = [
                ('😊', '친절한 서비스', 3),
                ('🚪', '출입구 단차 없음', 2),
                ('🔄', '자동문 출입구', 2),
                ('🌸', '분위기', 4)
            ]
            
            # 2x2 그리드로 표시 (높이 축소)
            for row in range(2):
                col1, col2 = st.columns(2)
                
                # 첫 번째 열
                with col1:
                    idx_item = row * 2
                    if idx_item < len(info_cards):
                        emoji, label, count = info_cards[idx_item]
                        
                        # 하늘색 카드 (패딩 줄임)
                        card_html = f'''
                        <div style="
                            background: #E3F2FD;
                            border: 2px solid #90CAF9;
                            border-radius: 8px;
                            padding: 8px 12px;
                            margin-bottom: 6px;
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                        ">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-size: 16px;">{emoji}</span>
                                <span style="font-size: 12px; font-weight: 600; color: #1565C0;">{label}</span>
                            </div>
                            <span style="
                                font-size: 10px;
                                color: #1565C0;
                                background: #BBDEFB;
                                padding: 2px 6px;
                                border-radius: 10px;
                            ">{count}</span>
                        </div>
                        '''
                        
                        st.markdown(card_html, unsafe_allow_html=True)
                
                # 두 번째 열
                with col2:
                    idx_item = row * 2 + 1
                    if idx_item < len(info_cards):
                        emoji, label, count = info_cards[idx_item]
                        
                        # 하늘색 카드 (패딩 줄임)
                        card_html = f'''
                        <div style="
                            background: #E3F2FD;
                            border: 2px solid #90CAF9;
                            border-radius: 8px;
                            padding: 8px 12px;
                            margin-bottom: 6px;
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                        ">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-size: 16px;">{emoji}</span>
                                <span style="font-size: 12px; font-weight: 600; color: #1565C0;">{label}</span>
                            </div>
                            <span style="
                                font-size: 10px;
                                color: #1565C0;
                                background: #BBDEFB;
                                padding: 2px 6px;
                                border-radius: 10px;
                            ">{count}</span>
                        </div>
                        '''
                        
                        st.markdown(card_html, unsafe_allow_html=True)
            
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            
            # ===== 리뷰 작성 섹션 - 아래로 이동 (높이 축소) =====
            st.markdown('''
                <div style="font-size: 13px; font-weight: 700; color: #666; margin-bottom: 8px;">💬 이 장소에 대한 의견을 남겨주세요</div>
            ''', unsafe_allow_html=True)
            
            # 리뷰 작성 영역 스타일 변경 (흰색 배경, 검정 글씨)
            st.markdown("""
                <style>
                textarea {
                    background-color: #FFFFFF !important;
                    color: #000 !important;
                    border: 2px solid #E0E0E0 !important;
                }
                textarea::placeholder {
                    color: #999999 !important;
                }
                </style>
            """, unsafe_allow_html=True)
            
            review_text = st.text_area(
                "리뷰 작성",
                placeholder="이 장소의 접근성이나 편의시설에 대한 경험을 공유해주세요...",
                height=80,
                key=f"review_{category}_{idx}",
                label_visibility="collapsed"
            )
            
            if st.button("✍️ 작성하기", key=f"submit_{category}_{idx}", use_container_width=True):
                if review_text:
                    st.success("리뷰가 등록되었습니다!")
                else:
                    st.warning("리뷰 내용을 입력해주세요.")

# ==================== 하단 버튼 ====================
st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("⬅️ 코스 목록", use_container_width=True):
        st.switch_page("pages/4_rec.py")

with col3:
    if st.button("🏠 처음으로", use_container_width=True):
        st.switch_page("app.py")