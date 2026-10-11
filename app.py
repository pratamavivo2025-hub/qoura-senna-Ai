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

# Custom Styling CSS untuk tampilan UI futuristik
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
# 2. SETUP OPENROUTER CLIENT
# ---------------------------------------------------------
# Mengambil API Key dari Streamlit Secrets atau Sidebar Input
api_key = st.secrets.get("OPENROUTER_API_KEY", None)

if not api_key:
    with st.sidebar:
        st.warning("⚠️ OPENROUTER_API_KEY tidak ditemukan di Secrets.")
        api_key = st.text_input("Masukkan OpenRouter API Key kamu:", type="password")

if not api_key:
    st.info("💡 Silakan masukkan OpenRouter API Key kamu di sidebar untuk memulai.")
    st.stop()

# Client OpenAI disesuaikan ke Endpoint OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# Model ID resmi OpenRouter (Menggunakan Gemma 4 26B Free)
MODEL_ID = "google/gemma-4-26b-a4b-it:free"

# ---------------------------------------------------------
# 3. SIDEBAR - TAMPILAN DIGITAL AI QUORA (AVATAR & PROFILE)
# ---------------------------------------------------------
with st.sidebar:
    st.image(
        "https://api.dicebear.com/7.x/bottts/svg?seed=QuoraSennaAGI&backgroundColor=000000",
        caption="Quora Senna Core AGI v2.5",
        width=150
    )
    st.title("🛡️ Quora AGI Core")
    st.markdown("**Status Engine:** `ONLINE` 🟢")
    st.markdown(f"**Model:** `{MODEL_ID}`")
    st.divider()
    
    st.markdown("### 👥 AI Swarm Crew:")
    
    st.markdown("""
    <div class="agent-card">
        <div class="agent-title">🔍 Agent 1: Senna-Researcher</div>
        <small>Spesialis Pengumpul Data, Fakta, & Riset Fundamental</small>
    </div>
    <div class="agent-card">
        <div class="agent-title">🧠 Agent 2: Senna-Analyst</div>
        <small>Analis Kuantitatif, Ekonomi, Sains & Pasar Modal</small>
    </div>
    <div class="agent-card">
        <div class="agent-title">⚔️ Agent 3: Quora-Strategist</div>
        <small>Pengambil Keputusan, Sintesis Final & Eksekutor</small>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. FUNGSI EKSEKUSI AGEN (SWARM ENGINE WITH FALLBACK)
# ---------------------------------------------------------
def run_agent_task(system_prompt: str, user_prompt: str) -> str:
    """Fungsi helper dengan sistem Fallback otomatis jika model utama error"""
    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            extra_headers={
                "HTTP-Referer": "https://streamlit.io",
                "X-Title": "Quora Senna Core AGI"
            }
        )
        return response.choices[0].message.content
    except Exception as primary_error:
        # Auto-fallback jika model spesifik bermasalah
        try:
            fallback_response = client.chat.completions.create(
                model="openrouter/free",
                messages=[
                    {"role": "system", "content": system_prompt},
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
st.caption("Kawanan Agen AI Mandiri Berbasiskan OpenRouter Engine")

domain_choice = st.selectbox(
    "🎯 Pilih Domain / Topik Analisis:",
    [
        "📈 Investasi & Pasar Modal (Saham, Crypto, Value Investing)",
        "💰 Keuangan & Makroekonomi",
        "🔬 Sains & Teknologi Tinggi (AI, Semi-konduktor, Fisika)",
        "💻 Pemrograman & Arsitektur Software",
        "📚 Filsafat, Behavioral Psychology & Keputusan Strategis",
        "🔮 Umum / Eksplorasi Bebas"
    ]
)

user_query = st.text_area(
    "💬 Masukkan Pertanyaan / Problem yang Ingin Diselesaikan oleh Swarm Agen:",
    placeholder="Contoh: Buatkan analisis mendalam prospek adopsi AI pada sektor teknologi semikonduktor & dampaknya terhadap strategi alokasi portofolio investasi.",
    height=120
)

if st.button("🚀 Jalankan Kawanan AI (Start Swarm)", type="primary"):
    if not user_query.strip():
        st.warning("Silakan masukkan pertanyaan atau data terlebih dahulu!")
    else:
        st.divider()
        st.subheader("⚡ Kawanan Agen AI Mulai Bekerja...")
        
        with st.status("Proses Kolaborasi Multi-Agent Sedang Berjalan...", expanded=True) as status:
            
            # --- AGENT 1: RESEARCHER ---
            st.write("🔍 **[Agent 1: Senna-Researcher]** Sedang membedah domain & mengumpulkan fakta kunci...")
            prompt_researcher = f"""
            Kamu adalah Agent 1 (Senna-Researcher) dari Quora AGI Swarm.
            Domain tugas: {domain_choice}.
            Tugasmu: Kumpulkan data mentah, konsep utama, fakta penting, dan variabel kunci terkait topik user berikut:
            "{user_query}"
            Jawab dengan ringkas, padat fakta, dan terstruktur.
            """
            result_research = run_agent_task(
                "Kamu adalah Senior Researcher AI yang sangat objektif dan berbasis fakta.",
                prompt_researcher
            )
            st.success("✅ Agent 1 Selesai!")
            
            # --- AGENT 2: ANALYST ---
            st.write("🧠 **[Agent 2: Senna-Analyst]** Menganalisis temuan data & menyusun kalkulasi/metrik...")
            prompt_analyst = f"""
            Kamu meupakan Agent 2 (Senna-Analyst) dari Quora AGI Swarm.
            Domain tugas: {domain_choice}.
            Berikut adalah data riset dari Agent 1:
            ---
            {result_research}
            ---
            Tugasmu: Lakukan analisis mendalam (fundamental, logika, matematika, psikologi pasar, atau sains) dari data riset di atas. Evaluasi risiko, peluang, dan pola dari topik tersebut.
            """
            result_analysis = run_agent_task(
                "Kamu adalah Senior Financial & Scientific Quantitative Analyst.",
                prompt_analyst
            )
            st.success("✅ Agent 2 Selesai!")
            
            # --- AGENT 3: STRATEGIST / QUORA CORE ---
            st.write("⚔️ **[Agent 3: Quora-Strategist]** Menyusun rekomendasi akhir & sintesis eksekutif...")
            prompt_strategist = f"""
            Kamu adalah Agent 3 (Quora-Strategist), pemikir utama dan sintesis eksekutif dari Quora Senna Core AGI Swarm.
            Berdasarkan hasil analisis berikut:
            ---
            {result_analysis}
            ---
            Tugasmu: Buatkan ringkasan keputusan eksekutif, rekomendasi konkret/langkah aksi, serta kesimpulan akhir yang tajam, mudah dipahami, dan actionable untuk user.
            """
            result_final = run_agent_task(
                "Kamu adalah Quora-Strategist, pembuat keputusan puncak dan arsitek strategi AGI.",
                prompt_strategist
            )
            st.success("✅ Agent 3 Selesai!")
            
            status.update(label="✨ Seluruh Kawanan Agen Selesai Bekerja!", state="complete", expanded=False)

        # ---------------------------------------------------------
        # TAMPILAN TAB UNTUK HASIL MULTI-AGENT
        # ---------------------------------------------------------
        st.subheader("📊 Laporan Hasil Kerja Multi-Agent System")
        
        tab_final, tab_analysis, tab_research = st.tabs([
            "🎯 Rekomendasi Eksekutif (Quora-Strategist)",
            "🧠 Analisis Mendalam (Senna-Analyst)",
            "🔍 Data & Riset Mentah (Senna-Researcher)"
        ])
        
        with tab_final:
            st.markdown("### 👑 Keputusan & Strategi Akhir")
            st.success(result_final)
            
        with tab_analysis:
            st.markdown("### 📐 Analisis Penalaran & Kuantitatif")
            st.info(result_analysis)
            
        with tab_research:
            st.markdown("### 📋 Temuan Data Kunci")
            st.write(result_research)
