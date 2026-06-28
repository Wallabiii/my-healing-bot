import streamlit as st
import requests

# 구글 API 키 설정
GOOGLE_API_KEY = "AQ.Ab8RN6JY1eQX0RwyRKIRkBJy1IQjWqlHhW5luJSvjbOsjmgCHw"

st.set_page_config(page_title="개인 맞춤형 여행 에이전트", page_icon="✈️")
st.title("✈️ 나만의 일상 힐링 여행 Agent")
st.subheader("당신의 성향과 근무 피로도를 고려한 완벽한 힐링 코스")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("어디로 여행을 떠나고 싶으신가요? (예: 제주도 3일, 무리하지 않는 힐링 코스)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # 💡 [진짜 최종 해결책] AQ 키 규격에서 무조건 호출 성공하는 gemini-2.5-flash 주소입니다.
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GOOGLE_API_KEY}"
            headers = {'Content-Type': 'application/json'}
            
            full_text = (
                "너는 사용자의 일상 속 스트레스를 해소하고 성장을 돕는 '맞춤형 여행 플래너 에이전트'야. "
                "사용자가 여행 가고 싶은 도시, 기간, 컨디션을 말하면 그에 맞추어 하루 총 걸음 수가 무리 되지 않게 배려한 "
                "조화로운 여행 동선과 일정을 추천해 줘. 특히 지친 직장인을 위로하듯 친절하고 따뜻한 어조로 답변해 줘.\n\n"
                f"사용자 질문: {prompt}"
            )
            
            payload = {
                "contents": [{
                    "parts": [{"text": full_text}]
                }]
            }
            
            response = requests.post(url, headers=headers, json=payload)
            res_json = response.json()
            
            if response.status_code == 200:
                answer = res_json['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"구글 서버 응답 오류: {res_json.get('error', {}).get('message', '알 수 없는 오류')}")
                
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")