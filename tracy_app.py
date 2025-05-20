import streamlit as st
import requests
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Tracy, sua amiga pensativa", layout="centered")

# CSS para modo escuro, campo abaixo, respostas acima, e texto em português
st.markdown(
    '''
    <style>
    .main {
        background-color: #1e1e1e;
        color: #f0f0f0;
    }
    .chat-container {
        display: flex;
        flex-direction: column-reverse;
    }
    .message {
        padding: 0.8rem 1rem;
        margin: 0.4rem 0;
        border-radius: 12px;
        max-width: 85%;
        word-wrap: break-word;
        font-size: 1rem;
    }
    .user {
        background-color: #4a7c59;
        color: #fff;
        align-self: flex-end;
        margin-left: auto;
    }
    .assistant {
        background-color: #2f2f2f;
        color: #f0f0f0;
        border: 1px solid #444;
        align-self: flex-start;
        margin-right: auto;
    }
    .stTextInput > div > input {
        background-color: #2f2f2f;
        color: white;
    }
    .stButton > button {
        background-color: #4a7c59;
        color: white;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

st.title("Tracy, sua amiga pensativa")
st.caption("Conversas empáticas para te ajudar a parar de fumar maconha.")

HF_API_TOKEN = st.secrets["huggingface"]["api_key"]
HF_API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

# prompt inicial fixo em português
if "history" not in st.session_state:
    st.session_state.history: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": "Você é Tracy, uma amiga empática e compassiva. Fale apenas em português. Ofereça apoio emocional gentil, reflexivo e prático para quem deseja parar de fumar maconha, usando também linguagem inspirada em hipnose suave. Seja calorosa, envolvente e sem julgamentos."
        }
    ]

# Campo de mensagem ao final da tela
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Digite sua mensagem:", label_visibility="collapsed")
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
            "parameters": {"max_new_tokens": 256, "temperature": 0.7},
        }

        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        output = response.json()

        if isinstance(output, list) and "generated_text" in output[0]:
            generated = output[0]["generated_text"]
            assistant_reply = generated.split("<|assistant|>")[-1].strip()
        else:
            assistant_reply = output[0]["generated_text"]

        st.session_state.history.append({"role": "assistant", "content": assistant_reply})

    except Exception as e:
        logger.error(f"Erro ao chamar a IA Hugging Face: {e}")
        st.error(f"Erro ao chamar a IA: {e}")
        st.stop()

st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in reversed(st.session_state.history[1:]):
    role = msg["role"]
    content = msg["content"]
    css_class = "user" if role == "user" else "assistant"
    st.markdown(f'<div class="message {css_class}">{content}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
