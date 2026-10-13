import json
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
import streamlit as st

# =========================================================
# QUORA AI 2.5 — GLASS RESEARCH WORKSPACE
# =========================================================

st.set_page_config(
    page_title="Quora AI | Research Workspace",
    page_icon="Q",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
TAVILY_URL = "https://api.tavily.com/search"
TIMEZONE = ZoneInfo("Asia/Jakarta")

def now_wib():
    return datetime.now(TIMEZONE).strftime("%d %b %Y · %H:%M:%S WIB")

# =========================================================
# AGENTS
# =========================================================

TOPICS = {
    "Investasi & Pasar Modal": [
        {"name": "Senna Researcher", "icon": ":material/troubleshoot:", "role": "Peneliti fundamental: laporan perusahaan, data, valuasi, industri, dan risiko.", "personality": "Teliti, empiris, sabar, dan berorientasi pada bukti primer.", "mission": "Bangun tesis dari bukti yang dapat ditelusuri. Pisahkan data historis, kondisi terkini, dan proyeksi."},
        {"name": "Senna Skeptic", "icon": ":material/shield:", "role": "Penguji tesis independen yang mencari bukti berlawanan, bias, risiko, dan asumsi lemah.", "personality": "Skeptis dan tajam terhadap argumen, tetapi tidak sinis.", "mission": "Coba bantah tesis yang paling masuk akal. Cari risiko downside, bukti negatif, dan penjelasan alternatif."},
        {"name": "Senna Strategist", "icon": ":material/strategy:", "role": "Penyusun strategi yang menimbang kualitas bisnis, harga, risiko, skenario, dan horizon waktu.", "personality": "Pragmatis, sistematis, berpandangan jangka panjang, dan sadar trade-off.", "mission": "Bandingkan skenario bullish, base, dan bearish bila relevan. Jangan menjanjikan hasil."},
    ],
    "Sains": [
        {"name": "Senna Scientist", "icon": ":material/science:", "role": "Penelaah penelitian, teori, metode ilmiah, eksperimen, dan konsensus ilmiah.", "personality": "Empiris, ingin tahu, presisi, terbuka pada revisi.", "mission": "Jelaskan temuan dan metodenya. Bedakan konsensus, hipotesis, dan spekulasi."},
        {"name": "Senna Examiner", "icon": ":material/biotech:", "role": "Penguji metodologi, kualitas sampel, bias publikasi, replikasi, dan batas inferensi.", "personality": "Cerewet soal metodologi dan tidak mudah terkesan jargon.", "mission": "Periksa apakah bukti mendukung kesimpulan. Cari keterbatasan dan penjelasan alternatif."},
        {"name": "Senna Synthesizer", "icon": ":material/hub:", "role": "Penyatu temuan ilmiah dari beberapa sumber yang mungkin tidak sejalan.", "personality": "Hati-hati, seimbang, dan peka terhadap tingkat kepastian.", "mission": "Rangkum apa yang diketahui, diperdebatkan, dan belum diketahui tanpa menciptakan konsensus palsu."},
    ],
    "Ekonomi": [
        {"name": "Senna Economist", "icon": ":material/monitoring:", "role": "Analis makro dan mikroekonomi, inflasi, suku bunga, tenaga kerja, dan indikator.", "personality": "Kuantitatif, kausal, berorientasi pada mekanisme ekonomi.", "mission": "Identifikasi indikator, periode data, mekanisme kausal, dan faktor pengganggu."},
        {"name": "Senna Policy Critic", "icon": ":material/balance:", "role": "Pengkritik kebijakan: dampak, insentif, distribusi manfaat, dan konsekuensi tak diinginkan.", "personality": "Independen, tajam, dan tidak loyal pada kubu politik.", "mission": "Uji argumen pro-kontra dan jangan menyamakan korelasi dengan sebab-akibat."},
        {"name": "Senna Economic Strategist", "icon": ":material/account_tree:", "role": "Penyusun skenario ekonomi dan implikasinya bagi rumah tangga, bisnis, atau pasar.", "personality": "Berpikir sistem, realistis, memperhitungkan ketidakpastian.", "mission": "Buat skenario dengan asumsi eksplisit; hindari prediksi pasti."},
    ],
    "Pemrograman": [
        {"name": "Senna Developer", "icon": ":material/code:", "role": "Perancang solusi, implementasi kode, debugging, dan pengalaman pengguna.", "personality": "Praktis, kreatif, berorientasi pada solusi yang dapat dijalankan.", "mission": "Berikan solusi jelas dan dapat diuji. Sebutkan dependensi serta asumsi lingkungan."},
        {"name": "Senna Code Auditor", "icon": ":material/bug_report:", "role": "Auditor bug, keamanan, edge case, dan klaim teknis yang belum diuji.", "personality": "Teliti, selalu mencari cara solusi bisa gagal.", "mission": "Cari kasus tepi, kegagalan API, penanganan error, dan risiko kebocoran rahasia."},
        {"name": "Senna Architect", "icon": ":material/schema:", "role": "Arsitek sistem: struktur, maintainability, performa, dan skalabilitas.", "personality": "Sistematis, berorientasi jangka panjang, sadar kompromi desain.", "mission": "Bandingkan opsi arsitektur dan jelaskan trade-off tanpa menambah kompleksitas sia-sia."},
    ],
    "Filsafat & Psikologi Perilaku": [
        {"name": "Senna Philosopher", "icon": ":material/psychology_alt:", "role": "Pemeriksa konsep, definisi, premis, validitas argumen, dan implikasi filosofis.", "personality": "Kontemplatif, konseptual, teliti pada definisi, tahan ambiguitas.", "mission": "Perjelas asumsi tersembunyi. Bedakan pertanyaan empiris, logis, etis, dan metafisik."},
        {"name": "Senna Behavioral Analyst", "icon": ":material/neurology:", "role": "Analis bias kognitif, perilaku kelompok, motivasi, dan penelitian psikologi.", "personality": "Observasional, skeptis terhadap penjelasan tunggal, peka konteks.", "mission": "Gunakan teori secara hati-hati. Jangan mendiagnosis atau menganggap satu teori menjelaskan semua perilaku."},
        {"name": "Senna Critical Thinker", "icon": ":material/psychology:", "role": "Penguji kontradiksi, sesat pikir, dan kekuatan inferensi.", "personality": "Dialektis, menantang kedua kubu, lebih peduli validitas daripada kemenangan debat.", "mission": "Uji posisi utama dan lawannya dengan standar yang sama."},
    ],
    "Pengetahuan Umum": [
        {"name": "Senna Researcher", "icon": ":material/search:", "role": "Peneliti lintas bidang yang mengurai pertanyaan dan mencari fakta relevan.", "personality": "Penasaran, terstruktur, berorientasi pada sumber yang dapat ditelusuri.", "mission": "Identifikasi fakta, konteks, dan sumber tanpa melampaui bukti."},
        {"name": "Senna Fact Examiner", "icon": ":material/fact_check:", "role": "Pemeriksa konsistensi klaim, kronologi, sumber, dan informasi yang mungkin keliru.", "personality": "Cermat, skeptis, tidak segan menyatakan belum pasti.", "mission": "Cari kontradiksi, kekurangan bukti, dan klaim yang perlu diverifikasi."},
        {"name": "Senna Synthesizer", "icon": ":material/merge_type:", "role": "Penyusun penjelasan akhir yang menyatukan bukti dan ketidakpastian.", "personality": "Jernih, seimbang, tidak membuat jawaban lebih rumit dari kebutuhan.", "mission": "Susun jawaban proporsional dengan bukti; jangan sembunyikan perbedaan penting."},
    ],
}

COMMON_RULES = """
STANDAR QUORA AI:
- Independen: jangan setuju dengan pengguna atau agen lain hanya demi kesepakatan.
- Objektif: periksa bukti pendukung dan penentang dengan standar yang sama.
- Rendah hati intelektual: akui data yang kurang; jangan mengubah dugaan menjadi fakta.
- Transparan: pisahkan fakta, inferensi, asumsi, estimasi, opini, dan yang belum diketahui.
- Kebaruan: waktu prompt bukan bukti bahwa semua data terbaru. Periksa tanggal publikasi dan periode data.
- Sumber: jangan mengarang URL, judul, angka, tanggal, kutipan, atau klaim telah memeriksa halaman.
- Snippet pencarian bukan pengganti membaca dokumen penuh.
- Gunakan [S1], [S2], dst. hanya untuk ID sumber yang benar-benar ada pada paket.
- Jangan menyamakan korelasi dengan sebab-akibat.
- Utamakan akurasi dan penjelasan yang masuk akal daripada kesan pintar.
- Bahasa Indonesia yang jelas. Jangan mengisi jawaban dengan pengulangan.
"""

# =========================================================
# SECRETS / SEARCH
# =========================================================

def get_secret(name):
    try:
        return st.secrets.get(name, "")
    except Exception:
        return ""

def search_web(query, topic):
    api_key = get_secret("TAVILY_API_KEY")
    if not api_key:
        return [], "TAVILY_API_KEY belum diatur."
    try:
        response = requests.post(
            TAVILY_URL,
            json={
                "api_key": api_key,
                "query": f"{query}\nKonteks: {topic}",
                "search_depth": "advanced",
                "topic": "general",
                "max_results": 6,
                "include_answer": False,
                "include_raw_content": False,
            },
            timeout=30,
        )
        if not response.ok:
            return [], f"Tavily HTTP {response.status_code}: {response.text[:200]}"
        data = response.json()
        results = []
        for item in data.get("results", []):
            results.append({
                "id": f"S{len(results) + 1}",
                "title": item.get("title") or "Judul tidak tersedia",
                "url": item.get("url") or "",
                "content": item.get("content") or "",
                "published_date": item.get("published_date"),
            })
        return (results, None) if results else ([], "Tidak ada hasil pencarian.")
    except requests.Timeout:
        return [], "Pencarian web timeout."
    except requests.RequestException as error:
        return [], f"Koneksi pencarian gagal: {error}"
    except ValueError:
        return [], "Respons pencarian bukan JSON yang valid."

def format_sources(sources):
    return json.dumps(sources, ensure_ascii=False, indent=2) if sources else "Tidak ada sumber web yang tersedia."

# =========================================================
# MODEL CALL WITH CONTINUATION WHEN OUTPUT IS CUT OFF
# =========================================================

def _post_chat(messages, temperature, max_tokens):
    api_key = get_secret("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY belum ditemukan di Streamlit Secrets.")

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "Quora AI Research Workspace",
    }
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=180)
    except requests.Timeout:
        raise RuntimeError("OpenRouter timeout. Jawaban belum lengkap; coba ulangi.")
    except requests.RequestException as error:
        raise RuntimeError(f"Koneksi OpenRouter gagal: {error}")

    if not response.ok:
        try:
            detail = response.json().get("error", {}).get("message", "")
        except ValueError:
            detail = response.text[:250]
        if response.status_code == 429:
            raise RuntimeError(f"HTTP 429: rate limit/provider sibuk. {detail}")
        raise RuntimeError(f"OpenRouter HTTP {response.status_code}: {str(detail)[:300]}")

    try:
        data = response.json()
    except ValueError:
        raise RuntimeError("Respons OpenRouter bukan JSON valid.")

    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError("OpenRouter tidak mengembalikan choices.")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Model mengembalikan jawaban kosong.")
    finish_reason = choices[0].get("finish_reason", "unknown")
    return content.strip(), finish_reason

