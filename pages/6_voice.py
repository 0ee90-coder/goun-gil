"""
고운길 서비스 - 음성 인식 페이지
음성으로 편리하게 동행자, 유형, 지역을 선택할 수 있는 페이지
"""

import streamlit as st
from openai import OpenAI
import json
from dotenv import load_dotenv
import os
from style import (
    apply_common_style, 
    render_header, 
    show_help_modal,
    init_session_state,
    render_accessibility_toggle
)

# 페이지 설정
st.set_page_config(
    page_title="음성으로 선택하기 - 고운길",
    page_icon="🎤",
    layout="wide"
)

# ============================================================================
# OpenAI 정보 추출 함수
# ============================================================================
def extract_user_info(text, client):
    """
    OpenAI 모델을 사용해 텍스트에서 3가지 사용자 정보를 추출.
    JSON 형태로만 반환하도록 강제.
    """
    extraction_prompt = f"""
다음 문장에서 아래 정보를 JSON으로만 추출하세요.
**중요: 문장에 명시적으로 언급되지 않은 정보는 반드시 null로 반환하세요. 추측하거나 임의로 값을 생성하지 마세요.**

반환해야 하는 key:
- travel_type: 원하는 관광지 특성 (예: '전시 or 예술', '전통 or 유적', '공원 or 산책', '체험 or 놀이')
- companion: 사용자의 이동 특성(예: 유모차 이용, 휠체어 이용, 노인 등)
- region: 가고 싶은 서울의 지역구명(예: 종로구, 양천구 등)

문장: "{text}"

반환 형식 예시:
{{
"travel_type": "value or null",
"companion": "value or null",
"region": "value or null"
}}
    """

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": extraction_prompt}],
        response_format={"type": "json_object"}
    )
    content = resp.choices[0].message.content
    return json.loads(content)

# ============================================================================
# 세션 상태 초기화
# ============================================================================
init_session_state()

# 채팅 히스토리 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "안녕하세요! 예술, 전통, 산책, 체험 중 어떤 테마를 원하시나요?"}
    ]
    st.session_state.user_info = {
        "travel_type": None,
        "companion": None,
        "region": None
    }
    st.session_state.initial_tts_played = False

# ============================================================================
# 스타일 적용
# ============================================================================
accessibility_mode = st.session_state.get("accessibility_mode", False)
st.markdown(apply_common_style(accessibility_mode), unsafe_allow_html=True)

