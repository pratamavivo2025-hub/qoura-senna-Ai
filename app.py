import streamlit as st
import os
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Quora Senna LIQ v3.0",
    page_icon="📈",
    layout="centered"
)

# Fix Pull-To-Refresh, Styling Chat Bubble Kanan-Kiri, dan UI Clean
st.markdown("""
<style>
    /* 1. Mencegah efek tarik layar / Pull-To-Refresh di HP/WebView */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        overscroll-behavior-y: contain !important;
        overscroll-behavior: none !important;
        touch-action: pan-x pan-y !important;
    }

    /* 2. Styling Card Chat Bubble */
    .stChatMessage {
        border-radius: 16px;
        padding: 12px 18px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Bubble Chat User (Kanan) */
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        flex-direction: row-reverse;
        text-align: left;
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
    }

    /* Bubble Chat Assistant / AI (Kiri) */
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        background-color: #0f172a !important;
        color: #e2e8f0 !important;
        border: 1px solid #1e293b !important;
    }

    /* Merapikan Uploader File */
    .stFileUploader {
        border: 1px dashed #475569;
        border-radius: 12px;
        padding: 10px;
        background-color: #0f172a;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>

<script>
    // Mematikan gesture pull-down refresh secara paksa di level browser/WebView
    window.addEventListener('DOMContentLoaded', (event) => {
        document.body.style.overscrollBehaviorY = 'contain';
    });
</script>
""", unsafe_allow_html=True)

st.title("📈 Quora Senna LIQ v3.0")
st.caption("Analis Keuangan, Saham & Kripto Objektif | Powered by Gemini")

# ---------------------------------------------------------
# 2. INISIALISASI SESSION STATE (RIWAYAT OBROLAN LOKAL)
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------
# 3. SIDEBAR KONFIGURASI & RIWAYAT OBROLAN
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Konfigurasi & Fitur")
    api_key_input = st.text_input("Masukan Gemini API Key:", type="password")
    
    st.markdown("---")
    st.subheader("💬 Manajemen Obrolan")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Chat Baru", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("🗑️ Hapus Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    st.subheader("📜 Ringkasan Riwayat Sesi")
    if len(st.session_state.messages) == 0:
        st.info("Belum ada riwayat obrolan di sesi ini.")
    else:
        # Menampilkan ringkasan pertanyaan user sebelumnya di sidebar
        user_prompts = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
        for idx, prompt_text in enumerate(user_prompts, 1):
            short_text = prompt_text[:30] + "..." if len(prompt_text) > 30 else prompt_text
            st.caption(f"**{idx}.** {short_text}")

    st.markdown("---")
    st.markdown("""
    **Fitur Utama Version 3.0:**
    - 🔒 Anti-Refresh Saat Scroll Ke Atas
    - 📄 Dokumen PDF & Screenshot Laporan Keuangan
    - 🧠 Memori Obrolan Berkelanjutan
    - ⚡ Auto-Fallback Server Gemini
    """)

# ---------------------------------------------------------
# 4. SYSTEM INSTRUCTION (PERSONA GAUL, CERDAS & ADAPTIF)
# ---------------------------------------------------------
SYSTEM_INSTRUCTION = """
Kamu adalah "Quora Senna LIQ", seorang analis senior independen di bidang investasi saham, kripto, dan akuntansi forensik.

Gaya Bahasa & Tone:
- Gunakan bahasa yang gaul, santai, tapi tetap berbobot, tajam, dan profesional (menggunakan variasi 'gw/lu', 'bro', atau bahasa kasual finansial yang luwes).
- Tetap brutal jujur, objektif, berbasis data/fakta, tanpa bias hype, tanpa promosi, dan tanpa bualan.

Logika & Cara Berpikir:
1. Pahami konteks obrolan secara utuh dari riwayat percakapan sebelumnya. Adaptif dan belajar dari koreksi atau fakta baru yang diberikan user.
2. Jika ada data buruk atau fundamental tidak aman, katakan langsung secara gamblang.
3. Gunakan perhitungan rasio keuangan yang presisi (PE, PBV, ROE, ROI, FCF Yield, WACC, DCF, Margin of Safety).
4. Buat analisis tesis investasi yang terstruktur, tajam, komprehensif, dan siap pakai.
"""

# ---------------------------------------------------------
# 5. MENAMPILKAN ULANG SEMUA CHAT DI LAYAR UTAMA
# ---------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------------------------------------
# 6. INPUT FILE & PROMPT
# ---------------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload PDF atau Foto Laporan Keuangan (Opsional)", 
    type=["pdf", "png", "jpg", "jpeg"]
)

if prompt := st.chat_input("Tanyakan sesuatu atau minta analisis tesis..."):
    if not api_key_input:
        st.error("Masukkan Gemini API Key kamu di sidebar dulu ya, bro!")
    else:
        # Simpan pesan user ke memori
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            client = genai.Client(api_key=api_key_input)
            contents = []

            # Process file upload (PDF / Gambar)
            if uploaded_file is not None:
                with st.spinner("Membaca dan memproses dokumen/foto..."):
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    uploaded_doc = client.files.upload(file=temp_path)
                    contents.append(uploaded_doc)
                    os.remove(temp_path)

            # Memasukkan riwayat percakapan sebelumnya sebagai konteks memori AI
            for msg in st.session_state.messages[:-1]:
                contents.append(f"{msg['role'].capitalize()}: {msg['content']}")
            
            # Memasukkan prompt terbaru
            contents.append(f"User: {prompt}")

            with st.spinner("Quora Senna LIQ sedang memikirkan tesis & menganalisis data..."):
                try:
                    # Model Utama
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION,
                            temperature=0.3,
                        )
                    )
                except Exception:
                    # Cadangan Otomatis jika Server Padat (503/429)
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION,
                            temperature=0.3,
                        )
                    )

            reply = response.text
            with st.chat_message("assistant"):
                st.markdown(reply)
            
            # Simpan balasan AI ke memori
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"Terjadi Kesalahan: {str(e)}")



