"""
고운길 서비스 - 1단계: 동행 선택 페이지
누구와 함께 나들이를 떠나는지 선택하는 페이지
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
    page_title="고운길 - 동행 선택",
    page_icon="🛣️"
)

# ==================== 초기화 ====================
# 세션 상태 초기화
init_session_state()

# 노약자 친화 모드 토글
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
render_progress_indicator(current_step=1)

# ==================== 메인 컨텐츠 ====================
# 페이지 제목 (이모지 제거)
st.markdown("""
    <div class="main-title">
        누구와 함께 하나요?
    </div>
""", unsafe_allow_html=True)

# 설명 텍스트
st.markdown("""
    <div style="text-align: center; font-size: 18px; color: #666; margin-bottom: 35px;">
        동행자의 상황에 맞는 최적의 장소를 추천해드립니다
    </div>
""", unsafe_allow_html=True)

# ==================== 동행 옵션 정의 ====================
# 현재 파일의 디렉토리 경로 (pages 폴더)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# assets 폴더 경로 (pages의 상위 폴더에 있음)
ASSETS_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "assets")

# 동행 옵션: 이름과 이미지 파일명
companion_options = {
    "휠체어 사용자": {
        "image": "wheelchair.png",
        "description": "휠체어 접근 가능한 장소"
    },
    "영유아": {
        "image": "baby.png",
        "description": "유모차 이동이 편한 장소"
    },
    "고령자": {
        "image": "elderly.png",
        "description": "편안하게 이동 가능한 장소"
    }
}

# ==================== 옵션 카드 렌더링 ====================
# 중앙 정렬을 위한 컬럼 구성
col_left, col_center, col_right = st.columns([0.5, 5, 0.5])

with col_center:
    # 3개의 카드를 나란히 배치
    cols = st.columns(3, gap="large")
    
    for idx, (key, info) in enumerate(companion_options.items()):
        with cols[idx]:
            # 이미지 경로 설정 (assets 폴더 사용)
            image_path = os.path.join(ASSETS_DIR, info["image"])
            
            # 이미지 표시 (이미지가 없으면 기본 플레이스홀더 표시)
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True)
            else:
                # 이미지 파일이 없을 때 플레이스홀더
                st.markdown(
                    f"""<div style='text-align:center; padding:80px 20px; 
                    background:#F5F5F5; border-radius:16px; margin-bottom:20px;
                    border: 3px dashed #E0E0E0;'>
                    <div style='font-size: 16px; color: #999;'>이미지 준비중</div>
                    <div style='font-size: 12px; color: #CCC; margin-top: 8px;'>{info['image']}</div>
                    </div>""",
                    unsafe_allow_html=True
                )
            
            # 설명 텍스트
            st.markdown(
                f"""<div style='text-align:center; color:#666; 
                font-size:16px; margin:15px 0 20px 0;'>
                {info['description']}
                </div>""",
                unsafe_allow_html=True
            )
            
            # 선택 버튼 - 클릭 시 자동으로 다음 페이지로 이동
            is_selected = st.session_state["companion"] == key
            
            if st.button(
                key,
                key=f"companion_{idx}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                # 선택 정보를 세션에 저장
                st.session_state["companion"] = key
                # 바로 다음 페이지로 이동
                st.switch_page("pages/2_travel.py")

# ==================== 하단 버튼 ====================
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

# 홈으로 돌아가기 버튼만 표시 (이전 단계 없음)
col1, col2, col3 = st.columns([2, 2, 2])
with col2:
    if st.button("🏠 처음으로 돌아가기", use_container_width=True):
        st.switch_page("app.py")