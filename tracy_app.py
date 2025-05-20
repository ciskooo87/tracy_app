import streamlit as st
import requests
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Tracy, sua amiga pensativa", layout="centered")
st.title("Tracy, sua amiga pensativa")
st.write("Conversas empáticas para te ajudar a parar de fumar maconha.")

# Lê token da Hugging Face dos segredos
HF_API_TOKEN = st.secrets["huggingface"]["api_key"]
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

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
        prompt = ""
        for msg in st.session_state.history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                prompt += f"<|user|>
{content}
"
            elif role == "assistant":
                prompt += f"<|assistant|>
{content}
"
            elif role == "system":
                prompt = f"<|system|>
{content}
" + prompt
        prompt += "<|assistant|>
"

        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 256, "temperature": 0.7},
        }

        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
        st.write("Resposta bruta da API:", response.text)
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

for msg in st.session_state.history[1:]:
    speaker = "Tracy" if msg["role"] == "assistant" else "Você"
    st.markdown(f"**{speaker}:** {msg['content']}")