# 음성 페이지 전용 스타일 추가
st.markdown("""
    <style>
    /* ==================== 음성 페이지 텍스트 가독성 개선 ==================== */
    
    /* section-title 강제 표시 */
    .section-title {
        color: #212121 !important;
        background: white !important;
        padding: 16px 20px !important;
        border-radius: 12px !important;
        margin: 25px 0 20px 0 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* 안내 박스 텍스트 */
    div[style*="background: #E3F2FD"] div {
        color: #1976D2 !important;
    }
    
    div[style*="background: #E3F2FD"] {
        background: #E3F2FD !important;
    }
    
    /* 채팅 메시지 텍스트 */
    .stChatMessage {
        background: white !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin: 8px 0 !important;
    }
    
    .stChatMessage p {
        color: #212121 !important;
        font-size: 16px !important;
    }
    
    /* 인식 결과 카드 내 텍스트 */
    div[style*="min-height: 200px"] div {
        color: inherit !important;
    }
    
    /* 모든 텍스트 요소 강제 가시화 */
    .element-container, .stMarkdown, .stMarkdown p, .stMarkdown div {
        color: #212121 !important;
    }
    
    /* 경고 메시지 */
    .warning-message {
        color: #D32F2F !important;
        background: #FFEBEE !important;
    }
    
    /* 푸터 텍스트 */
    div[style*="color: #999"] p {
        color: #999 !important;
    }
    
    /* 성공 메시지 */
    .stSuccess {
        background: #E8F5E9 !important;
        color: #2E7D32 !important;
    }
    
    /* 정보 메시지 */
    .stInfo {
        background: #E3F2FD !important;
        color: #1565C0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 사이드바 렌더링
render_accessibility_toggle()

# 도움말 모달 처리
def toggle_help():
    st.session_state["show_help"] = not st.session_state.get("show_help", False)

# 헤더 렌더링
render_header(show_help_modal_callback=toggle_help)

# 도움말 모달 표시
if st.session_state.get("show_help", False):
    show_help_modal()
    if st.button("닫기", key="close_help"):
        st.session_state["show_help"] = False
        st.rerun()

# ============================================================================
# OpenAI API 설정
# ============================================================================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("⚠️ OPENAI_API_KEY가 .env 파일에 없습니다.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# ============================================================================
# 메인 타이틀
# ============================================================================
st.markdown('<h1 class="main-title">🎤 음성으로 편리하게 선택하세요</h1>', unsafe_allow_html=True)

# 진행 상황 표시
st.markdown("""
    <div class="progress-indicator">
        <div class="progress-step active">🎤</div>
    </div>
""", unsafe_allow_html=True)

# ============================================================================
# 첫 페이지 로딩 시 첫 질문의 TTS 자동 재생
# ============================================================================
if st.session_state.chat_history and not st.session_state.initial_tts_played:
    first_msg = st.session_state.chat_history[0]["content"]
    
    try:
        tts_audio = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="nova",
            input=first_msg
        )
        
        with open("assistant_tts_initial.mp3", "wb") as f:
            f.write(tts_audio.read())
        
        st.audio("assistant_tts_initial.mp3", autoplay=True)
        st.session_state.initial_tts_played = True
    except Exception as e:
        st.warning(f"TTS 오류: {e}")

# ============================================================================
# 안내 메시지
# ============================================================================
st.markdown("""
    <div style="text-align: center; margin: 30px 0; padding: 25px; background: #E3F2FD; border-radius: 16px;">
        <div style="font-size: 24px; font-weight: 700; color: #1976D2; margin-bottom: 15px;">
            🎙️ 마이크 버튼을 눌러 말씀해주세요
        </div>
        <div style="font-size: 18px; color: #555; line-height: 1.6;">
            예시: "예술 전시를 보러 종로구에 가고 싶어요"<br>
            "유모차를 끌고 공원 산책하러 강남구에 갈래요"
        </div>
    </div>
""", unsafe_allow_html=True)

# ============================================================================
# 음성 입력
# ============================================================================
st.markdown('<h2 class="section-title">🎤 음성 입력</h2>', unsafe_allow_html=True)

audio_bytes = st.audio_input("🎤 마이크를 클릭하여 말씀해주세요", key="audio_input_raw")

# ============================================================================
# STT 처리
# ============================================================================
if audio_bytes:
    try:
        with st.spinner("🎧 음성 인식 중…"):
            # 1) 오디오 읽기
            audio_content = audio_bytes.read()
            
            # 2) 파일 저장
            with open("temp_audio.webm", "wb") as f:
                f.write(audio_content)
            
            # 3) Whisper STT
            with open("temp_audio.webm", "rb") as audio_file:
                resp = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ko",
                    response_format="json"
                )
        
        recognized_text = resp.text
        
        # 사용자 입력 저장
        st.session_state.chat_history.append({
            "role": "user",
            "content": recognized_text
        })
        
        # -------- 사용자 정보 추출 --------
        extracted = extract_user_info(recognized_text, client)
        
        for k in ["travel_type", "companion", "region"]:
            if extracted.get(k):
                st.session_state.user_info[k] = extracted[k]
                # style.py의 세션 상태에도 저장
                st.session_state[k] = extracted[k]
        
        # -------- assistant 질문 생성 --------
        order = ["travel_type", "companion", "region"]
        missing_fields = [k for k in order if st.session_state.user_info[k] is None]
        
        question_map = {
            "travel_type": "예술, 전통, 산책, 체험 중 어떤 테마를 원하시나요?",
            "companion": "혹시 유모차/휠체어 사용 여부 등 동행인의 이동 특성을 알려주실 수 있을까요?",
            "region": "서울의 어느 구로 방문하고 싶으신가요?"
        }
        
        # 정보 부족 → 다음 질문
        if missing_fields:
            assistant_text = question_map[missing_fields[0]]
        # 모든 정보 수집 완료
        else:
            assistant_text = "네, 알겠습니다. 추천 코스를 안내해드리겠습니다."
        
        # assistant 메시지 누적
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": assistant_text
        })
        
        # 자동 TTS 출력
        try:
            tts_audio = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="nova",
                input=assistant_text
            )
            
            with open("assistant_tts.mp3", "wb") as f:
                f.write(tts_audio.read())
            
            st.audio("assistant_tts.mp3", autoplay=True)
        except Exception as e:
            st.warning(f"TTS 오류: {e}")
        
        # UI 표시
        st.success("✅ 음성 인식 완료!")
        st.info(f"인식된 텍스트: {recognized_text}")
        
    except Exception as e:
        st.error(f"❌ STT 처리 중 오류 발생: {e}")

# ============================================================================
# 채팅 히스토리 표시
# ============================================================================
st.markdown("---")
st.markdown('<h2 class="section-title">💬 대화 내용</h2>', unsafe_allow_html=True)

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ============================================================================
# 인식 결과 표시
# ============================================================================
st.markdown("---")
st.markdown('<h2 class="section-title">📝 인식 결과</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    travel_type_display = st.session_state.user_info.get("travel_type") or "미선택"
    card_style = "border: 3px solid #2196F3; background: #E3F2FD;" if st.session_state.user_info.get("travel_type") else "border: 3px solid #E0E0E0;"
    
    st.markdown(f"""
        <div style="{card_style} border-radius: 16px; 
                    padding: 30px; text-align: center; min-height: 200px;
                    display: flex; flex-direction: column; justify-content: center;">
            <div style="font-size: 48px; margin-bottom: 15px;">🎯</div>
            <div style="font-size: 20px; font-weight: 700; color: #333; margin-bottom: 10px;">나들이 테마</div>
            <div style="font-size: 24px; font-weight: 600; color: #2196F3;">
                {travel_type_display}
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    companion_display = st.session_state.user_info.get("companion") or "미선택"
    card_style = "border: 3px solid #2196F3; background: #E3F2FD;" if st.session_state.user_info.get("companion") else "border: 3px solid #E0E0E0;"
    
    st.markdown(f"""
        <div style="{card_style} border-radius: 16px; 
                    padding: 30px; text-align: center; min-height: 200px;
                    display: flex; flex-direction: column; justify-content: center;">
            <div style="font-size: 48px; margin-bottom: 15px;">👥</div>
            <div style="font-size: 20px; font-weight: 700; color: #333; margin-bottom: 10px;">동행 특성</div>
            <div style="font-size: 24px; font-weight: 600; color: #2196F3;">
                {companion_display}
            </div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    region_display = st.session_state.user_info.get("region") or "미선택"
    card_style = "border: 3px solid #2196F3; background: #E3F2FD;" if st.session_state.user_info.get("region") else "border: 3px solid #E0E0E0;"
    
    st.markdown(f"""
        <div style="{card_style} border-radius: 16px; 
                    padding: 30px; text-align: center; min-height: 200px;
                    display: flex; flex-direction: column; justify-content: center;">
            <div style="font-size: 48px; margin-bottom: 15px;">📍</div>
            <div style="font-size: 20px; font-weight: 700; color: #333; margin-bottom: 10px;">방문 지역</div>
            <div style="font-size: 24px; font-weight: 600; color: #2196F3;">
                {region_display}
            </div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# 버튼 영역
# ============================================================================
st.markdown("---")

# 최종 제출 버튼 (모든 정보가 있을 때)
if all([st.session_state.user_info.get("travel_type"), 
        st.session_state.user_info.get("companion"), 
        st.session_state.user_info.get("region")]):
    
    st.markdown('<div class="final-button">', unsafe_allow_html=True)
    
    if st.button("✅ 추천 코스 보기", use_container_width=True):
        # style.py 세션 상태에 저장
        st.session_state["travel_type"] = st.session_state.user_info["travel_type"]
        st.session_state["companion"] = st.session_state.user_info["companion"]
        st.session_state["region"] = st.session_state.user_info["region"]
        
        # 페이지 이동
        st.switch_page("pages/4_rec.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # 경고 메시지
    st.markdown("""
        <div class="warning-message">
            ⚠️ 음성을 녹음하여 모든 정보를 입력해주세요
        </div>
    """, unsafe_allow_html=True)
    
    # 직접 선택 옵션
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 음성 입력 초기화", use_container_width=True):
            st.session_state.chat_history = [
                {"role": "assistant", "content": "안녕하세요! 예술, 전통, 산책, 체험 중 어떤 테마를 원하시나요?"}
            ]
            st.session_state.user_info = {
                "travel_type": None,
                "companion": None,
                "region": None
            }
            st.session_state.initial_tts_played = False
            st.rerun()
    
    with col2:
        if st.button("✏️ 직접 선택하기", use_container_width=True):
            st.switch_page("pages/1_companion.py")

# ============================================================================
# 푸터
# ============================================================================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 20px; color: #999; font-size: 14px;">
        <p>🛣️ 고운길 - 모두를 위한 나들이 추천 서비스</p>
        <p>음성 인식 기능으로 더욱 편리하게 이용하세요</p>
    </div>
""", unsafe_allow_html=True)