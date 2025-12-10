"""
고운길 서비스 - 3단계: 지역 선택 페이지
서울시 25개 자치구 중 방문할 지역을 선택하는 페이지
"""

import streamlit as st
from style import (
    apply_common_style,
    render_header,
    init_session_state,
    render_accessibility_toggle,
    render_progress_indicator,
    show_help_modal
)

# ==================== 페이지 설정 ====================
st.set_page_config(
    layout="wide",
    page_title="고운길 - 지역 선택",
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

# ==================== 진행 단계 표시 ====================
render_progress_indicator(current_step=3)

# ==================== 메인 컨텐츠 ====================
# 페이지 제목 (이모지 제거)
st.markdown("""
    <div class="main-title">
        어느 지역으로 갈까요?
    </div>
""", unsafe_allow_html=True)

# 설명 텍스트
st.markdown("""
    <div style="text-align: center; font-size: 18px; color: #666; margin-bottom: 35px;">
        서울시 25개 자치구 중 원하는 곳을 선택해주세요
    </div>
""", unsafe_allow_html=True)

# ==================== 서울시 자치구 목록 ====================
# 가나다 순으로 정렬된 25개 자치구
regions = [
    "강남구", "강동구", "강북구", "강서구", "관악구",
    "광진구", "구로구", "금천구", "노원구", "도봉구",
    "동대문구", "동작구", "마포구", "서대문구", "서초구",
    "성동구", "성북구", "송파구", "양천구", "영등포구",
    "용산구", "은평구", "종로구", "중구", "중랑구"
]

# ==================== 지역 버튼 렌더링 ====================
# 5x5 그리드로 배치
col_left, col_center, col_right = st.columns([0.5, 5, 0.5])

with col_center:
    # 5개 행으로 구성
    for row in range(5):
        # 각 행마다 5개 컬럼
        cols = st.columns(5, gap="small")
        
        for col_idx in range(5):
            # 현재 버튼의 인덱스 계산
            idx = row * 5 + col_idx
            
            # 25개 지역 범위 내인지 확인
            if idx < len(regions):
                region = regions[idx]
                
                with cols[col_idx]:
                    # 현재 선택된 지역인지 확인
                    is_selected = st.session_state["region"] == region
                    
                    # 지역 선택 버튼 - 클릭 시 자동으로 추천 페이지로 이동
                    if st.button(
                        region,
                        key=f"region_{idx}",
                        use_container_width=True,
                        type="primary" if is_selected else "secondary"
                    ):
                        # 선택한 지역을 세션에 저장
                        st.session_state["region"] = region
                        # 바로 추천 페이지로 이동
                        st.switch_page("pages/4_rec.py")

# ==================== 하단 버튼 ====================
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

# 이전 단계, 홈 버튼
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    # 이전 단계로 (2_travel.py로 수정)
    if st.button("⬅️ 이전 단계", use_container_width=True):
        st.switch_page("pages/2_travel.py")

with col3:
    # 홈으로
    if st.button("🏠 처음으로", use_container_width=True):
        st.switch_page("app.py")