import streamlit as st
import json
import pandas as pd
import base64

# 페이지 설정
st.set_page_config(
    page_title="서울시 무장애 편의시설 정보",
    page_icon="♿",
    layout="centered"
)

# ==================== 스타일 적용 ====================
def apply_page_style():
    """페이지 공통 스타일 적용"""
    st.markdown("""
    <style>
    /* ==================== 전역 설정 ==================== */
    .stApp {
        background: white;
    }
    
    /* 페이지 컨테이너 크기 및 여백 조정 */
    .block-container {
        padding-top: 4rem !important;
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
    
    /* ==================== 정보 박스 ==================== */
    .info-box {
        background: #E3F2FD;
        border-left: 6px solid #2196F3;
        border-radius: 12px;
        padding: 18px 24px;
        margin: 20px 0;
        font-size: 16px;
        color: #1565C0;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(33, 150, 243, 0.1);
    }
    
    /* ==================== 구분선 ==================== */
    hr {
        margin: 30px 0;
        border: none;
        border-top: 2px solid #E3F2FD;
    }
    
    /* ==================== Streamlit 기본 요소 스타일링 ==================== */
    .stMarkdown {
        font-size: 16px;
    }
    
    /* 반응형 디자인 */
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
        
        .subtitle {
            font-size: 16px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 스타일 적용
apply_page_style()

# ==================== style.py 함수들 추가 ====================
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

# 이미지를 base64로 인코딩하는 함수
def encode_image_to_base64(image_path):
    try:
        with open(image_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
        return f"data:image/png;base64,{img_data}"
    except:
        return None

# JSON 데이터 로드
@st.cache_data
def load_data():
    with open('map_fac.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # subcategory에서 | 뒷부분만 추출
    for item in data:
        if 'subcategory' in item and item['subcategory']:
            parts = item['subcategory'].split('|')
            item['category'] = parts[1].strip() if len(parts) > 1 else parts[0].strip()
        else:
            item['category'] = '기타'
    
    return data

# 데이터 로드
data = load_data()

# 카테고리별 색상 및 아이콘 설정
category_config = {
    '전동휠체어충전소': {'color': '#FF6B6B', 'icon': '🔋'},
    '장애인화장실': {'color': '#4ECDC4', 'icon': '🚻'},
    '지하철엘리베이터': {'color': '#45B7D1', 'icon': '🛗'},
    '동주민센터': {'color': '#FFA07A', 'icon': '🏢'},
    '보건소': {'color': '#98D8C8', 'icon': '🏥'},
    '장애인복지관': {'color': '#F7DC6F', 'icon': '♿'},
    '장애인자립생활센터': {'color': '#BB8FCE', 'icon': '🏠'},
    '지하철출입구리프트': {
        'color': '#85C1E2', 
        'icon': '🔼',
        'use_image': True,
        'image_path': 'lift.png'
    }
}

# 이미지를 base64로 인코딩
for category, config in category_config.items():
    if config.get('use_image') and config.get('image_path'):
        base64_image = encode_image_to_base64(config['image_path'])
        if base64_image:
            config['image_base64'] = base64_image

        # ★ 이미지가 있으면 텍스트 아이콘 비활성화
        config['icon'] = ''


# ==================== 헤더 렌더링 ====================
def toggle_help():
    """도움말 토글 콜백"""
    st.session_state["show_help"] = not st.session_state.get("show_help", False)

render_header(toggle_help)

# 도움말 모달 표시
if st.session_state.get("show_help", False):
    show_help_modal()

st.markdown("---")

# HTML 지도 생성
map_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>무장애 편의시설 지도</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
    <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/leaflet.locatecontrol@0.79.0/dist/L.Control.Locate.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet.locatecontrol@0.79.0/dist/L.Control.Locate.min.css" />
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        
        #map {{
            width: 100%;
            height: 100vh;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}
        
        /* 필터 버튼 컨테이너 - style.py 디자인 적용 (배경 투명) */
        .filter-container {{
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            display: flex;
            gap: 12px;
            max-width: 95%;
            overflow-x: auto;
            overflow-y: visible;
            padding: 12px;
            padding-bottom: 18px;
            background: transparent;
        }}
        
        /* 스크롤바 스타일링 */
        .filter-container::-webkit-scrollbar {{
            height: 8px;
        }}
        
        .filter-container::-webkit-scrollbar-track {{
            background: rgba(0,0,0,0.05);
            border-radius: 10px;
        }}
        
        .filter-container::-webkit-scrollbar-thumb {{
            background: rgba(33, 150, 243, 0.4);
            border-radius: 10px;
        }}
        
        .filter-container::-webkit-scrollbar-thumb:hover {{
            background: rgba(33, 150, 243, 0.7);
        }}
        
        /* 필터 버튼 - style.py 디자인 적용 */
        .filter-btn {{
            padding: 12px 24px;
            border-radius: 20px;
            border: 3px solid #E0E0E0;
            background: white;
            color: #333;
            cursor: pointer;
            font-size: 16px;
            font-weight: 700;
            transition: all 0.3s ease;
            white-space: nowrap;
            user-select: none;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        
        .filter-btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 16px rgba(33, 150, 243, 0.25);
            border-color: #64B5F6;
        }}
        
        .filter-btn.active {{
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
            color: white;
            border-color: #1976D2;
            box-shadow: 0 4px 14px rgba(33, 150, 243, 0.4);
        }}
        
        .filter-btn.active:hover {{
            background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
            box-shadow: 0 6px 18px rgba(33, 150, 243, 0.5);
        }}
        
        /* 전체 버튼 스타일 */
        .all-btn {{
            background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
            color: white;
            border-color: #388E3C;
            font-weight: 800;
        }}
        
        .all-btn:hover {{
            background: linear-gradient(135deg, #66BB6A 0%, #43A047 100%);
        }}
        
        .all-btn.active {{
            background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
            box-shadow: 0 5px 16px rgba(76, 175, 80, 0.4);
        }}
        
        /* 마커 기본 스타일 */
        .leaflet-marker-icon {{
            transition: transform 0.2s ease;
            transform-origin: bottom center;
        }}
        
        .leaflet-marker-icon:hover {{
            transform: scale(1.2);
            z-index: 10000;
        }}
        
        /* 팝업 스타일 개선 */
        .leaflet-popup-content-wrapper {{
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }}
        
        .leaflet-popup-content {{
            margin: 16px;
            font-size: 15px;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    
    <!-- 필터 버튼 (1줄) -->
    <div class="filter-container">
        <button class="filter-btn all-btn active" onclick="toggleAll()">🌟 전체</button>
        <button class="filter-btn active" data-category="전동휠체어충전소">🔋 전동 휠체어 충전소</button>
        <button class="filter-btn active" data-category="장애인화장실">🚻 장애인 화장실</button>
        <button class="filter-btn active" data-category="지하철엘리베이터">🛗 지하철 엘리베이터</button>
        <button class="filter-btn active" data-category="동주민센터">🏢 동 주민센터</button>
        <button class="filter-btn active" data-category="보건소">🏥 보건소</button>
        <button class="filter-btn active" data-category="장애인복지관">♿ 장애인 복지관</button>
        <button class="filter-btn active" data-category="장애인자립생활센터">🏠 장애인 자립 센터</button>
        <button class="filter-btn active" data-category="지하철출입구리프트">🔼 지하철 출입구 리프트</button>
    </div>

    <script>
        // 데이터
        const facilities = {json.dumps(data, ensure_ascii=False)};
        
        // 카테고리별 색상
        const categoryColors = {json.dumps({k: v['color'] for k, v in category_config.items()})};
        
        const categoryIcons = {json.dumps({k: v['icon'] for k, v in category_config.items()})};
        
        // 카테고리별 이미지 (base64)
        const categoryImages = {json.dumps({k: v.get('image_base64', '') for k, v in category_config.items()})};
        
        const categoryUseImage = {json.dumps({k: v.get('use_image', False) for k, v in category_config.items()})};
        
        // 지도 초기화
        const map = L.map('map').setView([37.5735, 126.9788], 13);
        
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);
        
        // 마커 클러스터 그룹 (카테고리별)
        const markerGroups = {{}};
        const allMarkers = [];
        
        // 카테고리별 레이어 그룹 생성
        Object.keys(categoryColors).forEach(category => {{
            markerGroups[category] = L.layerGroup().addTo(map);
        }});
        
        // 마커 생성
        facilities.forEach(facility => {{
            const category = facility.category;
            if (!markerGroups[category]) return;
            
            const lat = facility.y;
            const lng = facility.x;
            const color = categoryColors[category] || '#gray';
            const emoji = categoryIcons[category] || '📍';
            const useImage = categoryUseImage[category];
            const imageUrl = categoryImages[category];
            
            let customIcon;
            
            if (useImage && imageUrl) {{
                // 이미지 아이콘 사용
                const iconHtml = `
                    <div style="
                        width: 40px;
                        height: 40px;
                        background-color: white;
                        border: 3px solid ${{color}};
                        border-radius: 8px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
                        overflow: hidden;
                    ">
                        <img src="${{imageUrl}}" style="width: 100%; height: 100%; object-fit: cover;" />
                    </div>
                `;
                
                customIcon = L.divIcon({{
                    html: iconHtml,
                    className: 'custom-marker',
                    iconSize: [40, 40],
                    iconAnchor: [20, 40]
                }});
            }} else {{
                // 이모지 아이콘 사용 - 네모난 모양, 적당한 크기
                const iconHtml = `
                    <div style="
                        font-size: 28px;
                        text-align: center;
                        line-height: 1;
                        width: 48px;
                        height: 48px;
                        background-color: white;
                        border: 3px solid ${{color}};
                        border-radius: 10px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        box-shadow: 0 3px 8px rgba(0,0,0,0.35);
                        padding: 2px;
                    ">
                        ${{emoji}}
                    </div>
                `;
                
                customIcon = L.divIcon({{
                    html: iconHtml,
                    className: 'custom-marker',
                    iconSize: [48, 48],
                    iconAnchor: [24, 48]
                }});
            }}
            
            // 팝업 - 스타일 개선
            const popupContent = `
                <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; min-width: 220px;">
                    <h3 style="margin: 0 0 12px 0; color: #2196F3; font-size: 18px; font-weight: 700;">${{facility.content_name}}</h3>
                    <div style="background: #F5F5F5; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                        <p style="margin: 0; font-size: 14px;"><strong style="color: #1976D2;">카테고리:</strong> <span style="color: #333;">${{category}}</span></p>
                    </div>
                    <p style="margin: 0; font-size: 14px; line-height: 1.5; color: #666;"><strong style="color: #1976D2;">📍 주소:</strong><br>${{facility.address}}</p>
                </div>
            `;
            
            const marker = L.marker([lat, lng], {{ icon: customIcon }})
                .bindPopup(popupContent)
                .bindTooltip(`${{emoji}} ${{facility.content_name}}`);
            
            marker.category = category;
            marker.addTo(markerGroups[category]);
            allMarkers.push(marker);
        }});
        
        // 위치 추적 버튼
        L.control.locate({{
            position: 'bottomright',
            strings: {{
                title: '내 위치 찾기'
            }},
            locateOptions: {{
                enableHighAccuracy: true
            }}
        }}).addTo(map);
        
        // 자동 위치 찾기
        setTimeout(() => {{
            const locateBtn = document.querySelector('.leaflet-control-locate a');
            if (locateBtn) locateBtn.click();
        }}, 1000);
        
        // 필터 버튼 클릭
        document.querySelectorAll('.filter-btn[data-category]').forEach(btn => {{
            btn.addEventListener('click', function() {{
                const category = this.dataset.category;
                const isActive = this.classList.contains('active');
                
                if (isActive) {{
                    this.classList.remove('active');
                    map.removeLayer(markerGroups[category]);
                }} else {{
                    this.classList.add('active');
                    map.addLayer(markerGroups[category]);
                }}
                
                updateAllButton();
            }});
        }});
        
        // 전체 선택/해제
        function toggleAll() {{
            const allBtn = document.querySelector('.all-btn');
            const filterBtns = document.querySelectorAll('.filter-btn[data-category]');
            const isActive = allBtn.classList.contains('active');
            
            if (isActive) {{
                // 전체 해제
                allBtn.classList.remove('active');
                filterBtns.forEach(btn => {{
                    btn.classList.remove('active');
                    const category = btn.dataset.category;
                    map.removeLayer(markerGroups[category]);
                }});
            }} else {{
                // 전체 선택
                allBtn.classList.add('active');
                filterBtns.forEach(btn => {{
                    btn.classList.add('active');
                    const category = btn.dataset.category;
                    map.addLayer(markerGroups[category]);
                }});
            }}
        }}
        
        // 전체 버튼 상태 업데이트
        function updateAllButton() {{
            const allBtn = document.querySelector('.all-btn');
            const filterBtns = document.querySelectorAll('.filter-btn[data-category]');
            const activeBtns = document.querySelectorAll('.filter-btn[data-category].active');
            
            if (activeBtns.length === filterBtns.length) {{
                allBtn.classList.add('active');
            }} else {{
                allBtn.classList.remove('active');
            }}
        }}
    </script>
</body>
</html>
"""

# 지도 표시
st.components.v1.html(map_html, height=800, scrolling=False)

st.markdown("---")
st.markdown('<div class="info-box">💡 지도 상단의 필터 버튼을 클릭하여 원하는 시설 유형만 표시할 수 있습니다.</div>', unsafe_allow_html=True)
