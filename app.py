"""
고운길 서비스 - 메인 홈페이지
서비스 소개 및 시작 페이지
"""

import streamlit as st
from style import (
    apply_common_style, 
    render_header, 
    init_session_state, 
    render_accessibility_toggle,
    show_help_modal
)

# ==================== 페이지 설정 ====================
st.set_page_config(
    layout="wide",
    page_title="고운길 - 무장애 나들이 코스 추천",
    page_icon="🛣️"
)

# ==================== 초기화 ====================
# 세션 상태 초기화 (사용자 선택 정보 저장)
init_session_state()

# 노약자 친화 모드 토글 버튼 렌더링
render_accessibility_toggle()

# 스타일 적용
st.markdown(
    apply_common_style(st.session_state["accessibility_mode"]),
    unsafe_allow_html=True
)

# ==================== 헤더 ====================
render_header(show_help_modal_callback=lambda: st.session_state.update({"show_help": True}))

# ==================== 도움말 모달 ====================
# 도움말 버튼 클릭 시 모달 표시
if st.session_state.get("show_help", False):
    show_help_modal()
    # 닫기 버튼
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("✖️ 닫기", use_container_width=True):
            st.session_state["show_help"] = False
            st.rerun()
    st.markdown("---")

# ==================== 메인 컨텐츠 ====================
# 메인 타이틀
st.markdown("""
    <div class="main-title">
        편안한 나들이를<br>
        함께 계획해요 ✨
    </div>
""", unsafe_allow_html=True)

# 서비스 소개
st.markdown("""
    <div style="text-align: center; font-size: 24px; color: #666; margin: 40px 0 60px 0; line-height: 1.6;">
        휠체어 사용자, 고령자, 영유아 동반자 등<br>
        이동 약자를 위한 <strong style="color: #2196F3;">맞춤형 무장애 나들이 코스</strong>를 추천해드립니다
    </div>
""", unsafe_allow_html=True)

# 서비스 특징 카드
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
        <div style="text-align: center; padding: 40px 20px; background: #E3F2FD; border-radius: 20px; height: 100%;">
            <div style="font-size: 60px; margin-bottom: 20px;">♿</div>
            <div style="font-size: 24px; font-weight: 700; color: #1976D2; margin-bottom: 12px;">
                무장애 정보
            </div>
            <div style="font-size: 16px; color: #666; line-height: 1.6;">
                휠체어 접근성, 엘리베이터,<br>
                경사로 등 상세한<br>
                무장애 시설 정보 제공
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div style="text-align: center; padding: 40px 20px; background: #F3E5F5; border-radius: 20px; height: 100%;">
            <div style="font-size: 60px; margin-bottom: 20px;">🎯</div>
            <div style="font-size: 24px; font-weight: 700; color: #7B1FA2; margin-bottom: 12px;">
                맞춤형 추천
            </div>
            <div style="font-size: 16px; color: #666; line-height: 1.6;">
                동행자 유형과 관심사에<br>
                맞는 최적의<br>
                나들이 코스 제안
            </div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div style="text-align: center; padding: 40px 20px; background: #E8F5E9; border-radius: 20px; height: 100%;">
            <div style="font-size: 60px; margin-bottom: 20px;">🗺️</div>
            <div style="font-size: 24px; font-weight: 700; color: #388E3C; margin-bottom: 12px;">
                상세한 경로
            </div>
            <div style="font-size: 16px; color: #666; line-height: 1.6;">
                지도와 함께 제공되는<br>
                쉽고 안전한<br>
                이동 경로 안내
            </div>
        </div>
    """, unsafe_allow_html=True)

# 시작하기 버튼
st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)

# 버튼을 위한 커스텀 CSS (음성 버튼용)
st.markdown("""
    <style>
    .voice-button button {
        background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%) !important;
        border: none !important;
        color: white !important;
        font-size: 24px !important;
        font-weight: 800 !important;
        padding: 22px 50px !important;
        border-radius: 16px !important;
        box-shadow: 0 6px 20px rgba(156, 39, 176, 0.4) !important;
        min-height: 75px !important;
    }
    
    .voice-button button:hover {
        background: linear-gradient(135deg, #AB47BC 0%, #8E24AA 100%) !important;
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 28px rgba(156, 39, 176, 0.5) !important;
    }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown('<div class="final-button">', unsafe_allow_html=True)
    if st.button("🚀 나들이 계획 시작하기", use_container_width=True):
        # 1단계 페이지로 이동
        st.switch_page("pages/1_companion.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="voice-button">', unsafe_allow_html=True)
    if st.button("🎤 음성으로 빠르게 시작", use_container_width=True):
        # 음성 입력 페이지로 이동
        st.switch_page("pages/6_voice.py")
    st.markdown('</div>', unsafe_allow_html=True)
