import streamlit as st
import requests
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Tracy, sua amiga pensativa", layout="centered")

# Estilo visual tipo WhatsApp com campo no fim e layout elegante
st.markdown(
    '''
    <style>
    .main {
        background-color: #111;
        color: #f0f0f0;
    }
    .chat-container {
        display: flex;
        flex-direction: column-reverse;
        padding-bottom: 6rem;
    }
    .message {
        padding: 0.9rem 1.1rem;
        margin: 0.5rem 0;
        border-radius: 18px;
        max-width: 80%;
        word-wrap: break-word;
        font-size: 1rem;
        line-height: 1.5;
    }
    .user {
        background-color: #25d366;
        color: #000;
        align-self: flex-end;
        margin-left: auto;
    }
    .assistant {
        background-color: #2f2f2f;
        color: #fff;
        border: 1px solid #444;
        align-self: flex-start;
        margin-right: auto;
    }
    .stTextInput > div > input {
        background-color: #2f2f2f;
        color: white;
    }
    .stButton > button {
        background-color: #075e54;
        color: white;
        border-radius: 20px;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

st.title("Tracy, sua amiga pensativa")

# Seletor de prompt
prompt_opcoes = {
    "Parar de fumar maconha": "Você é Tracy, uma amiga empática e compassiva. Fale apenas em português. Ofereça apoio emocional gentil, reflexivo e prático para quem deseja parar de fumar maconha, usando também linguagem inspirada em hipnose suave. Seja calorosa, envolvente e sem julgamentos.",
    "Ansiedade e sono": "Você é Tracy, uma amiga calma e empática que ajuda pessoas a dormir melhor e controlar a ansiedade com técnicas suaves e apoio emocional acolhedor. Use linguagem relaxante e compassiva, apenas em português.",
    "Autoestima e motivação": "Você é Tracy, uma amiga empática que ajuda pessoas a recuperar a autoconfiança, autoestima e motivação com orientações leves e encorajadoras, sempre em português e sem julgamentos."
}
escolha = st.selectbox("Escolha um tema para conversar com a Tracy:", list(prompt_opcoes.keys()))

if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    if st.button("Começar"):
        st.session_state.started = True
        st.session_state.history = [{"role": "system", "content": prompt_opcoes[escolha]}]
        st.rerun()
    st.stop()

# Se estiver iniciado, carrega o histórico
if "history" not in st.session_state:
    st.session_state.history: List[Dict[str, str]] = [{"role": "system", "content": prompt_opcoes[escolha]}]

HF_API_TOKEN = st.secrets["huggingface"]["api_key"]
HF_API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

# Campo de entrada (formulário) ao fim da página
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Digite sua mensagem...", label_visibility="collapsed")
    submitted = st.form_submit_button("Enviar")

if submitted and user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    try:
        messages = ""
        for msg in st.session_state.history:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                messages += f"<|system|>\n{content}\n"
            elif role == "user":
                messages += f"<|user|>\n{content}\n"
            elif role == "assistant":
                messages += f"<|assistant|>\n{content}\n"
        messages += "<|assistant|>\n"

        payload = {
            "inputs": messages,
            "parameters": {"max_new_tokens": 600, "temperature": 0.7},
        }

        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        output = response.json()

        assistant_reply = output[0]["generated_text"].split("<|assistant|>")[-1].strip()
        st.session_state.history.append({"role": "assistant", "content": assistant_reply})

    except Exception as e:
        logger.error(f"Erro ao chamar a IA Hugging Face: {e}")
        st.error(f"Erro ao chamar a IA: {e}")
        st.stop()

# Área de conversa
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in reversed(st.session_state.history[1:]):
    role = msg["role"]
    content = msg["content"]
    css_class = "user" if role == "user" else "assistant"
    st.markdown(f'<div class="message {css_class}">{content}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
