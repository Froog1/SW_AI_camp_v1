import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("스무고개 게임")
st.write(
    "스무고개 게임은 한 사람이 생각한 단어를 다른 사람들이 질문을 통해 맞추는 게임입니다. 질문은 예/아니오로 답할 수 있으며,꼭 20번의 질문 안에 단어를 맞춰야 합니다."
)

st.write("Please enter your OpenAI API key below.")
openai_api_key = st.text_input("OpenAI API Key", type="password")

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.write("API 키를 입력하고 출제자와 도전자 중에서 선택하세요")

    # 메시지와 역할 메시지 추가 플래그 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "system", "content": "스무고개 게임입니다. 한 사람이 단어를 생각하고 다른 사람은 예/아니오 질문으로 단어를 맞춥니다. 20번의 질문 안에 단어를 맞춰야 합니다."})

    if "role_message_added" not in st.session_state:
        st.session_state.role_message_added = False

    # 출제자와 도전자 선택
    choice1 = st.checkbox("출제자")
    choice2 = st.checkbox("도전자")

    if choice1 and not st.session_state.role_message_added:
        role_message = "당신은 질문을 통해 답을 맞추는 역할입니다. 먼저 질문을 던져 단어를 맞추세요. 답변은 예/아니오로만 할 수 있습니다. 예/아니오가 나오는 질문을 통해 단어를 맞추세요"
        st.session_state.messages.append({"role": "system", "content": role_message})
        st.session_state.role_message_added = True
        st.write("문제를 내보시지, 다 맞춰버릴테다!")

        # Assistant가 질문을 먼저 시작하도록 OpenAI API 호출
        stream = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )


        # Stream the response to the chat using st.write_stream, then store it in 
        # session state.
        with st.chat_message("assistant"):
            initial_question = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": initial_question})

    elif choice2 and not st.session_state.role_message_added:
        role_message = "당신은 출제자입니다. 단어를 생각하고 사용자 질문에 예/아니오로 답하세요."
        st.session_state.messages.append({"role": "system", "content": role_message})
        st.session_state.role_message_added = True
        st.write("맞추기 어려울걸? 힘내보라고")




    # Display the existing chat messages via st.chat_message.
   # 기존 채팅 메시지 표시 (system 메시지는 제외)
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("Are you ready?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream the response to the chat using st.write_stream, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})