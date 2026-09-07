import streamlit as st
from rag_engine import answer_question

st.set_page_config(page_title="Quantum AI Tutor", page_icon="⚛️")
st.title("⚛️ Quantum Computing AI Tutor")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask any quantum computing question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            response = answer_question(prompt)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})