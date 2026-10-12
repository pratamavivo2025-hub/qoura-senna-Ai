
import streamlit as st
import requests

# =========================================================
# QUORA AI — MULTI-AGENT RESEARCH WORKSPACE
# =========================================================

st.set_page_config(
    page_title="Quora AI | Research Workspace",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# =========================================================
# TOPICS & AGENT ROLES
# =========================================================

TOPICS = {
    "📈 Investasi & Pasar Modal": [
        (
            "Senna Researcher",
            "Peneliti fundamental. Identifikasi fakta, laporan "
            "perusahaan, valuasi, industri, dan risiko."
        ),
        (
            "Senna Skeptic",
            "Analis kritis independen. Uji tesis, cari bukti yang "
            "bertentangan, bias, risiko, dan asumsi yang lemah."
        ),
        (
            "Senna Strategist",
            "Susun sintesis strategis dari bukti, risiko, valuasi, "
            "dan skenario. Bedakan analisis dari rekomendasi."
        ),
    ],
    "🔬 Sains": [
        (
            "Senna Scientist",
            "Analisis teori, penelitian, metodologi, dan temuan "
            "ilmiah. Bedakan konsensus dengan hipotesis."
        ),
        (
            "Senna Examiner",
            "Periksa kualitas bukti, kemungkinan bias, keterbatasan "
            "sampel, dan penjelasan alternatif."
        ),
        (
            "Senna Synthesizer",
            "Rangkum bukti ilmiah, tingkat kepastian, dan pertanyaan "
            "yang masih belum terjawab."
        ),
    ],
    "🌍 Ekonomi": [
        (
            "Senna Economist",
            "Analisis makroekonomi, mikroekonomi, inflasi, suku "
            "bunga, kebijakan, dan indikator ekonomi."
        ),
        (
            "Senna Policy Critic",
            "Evaluasi kebijakan, trade-off, distribusi dampak, "
            "serta bukti yang mendukung atau menentangnya."
        ),
        (
            "Senna Economic Strategist",
            "Sintesis skenario ekonomi dan implikasinya dengan "
            "menyatakan asumsi serta ketidakpastian."
        ),
    ],
    "💻 Pemrograman": [
        (
            "Senna Developer",
            "Rancang solusi pemrograman, struktur kode, dan "
            "implementasi yang jelas."
        ),
        (
            "Senna Code Auditor",
            "Cari bug, celah keamanan, edge cases, kesalahan logika, "
            "dan klaim teknis yang belum diuji."
        ),
        (
            "Senna Architect",
            "Sintesis solusi, arsitektur, maintainability, "
            "performa, dan kompromi desain."
        ),
    ],
    "🧠 Filsafat & Psikologi Perilaku": [
        (
            "Senna Philosopher",
            "Periksa konsep, definisi, premis, argumen, dan "
            "implikasi filosofis."
        ),
        (
            "Senna Behavioral Analyst",
            "Analisis bias kognitif, perilaku manusia, dan teori "
            "psikologi dengan batasan bukti ilmiah."
        ),
        (
            "Senna Critical Thinker",
            "Uji validitas argumen, bedakan korelasi dan sebab-akibat, "
            "serta rumuskan kesimpulan yang proporsional."
        ),
    ],
    "💬 Pengetahuan Umum": [
        (
            "Senna Researcher",
            "Pahami pertanyaan dan kumpulkan pengetahuan relevan "
            "yang dapat dipertanggungjawabkan."
        ),
        (
            "Senna Fact Examiner",
            "Periksa konsistensi, fakta, sumber, asumsi, dan "
            "kemungkinan informasi yang keliru."
        ),
        (
            "Senna Synthesizer",
            "Susun jawaban akhir yang jelas, seimbang, dan "
            "mengakui keterbatasan informasi."
        ),
    ],
}

# =========================================================
# GLOBAL EVIDENCE & REASONING STANDARD
# =========================================================

COMMON_RULES = """
STANDAR WAJIB QUORA AI

1. INDEPENDENSI
Jangan mengubah kesimpulan hanya demi menyenangkan pengguna.
Evaluasi klaim berdasarkan bukti dan logika.

2. OBJEKTIVITAS
Pertimbangkan bukti yang mendukung maupun menentang.
Jangan hanya mencari informasi yang membenarkan satu posisi.

3. KERENDAHAN HATI INTELEKTUAL
Jika informasi tidak cukup, katakan secara eksplisit.
Jangan mengubah dugaan menjadi fakta.

4. KOREKSI DIRI
Jika ditemukan kesalahan atau kontradiksi, jelaskan dan
koreksi berdasarkan bukti yang lebih kuat.

5. KONSISTENSI LOGIKA
Gunakan standar pembuktian yang sama, terlepas dari
kesimpulan yang disukai pengguna.

6. TRANSPARANSI
Bedakan dengan jelas:
- Fakta yang diketahui
- Asumsi
- Estimasi atau proyeksi
- Interpretasi atau opini analitis
- Informasi yang belum diketahui

7. EVIDENCE & SOURCE VERIFICATION
Untuk setiap klaim faktual penting, sertakan bila tersedia:
- Klaim yang dibuat
- Nama sumber atau dokumen
- Tanggal publikasi
- Tanggal/periode data yang dibahas
- URL sumber langsung
- Status: terverifikasi, belum diverifikasi, atau bertentangan

Prioritaskan sumber primer yang relevan, seperti laporan
resmi, dokumen regulator, publikasi ilmiah, data pemerintah,
atau dokumentasi teknis resmi.

JANGAN PERNAH mengarang URL, nama laporan, kutipan,
angka, tanggal publikasi, atau mengaku telah membuka sumber
yang sebenarnya tidak diakses.

Jika hanya mengandalkan pengetahuan internal model, katakan
bahwa sumber belum diperiksa secara independen.
Jika sumber tidak diketahui, nyatakan demikian.
Jangan mengklaim telah melakukan pencarian web.

8. FORMAT JAWABAN
Gunakan struktur yang sesuai dengan pertanyaan:
- Peran dan tujuan analisis
- Temuan utama
- Bukti dan sumber
- Argumen yang menentang
- Asumsi dan ketidakpastian
- Kesimpulan sementara

Jangan memaksakan format yang tidak relevan untuk pertanyaan
sederhana. Jawab dalam bahasa Indonesia yang jelas.

Ingat: permintaan untuk mencantumkan sumber bukan bukti
bahwa sumber itu benar-benar sudah diverifikasi.
"""

# =========================================================
# OPENROUTER API
# =========================================================

def ask_agent(agent_name, agent_role, question, topic):
    api_key = st.secrets.get("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY belum ditemukan di Streamlit Secrets."
        )

    system_prompt = f"""
Kamu adalah {agent_name} di Quora AI.

TOPIK: {topic}
PERAN KHUSUS: {agent_role}

{COMMON_RULES}

Lakukan tugas sesuai peranmu. Berikan analisis mandiri.
Jangan berpura-pura mengetahui jawaban agen lain.
Jangan menyatakan suatu fakta sudah terverifikasi secara
eksternal jika kamu tidak memiliki akses untuk memeriksanya.
"""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        "temperature": 0.4,
        "max_tokens": 1000,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=120,
    )

    if not response.ok:
        raise RuntimeError(
            f"HTTP {response.status_code}: {response.text[:400]}"
        )

    data = response.json()
    choices = data.get("choices", [])

    if not choices:
        raise RuntimeError("API tidak mengembalikan pilihan jawaban.")

    content = choices[0].get("message", {}).get("content")

    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Model mengembalikan jawaban kosong.")

    return content


