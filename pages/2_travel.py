"""
고운길 서비스 - 2단계: 나들이 유형 선택 페이지
어떤 종류의 나들이를 원하는지 선택하는 페이지
"""

import streamlit as st
import os
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
    page_title="고운길 - 나들이 유형 선택",
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
render_progress_indicator(current_step=2)

# ==================== 메인 컨텐츠 ====================
# 페이지 제목 (이모지 제거)
st.markdown("""
    <div class="main-title">
        어떤 나들이를 가볼까요?
    </div>
""", unsafe_allow_html=True)

# 설명 텍스트
st.markdown("""
    <div style="text-align: center; font-size: 18px; color: #666; margin-bottom: 35px;">
        관심사에 맞는 테마를 선택해주세요
    </div>
""", unsafe_allow_html=True)

# ==================== 나들이 유형 옵션 ====================
# 현재 파일의 디렉토리 경로
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# assets 폴더 경로
ASSETS_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "assets")

travel_options = {
    "예술": {
        "image": "culture.png",
        "description": "미술관, 박물관, 공연장"
    },
    "전통": {
        "image": "traditional.png",
        "description": "고궁, 전통 시장, 한옥마을"
    },
    "자연": {
        "image": "nature.png",
        "description": "공원, 정원, 산책로"
    },
    "체험": {
        "image": "active.png",
        "description": "체험관, 놀이시설, 테마파크"
    }
}

# ==================== 옵션 카드 렌더링 ====================
col_left, col_center, col_right = st.columns([0.3, 5, 0.3])

with col_center:
    # 4개의 카드를 나란히 배치
    cols = st.columns(4, gap="medium")
    
    for idx, (key, info) in enumerate(travel_options.items()):
        with cols[idx]:
            # 이미지 경로
            image_path = os.path.join(ASSETS_DIR, info["image"])
            
            # 이미지 표시
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True)
            else:
                # 이미지 파일이 없을 때 플레이스홀더
                st.markdown(
                    f"""<div style='text-align:center; padding:70px 20px; 
                    background:#F5F5F5; border-radius:16px; margin-bottom:20px;
                    border: 3px dashed #E0E0E0;'>
                    <div style='font-size: 14px; color: #999;'>이미지 준비중</div>
                    <div style='font-size: 12px; color: #CCC; margin-top: 6px;'>{info['image']}</div>
                    </div>""",
                    unsafe_allow_html=True
                )
            
            # 설명 텍스트
            st.markdown(
                f"""<div style='text-align:center; color:#666; 
                font-size:14px; margin:15px 0 20px 0; line-height:1.5;'>
                {info['description']}
                </div>""",
                unsafe_allow_html=True
            )
            
            # 선택 버튼 - 클릭 시 자동으로 다음 페이지로 이동
            is_selected = st.session_state["travel_type"] == key
            
            if st.button(
                key,
                key=f"travel_{idx}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                # 선택 정보 저장
                st.session_state["travel_type"] = key
                # 바로 다음 페이지로 이동
                st.switch_page("pages/3_region.py")

# ==================== 하단 버튼 ====================
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

# 이전 단계, 홈 버튼
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    # 이전 단계로 돌아가기
    if st.button("⬅️ 이전 단계", use_container_width=True):
        st.switch_page("pages/1_companion.py")

with col3:
    # 홈으로 돌아가기
    if st.button("🏠 처음으로", use_container_width=True):
        st.switch_page("app.py")