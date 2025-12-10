"""
고운길 서비스 - 공통 스타일 관리 모듈
모든 페이지에서 일관된 디자인을 적용하기 위한 스타일 정의
"""

import streamlit as st

def apply_common_style(accessibility_mode=False):
    """
    모든 페이지에 공통으로 적용되는 CSS 스타일
    
    Args:
        accessibility_mode (bool): 노약자 친화 모드 활성화 여부
    """
    
    # 기본 스타일 정의
    base_css = """
    <style>
    /* ==================== 전역 설정 ==================== */
    .stApp {
        background: white;
    }
    
    /* 페이지 컨테이너 크기 및 여백 조정 */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 2rem !important;
        max-width: 1100px !important;
        margin: 0 auto !important;
        transform-origin: top center !important;
    }
    
    /* ==================== 헤더 영역 ==================== */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 30px;
        background: white;
        border-bottom: 2px solid #E3F2FD;
        margin-bottom: 25px;
    }
    
    .logo {
        font-size: 36px;
        font-weight: 800;
        color: #000;
        letter-spacing: -1px;
    }
    
    /* 도움말 뱃지 - 클릭 가능하도록 스타일 강화 */
    .help-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 18px;
        background: #E3F2FD;
        border-radius: 20px;
        color: #1976D2;
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .help-badge:hover {
        background: #BBDEFB;
        transform: translateY(-2px);
    }
    
    /* ==================== 제목 스타일 ==================== */
    .main-title {
        font-size: 38px;
        font-weight: 800;
        text-align: center;
        color: #212121;
        margin: 20px 0 30px 0;
        line-height: 1.3;
    }
    
    .section-title {
        font-size: 28px;
        font-weight: 700;
        color: #333;
        margin: 30px 0 20px 0;
        padding-left: 16px;
        border-left: 6px solid #2196F3;
    }
    
    /* ==================== 선택 카드 스타일 ==================== */
    .option-card {
        background: white;
        border: 3px solid #E0E0E0;
        border-radius: 20px;
        padding: 30px 25px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        min-height: 240px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .option-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 10px 20px rgba(33, 150, 243, 0.2);
        border-color: #64B5F6;
    }
    
    .option-card.selected {
        border-color: #2196F3;
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        box-shadow: 0 6px 16px rgba(33, 150, 243, 0.3);
    }
    
    /* 이미지 스타일 - 깔끔한 회색 배경 */
    .stImage img {
        border-radius: 16px;
        border: none !important;
        padding: 20px;
        background: #F8F9FA !important;
        box-shadow: none !important;
    }
    
    /* ==================== 버튼 스타일 ==================== */
    /* 일반 버튼 (선택 안됨) */
    .stButton > button {
        width: 100%;
        background: white !important;
        border: 3px solid #E0E0E0 !important;
        color: #333 !important;
        border-radius: 14px !important;
        padding: 16px 25px !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        min-height: 60px !important;
    }
    
    .stButton > button:hover {
        background: #F5F5F5 !important;
        border-color: #2196F3 !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 14px rgba(33, 150, 243, 0.2) !important;
    }
    
    /* 선택된 버튼 */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%) !important;
        border: 3px solid #1976D2 !important;
        color: white !important;
        box-shadow: 0 5px 16px rgba(33, 150, 243, 0.4) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%) !important;
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 6px 18px rgba(33, 150, 243, 0.5) !important;
    }
    
    /* 최종 제출 버튼 */
    .final-button button {
        background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%) !important;
        border: none !important;
        color: white !important;
        font-size: 24px !important;
        font-weight: 800 !important;
        padding: 22px 50px !important;
        border-radius: 16px !important;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4) !important;
        min-height: 75px !important;
    }
    
    .final-button button:hover {
        background: linear-gradient(135deg, #66BB6A 0%, #43A047 100%) !important;
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 28px rgba(76, 175, 80, 0.5) !important;
    }
    
    /* ==================== 경고 메시지 ==================== */
    .warning-message {
        text-align: center;
        color: #F44336;
        font-size: 18px;
        font-weight: 700;
        margin: 25px 0;
        padding: 14px;
        background: #FFEBEE;
        border-radius: 12px;
        border-left: 6px solid #F44336;
    }
    
    /* ==================== 진행 상황 표시 ==================== */
    .progress-indicator {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        margin: 20px 0 30px 0;
        padding: 16px;
        background: #F5F5F5;
        border-radius: 14px;
    }
    
    .progress-step {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        background: #E0E0E0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: 700;
        color: #999;
    }
    
    .progress-step.active {
        background: #2196F3;
        color: white;
        box-shadow: 0 3px 10px rgba(33, 150, 243, 0.4);
    }
    
    .progress-step.completed {
        background: #4CAF50;
        color: white;
    }
    
    .progress-connector {
        width: 50px;
        height: 3px;
        background: #E0E0E0;
        border-radius: 2px;
    }
    
    /* ==================== 반응형 디자인 ==================== */
    @media (max-width: 768px) {
        .header-container {
            padding: 12px 20px;
        }
        
        .logo {
            font-size: 28px;
        }
        
        .main-title {
            font-size: 32px;
        }
        
        .section-title {
            font-size: 24px;
        }
    }
    
    /* ========= 운영 정보 카드 스타일 ========= */
    .info-row {
        display: flex;
        align-items: center;
        margin-bottom: 14px;
    }
    
    .info-label {
        font-size: 16px;
        font-weight: 700;
        color: #1A237E;
        min-width: 110px;  /* 라벨 폭 고정 */
    }
    
    .info-value {
        font-size: 15px;
        color: #424242;
        line-height: 1.6;
    }
    </style>
    """
    
    # 노약자 친화 모드 추가 스타일 (확실하게 크게)
    if accessibility_mode:
        accessibility_css = """
    <style>
    /* ==================== 접근성 모드 - 크게 확대 ==================== */
    
    /* 헤더 영역 확대 */
    .logo {
        font-size: 56px !important;
    }
    
    .help-badge {
        font-size: 22px !important;
        padding: 16px 26px !important;
    }
    
    /* 제목 크게 확대 */
    .main-title {
        font-size: 60px !important;
        font-weight: 900 !important;
    }
    
    .section-title {
        font-size: 44px !important;
    }
    
    /* 설명 텍스트 확대 */
    div[style*="font-size: 18px"] {
        font-size: 26px !important;
    }
    
    div[style*="font-size: 16px"] {
        font-size: 24px !important;
    }
    
    div[style*="font-size: 14px"] {
        font-size: 20px !important;
    }
    
    /* 버튼 크게 확대 */
    .stButton > button {
        font-size: 32px !important;
        padding: 28px 40px !important;
        min-height: 90px !important;
    }
    
    .final-button button {
        font-size: 40px !important;
        padding: 36px 80px !important;
        min-height: 110px !important;
    }
    
    .warning-message {
        font-size: 28px !important;
        padding: 20px !important;
    }
    
    /* 진행 표시 확대 */
    .progress-step {
        width: 60px !important;
        height: 60px !important;
        font-size: 24px !important;
    }
    
    .progress-connector {
        width: 60px !important;
        height: 4px !important;
    }
    
    /* 이미지 패딩 증가 */
    .stImage img {
        padding: 28px !important;
    }
    
    /* 카드 내부 여백 조정 */
    .option-card {
        padding: 40px 35px !important;
        min-height: 300px !important;
    }
    </style>
        """
        return base_css + accessibility_css
    
    return base_css


