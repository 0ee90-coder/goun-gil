"""
고운길 서비스 - 4단계: 추천 코스 결과 페이지
AI가 추천한 3개의 나들이 코스를 비교하여 선택하는 페이지
"""

import streamlit as st
import os
import re
from style import (
    apply_common_style,
    render_header,
    init_session_state,
    render_accessibility_toggle,
    show_help_modal
)

# ==================== RAG 엔진 임포트 ====================
try:
    from rag_engine import CourseRecommender
    import openrouteservice as ors
    RAG_AVAILABLE = True
except ImportError as e:
    RAG_AVAILABLE = False
    print(f"⚠️ RAG 엔진 임포트 실패: {e}")

# ==================== 페이지 설정 ====================
st.set_page_config(
    layout="wide",
    page_title="고운길 - 추천 코스",
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

# ==================== 코스 카드 스타일 ====================
st.markdown("""
<style>
.full-card-container {
    transition: all 0.3s ease;
    max-width: 400px;
    margin: 0 auto;
}
.full-card-container:hover {
    transform: translateY(-4px);
}
.course-number-banner {
    position: absolute;
    top: 16px;
    left: 16px;
    padding: 8px 20px;
    font-size: 16px;
    font-weight: 800;
    color: white;
    border-radius: 20px;
    z-index: 20;
}
.banner-color-1 { background: #2196F3; }
.banner-color-2 { background: #4CAF50; }
.banner-color-3 { background: #FF9800; }
.card-image-section {
    position: relative;
    width: 100%;
    height: 260px;
    overflow: hidden;
    border-radius: 12px 12px 0 0;
}
.card-image-section img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.distance-info-badge {
    position: absolute;
    bottom: 16px;
    right: 16px;
    background: rgba(255, 255, 255, 0.95);
    padding: 8px 14px;
    border-radius: 16px;
    font-size: 13px;
    font-weight: 600;
    color: #333;
    z-index: 10;
}
.course-card-body {
    background: white;
    border: 2px solid #d0d0d0;
    border-radius: 0 0 12px 12px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}
.card-main-title {
    font-size: 20px;
    font-weight: 700;
    color: #212121;
    margin-bottom: 20px;
    line-height: 1.4;
    min-height: 56px;
}
.benefits-section {
    margin-bottom: 20px;
}
.benefits-header {
    font-size: 15px;
    font-weight: 700;
    color: #666;
    margin-bottom: 12px;
}
.benefit-row {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 12px;
    font-size: 14px;
    color: #424242;
    line-height: 1.5;
}
.benefit-checkmark {
    font-size: 16px;
    margin-top: 2px;
    flex-shrink: 0;
    font-weight: 700;
}
.check-color-1 { color: #2196F3; }
.check-color-2 { color: #4CAF50; }
.check-color-3 { color: #FF9800; }
.amenities-section {
    padding-top: 20px;
    border-top: 1px solid #E0E0E0;
}
.amenities-header {
    font-size: 13px;
    font-weight: 600;
    color: #666;
    margin-bottom: 14px;
}
.amenities-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
}
.amenity-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
}
.amenity-emoji {
    font-size: 26px;
}
.amenity-text {
    font-size: 11px;
    color: #666;
    text-align: center;
}

/* 버튼 색상 */
.stButton > button[data-course="1"] {
    background: #2196F3 !important;
}
.stButton > button[data-course="2"] {
    background: #4CAF50 !important;
}
.stButton > button[data-course="3"] {
    background: #FF9800 !important;
}

/* Spinner 텍스트 색상 - 검정색으로 변경 */
.stSpinner > div {
    color: #000000 !important;
}
.stSpinner > div > div {
    color: #000000 !important;
}
div[data-testid="stSpinner"] {
    color: #000000 !important;
}
div[data-testid="stSpinner"] > div {
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

# ==================== 헤더 ====================
render_header(show_help_modal_callback=lambda: st.session_state.update({"show_help": True}))

if st.session_state.get("show_help", False):
    show_help_modal()
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("✖️ 닫기", use_container_width=True, key="close_help"):
            st.session_state["show_help"] = False
            st.rerun()
    st.markdown("---")

# ==================== 선택 조건 확인 ====================
if (not st.session_state.get("companion") or 
    not st.session_state.get("travel_type") or 
    not st.session_state.get("region")):
    st.error("⚠️ 모든 선택 항목을 완료해주세요!")
    col1, col2, col3 = st.columns([2, 2, 2])
    with col2:
        if st.button("🏠 처음으로 돌아가기", use_container_width=True):
            st.switch_page("app.py")
    st.stop()

# ==================== 메인 컨텐츠 ====================
st.markdown('<div class="main-title">당신을 위한 맞춤 코스✨</div>', unsafe_allow_html=True)
# st.markdown('<div style="text-align: center; font-size: 16px; color: #666; margin-bottom: 40px;">안전하고 편안한 나들이를 위한 세 가지 추천 코스</div>', unsafe_allow_html=True)

# ==================== RAG 엔진 ====================
if RAG_AVAILABLE:
    try:
        ORS_API_KEY = st.secrets.get("OPENROUTESERVICE_API_KEY", "")
    except:
        ORS_API_KEY = os.getenv("OPENROUTESERVICE_API_KEY", "")
    
    def calculate_walking_distance(course):
        if not ORS_API_KEY:
            return 2.0
        try:
            optimized_order = course.get('optimized_order', ['tour', 'cafe', 'restaurant'])
            places = [course[category] for category in optimized_order if category in course]
            if len(places) < 2:
                return 2.0
            
            coordinates = []
            for place in places:
                lat = lng = None
                if 'coordinates' in place:
                    coords = place['coordinates']
                    lat = coords.get('latitude')
                    lng = coords.get('longitude')
                if not lat:
                    lat = place.get('latitude') or place.get('mapy')
                if not lng:
                    lng = place.get('longitude') or place.get('mapx')
                if lat and lng:
                    coord = [float(lng), float(lat)]
                    if coord not in coordinates:
                        coordinates.append(coord)
            
            if len(coordinates) < 2:
                return 2.0
            
            client = ors.Client(key=ORS_API_KEY)
            route = client.directions(coordinates=coordinates, profile='foot-walking', format='geojson')
            distance_m = route['features'][0]['properties']['segments'][0]['distance']
            return round(distance_m / 1000, 1)
        except:
            return 2.0
    
    def extract_advantages(course):
        """장점 추출 - 번호 형식 파싱"""
        advantages = []
        
        # 1. explanation 필드에서 추출
        explanation = course.get('explanation', '')
        
        if explanation:
            # "**이 코스의 장점**" 헤더 제거
            explanation = explanation.replace('**이 코스의 장점**\n', '').replace('**이 코스의 장점**', '').strip()
            
            # 번호 형식으로 분리 (1. 2. 3.)
            lines = explanation.split('\n')
            
            for line in lines:
                line = line.strip()
                # 번호 형식 찾기 (1. 또는 2. 또는 3.)
                match = re.match(r'^(\d+)\.\s*(.+)$', line)
                if match:
                    advantage_text = match.group(2).strip()
                    if len(advantage_text) > 5:  # 의미 있는 텍스트만
                        advantages.append(advantage_text)
                        if len(advantages) >= 3:
                            break
        
        # 2. 데이터가 부족하면 기본값
        if len(advantages) < 3:
            advantages = [
                "접근성이 우수한 편리한 위치",
                "다양한 볼거리와 즐길거리", 
                "쾌적하고 안전한 환경"
            ]
        
        return advantages[:3]
    
    def collect_facilities(course):
        """각 장소의 실제 편의시설 수집"""
        facilities = {'휠체어': False, '화장실': False, '주차장': False, '승강기': False}
        
        # tour, cafe, restaurant 3곳의 편의시설 통합
        for place_type in ['tour', 'cafe', 'restaurant']:
            place = course.get(place_type, {})
            if not place:
                continue
            
            # facilities 필드 가져오기
            place_facilities = place.get('facilities', [])
            
            # 리스트가 아니면 변환
            if isinstance(place_facilities, str):
                place_facilities = [place_facilities]
            elif not isinstance(place_facilities, list):
                place_facilities = []
            
            # 각 항목 확인
            for facility in place_facilities:
                facility_str = str(facility).strip()
                
                # 승강기 체크
                if '장애인 엘리베이터 이용이 용이함' in facility_str or '장애인 엘리베이터가 있으나 일부 이용이 불편함' in facility_str:
                    facilities['승강기'] = True
                
                # 휠체어 체크
                if '진입로 접근성이 좋음' in facility_str or '휠체어 전용 매표소 있음' in facility_str or '휠체어 사용자 테이블 접근이 용이함' in facility_str:
                    facilities['휠체어'] = True
                
                # 주차장 체크
                if '장애인 주차장 이용이 용이함' in facility_str or '장애인 주차장 이용이 조금 불편함' in facility_str:
                    facilities['주차장'] = True
                
                # 화장실 체크
                if '장애인 화장실 접근성이 좋음' in facility_str or '장애인 화장실이 있으나 일부 이용이 불편함' in facility_str:
                    facilities['화장실'] = True
        
        return facilities
    
    @st.cache_resource
    def get_recommender_v2():
        recommender = CourseRecommender()
        recommender.load_json_with_dedup('./data/tour_final.json', './data/cafe_final.json', './data/restaurant_final.json')
        recommender.setup_vectorstore()
        return recommender
    
    current_condition = f"{st.session_state['companion']}_{st.session_state['travel_type']}_{st.session_state['region']}"
    need_new = (st.session_state.get("last_condition") != current_condition or st.session_state.get("recommended_courses") is None)
    
    if need_new:
        with st.spinner("🤖 AI가 최적의 코스를 추천하고 있습니다..."):
            try:
                recommender = get_recommender_v2()
                travel_type_str = st.session_state["travel_type"]
                trip_purpose = [travel_type_str] if isinstance(travel_type_str, str) else travel_type_str
                courses = recommender.create_courses(
                    user_type=st.session_state["companion"],
                    trip_purpose=trip_purpose,
                    region=st.session_state["region"]
                )
                st.session_state["recommended_courses"] = courses
                st.session_state["last_condition"] = current_condition
                st.rerun()
            except Exception as e:
                st.error(f"❌ 추천 중 오류: {e}")
                st.stop()
    
    courses = st.session_state.get("recommended_courses", [])
else:
    st.warning("⚠️ RAG 엔진을 사용할 수 없어 테스트 데이터를 표시합니다.")
    courses = []
    def calculate_walking_distance(course): return 2.3
    def extract_advantages(course): return ["접근성이 우수한 편리한 위치", "다양한 볼거리와 즐길거리", "쾌적하고 안전한 환경"]
    def collect_facilities(course): return {'휠체어': True, '화장실': True, '주차장': True, '승강기': False}

if not courses:
    st.warning("⚠️ 조건에 맞는 코스를 찾을 수 없습니다.")
    col1, col2, col3 = st.columns([2, 2, 2])
    with col2:
        if st.button("🏠 처음으로 돌아가기", use_container_width=True):
            st.switch_page("app.py")
    st.stop()

# ==================== 코스 카드 렌더링 ====================
cols = st.columns(3, gap="large")

for idx, (col, course) in enumerate(zip(cols, courses[:3]), 1):
    with col:
        tour_place = course.get('tour', {})
        thumbnail = tour_place.get('thumbnail_url') or tour_place.get('firstimage') or 'https://via.placeholder.com/400x280?text=No+Image'
        distance = calculate_walking_distance(course)
        advantages = extract_advantages(course)
        facilities = collect_facilities(course)
        title = course.get('title', f'코스 {idx}')
        
        st.markdown('<div class="full-card-container">', unsafe_allow_html=True)
        
        # 이미지 섹션 (코스 번호 포함)
        st.markdown(f'''<div class="card-image-section">
            <div class="course-number-banner banner-color-{idx}">코스 {idx}</div>
            <div class="distance-info-badge">🗺️ {distance}km</div>
            <img src="{thumbnail}" alt="코스 {idx}">
        </div>''', unsafe_allow_html=True)
        
        card_html = f'<div class="course-card-body"><div class="card-main-title">{title}</div><div class="benefits-section"><div class="benefits-header">이 코스의 장점</div>'
        for advantage in advantages:
            card_html += f'<div class="benefit-row"><span class="benefit-checkmark check-color-{idx}">✓</span><span>{advantage}</span></div>'
        
        card_html += f'''</div><div class="amenities-section"><div class="amenities-header">편의시설</div><div class="amenities-grid">
        <div class="amenity-item" style="opacity: {1 if facilities.get('휠체어') else 0.3}"><div class="amenity-emoji">♿</div><div class="amenity-text">휠체어</div></div>
        <div class="amenity-item" style="opacity: {1 if facilities.get('화장실') else 0.3}"><div class="amenity-emoji">🚻</div><div class="amenity-text">화장실</div></div>
        <div class="amenity-item" style="opacity: {1 if facilities.get('주차장') else 0.3}"><div class="amenity-emoji">🅿️</div><div class="amenity-text">주차장</div></div>
        <div class="amenity-item" style="opacity: {1 if facilities.get('승강기') else 0.3}"><div class="amenity-emoji">🛗</div><div class="amenity-text">승강기</div></div>
        </div></div></div>'''
        
        st.markdown(card_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
        
        # 상세보기 버튼
        if st.button("상세보기", key=f"btn_{idx}", use_container_width=True, type="secondary"):
            st.session_state["selected_course"] = course
            st.session_state["selected_course_idx"] = idx
            st.switch_page("pages/5_map.py")

# ==================== 하단 버튼 ====================
st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 2, 2])
with col2:
    if st.button("⬅️ 다시 선택하기", use_container_width=True):
        st.switch_page("pages/3_region.py")
