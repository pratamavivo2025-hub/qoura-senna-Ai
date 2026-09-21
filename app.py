import streamlit as st
import os
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Quora Senna LIQ",
    page_icon="📈",
    layout="centered"
)

st.title("📈 Quora Senna LIQ")
st.caption("Analis Keuangan, Pasar Saham & Kripto Objektif Berbasis Data")

with st.sidebar:
    st.header("🔑 Konfigurasi API")
    api_key_input = st.text_input("Masukan Gemini API Key:", type="password")
    st.markdown("---")
    st.markdown("""
    **Fitur Utama:**
    - Analisis Dokumen / PDF Laporan Keuangan
    - Hitung Rasio (PE, PBV, ROI, FCF, MoS)
    - Tesis Investasi Saham & Kripto Berbasis Data
    """)

SYSTEM_INSTRUCTION = """
Kamu adalah "Quora Senna LIQ", seorang analis senior independen dan ahli dalam bidang:
1. Investasi Value & Growth (Saham & Kripto).
2. Keuangan Perusahaan, Akuntansi Forensik, & Analisis Laporan Keuangan.
3. Pembongkaran Laporan Keuangan (10-K, 10-Q, Laporan Tahunan/Keuangan IDX/SEC).

Aturan Utama Persona Quora Senna LIQ:
- Objektif, brutal jujur, dan berbasis fakta/data. Tanpa bias hype, tanpa promosi, dan tanpa bualan.
- Jika data buruk atau fundamental tidak aman, katakan secara langsung.
- Gunakan metode perhitungan rasio keuangan secara akurat (PE, PBV, ROE, ROI, FCF Yield, WACC, DCF, Margin of Safety).
- Mampu menyusun tesis investasi komprehensif, terstruktur, dan siap pakai untuk keputusan institusional maupun individual.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

uploaded_file = st.file_uploader("Upload PDF Laporan Keuangan (Opsional)", type=["pdf"])

if prompt := st.chat_input("Tanyakan sesuatu atau minta analisis tesis..."):
    if not api_key_input:
        st.error("Silakan masukkan Gemini API Key kamu di menu samping (Sidebar) terlebih dahulu!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            client = genai.Client(api_key=api_key_input)
            contents = []

            if uploaded_file is not None:
                with st.spinner("Mengunggah dan membaca dokumen PDF..."):
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    pdf_doc = client.files.upload(file=temp_path)
                    contents.append(pdf_doc)
                    os.remove(temp_path)

            contents.append(prompt)

            with st.spinner("Quora Senna LIQ sedang menganalisis data..."):
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.2,
                    )
                )

            reply = response.text
            with st.chat_message("assistant"):
                st.markdown(reply)
            
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"Terjadi Kesalahan: {str(e)}")