def render_header(show_help_modal_callback=None):
    """
    모든 페이지 상단에 표시되는 공통 헤더
    - 고운길 로고
    - 도움말 버튼 (클릭 시 모달 표시)
    
    Args:
        show_help_modal_callback: 도움말 버튼 클릭 시 실행할 함수
    """
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<div class="logo">🛣️ 고운길</div>', unsafe_allow_html=True)
    
    with col2:
        # 도움말 버튼 - 클릭하면 모달 표시
        if st.button("❓ 도움말", key="help_button", use_container_width=True):
            if show_help_modal_callback:
                show_help_modal_callback()


def show_help_modal():
    """
    도움말 모달 창 표시
    서비스 이용 방법을 팝업으로 안내
    """
    st.markdown("""
        <div style="background: #F5F5F5; border-radius: 20px; padding: 40px; margin: 20px 0;">
            <div style="text-align: center; font-size: 28px; font-weight: 700; color: #333; margin-bottom: 30px;">
                💡 이용 방법
            </div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 20px;">
                <div style="text-align: center; flex: 1; min-width: 200px;">
                    <div style="font-size: 48px; margin-bottom: 15px;">1️⃣</div>
                    <div style="font-size: 20px; font-weight: 600; color: #333; margin-bottom: 8px;">동행 선택</div>
                    <div style="font-size: 16px; color: #666;">누구와 함께 하는지<br>선택해주세요</div>
                </div>
                <div style="text-align: center; flex: 1; min-width: 200px;">
                    <div style="font-size: 48px; margin-bottom: 15px;">2️⃣</div>
                    <div style="font-size: 20px; font-weight: 600; color: #333; margin-bottom: 8px;">유형 선택</div>
                    <div style="font-size: 16px; color: #666;">원하는 나들이<br>유형을 골라주세요</div>
                </div>
                <div style="text-align: center; flex: 1; min-width: 200px;">
                    <div style="font-size: 48px; margin-bottom: 15px;">3️⃣</div>
                    <div style="font-size: 20px; font-weight: 600; color: #333; margin-bottom: 8px;">지역 선택</div>
                    <div style="font-size: 16px; color: #666;">방문하고 싶은<br>지역을 선택하세요</div>
                </div>
                <div style="text-align: center; flex: 1; min-width: 200px;">
                    <div style="font-size: 48px; margin-bottom: 15px;">✅</div>
                    <div style="font-size: 20px; font-weight: 600; color: #333; margin-bottom: 8px;">추천 확인</div>
                    <div style="font-size: 16px; color: #666;">맞춤형 코스<br>추천을 받아보세요</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def init_session_state():
    """
    세션 상태 초기화
    사용자가 선택한 정보를 페이지 간 공유하기 위해 사용
    """
    if "companion" not in st.session_state:
        st.session_state["companion"] = None
    
    if "travel_type" not in st.session_state:
        st.session_state["travel_type"] = None
    
    if "region" not in st.session_state:
        st.session_state["region"] = None
    
    if "accessibility_mode" not in st.session_state:
        st.session_state["accessibility_mode"] = False
    
    # 도움말 모달 표시 상태
    if "show_help" not in st.session_state:
        st.session_state["show_help"] = False


def render_accessibility_toggle():
    """
    사이드바에 노약자 친화 모드 토글 버튼 표시
    """
    with st.sidebar:
        st.markdown("### ⚙️ 설정")
        
        accessibility_mode = st.toggle(
            "👓 노약자 친화 모드",
            value=st.session_state.get("accessibility_mode", False),
            help="큰 글씨와 높은 대비로 화면을 표시합니다"
        )
        
        st.session_state["accessibility_mode"] = accessibility_mode
        
        if accessibility_mode:
            st.success("✅ 큰 글씨 모드 활성화됨")
        
        # 현재 선택 상태 표시
        st.markdown("---")
        st.markdown("### 📋 선택 현황")
        
        if st.session_state.get("companion"):
            st.info(f"👥 동행: {st.session_state['companion']}")
        
        if st.session_state.get("travel_type"):
            st.info(f"🎯 유형: {st.session_state['travel_type']}")
        
        if st.session_state.get("region"):
            st.info(f"📍 지역: {st.session_state['region']}")


def render_progress_indicator(current_step):
    """
    현재 진행 단계를 시각적으로 표시
    
    Args:
        current_step (int): 현재 단계 (1: 동행, 2: 유형, 3: 지역)
    """
    steps = [
        ("1", "동행"),
        ("2", "유형"),
        ("3", "지역")
    ]
    
    progress_html = '<div class="progress-indicator">'
    
    for idx, (num, label) in enumerate(steps, 1):
        if idx < current_step:
            status = "completed"
            icon = "✓"
        elif idx == current_step:
            status = "active"
            icon = num
        else:
            status = ""
            icon = num
        
        progress_html += f'<div class="progress-step {status}">{icon}</div>'
        
        if idx < len(steps):
            progress_html += '<div class="progress-connector"></div>'
    
    progress_html += '</div>'
    
    st.markdown(progress_html, unsafe_allow_html=True)