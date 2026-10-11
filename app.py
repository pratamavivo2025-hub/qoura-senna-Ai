import datetime
import streamlit as st
from openai import OpenAI

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Quora Senna Core AGI - Swarm Engine",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .agent-card {
        background-color: #1e222d;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #2e3440;
    }
    .agent-title {
        color: #00d2ff;
        font-weight: bold;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SETUP TIME & OPENROUTER CLIENT
# ---------------------------------------------------------
# Mendapatkan tanggal hari ini secara otomatis dalam format Indonesia
now = datetime.datetime.now()
CURRENT_DATE_STR = now.strftime("%d %B %Y") # Contoh: 11 October 2026

api_key = st.secrets.get("OPENROUTER_API_KEY", None)

if not api_key:
    with st.sidebar:
        st.warning("⚠️ OPENROUTER_API_KEY tidak ditemukan di Secrets.")
        api_key = st.text_input("Masukkan OpenRouter API Key kamu:", type="password")

if not api_key:
    st.info("💡 Silakan masukkan OpenRouter API Key kamu di sidebar untuk memulai.")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

MODEL_ID = "google/gemma-4-26b-a4b-it:free"

# ---------------------------------------------------------
# 3. SIDEBAR - TAMPILAN DIGITAL AI QUORA
# ---------------------------------------------------------
with st.sidebar:
    st.image(
        "https://api.dicebear.com/7.x/bottts/svg?seed=QuoraSennaAGI&backgroundColor=000000",
        caption="Quora Senna Core AGI v2.5",
        width=150
    )
    st.title("🛡️ Quora AGI Core")
    st.markdown("**Status Engine:** `ONLINE` 🟢")
    st.markdown(f"**Waktu Sistem:** `{CURRENT_DATE_STR}`")
    st.markdown(f"**Model:** `{MODEL_ID}`")
    st.divider()
    
    st.markdown("### 👥 AI Swarm Crew:")
    
    st.markdown("""
    <div class="agent-card">
        <div class="agent-title">🔍 Agent 1: Senna-Researcher</div>
        <small>Pengumpul Data, Informasi & Konsep Utama</small>
    </div>
    <div class="agent-card">
        <div class="agent-title">🧠 Agent 2: Senna-Analyst</div>
        <small>Analis Spesialis Sesuai Domain Topik</small>
    </div>
    <div class="agent-card">
        <div class="agent-title">⚔️ Agent 3: Quora-Strategist</div>
        <small>Sintesis Eksekutif & Pengambil Keputusan Final</small>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. FUNGSI EKSEKUSI AGEN
# ---------------------------------------------------------
def run_agent_task(system_prompt: str, user_prompt: str) -> str:
    """Fungsi helper pemanggilan API dengan injection Waktu Hari Ini"""
    
    # Inject waktu saat ini ke dalam system prompt agar AI sadar waktu sekarang
    time_awareness_prompt = (
        f"PERHATIAN TANGGAL SAKRAL: Waktu sistem saat ini adalah {CURRENT_DATE_STR} (Tahun 2026). "
        f"Gunakan konteks waktu tahun 2026 dalam semua analisis dan jawabanmu.\n\n"
        f"{system_prompt}"
    )
    
    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": time_awareness_prompt},
                {"role": "user", "content": user_prompt}
            ],
            extra_headers={
                "HTTP-Referer": "https://streamlit.io",
                "X-Title": "Quora Senna Core AGI"
            }
        )
        return response.choices[0].message.content
    except Exception as primary_error:
        try:
            fallback_response = client.chat.completions.create(
                model="openrouter/free",
                messages=[
                    {"role": "system", "content": time_awareness_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return fallback_response.choices[0].message.content
        except Exception as fallback_error:
            return f"Error pada eksekusi agen: {str(primary_error)} | Fallback Error: {str(fallback_error)}"

# ---------------------------------------------------------
# 5. UI UTAMA & INTERAKSI USER
# ---------------------------------------------------------
st.title("🌐 Quora Senna Core AGI - Multi-Agent System")
st.caption(f"Kawanan Agen AI Mandiri Berbasiskan OpenRouter Engine (System Date: {CURRENT_DATE_STR})")

domain_choice = st.selectbox(
    "🎯 Pilih Domain / Topik Analisis:",
    [
        "📈 Investasi & Pasar Modal (Saham, Crypto, Value Investing)",
        "💰 Keuangan & Makroekonomi",
        "🔬 Sains & Teknologi Tinggi (AI, Semikonduktor, Fisika)",
        "💻 Pemrograman & Arsitektur Software",
        "📚 Filsafat, Behavioral Psychology & Keputusan Strategis",
        "🔮 Umum / Eksplorasi Bebas"
    ]
)

user_query = st.text_area(
    "💬 Masukkan Pertanyaan:",
    placeholder="Masukkan topik atau pertanyaan kamu di sini...",
    height=120
)

if st.button("🚀 Jalankan Kawanan AI (Start Swarm)", type="primary"):
    if not user_query.strip():
        st.warning("Silakan masukkan pertanyaan terlebih dahulu!")
    else:
        st.divider()
        st.subheader("⚡ Kawanan Agen AI Mulai Bekerja...")
        
        with st.status("Proses Kolaborasi Multi-Agent Sedang Berjalan...", expanded=True) as status:
            
            # --- AGENT 1: RESEARCHER ---
            st.write("🔍 **[Agent 1: Senna-Researcher]** Membedah konteks domain & mengumpulkan data...")
            sys_researcher = f"Kamu adalah Agent 1 (Senna-Researcher) spesialis domain {domain_choice}. Tugasmu fokus mengumpulkan fakta, struktur dasar, dan data kunci yang relevan."
            prompt_researcher = f"""
            Domain: {domain_choice}
            Waktu Saat Ini: {CURRENT_DATE_STR}
            Topik User: "{user_query}"
            
            Instruksi: Kumpulkan poin-poin riset, konsep utama, dan fakta tepercaya sesuai domain {domain_choice}.
            """
            result_research = run_agent_task(sys_researcher, prompt_researcher)
            st.success("✅ Agent 1 Selesai!")
            
            # --- AGENT 2: ANALYST ---
            st.write("🧠 **[Agent 2: Senna-Analyst]** Menganalisis temuan sesuai kepakaran domain...")
            sys_analyst = f"Kamu adalah Agent 2 (Senna-Analyst) pakar di bidang {domain_choice}. Tugasmu menganalisis logika, kerangka kerja, atau pola sesuai konteks domain tersebut."
            prompt_analyst = f"""
            Domain: {domain_choice}
            Waktu Saat Ini: {CURRENT_DATE_STR}
            Data dari Agent 1:
            ---
            {result_research}
            ---
            
            Instruksi: Lakukan analisis mendalam berdasarkan metode yang relevan dengan domain {domain_choice}. Jangan memaksakan analisis keuangan jika topiknya adalah Sains, Coding, atau Filsafat!
            """
            result_analysis = run_agent_task(sys_analyst, prompt_analyst)
            st.success("✅ Agent 2 Selesai!")
            
            # --- AGENT 3: STRATEGIST / QUORA CORE ---
            st.write("⚔️ **[Agent 3: Quora-Strategist]** Menyusun sintesis eksekutif & jawaban akhir...")
            sys_strategist = f"Kamu adalah Agent 3 (Quora-Strategist), sintesis eksekutif dari Quora AGI Swarm untuk domain {domain_choice}."
            prompt_strategist = f"""
            Domain: {domain_choice}
            Waktu Saat Ini: {CURRENT_DATE_STR}
            Hasil Analisis Agent 2:
            ---
            {result_analysis}
            ---
            
            Instruksi: Susun jawaban akhir yang utuh, solutif, terstruktur, dan siap dieksekusi oleh user sesuai konteks {domain_choice}.
            """
            result_final = run_agent_task(sys_strategist, prompt_strategist)
            st.success("✅ Agent 3 Selesai!")
            
            status.update(label="✨ Seluruh Kawanan Agen Selesai Bekerja!", state="complete", expanded=False)

        # ---------------------------------------------------------
        # TAMPILAN TAB HASIL
        # ---------------------------------------------------------
        st.subheader("📊 Laporan Hasil Kerja Multi-Agent System")
        
        tab_final, tab_analysis, tab_research = st.tabs([
            "🎯 Jawaban / Strategi Akhir (Quora-Strategist)",
            "🧠 Analisis Mendalam (Senna-Analyst)",
            "🔍 Data & Riset Mentah (Senna-Researcher)"
        ])
        
        with tab_final:
            st.markdown("### 👑 Keputusan / Jawaban Akhir")
            st.success(result_final)
            
        with tab_analysis:
            st.markdown("### 📐 Analisis Penalaran Domain")
            st.info(result_analysis)
            
        with tab_research:
            st.markdown("### 📋 Temuan Data Kunci")
            st.write(result_research)
