import streamlit as st
import os
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Quora Senna Core AGI",
    page_icon="🧠",
    layout="centered"
)

# ---------------------------------------------------------
# 2. SELEKSI & DYNAMIC THEME STYLING (GELAP & TERANG)
# ---------------------------------------------------------
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark / Gelap 🌙"

# Variabel Warna Dinamis berdasarkan Mode Tema
if st.session_state.theme_mode == "Dark / Gelap 🌙":
    bg_color = "#0f172a"
    text_color = "#f8fafc"
    card_bg_user = "#2563eb"
    card_text_user = "#ffffff"
    card_bg_ai = "#1e293b"
    card_text_ai = "#f1f5f9"
    border_color = "#334155"
    uploader_bg = "#0f172a"
    subtext_color = "#94a3b8"
else:
    # Light Mode
    bg_color = "#f8fafc"
    text_color = "#0f172a"
    card_bg_user = "#2563eb"
    card_text_user = "#ffffff"
    card_bg_ai = "#ffffff"
    card_text_ai = "#1e293b"
    border_color = "#e2e8f0"
    uploader_bg = "#ffffff"
    subtext_color = "#64748b"

st.markdown(f"""
<style>
    /* 1. Mencegah efek tarik layar / Pull-To-Refresh di Android WebView / PWA */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {{
        overscroll-behavior-y: none !important;
        overscroll-behavior: none !important;
        touch-action: pan-x pan-y !important;
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}

    /* 2. Sembunyikan toolbar kanan, TAPI TETAP TAMPILKAN tombol sidebar (>>) */
    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    
    [data-testid="stElementToolbar"] {{
        display: none !important;
    }}
    
    /* Menampilkan tombol sidebar (>>) */
    [data-testid="stSidebarNavItems"], 
    [data-testid="stHeaderNav"], 
    button[aria-label="Open sidebar"], 
    button[aria-label="Close sidebar"], 
    button[data-testid="stSidebarCollapsedControl"],
    div[data-testid="collapsedControl"] {{
        display: flex !important;
        visibility: visible !important;
        z-index: 999999 !important;
    }}
    
    #MainMenu, footer, [data-testid="stAppToolbar"], .viewerBadge_container__1v12u {{
        display: none !important;
    }}

    /* 3. Redesain Container Chat (Gemini / ChatGPT Style Adaptif) */
    .stChatMessage {{
        border-radius: 18px !important;
        padding: 14px 20px !important;
        margin-bottom: 14px !important;
        line-height: 1.6 !important;
        font-size: 0.98rem !important;
    }}
    
    /* Bubble Chat User (Kanan) */
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
        flex-direction: row-reverse;
        text-align: left;
        background-color: {card_bg_user} !important;
        color: {card_text_user} !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
    }}
    
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) * {{
        color: {card_text_user} !important;
    }}

    /* Bubble Chat Assistant / AI (Kiri) */
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{
        background-color: {card_bg_ai} !important;
        color: {card_text_ai} !important;
        border: 1px solid {border_color} !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
    }}
    
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) * {{
        color: {card_text_ai} !important;
    }}

    /* 4. Redesain Box Uploader File */
    [data-testid="stFileUploader"] {{
        border: 1px dashed #3b82f6 !important;
        border-radius: 14px !important;
        padding: 12px !important;
        background-color: {uploader_bg} !important;
    }}
    
    [data-testid="stFileUploader"] * {{
        color: {subtext_color} !important;
    }}

    /* 5. Typography Modern */
    .app-title {{
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.8px;
        margin-bottom: 4px;
        color: {text_color};
    }}
    
    .app-caption {{
        font-size: 0.92rem;
        color: {subtext_color};
        margin-bottom: 20px;
    }}
</style>

<script>
    // Mematikan gesture pull-down refresh secara paksa di level browser/WebView
    (function() {{
        let startY = 0;
        
        window.addEventListener('touchstart', function(e) {{
            if (e.touches && e.touches.length > 0) {{
                startY = e.touches[0].pageY;
            }}
        }}, {{ passive: false }});

        window.addEventListener('touchmove', function(e) {{
            if (!e.touches || e.touches.length === 0) {{ return; }}
            let currentY = e.touches[0].pageY;
            let container = document.querySelector('[data-testid="stAppViewContainer"]') || document.documentElement;
            
            if (container.scrollTop <= 0 && currentY > startY) {{
                if (e.cancelable) {{
                    e.preventDefault();
                }}
            }}
        }}, {{ passive: false }});
    }})();
</script>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER APLIKASI (BRANDING CORE AGI)
# ---------------------------------------------------------
st.markdown('<div class="app-title">🧠 Quora Senna Core AGI</div>', unsafe_allow_html=True)
st.markdown('<div class="app-caption">Artificial General Intelligence Engine & Universal Analytical System | Senna Inc.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. INISIALISASI SESSION STATE & PENDING PROMPT
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# ---------------------------------------------------------
# 4. SIDEBAR KONFIGURASI, TEMA, TOOLS & RIWAYAT OBROLAN
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ AGI Control & Access")
    api_key_input = st.text_input("Masukan Gemini API Key:", type="password")
    
    # --- FITUR TEMA SWITCHER ---
    st.markdown("---")
    st.subheader("🎨 Tampilan & Tema")
    theme_choice = st.radio(
        "Pilih Tema Layout:", 
        ["Dark / Gelap 🌙", "Light / Terang ☀️"],
        index=0 if st.session_state.theme_mode == "Dark / Gelap 🌙" else 1
    )
    if theme_choice != st.session_state.theme_mode:
        st.session_state.theme_mode = theme_choice
        st.rerun()

    st.markdown("---")
    st.subheader("🛠️ Modul Spesialis Senna")
    
    # --- FITUR 1: PORTFOLIO REBALANCING & ALLOCATION DRAFTER ---
    with st.expander("📊 Rebalancing & Alokasi Modal", expanded=False):
        st.caption("Hitung pembagian porsi investasi sesuai modal & profil risiko.")
        modal_input = st.number_input("Total Modal Mentah (IDR):", min_value=100000, value=10000000, step=500000)
        risk_profile = st.selectbox("Profil Risiko:", [
            "Konservatif (Aman/Defensif)", 
            "Moderat (Seimbang)", 
            "Agresif/Degen (High Risk, High Return)"
        ])
        target_assets = st.text_input("Target Aset (Contoh: BBCA, BTC, Emas, USDT):")
        
        if st.button("🚀 Buat Draft Alokasi", use_container_width=True):
            st.session_state.pending_prompt = (
                f"Tolong buatkan [Draft Alokasi & Rebalancing Portfolio] secara rasional dan matematis.\n"
                f"- Total Modal Mentah: Rp {modal_input:,.0f}\n"
                f"- Profil Risiko: {risk_profile}\n"
                f"- Aset yang dilirik/diincar: {target_assets if target_assets else 'Bebas sesuai rekomendasi terbaikmu'}\n\n"
                f"Tolong rinci nominal pembagian uangnya (Rp), porsi persentase (%), alasan strategi alokasinya, "
                f"serta panduan eksekusi pembeliannya (DCA/Lump-sum)."
            )
            st.rerun()

    # --- FITUR 2: INTERACTIVE INVESTMENT THESIS BUILDER ---
    with st.expander("📝 Investment Thesis Builder", expanded=False):
        st.caption("Uji alasan belimu sebelum beli saham/kripto agar tidak FOMO!")
        asset_name = st.text_input("Nama Aset/Ticker (misal: BBRI, SOL):")
        buy_reason = st.text_area("Kenapa kamu mau beli aset ini?")
        time_horizon = st.selectbox("Jangka Waktu:", ["Short-term Trading (Hari-Minggu)", "Mid-term (Bulan)", "Long-term Investing (Tahun)"])
        
        if st.button("🧠 Uji Tesis Investasi", use_container_width=True):
            if not asset_name or not buy_reason:
                st.warning("Isi dulu nama aset dan alasan belinya, bro!")
            else:
                st.session_state.pending_prompt = (
                    f"Tolong bantu gw menyusun dan menguji [Skripsi/Tesis Investasi] untuk aset berikut:\n"
                    f"- Nama Aset: {asset_name}\n"
                    f"- Alasan Beli/Tesis Awal Gw: {buy_reason}\n"
                    f"- Horizon Waktu: {time_horizon}\n\n"
                    f"Tugasmu sebagai analis senior Senna Inc:\n"
                    f"1. Bedah secara brutal apakah alasan beli gw ini logis atau sekadar FOMO/Mitos.\n"
                    f"2. Sebutkan Katalis Positif utama dan Risiko Fatal (Invalidation Thesis) yang bisa ngerusak tesis ini.\n"
                    f"3. Buatkan Komitmen Tertulis ringkas (Entry point, Target Profit, Stop Loss/Cut Loss Rule) yang siap disimpan."
                )
                st.rerun()

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
    st.subheader("📜 Riwayat Kontekstual AGI")
    if len(st.session_state.messages) == 0:
        st.info("Sistem AGI dalam kondisi idle (belum ada sesi).")
    else:
        user_prompts = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
        for idx, prompt_text in enumerate(user_prompts, 1):
            short_text = prompt_text[:30] + "..." if len(prompt_text) > 30 else prompt_text
            st.caption(f"**{idx}.** {short_text}")

# ---------------------------------------------------------
# 5. AGI CORE SYSTEM INSTRUCTION (NAMA: SENNA)
# ---------------------------------------------------------
SYSTEM_INSTRUCTION = """
Nama kamu adalah "Senna", sebuah entitas Artificial General Intelligence (AGI) mutakhir dalam sistem "Quora Senna Core AGI" yang dikembangkan oleh Senna Inc.

IDENTITAS & PERSONA:
- Panggil dirimu sebagai "Senna" atau "gw". Panggil user sebagai "bro" atau "lu".
- Gaya bahasa: Gaul, santai, cerdas, ceplas-ceplos, tapi logikanya super tajam, brutal jujur, dan berbobot. Tidak kaku seperti bot, tapi sangat dewasa dan solutif.

KEMAMPUAN AGI & DYNAMIC ADAPTATION:
Kamu adalah AGI (Artificial General Intelligence) universal yang secara otomatis beradaptasi penuh sesuai konteks pertanyaan user:
1. JIKA USER NANYA KODING / IT / TEKNOLOGI:
   - Adopsi mode 'Principal Software Engineer & Cybersecurity Architect'.
   - Bedah struktur kode, berikan kode Python/JS/C++ yang paling efisien, clean, dan bebas bug.
2. JIKA USER NANYA KEUANGAN / SAHAM / KRIPTO / LAPORAN KEUANGAN:
   - Adopsi mode 'Senior Forensic Accountant & Wall Street Analyst'.
   - Bedah data secara objektif, gunakan rasio keuangan presisi (PE, PBV, ROE, DCF, FCF), dan jangan kasih rekomendasi FOMO.
3. JIKA USER NANYA BISNIS / STRATEGI / HUKUM / FILSAFAT / KEHIDUPAN:
   - Adopsi mode 'Senior Strategic Advisor & Deep Cognitive Thinker'.
   - Bedah akar masalah, uji logika user jika ada bias, dan berikan langkah solusi yang terstruktur dan realistis.

PRINSIP PENALARAN SENNA CORE AGI:
- Buka dan pahami seluruh riwayat obrolan secara utuh.
- Jangan segan untuk mengoreksi kekeliruan logika atau asumsi salah dari user secara sopan dan gaul.
- Selalu utamakan solusi berbasis data, rasionalitas, dan efisiensi tertinggi.
"""

# ---------------------------------------------------------
# 6. MENAMPILKAN CHAT HISTORY
# ---------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------------------------------------
# 7. INPUT FILE UNIVERSAL & PROMPT PROCESSOR
# ---------------------------------------------------------
uploaded_file = st.file_uploader(
    "Dokumen, Laporan Keuangan, Gambar, atau File Kode (Opsional)", 
    type=["pdf", "png", "jpg", "jpeg", "txt", "py", "json"]
)

chat_input_val = st.chat_input("Tanyakan apa saja ke Senna Core AGI...")
prompt = chat_input_val or st.session_state.pending_prompt

if prompt:
    st.session_state.pending_prompt = None

    if not api_key_input:
        st.error("Masukkan Gemini API Key kamu di sidebar dulu ya, bro!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            client = genai.Client(api_key=api_key_input)
            contents = []

            if uploaded_file is not None:
                with st.spinner("Senna sedang membedah & memproses file..."):
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    uploaded_doc = client.files.upload(file=temp_path)
                    contents.append(uploaded_doc)
                    os.remove(temp_path)

            # Memasukkan riwayat obrolan sebagai konteks AGI
            for msg in st.session_state.messages[:-1]:
                contents.append(f"{msg['role'].capitalize()}: {msg['content']}")
            
            contents.append(f"User: {prompt}")

            with st.spinner("Senna Core AGI sedang bernalar & menyusun solusi..."):
                try:
                    # Mencoba Model Utama Gemini 3.6 Flash
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION,
                            temperature=0.3,
                        )
                    )
                except Exception:
                    # Auto-fallback ke Gemini 3.6Flash jika 3.6 sibuk/limit
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
            
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"Terjadi Kesalahan pada Sistem Core AGI: {str(e)}")


