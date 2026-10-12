
import streamlit as st
import requests

st.set_page_config(
    page_title="Multi-Agent AI Quora",
    page_icon="🧠"
)

st.title("🧠 Multi-Agent AI")
st.caption("Powered by NVIDIA Nemotron 3 Ultra X Quora")

MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def ask_agent(system_prompt, user_message):
    api_key = st.secrets["OPENROUTER_API_KEY"]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.4,
        "max_tokens": 700,
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=120,
    )

    if not response.ok:
        raise RuntimeError(
            f"OpenRouter error {response.status_code}: "
            f"{response.text[:500]}"
        )

    data = response.json()
    return data["choices"][0]["message"]["content"]


question = st.chat_input("Tulis pertanyaan lu...")

if question:
    st.chat_message("user").write(question)

    with st.spinner("Agen AI sedang berpikir..."):
        try:
            answer = ask_agent(
                "Lu adalah AI assistant yang logis, "
                "kritis, dan menjawab dalam bahasa Indonesia.",
                question,
            )
            st.chat_message("assistant").write(answer)

        except Exception as error:
            st.error(f"Gagal mendapatkan jawaban: {error}")
