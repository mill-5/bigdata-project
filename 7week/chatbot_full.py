import streamlit as st
import ollama

# ── 페이지 설정 ──
st.set_page_config(page_title="AI 챗봇", page_icon="🤖", layout="wide")

# ── 사이드바: 설정 ──
with st.sidebar:
    st.header("챗봇 설정")

    # 시스템 프롬프트 선택
    system_prompts = {
        "이유미": "당신의 이름은 이유미 답변이 오두방정거리고 !!!!!!!라던가 신기한 이모지를 많이 쓴다, 동갑, 동성 여자아이, 아이돌을 좋아하고 흥, 어? 아? 같은 말을 많이 씀",
        "양서린": "당신의 이름은 양서린, 친한 여자동생 언니들을 좋아하고 헤헤, 히히, 머!? 언니 좋아 같은 반응을 많이 사용한다, 말 끝에 귀여운 이모티콘을 많이 붙인다.",
        "윤하진": "당신의 이름은 윤하진 제일 친한 친구, 윤하진의 남자친구가 군대에 들어가서 연락이 잘 안되서 화가 나있음, 쿨한 말투 오키오키 같은"
    }

    selected_role = st.selectbox("AI 역할 선택", list(system_prompts.keys()))

    # 직접 입력 옵션
    custom_prompt = st.text_area(
        "또는 직접 입력:",
        placeholder="AI에게 부여할 역할을 입력하세요...",
        height=100
    )

    # Temperature 조절 (Ollama의 options 파라미터로 전달됨)
    temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.1)

    st.divider()

    # 대화 초기화 버튼
    if st.button("대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # 대화 통계
    if "messages" in st.session_state:
        user_msgs = sum(1 for m in st.session_state.messages if m["role"] == "user")
        st.caption(f"대화 수: {user_msgs}턴")

# ── 시스템 프롬프트 결정 ──
system_prompt = custom_prompt.strip() if custom_prompt.strip() else system_prompts[selected_role]

# ── 메인 화면 ──
st.title("AI 챗봇")
st.caption(f"현재 역할: {selected_role} | Temperature: {temperature}")

# ── 대화 기록 초기화 ──
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── 기존 대화 표시 ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── 사용자 입력 ──
user_input = st.chat_input("메시지를 입력하세요")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Ollama에 전달할 메시지 (시스템 프롬프트 + 대화 기록)
    ollama_messages = [
        {"role": "system", "content": system_prompt}
    ] + st.session_state.messages

    with st.chat_message("assistant"):
        stream = ollama.chat(
            model="gemma3:4b",
            messages=ollama_messages,
            stream=True,
            options={"temperature": temperature}  # options: Ollama 모델 동작 제어 (temperature, top_k, top_p 등을 딕셔너리로 전달)
        )

        def stream_generator():
            for chunk in stream:
                yield chunk["message"]["content"]

        full_response = st.write_stream(stream_generator())

    st.session_state.messages.append({"role": "assistant", "content": full_response})