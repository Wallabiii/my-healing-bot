import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# 구글 API 키 설정 (검증된 키)
GOOGLE_API_KEY = "AQ.Ab8RN6JY1eQX0RwyRKIRkBJy1IQjWqlHhW5luJSvjbOsjmgCHw"

# 1. 페이지 레이아웃 설정
st.set_page_config(page_title="나만의 일상 힐링 여행 에이전트", page_icon="✈️", layout="wide")

# 2. 왼쪽 사이드바 (여행 스타일 + 동행자 + 구체적 액수 슬라이더)
with st.sidebar:
    # 📸 원본 해변 풍경 이미지 유지
    st.image("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=500", width="stretch")
    
    st.markdown("### 🎯 나의 여행 스타일")
    travel_style = st.selectbox(
        "어떤 여행을 선호하시나요?",
        ["🌿 조용한 감성 힐링 (최소 동선)", "📸 인생샷 투어 (명소 중심)", "🍕 핫플레이스 & 맛집 탐방", "🏃 액티비티 & 알찬 관광"]
    )
    
    st.markdown("### 👥 누구와 떠나시나요?")
    companion = st.radio(
        "동행자 선택",
        ["혼자만의 리프레시", "연인과 로맨틱 데이트", "가족/부모님과 효도 관광", "친구들과 우정 여행"],
        index=0
    )
    
    st.divider()
    
    # 💰 [구체적 액수 개조] 만원 단위 직관적 경비 슬라이더
    st.markdown("### 💵 하루 예상 경비 (1인 기준)")
    budget_amount = st.slider(
        "식비, 숙박, 교통 등을 포함한 하루 예산",
        min_value=3,      # 최소 3만원
        max_value=50,     # 최대 50만원
        value=15,         # 기본값 15만원
        step=1,           # 1만원 단위 조정
        format="%d 만원"
    )
    st.info(f"선택된 하루 예산: **{budget_amount}만 원**")

# 3. 메인 화면 타이틀 및 상단 상태창 (선택된 구체적 액수 실시간 노출)
st.title("✈️ 나만의 일상 힐링 여행 Agent")
st.markdown(f"#### *현재 세팅: **[{travel_style}]** | **[{companion}]** | **[하루 {budget_amount}만 원]** 맞춤형 동선 가이드*")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. 사용자 입력창 및 핵심 로직
if prompt := st.chat_input("어디로 여행을 떠나고 싶으신가요? (예: 제주도 3일)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GOOGLE_API_KEY}"
            headers = {'Content-Type': 'application/json'}
            
            # 🔥 구체적인 액수 수치 데이터를 프롬프트에 정확히 주입
            full_text = (
                "너는 사용자의 요구와 성향, 구체적인 예산 규모를 완벽하게 분석하는 '프리미엄 여행 플래너 에이전트'야.\n"
                f"현재 사용자가 선택한 여행 스타일은 [{travel_style}] 이며, 동행자는 [{companion}], 1인당 하루 총 예산은 정확히 [{budget_amount}만 원] 입니다.\n"
                f"사용자가 제시한 하루 {budget_amount}만 원이라는 구체적인 금액 안에서 해결 가능한 가성비 숙소나 고급 호텔, 식당, 유료 입장료 액티비티 등을 고려해서 지극히 '현실적인 일정'을 설계해 줘야 해.\n\n"
                "대답할 때 아래의 3가지 규칙을 '무조건' 지켜서 대답해줘:\n"
                "1. 선택된 스타일, 동행자, 구체적 예산 액수에 걸맞은 장소와 팁을 포함하여 다정하고 전문적인 어조로 일정을 추천해줘.\n"
                "2. [필수] 일정 소개 본문 바로 직후(중간 부분)에, 여행지 분위기에 어울리는 고화질 이미지 마크다운 스크립트를 '반드시' 한 줄 포함해 줘. 이미지 주소는 무조건 아래 예시 중 하나를 골라서 그대로 출력해.\n"
                "   - 제주/바다 감성일 때: ![jeju](https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600)\n"
                "   - 숲/힐링 감성일 때: ![forest](https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=600)\n"
                "3. 맨 마지막 줄에는 반드시 지도에 표시할 수 있도록 주요 경유지 3곳의 이름과 위도, 경도를 아래 포맷 예시처럼 정확히 한 줄만 출력해줘.\n"
                "포맷 예시: [MAP_DATA] 관광지1:33.51,126.53 | 관광지2:33.45,126.55 | 관광지3:33.48,126.48\n\n"
                f"사용자 질문: {prompt}"
            )
            
            payload = {"contents": [{"parts": [{"text": full_text}]}]}
            
            with st.spinner(f"하루 {budget_amount}만 원 예산에 딱 맞춘 최적의 힐링 코스를 계산 중입니다..."):
                response = requests.post(url, headers=headers, json=payload)
                res_json = response.json()
            
            if response.status_code == 200:
                raw_answer = res_json['candidates'][0]['content']['parts'][0]['text']
                
                if "[MAP_DATA]" in raw_answer:
                    main_answer, map_part = raw_answer.split("[MAP_DATA]", 1)
                else:
                    main_answer = raw_answer
                    map_part = ""
                
                st.markdown(main_answer)
                st.session_state.messages.append({"role": "assistant", "content": main_answer})
                
                if map_part and ":" in map_part and "," in map_part:
                    try:
                        st.markdown("### 🟩 AI 추천 맞춤형 최적 동선 레이아웃")
                        locations = []
                        points = map_part.strip().split("|")
                        
                        for p in points:
                            if ":" in p:
                                name, coord = p.split(":")
                                if "," in coord:
                                    lat, lon = map(float, coord.split(","))
                                    locations.append(([lat, lon], name.strip()))
                        
                        if locations:
                            m = folium.Map(location=locations[0][0], zoom_start=11)
                            coord_list = [loc[0] for loc in locations]
                            
                            for coord, name in locations:
                                folium.Marker(coord, popup=name, icon=folium.Icon(color='cadetblue', icon='info-sign')).add_to(m)
                            
                            folium.PolyLine(locations=coord_list, color="green", weight=4, opacity=0.8).add_to(m)
                            st_folium(m, width=700, height=400, returned_objects=[])
                    except Exception:
                        st.caption("📌 일정 전송이 완료되었습니다.")
            else:
                st.error(f"구글 서버 응답 오류: {res_json.get('error', {}).get('message', '알 수 없는 오류')}")
                
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