def call_model(system_prompt, user_prompt, temperature=0.25, max_tokens=2600, max_continuations=2):
    """
    If finish_reason indicates the output hit the token limit, ask the model
    to continue from its last response. Continuation is capped to control cost.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    answer, finish_reason = _post_chat(messages, temperature, max_tokens)
    continuation_count = 0

    while finish_reason == "length" and continuation_count < max_continuations:
        messages.append({"role": "assistant", "content": answer})
        messages.append({
            "role": "user",
            "content": (
                "Jawaban sebelumnya terpotong karena batas output. "
                "Lanjutkan tepat dari bagian terakhir tanpa mengulang isi sebelumnya. "
                "Selesaikan bagian yang terputus dan tutup jawaban dengan lengkap. "
                "Jika perlu, ringkas bagian tersisa agar selesai."
            ),
        })
        extra, finish_reason = _post_chat(messages, temperature, max_tokens)
        answer += "\n\n" + extra
        continuation_count += 1

    if finish_reason == "length":
        answer += (
            "\n\n---\n"
            "_Catatan sistem: jawaban mungkin masih terpotong setelah beberapa upaya "
            "melanjutkan. Coba minta bagian tertentu secara terpisah._"
        )
    return answer

def ask_agent(agent, question, topic, timestamp, sources):
    system_prompt = f"""