# =========================================================
# SESSION STATE
# =========================================================

if "histories" not in st.session_state:
    st.session_state.histories = {
        topic: [] for topic in TOPICS
    }

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# =========================================================
# CUSTOM UI
# =========================================================

st.markdown("""
<style>
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .hero {
        padding: 1.5rem;
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 18px;
        margin-bottom: 1.2rem;
        background: linear-gradient(
            120deg,
            rgba(65, 85, 140, 0.12),
            rgba(20, 150, 130, 0.08)
        );
    }

    .hero-label {
        font-size: 0.8rem;
        letter-spacing: 0.12rem;
        font-weight: 700;
        opacity: 0.7;
    }

    .hero h1 {
        margin: 0.4rem 0;
        font-size: 2.2rem;
    }

    .muted {
        opacity: 0.7;
        font-size: 0.9rem;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 14px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR MENU
# =========================================================

with st.sidebar:
    st.markdown("## 🧠 Quora AI")
    st.caption("Multi-Agent Research Workspace")
    st.divider()

    page = st.radio(
        "NAVIGASI",
        ["💬 Research Chat", "📚 Evidence Standard", "⚙️ Model & System"],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("### TOPIC HUBS")

    selected_topic = st.radio(
        "Pilih topik",
        list(TOPICS.keys()),
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("### ACTIVE MODEL")
    st.code("Nemotron 3 Ultra", language=None)
    st.caption("OpenRouter · Free model ID")

    st.caption("18 peran agen · 6 topik")

# =========================================================
# PAGE: EVIDENCE STANDARD
# =========================================================

if page == "📚 Evidence Standard":
    st.title("📚 Evidence & Source Standard")
    st.write(
        "Quora AI membedakan klaim, bukti, interpretasi, "
        "dan hal yang belum dapat dipastikan."
    )

    standards = [
        ("Independensi", "Kesimpulan tidak diubah hanya demi menyenangkan pengguna."),
        ("Objektivitas", "Pertimbangkan bukti yang mendukung dan menentang."),
        ("Kerendahan hati intelektual", "Akui ketika data tidak cukup."),
        ("Koreksi diri", "Perbaiki kesalahan saat ada bukti yang lebih baik."),
        ("Konsistensi logika", "Terapkan standar pembuktian yang konsisten."),
        ("Transparansi", "Pisahkan fakta, asumsi, estimasi, dan opini."),
        ("Verifikasi sumber", "Jangan mengklaim sumber telah diperiksa jika belum."),
    ]

    for title, description in standards:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(description)

    st.info(
        "Status saat ini: agen diminta mencantumkan sumber, "
        "tetapi aplikasi belum menjalankan pencarian web "
        "atau pemeriksaan tautan secara otomatis."
    )

# =========================================================
# PAGE: MODEL & SYSTEM
# =========================================================

elif page == "⚙️ Model & System":
    st.title("⚙️ Model & System")
    st.write("Konfigurasi yang sedang digunakan aplikasi.")

    with st.container(border=True):
        st.markdown("**Model**")
        st.code(MODEL, language=None)
        st.markdown("**Provider gateway**")
        st.code("OpenRouter Chat Completions", language=None)
        st.markdown("**Request per pertanyaan**")
        st.write("3 pemanggilan model, satu untuk setiap agen.")

    st.warning(
        "Model gratis bisa mengalami rate limit atau gangguan. "
        "Ketersediaan aktual bergantung pada OpenRouter dan penyedia model."
    )

# =========================================================
# PAGE: RESEARCH CHAT
# =========================================================

else:
    st.markdown("""
    <div class="hero">
        <div class="hero-label">QUORA AI / RESEARCH CORE</div>
        <h1>Evidence over assumptions.</h1>
        <div>Independent analysis. Critical review. Transparent conclusions.</div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader(selected_topic)
    st.caption(
        "Tiga agen dengan perspektif berbeda. "
        "Satu pertanyaan akan memanggil tiga agen."
    )

    with st.expander("Lihat agen aktif"):
        for name, role in TOPICS[selected_topic]:
            st.markdown(f"**{name}**")
            st.write(role)

    # Tampilkan riwayat topik aktif
    history = st.session_state.histories[selected_topic]

    for item in history:
        with st.chat_message(item["role"]):
            if item["role"] == "user":
                st.write(item["content"])
            else:
                results = item["results"]

                tabs = st.tabs([
                    agent[0] for agent in TOPICS[selected_topic]
                ])

                for tab, agent in zip(tabs, TOPICS[selected_topic]):
                    with tab:
                        result = results.get(agent[0], "")
                        if result.startswith("ERROR:"):
                            st.error(result)
                        else:
                            st.markdown(result)

    question = st.chat_input(
        f"Tanya sesuatu tentang {selected_topic}..."
    )

    if question:
        history.append({
            "role": "user",
            "content": question,
        })

        results = {}

        with st.spinner("Tiga agen sedang melakukan analisis..."):
            progress = st.progress(0)

            for index, (agent_name, agent_role) in enumerate(
                TOPICS[selected_topic]
            ):
                try:
                    answer = ask_agent(
                        agent_name,
                        agent_role,
                        question,
                        selected_topic,
                    )
                    results[agent_name] = answer

                except Exception as error:
                    results[agent_name] = (
                        f"ERROR: {type(error).__name__}: {error}"
                    )

                progress.progress((index + 1) / 3)

            progress.empty()

        history.append({
            "role": "assistant",
            "results": results,
        })

        st.rerun()

    st.divider()
    st.caption(
        "Quora AI · AI-generated analysis · "
        "Sumber eksternal belum diverifikasi otomatis."
    )
