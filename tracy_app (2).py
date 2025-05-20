import streamlit as st
import requests
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Tracy, sua amiga pensativa", layout="centered")
st.title("Tracy, sua amiga pensativa")
st.write("Conversas empáticas para te ajudar a parar de fumar maconha.")

if "history" not in st.session_state:
    st.session_state.history: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": "Você é Tracy, uma amiga empática e compassiva. Use o seguinte prompt base para responder com apoio emocional e técnicas de hipnose.\n\nPROMPT: Tracy, a Amiga Pensativa [resumo do prompt real]."
        }
    ]

user_input = st.text_input("Você:", key="user_input")

if st.button("Enviar") and user_input:
    st.session_state.history.append({"role": "user", "content": user_input})

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer SUA_NOVA_CHAVE_AQUI",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": st.session_state.history,
                "temperature": 0.7
            },
            timeout=30
        )

        st.write("Resposta bruta da API:", response.text)  # DEBUG

        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        st.session_state.history.append({"role": "assistant", "content": reply})

    except Exception as e:
        logger.error(f"Erro ao chamar o modelo: {e}")
        st.error(f"Erro ao chamar a IA: {e}")
        st.stop()

for msg in st.session_state.history[1:]:
    speaker = "Tracy" if msg["role"] == "assistant" else "Você"
    st.markdown(f"**{speaker}:** {msg['content']}")