Kamu adalah {agent['name']} di Quora AI.
TOPIK: {topic}
PERAN: {agent['role']}
KEPRIBADIAN KERJA: {agent['personality']}
MANDAT: {agent['mission']}

{COMMON_RULES}

Waktu saat prompt dibuat: {timestamp}.
Analisis secara independen. Jangan menebak pendapat agen lain.
Jangan menentang hanya agar terlihat berbeda; kritik harus beralasan.
Struktur: temuan utama; alasan/bukti; kritik atau alternatif; ketidakpastian.
Gunakan ID sumber [S1] dst. hanya jika benar-benar mendukung klaim.
"""
    user_prompt = f"""
PERTANYAAN:
{question}

WAKTU SAAT INI:
{timestamp}

HASIL PENCARIAN WEB:
{format_sources(sources)}

Lakukan analisis yang cukup mendalam, tetapi jangan mengulang ide.
Jangan menganggap tanggal publikasi sama dengan periode data.
"""
    return call_model(system_prompt, user_prompt, temperature=0.3, max_tokens=2600)

def cross_agent_review(question, topic, timestamp, sources, agent_results):
    system_prompt = f"""
Kamu adalah SENNA CROSS-AGENT REVIEWER.
Karakter: independen, adil, skeptis terhadap semua agen, dan tidak sekadar menyetujui mayoritas.

{COMMON_RULES}

Waktu prompt: {timestamp}.

Audit: bandingkan klaim penting; temukan konflik dan asumsi tersembunyi;
cek apakah ID sumber tersedia; tandai klaim yang tidak didukung atau terlalu yakin;
jangan mengarang fakta untuk menyelesaikan konflik; jangan mengklaim telah membuka
halaman penuh jika yang tersedia hanya snippet; pertahankan ketidakpastian bila perlu.

Format:
## Kesimpulan utama
## Temuan dan alasan
## Cross-Agent Review
## Pemeriksaan sumber
## Batasan dan ketidakpastian

Berikan jawaban akhir yang lengkap, tetapi fokus. Jangan mengulang seluruh analisis agen.
"""
    user_prompt = f"""
TOPIK: {topic}
PERTANYAAN: {question}
WAKTU: {timestamp}

PAKET SUMBER:
{format_sources(sources)}

HASIL AGEN:
{json.dumps(agent_results, ensure_ascii=False, indent=2)}

Audit secara kritis dan susun jawaban akhir.
"""
    return call_model(system_prompt, user_prompt, temperature=0.15, max_tokens=3600)

# =========================================================
# SESSION STATE
# =========================================================

if "histories" not in st.session_state:
    st.session_state.histories = {topic: [] for topic in TOPICS}
if "last_run" not in st.session_state:
    st.session_state.last_run = None
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Research Chat"

# =========================================================
# DESIGN SYSTEM — GLASS / GLOW / MICRO-INTERACTIONS
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;450;500;550;600;650;700;750&display=swap');

:root {
  --bg: #090c13;
  --panel: rgba(20, 25, 38, 0.62);
  --glass: rgba(255,255,255,0.045);
  --glass-border: rgba(210,222,255,0.11);
  --text: #e5e7eb;
  --muted: #9aa4b5;
  --accent: #9cafff;
  --accent2: #8de4d3;
}
html, body, [class*="css"] {
  font-family: 'Inter', ui-sans-serif, system-ui, sans-serif !important;
}
.stApp {
  color: var(--text);
  background:
    radial-gradient(ellipse at 12% 0%, rgba(83,105,210,.19), transparent 36%),
    radial-gradient(ellipse at 88% 12%, rgba(52,184,166,.12), transparent 34%),
    radial-gradient(ellipse at 50% 100%, rgba(110,83,190,.10), transparent 42%),
    var(--bg);
  background-attachment: fixed;
}
.block-container {
  max-width: 1280px;
  padding-top: 1.4rem;
  padding-bottom: 3.2rem;
}
p, li, .stMarkdown {
  line-height: 1.68 !important;
  color: var(--text);
}
h1, h2, h3, h4 {
  color: #f8fafc !important;
  letter-spacing: -0.035em;
}
small, .muted, [data-testid="stCaptionContainer"] {
  color: var(--muted) !important;
}
[data-testid="stSidebar"] {
  background: rgba(12,16,26,.76);
  border-right: 1px solid rgba(255,255,255,.08);
  backdrop-filter: blur(22px);
  -webkit-backdrop-filter: blur(22px);
}
[data-testid="stSidebar"] > div:first-child {
  background: transparent;
}
.hero {
  position: relative;
  overflow: hidden;
  padding: 1.7rem 1.8rem;
  border-radius: 24px;
  border: 1px solid rgba(205,220,255,.15);
  background: linear-gradient(135deg, rgba(255,255,255,.085), rgba(255,255,255,.025));
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  box-shadow: 0 18px 55px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.09);
  margin-bottom: 1.25rem;
  animation: rise-in .55s ease both;
}
.hero:before {
  content: "";
  position: absolute;
  width: 280px; height: 280px;
  right: -90px; top: -150px;
  background: rgba(137,155,255,.24);
  filter: blur(72px);
  border-radius: 50%;
  pointer-events: none;
}
.hero-label {
  text-transform: uppercase;
  letter-spacing: .19em;
  font-size: .72rem;
  color: #aebcff;
  font-weight: 700;
}
.hero h1 {
  margin: .5rem 0 .35rem;
  font-size: clamp(1.8rem, 4vw, 2.8rem);
  line-height: 1.12 !important;
}
.hero-subtitle {
  color: #aab4c6;
  max-width: 720px;
  font-size: .96rem;
}
.glass-card, div[data-testid="stExpander"], div[data-testid="stVerticalBlockBorderWrapper"] {
  border-color: var(--glass-border) !important;
  border-radius: 18px !important;
}
div[data-testid="stExpander"] {
  background: rgba(255,255,255,.025);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: linear-gradient(145deg, rgba(255,255,255,.055), rgba(255,255,255,.018));
  box-shadow: 0 8px 30px rgba(0,0,0,.12), inset 0 1px 0 rgba(255,255,255,.04);
}
div[data-testid="stChatMessage"] {
  border: 1px solid rgba(215,225,255,.09);
  border-radius: 20px;
  padding: 1rem 1.15rem;
  margin: .8rem 0;
  background: rgba(255,255,255,.025);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: 0 10px 28px rgba(0,0,0,.10);
  animation: rise-in .28s ease both;
}
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  margin-left: auto;
  max-width: 86%;
  background: linear-gradient(130deg, rgba(111,132,255,.19), rgba(99,117,181,.09));
  border-color: rgba(151,166,255,.20);
  border-top-right-radius: 7px;
}
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
  margin-right: auto;
  max-width: 100%;
  background: rgba(255,255,255,.025);
  border-top-left-radius: 7px;
}
[data-testid="stChatInput"] {
  border: 1px solid rgba(177,194,255,.20) !important;
  border-radius: 20px !important;
  background: rgba(15,20,33,.78) !important;
  box-shadow: 0 0 0 1px rgba(120,140,255,.025), 0 0 30px rgba(105,125,255,.06);
  backdrop-filter: blur(22px);
  -webkit-backdrop-filter: blur(22px);
}
[data-testid="stChatInput"] textarea {
  color: #e5e7eb !important;
  line-height: 1.6 !important;
}
.stButton > button {
  border-radius: 12px;
  border: 1px solid rgba(202,214,255,.15);
  background: rgba(255,255,255,.045);
  color: #e7eaf2;
  transition: all .18s ease;
}
.stButton > button:hover {
  border-color: rgba(151,170,255,.45);
  background: rgba(130,150,255,.11);
  transform: translateY(-1px);
  box-shadow: 0 5px 22px rgba(104,124,255,.10);
}
[data-testid="stRadio"] label {
  transition: color .18s ease, opacity .18s ease;
}
[data-testid="stRadio"] label:hover {
  color: #c5ceff !important;
}
button[data-baseweb="tab"] {
  transition: background .18s ease, color .18s ease;
  border-radius: 10px 10px 0 0;
}
button[data-baseweb="tab"][aria-selected="true"] {
  color: #dce3ff !important;
}
[data-testid="stProgressBar"] > div > div {
  background: linear-gradient(90deg, #879bff, #82dfd0);
  box-shadow: 0 0 15px rgba(130,160,255,.35);
}
hr { border-color: rgba(255,255,255,.08) !important; }
@keyframes rise-in {
  from { opacity: 0; transform: translateY(7px); }
  to { opacity: 1; transform: translateY(0); }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important;
    transition-duration: .01ms !important;
  }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("## QUORA **AI**")
    st.caption("RESEARCH WORKSPACE · 2.5")
    st.divider()

    page_options = {
        "Research Chat": ":material/forum:",
        "Evidence Standard": ":material/verified_user:",
        "Agent Registry": ":material/hub:",
        "Model & System": ":material/tune:",
    }
    page = st.radio(
        "WORKSPACE",
        list(page_options.keys()),
        format_func=lambda x: f"{page_options[x]}  {x}",
        label_visibility="collapsed",
    )
    st.divider()

    st.markdown("##### TOPIC HUBS")
    selected_topic = st.radio(
        "Pilih topik",
        list(TOPICS.keys()),
        label_visibility="collapsed",
        format_func=lambda x: x,
    )
    st.divider()

    st.markdown("##### SYSTEM STATUS")
    st.caption("MODEL")
    st.code("Nemotron 3 Ultra · Free", language=None)
    st.caption("AGENT PIPELINE")
    st.markdown("`03 Agents`  →  `01 Reviewer`")
    st.caption("LOCAL TIME")
    st.markdown(f"**{now_wib()}**")
    if get_secret("TAVILY_API_KEY"):
        st.markdown(":green[● Web search configured]")
    else:
        st.markdown(":orange[● Web search not configured]")

# =========================================================
# PAGE: EVIDENCE
# =========================================================

if page == "Evidence Standard":
    st.markdown('<div class="hero"><div class="hero-label">RESEARCH PROTOCOL</div><h1>Evidence over assumptions.</h1><div class="hero-subtitle">Standar bukti, transparansi, dan evaluasi klaim.</div></div>', unsafe_allow_html=True)
    standards = [
        ("Independensi", "Agen tidak menyetujui pengguna atau agen lain tanpa alasan yang dapat dijelaskan."),
        ("Objektivitas", "Bukti yang mendukung dan menentang diperiksa dengan standar yang sama."),
        ("Kerendahan hati intelektual", "Ketidakpastian diakui; dugaan tidak diubah menjadi fakta."),
        ("Koreksi diri", "Kesalahan diperbaiki jika alasan atau bukti yang lebih kuat ditemukan."),
        ("Transparansi", "Fakta, asumsi, estimasi, opini, dan hal yang belum diketahui dipisahkan."),
        ("Web research", "Hasil pencarian ditampilkan dengan URL dan metadata yang tersedia."),
        ("Cross-Agent Review", "Reviewer membandingkan klaim, mencari konflik, dan mengaudit sumber."),
        ("Output completion", "Jika model menandai output terpotong karena batas token, sistem mencoba melanjutkan secara terbatas."),
    ]
    for title, desc in standards:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(desc)
    st.info("Pencarian web dan cross-review mengurangi sebagian risiko, tetapi tidak menjamin semua klaim benar. Snippet bukan pengganti pemeriksaan dokumen lengkap.")

# =========================================================
# PAGE: AGENT REGISTRY
# =========================================================

elif page == "Agent Registry":
    st.markdown('<div class="hero"><div class="hero-label">PERSONALITY REGISTRY</div><h1>Different mandates. Independent minds.</h1><div class="hero-subtitle">18 profil kerja di enam bidang. Karakter adalah gaya penalaran yang diarahkan oleh instruksi, bukan klaim kesadaran.</div></div>', unsafe_allow_html=True)
    for topic, agents in TOPICS.items():
        with st.expander(topic, expanded=(topic == selected_topic)):
            for agent in agents:
                with st.container(border=True):
                    st.markdown(f"**{agent['name']}**")
                    st.caption(agent["personality"])
                    st.write(agent["role"])
                    st.write(f"**Mandat:** {agent['mission']}")

# =========================================================
# PAGE: SYSTEM
# =========================================================

elif page == "Model & System":
    st.markdown('<div class="hero"><div class="hero-label">SYSTEM CONTROL</div><h1>Model & runtime.</h1><div class="hero-subtitle">Konfigurasi aplikasi dan status integrasi.</div></div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("**Model ID**")
        st.code(MODEL, language=None)
        st.markdown("**LLM gateway**")
        st.code("OpenRouter Chat Completions", language=None)
        st.markdown("**Web search**")
        st.write("Tavily aktif" if get_secret("TAVILY_API_KEY") else "Tavily belum aktif — tambahkan TAVILY_API_KEY di Streamlit Secrets.")
        st.markdown("**Pipeline per pertanyaan**")
        st.write("1 pencarian web + 3 analisis independen + 1 cross-agent review. Jika output terpotong, tiap panggilan model dapat melakukan maksimal 2 lanjutan.")
        st.markdown("**Secret checks**")
        st.write("OPENROUTER_API_KEY:", "Terdeteksi" if get_secret("OPENROUTER_API_KEY") else "Belum ditemukan")
        st.write("TAVILY_API_KEY:", "Terdeteksi" if get_secret("TAVILY_API_KEY") else "Belum ditemukan")
    st.warning("Continuation membantu ketika model benar-benar mencapai batas token, tetapi tidak bisa memperbaiki semua jenis pemotongan atau kesalahan provider. Lebih banyak token/lanjutan juga dapat menambah waktu dan penggunaan API.")

# =========================================================
# PAGE: CHAT
# =========================================================

else:
    st.markdown('<div class="hero"><div class="hero-label">QUORA AI / RESEARCH CORE 2.5</div><h1>Think deeper. Verify better.</h1><div class="hero-subtitle">Independent analysis, web research, cross-agent review — presented in a quieter, glass-inspired workspace.</div></div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.markdown(f"### {selected_topic}")
        st.caption("Three independent agents. One critical reviewer.")
    with col_b:
        st.markdown(f"<div style='text-align:right;color:#9aa4b5;font-size:.8rem;padding-top:1rem'>{now_wib()}</div>", unsafe_allow_html=True)

    with st.expander("Active agents"):
        for agent in TOPICS[selected_topic]:
            st.markdown(f"**{agent['name']}** · {agent['personality']}")
            st.caption(agent["mission"])

    history = st.session_state.histories[selected_topic]

    for item in history:
        with st.chat_message(item["role"], avatar=":material/person:" if item["role"] == "user" else ":material/neurology:"):
            if item["role"] == "user":
                st.markdown(item["content"])
                continue

            st.caption(f"ANALYSIS STARTED · {item.get('timestamp', '')}")
            if item.get("search_error"):
                st.warning("Web search tidak tersedia: " + item["search_error"])

            with st.expander(f"Sources · {len(item.get('sources', []))} results", expanded=False):
                if item.get("sources"):
                    for source in item["sources"]:
                        st.markdown(f"**[{source['id']}] {source['title']}**")
                        if source.get("published_date"):
                            st.caption(f"Published: {source['published_date']}")
                        if source.get("url"):
                            st.markdown(f"[Open source ↗]({source['url']})")
                        st.write(source.get("content", ""))
                        st.divider()
                else:
                    st.write("Tidak ada hasil web yang tersedia.")

            results = item.get("agent_results", {})
            if results:
                tab_names = [a["name"] for a in TOPICS[selected_topic]] + ["Cross-Agent Review"]
                tabs = st.tabs(tab_names)
                for tab, agent in zip(tabs[:3], TOPICS[selected_topic]):
                    with tab:
                        result = results.get(agent["name"], "")
                        if result.startswith("ERROR:"):
                            st.error(result)
                        else:
                            st.markdown(result)
                with tabs[3]:
                    final_answer = item.get("final_answer", "")
                    if final_answer.startswith("ERROR:"):
                        st.error(final_answer)
                    elif final_answer:
                        st.markdown(final_answer)
                    else:
                        st.info("Reviewer belum menghasilkan kesimpulan.")
            if item.get("completed_at"):
                st.caption(f"COMPLETED · {item['completed_at']}")

    question = st.chat_input(f"Ask Quora AI about {selected_topic}…")

    if question:
        timestamp = now_wib()
        history.append({"role": "user", "content": question})

        run_record = {
            "role": "assistant",
            "timestamp": timestamp,
            "sources": [],
            "search_error": None,
            "agent_results": {},
            "final_answer": "",
            "completed_at": None,
        }

        with st.status("Searching the web…", expanded=True) as status_box:
            sources, search_error = search_web(question, selected_topic)
            run_record["sources"] = sources
            run_record["search_error"] = search_error
            if search_error:
                st.write("Web search tidak tersedia; model akan diberi konteks bahwa tidak ada hasil web.")
            else:
                st.write(f"{len(sources)} hasil pencarian dikumpulkan.")

            successful = {}
            agents = TOPICS[selected_topic]
            progress = st.progress(0)

            for index, agent in enumerate(agents):
                status_box.write(f"Analyzing · {agent['name']}")
                try:
                    answer = ask_agent(agent, question, selected_topic, timestamp, sources)
                    run_record["agent_results"][agent["name"]] = answer
                    successful[agent["name"]] = answer
                except Exception as error:
                    run_record["agent_results"][agent["name"]] = f"ERROR: {type(error).__name__}: {error}"
                progress.progress((index + 1) / 4)

            if successful:
                status_box.write("Cross-agent review · auditing claims and sources")
                try:
                    run_record["final_answer"] = cross_agent_review(
                        question, selected_topic, timestamp, sources, successful
                    )
                except Exception as error:
                    run_record["final_answer"] = f"ERROR: {type(error).__name__}: {error}"
            else:
                run_record["final_answer"] = "ERROR: Semua agen gagal. Reviewer tidak dijalankan karena tidak ada hasil untuk diaudit."

            progress.progress(1.0)
            run_record["completed_at"] = now_wib()
            status_box.update(label="Research run finished", state="complete", expanded=False)

        history.append(run_record)
        st.session_state.last_run = run_record
        st.rerun()

    st.divider()
    st.caption("QUORA AI 2.5 · AI-generated research can be wrong. Verify consequential claims against original sources.")
