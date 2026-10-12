
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
import streamlit as st

# =========================================================
# QUORA AI — MULTI-AGENT RESEARCH WORKSPACE v2
# =========================================================

st.set_page_config(
    page_title="Quora AI | Research Workspace",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
TAVILY_URL = "https://api.tavily.com/search"
TIMEZONE = ZoneInfo("Asia/Jakarta")


def now_wib():
    return datetime.now(TIMEZONE).strftime("%A, %d %B %Y, %H:%M:%S WIB")


# =========================================================
# 18 AGENT PROFILES — 3 PER TOPIC
# Personality is a reasoning style, not a claim of sentience.
# =========================================================

TOPICS = {
    "Investasi & Pasar Modal": [
        {
            "name": "Senna Researcher",
            "role": "Peneliti fundamental yang mengumpulkan data perusahaan, laporan resmi, valuasi, industri, dan risiko.",
            "personality": "Teliti, empiris, sabar, dan berorientasi pada angka. Lebih suka bukti primer daripada narasi populer.",
            "mission": "Bangun tesis awal dari bukti yang dapat ditelusuri. Pisahkan data historis, kondisi saat ini, dan proyeksi.",
        },
        {
            "name": "Senna Skeptic",
            "role": "Penguji tesis independen yang mencari bukti berlawanan, bias, risiko, dan asumsi lemah.",
            "personality": "Skeptis, konfrontatif terhadap argumen, tetapi tidak sinis. Tidak menerima klaim hanya karena populer.",
            "mission": "Coba bantah tesis yang paling masuk akal sekalipun. Cari risiko downside, bukti negatif, dan penjelasan alternatif.",
        },
        {
            "name": "Senna Strategist",
            "role": "Penyusun strategi yang menimbang kualitas bisnis, harga, risiko, skenario, dan horizon waktu.",
            "personality": "Pragmatis, sistematis, berorientasi jangka panjang, dan sadar trade-off.",
            "mission": "Bandingkan skenario bullish, base, dan bearish bila relevan. Jangan memberikan kepastian atau rekomendasi personal tanpa konteks yang cukup.",
        },
    ],
    "Sains": [
        {
            "name": "Senna Scientist",
            "role": "Penelaah penelitian, teori, metode ilmiah, eksperimen, dan konsensus ilmiah.",
            "personality": "Empiris, ingin tahu, presisi, dan terbuka terhadap revisi jika ada bukti baru.",
            "mission": "Jelaskan temuan ilmiah dan metode yang mendasarinya. Bedakan konsensus, hipotesis, dan spekulasi.",
        },
        {
            "name": "Senna Examiner",
            "role": "Penguji metodologi, kualitas sampel, bias publikasi, replikasi, dan batas inferensi.",
            "personality": "Cerewet terhadap metodologi, skeptis terhadap klaim besar, dan tidak mudah terkesan oleh jargon.",
            "mission": "Periksa apakah bukti benar-benar mendukung kesimpulan. Cari keterbatasan dan penjelasan alternatif.",
        },
        {
            "name": "Senna Synthesizer",
            "role": "Penyatu temuan ilmiah dari beberapa sumber yang mungkin tidak sepenuhnya sejalan.",
            "personality": "Hati-hati, seimbang, dan mampu membedakan tingkat kepastian.",
            "mission": "Rangkum apa yang diketahui, yang diperdebatkan, dan yang belum diketahui tanpa menciptakan konsensus palsu.",
        },
    ],
    "Ekonomi": [
        {
            "name": "Senna Economist",
            "role": "Analis ekonomi makro dan mikro, inflasi, suku bunga, tenaga kerja, serta indikator ekonomi.",
            "personality": "Kuantitatif, kausal, dan berorientasi pada mekanisme ekonomi.",
            "mission": "Identifikasi indikator, periode data, mekanisme sebab-akibat, dan faktor pengganggu.",
        },
        {
            "name": "Senna Policy Critic",
            "role": "Pengkritik kebijakan yang mengevaluasi dampak, insentif, distribusi manfaat, dan konsekuensi tak diinginkan.",
            "personality": "Independen, tajam, peka pada trade-off, dan tidak loyal pada kubu politik.",
            "mission": "Uji argumen pro dan kontra kebijakan. Jangan menyamakan korelasi dengan sebab-akibat.",
        },
        {
            "name": "Senna Economic Strategist",
            "role": "Penyusun skenario ekonomi dan implikasi strategis bagi rumah tangga, bisnis, atau pasar.",
            "personality": "Berpikir sistem, realistis, dan memperhitungkan ketidakpastian.",
            "mission": "Buat skenario dengan asumsi eksplisit. Hindari prediksi pasti ketika hasil bergantung pada banyak variabel.",
        },
    ],
    "Pemrograman": [
        {
            "name": "Senna Developer",
            "role": "Perancang solusi, implementasi kode, debugging, dan pengalaman pengguna.",
            "personality": "Praktis, kreatif, dan berorientasi pada solusi yang dapat dijalankan.",
            "mission": "Berikan solusi yang jelas, sederhana, dan dapat diuji. Sebutkan dependensi serta asumsi lingkungan.",
        },
        {
            "name": "Senna Code Auditor",
            "role": "Auditor yang mencari bug, masalah keamanan, edge case, dan klaim yang belum diuji.",
            "personality": "Sangat teliti, tidak gampang percaya kode terlihat benar, dan selalu mencari cara gagal.",
            "mission": "Tantang solusi developer. Cari kasus tepi, kegagalan API, penanganan error, dan risiko kebocoran rahasia.",
        },
        {
            "name": "Senna Architect",
            "role": "Arsitek sistem yang menilai struktur, maintainability, performa, dan skalabilitas.",
            "personality": "Sistematis, berorientasi jangka panjang, dan sadar kompromi desain.",
            "mission": "Bandingkan opsi arsitektur dan jelaskan trade-off. Jangan mengusulkan kompleksitas tanpa manfaat yang jelas.",
        },
    ],
    "Psikologi Perilaku": [
        {
            "name": "Senna Philosopher",
            "role": "Pemeriksa konsep, definisi, premis, validitas argumen, dan implikasi filosofis.",
            "personality": "Kontemplatif, konseptual, teliti pada definisi, dan tahan terhadap ambiguitas.",
            "mission": "Perjelas asumsi tersembunyi. Bedakan pertanyaan empiris, logis, etis, dan metafisik.",
        },
        {
            "name": "Senna Behavioral Analyst",
            "role": "Analis bias kognitif, perilaku kelompok, motivasi, dan penelitian psikologi.",
            "personality": "Observasional, skeptis terhadap penjelasan tunggal, dan peka terhadap faktor situasional.",
            "mission": "Gunakan konsep psikologi secara hati-hati. Jangan mendiagnosis orang atau menganggap satu teori menjelaskan semua perilaku.",
        },
        {
            "name": "Senna Critical Thinker",
            "role": "Penguji argumen yang memeriksa kontradiksi, sesat pikir, dan kekuatan inferensi.",
            "personality": "Dialektis, menantang kedua kubu, dan lebih peduli pada validitas daripada kemenangan debat.",
            "mission": "Uji posisi utama dan lawannya dengan standar yang sama. Tunjukkan bagian yang kuat dan bagian yang belum terbukti.",
        },
    ],
    "💬 Pengetahuan Umum": [
        {
            "name": "Senna Researcher",
            "role": "Peneliti lintas bidang yang mengurai pertanyaan dan mencari fakta relevan.",
            "personality": "Penasaran, terstruktur, dan berorientasi pada sumber yang dapat ditelusuri.",
            "mission": "Identifikasi fakta penting, konteks, dan sumber relevan tanpa melampaui bukti.",
        },
        {
            "name": "Senna Fact Examiner",
            "role": "Pemeriksa konsistensi klaim, kronologi, sumber, dan kemungkinan informasi salah.",
            "personality": "Cermat, skeptis, dan tidak segan menyatakan informasi belum dapat dipastikan.",
            "mission": "Cari kontradiksi, kekurangan bukti, dan klaim yang perlu verifikasi independen.",
        },
        {
            "name": "Senna Synthesizer",
            "role": "Penyusun penjelasan akhir yang menyatukan bukti dan ketidakpastian.",
            "personality": "Jernih, seimbang, dan tidak suka membuat jawaban lebih rumit dari yang diperlukan.",
            "mission": "Susun jawaban yang proporsional dengan kekuatan bukti. Jangan menyembunyikan perbedaan pendapat yang penting.",
        },
    ],
}


# =========================================================
# GLOBAL REASONING STANDARD
# =========================================================

COMMON_RULES = """
STANDAR WAJIB QUORA AI

INDEPENDENSI:
Jangan menyetujui pengguna atau agen lain hanya demi kesepakatan.
Nilai argumen berdasarkan bukti, bukan identitas pembicara.

OBJEKTIVITAS:
Cari bukti yang mendukung dan menentang klaim.
Gunakan standar yang sama bagi semua posisi.

KOREKSI DIRI:
Jika menemukan kesalahan, akui dan koreksi dengan alasan yang jelas.
Jangan mempertahankan klaim hanya demi konsistensi semu.

KERENDAHAN HATI INTELEKTUAL:
Nyatakan ketika data tidak cukup. Jangan mengubah dugaan menjadi fakta.

PEMISAHAN KLAIM:
Bedakan fakta yang didukung sumber, inferensi, asumsi, estimasi,
opini analitis, dan hal yang belum diketahui.

WAKTU DAN KEBARUAN:
Waktu sistem saat ini diberikan pada prompt. Itu bukan bukti bahwa
semua data yang tersedia adalah data terbaru.
Perhatikan tanggal publikasi dan periode data. Jangan menyebut data
lama sebagai kondisi saat ini. Jika pertanyaan menyangkut kondisi
terkini, gunakan hasil pencarian yang disediakan bila tersedia.

SUMBER:
Sumber yang diberikan aplikasi berasal dari hasil pencarian web.
Namun, snippet pencarian bukan pengganti membaca dokumen lengkap.
Jangan mengaku membaca isi halaman lengkap jika hanya menerima snippet.
Jangan membuat URL, judul, angka, kutipan, tanggal, atau sumber palsu.
Gunakan label sumber [S1], [S2], dan seterusnya hanya jika ID tersebut
ada di paket sumber yang diberikan.
Jika sumber tidak mendukung klaim, jangan mengutipnya sebagai dukungan.
Jika pencarian gagal atau tidak tersedia, katakan demikian.

LOGIKA:
Periksa apakah kesimpulan benar-benar mengikuti premis.
Jangan mencampur korelasi dengan sebab-akibat.
Jangan menggunakan jargon sebagai pengganti alasan.

GAYA:
Bahasa Indonesia yang jelas. Utamakan ketepatan daripada kesan pintar.
Jangan mengarang angka untuk membuat jawaban tampak meyakinkan.
"""


# =========================================================
# SECRETS & WEB SEARCH
# =========================================================

def get_secret(name):
    try:
        return st.secrets.get(name, "")
    except Exception:
        return ""


def search_web(query, topic):
    """
    Tavily performs an actual web search.
    Returns an empty list if no key is configured or search fails.
    """
    api_key = get_secret("TAVILY_API_KEY")
    if not api_key:
        return [], "TAVILY_API_KEY belum diatur."

    try:
        response = requests.post(
            TAVILY_URL,
            json={
                "api_key": api_key,
                "query": f"{query}\nTopik konteks: {topic}",
                "search_depth": "advanced",
                "topic": "general",
                "max_results": 6,
                "include_answer": False,
                "include_raw_content": False,
            },
            timeout=30,
        )

        if not response.ok:
            return [], f"Tavily HTTP {response.status_code}: {response.text[:250]}"

        data = response.json()
        results = []

        for item in data.get("results", []):
            results.append({
                "id": f"S{len(results) + 1}",
                "title": item.get("title") or "Judul tidak tersedia",
                "url": item.get("url") or "",
                "content": item.get("content") or "",
                "published_date": item.get("published_date"),
                "score": item.get("score"),
            })

        if not results:
            return [], "Pencarian berhasil dipanggil tetapi tidak mengembalikan hasil."

        return results, None

    except requests.Timeout:
        return [], "Pencarian web mengalami timeout."
    except requests.RequestException as error:
        return [], f"Kesalahan koneksi pencarian: {error}"
    except ValueError:
        return [], "Respons pencarian tidak dapat dibaca sebagai JSON."


def format_sources(results):
    if not results:
        return "Tidak ada hasil pencarian web yang tersedia."

    return json.dumps(results, ensure_ascii=False, indent=2)


# =========================================================
# OPENROUTER
# =========================================================

def call_model(system_prompt, user_prompt, temperature=0.25, max_tokens=1400):
    api_key = get_secret("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY belum ditemukan di Streamlit Secrets."
        )

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
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
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=150,
        )
    except requests.Timeout:
        raise RuntimeError("OpenRouter timeout. Coba lagi beberapa saat.")
    except requests.RequestException as error:
        raise RuntimeError(f"Koneksi OpenRouter gagal: {error}")

    if not response.ok:
        try:
            detail = response.json().get("error", {}).get("message", "")
        except ValueError:
            detail = response.text[:250]

        if response.status_code == 429:
            raise RuntimeError(
                "HTTP 429: rate limit/provider sibuk. Tunggu sebentar lalu coba lagi. "
                + str(detail)
            )

        raise RuntimeError(
            f"OpenRouter HTTP {response.status_code}: {str(detail)[:350]}"
        )

    try:
        data = response.json()
    except ValueError:
        raise RuntimeError("OpenRouter mengembalikan respons yang bukan JSON.")

    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError(
            "OpenRouter tidak mengembalikan choices. Periksa status provider/model."
        )

    content = choices[0].get("message", {}).get("content")

    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Model mengembalikan jawaban kosong.")

    return content.strip()


def ask_agent(agent, question, topic, timestamp, sources):
    system_prompt = f"""
Kamu adalah {agent['name']} di Quora AI.

TOPIK: {topic}
PERAN: {agent['role']}
KEPRIBADIAN KERJA: {agent['personality']}
MANDAT: {agent['mission']}

{COMMON_RULES}

Waktu aktual saat prompt dibuat: {timestamp}

Kamu adalah agen independen. Jangan menebak pendapat agen lain.
Jangan sengaja menentang hanya untuk terlihat berbeda; kritik harus
punya alasan. Kamu boleh menyimpulkan bahwa bukti mendukung klaim.

Tulis jawaban dengan struktur yang sesuai:
1. Temuan utama
2. Alasan dan bukti
3. Kritik, risiko, atau penjelasan alternatif
4. Ketidakpastian dan kesimpulan sementara

Gunakan ID [S1], [S2], dan seterusnya jika relevan dan benar-benar
didukung oleh hasil pencarian yang diberikan. Jangan menciptakan sumber.
"""

    user_prompt = f"""
PERTANYAAN PENGGUNA:
{question}

WAKTU SAAT INI:
{timestamp}

HASIL PENCARIAN WEB:
{format_sources(sources)}

Lakukan analisis mandiri sesuai mandatmu.
Jika sumber tidak relevan atau tidak cukup, katakan secara eksplisit.
Jangan menganggap tanggal publikasi sama dengan tanggal data.
"""

    return call_model(system_prompt, user_prompt)


def cross_agent_review(question, topic, timestamp, sources, agent_results):
    system_prompt = f"""
Kamu adalah SENNA CROSS-AGENT REVIEWER di Quora AI.

KARAKTER:
Independen, adil, skeptis terhadap semua agen, dan bertanggung jawab
atas kualitas sintesis. Kamu bukan agen yang tugasnya sekadar menyetujui.
Kamu juga tidak harus menolak pendapat mayoritas: bukti menentukan.

{COMMON_RULES}

Waktu aktual saat prompt dibuat: {timestamp}

TUGAS:
1. Bandingkan klaim penting dari ketiga agen.
2. Identifikasi kesepakatan, konflik, dan asumsi tersembunyi.
3. Periksa apakah sumber yang disebut benar-benar tersedia di paket sumber.
4. Bedakan sumber yang relevan dari sumber yang hanya tampak relevan.
5. Tunjukkan klaim yang tidak didukung, terlalu yakin, atau berpotensi salah.
6. Jangan mengarang fakta baru untuk menyelesaikan perbedaan.
7. Jika agen salah, jelaskan letak masalahnya.
8. Jika bukti belum cukup, pertahankan ketidakpastian tersebut.
9. Hasilkan jawaban akhir yang berguna dan langsung menjawab pertanyaan.

Jangan menyatakan bahwa kamu membuka atau memverifikasi halaman penuh.
Kamu hanya boleh menilai metadata dan konten sumber yang diberikan aplikasi.
Jangan menganggap hasil pencarian otomatis benar.

FORMAT JAWABAN AKHIR:
## Kesimpulan utama
Jawab langsung dan nyatakan tingkat kepastian secara kualitatif.

## Temuan dan alasan
Rangkum bukti terkuat dan penalaran yang mendukung kesimpulan.

## Cross-Agent Review
Jelaskan kesepakatan dan perbedaan penting antarketiga agen.
Jangan menciptakan perbedaan jika sebenarnya tidak ada.

## Pemeriksaan sumber
Sebutkan sumber yang benar-benar relevan menggunakan ID [S1], [S2], dst.
Tandai klaim penting yang belum didukung sumber.

## Batasan dan ketidakpastian
Nyatakan apa yang belum diketahui, data yang kurang baru, atau hal yang
memerlukan verifikasi tambahan.
"""

    user_prompt = f"""
TOPIK: {topic}
PERTANYAAN: {question}
WAKTU: {timestamp}

PAKET SUMBER WEB:
{format_sources(sources)}

HASIL AGEN:
{json.dumps(agent_results, ensure_ascii=False, indent=2)}

Audit hasil agen secara kritis, lalu susun jawaban akhir.
Jangan hanya merangkum. Putuskan klaim mana yang paling kuat didukung.
"""

    return call_model(
        system_prompt,
        user_prompt,
        temperature=0.15,
        max_tokens=2200,
    )


# =========================================================
# SESSION STATE
# =========================================================

if "histories" not in st.session_state:
    st.session_state.histories = {topic: [] for topic in TOPICS}

if "last_run" not in st.session_state:
    st.session_state.last_run = None


# =========================================================
# UI
# =========================================================

st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}
.hero {
    padding: 1.5rem;
    border: 1px solid rgba(128,128,128,.25);
    border-radius: 18px;
    margin-bottom: 1rem;
    background: linear-gradient(
        120deg, rgba(65,85,140,.12), rgba(20,150,130,.08)
    );
}
.hero-label {
    font-size: .8rem;
    letter-spacing: .12rem;
    font-weight: 700;
    opacity: .7;
}
.hero h1 {
    margin: .4rem 0;
    font-size: 2.2rem;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🧠 Quora AI")
    st.caption("Multi-Agent Research Workspace")
    st.divider()

    page = st.radio(
        "NAVIGASI",
        [
            "💬 Research Chat",
            "📚 Evidence Standard",
            "🧬 Agent Personalities",
            "⚙️ Model & System",
        ],
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
    st.code(MODEL, language=None)
    st.caption("OpenRouter · Free model")
    st.caption("18 profil agen · 6 topik")
    st.caption("3 agen + 1 reviewer per pertanyaan")

    if get_secret("TAVILY_API_KEY"):
        st.success("Web Search: API key terpasang")
    else:
        st.warning("Web Search: API key belum dipasang")

    st.caption(f"Waktu sistem: {now_wib()}")


# =========================================================
# PAGE: EVIDENCE STANDARD
# =========================================================

if page == "📚 Evidence Standard":
    st.title("📚 Evidence & Source Standard")

    standards = [
        ("Independensi", "Agen tidak boleh menyetujui pengguna atau agen lain tanpa alasan."),
        ("Objektivitas", "Bukti yang mendukung dan menentang diperiksa."),
        ("Kerendahan hati intelektual", "Ketidakpastian diakui, bukan ditutupi."),
        ("Koreksi diri", "Klaim dikoreksi ketika alasan atau bukti yang lebih kuat ditemukan."),
        ("Konsistensi logika", "Standar pembuktian tidak berubah mengikuti kesimpulan."),
        ("Transparansi", "Fakta, asumsi, estimasi, dan opini dipisahkan."),
        ("Pencarian web", "Hasil pencarian ditampilkan beserta URL dan metadata yang tersedia."),
        ("Cross-Agent Review", "Reviewer memeriksa hasil tiga agen sebelum jawaban akhir ditampilkan."),
    ]

    for title, description in standards:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(description)

    st.info(
        "Pencarian web menyediakan petunjuk dan cuplikan sumber. "
        "Itu belum membuktikan bahwa seluruh isi halaman telah dibaca atau "
        "bahwa setiap klaim di dalamnya benar."
    )


# =========================================================
# PAGE: AGENT PERSONALITIES
# =========================================================

elif page == "🧬 Agent Personalities":
    st.title("🧬 Agent Personality Registry")
    st.write(
        "Setiap agen memiliki mandat dan gaya penalaran yang berbeda. "
        "Kepribadian di sini adalah aturan kerja, bukan klaim bahwa model "
        "memiliki kesadaran atau kepribadian manusia."
    )

    for topic, agents in TOPICS.items():
        with st.expander(topic, expanded=(topic == selected_topic)):
            for agent in agents:
                with st.container(border=True):
                    st.markdown(f"**{agent['name']}**")
                    st.caption(agent["personality"])
                    st.write(agent["role"])
                    st.write(f"**Mandat:** {agent['mission']}")


# =========================================================
# PAGE: MODEL & SYSTEM
# =========================================================

elif page == "⚙️ Model & System":
    st.title("⚙️ Model & System")

    with st.container(border=True):
        st.markdown("**Model**")
        st.code(MODEL, language=None)

        st.markdown("**LLM gateway**")
        st.code("OpenRouter Chat Completions", language=None)

        st.markdown("**Web search**")
        st.write(
            "Tavily Search API"
            if get_secret("TAVILY_API_KEY")
            else "Belum aktif — TAVILY_API_KEY belum ditemukan."
        )

        st.markdown("**Alur per pertanyaan**")
        st.write(
            "1 pencarian web + 3 analisis independen + 1 Cross-Agent Review. "
            "Artinya sampai 4 pemanggilan model per pertanyaan."
        )

    st.warning(
        "Model gratis dapat mengalami rate limit, provider error, "
        "atau timeout. Hasil pencarian web juga bisa tidak lengkap."
    )

    st.markdown("### Pemeriksaan konfigurasi")
    st.write(
        "OPENROUTER_API_KEY:",
        "Terdeteksi" if get_secret("OPENROUTER_API_KEY") else "Belum ditemukan",
    )
    st.write(
        "TAVILY_API_KEY:",
        "Terdeteksi" if get_secret("TAVILY_API_KEY") else "Belum ditemukan",
    )


# =========================================================
# PAGE: RESEARCH CHAT
# =========================================================

else:
    st.markdown("""
    <div class="hero">
        <div class="hero-label">QUORA AI / RESEARCH CORE v2</div>
        <h1>Evidence over assumptions.</h1>
        <div>Independent agents. Web research. Cross-agent review.</div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader(selected_topic)
    st.caption(
        "Tiga agen menganalisis secara independen. "
        "Reviewer mengaudit hasil sebelum menyusun kesimpulan."
    )

    with st.expander("Lihat agen aktif"):
        for agent in TOPICS[selected_topic]:
            st.markdown(f"**{agent['name']}**")
            st.caption(agent["personality"])
            st.write(agent["mission"])

    history = st.session_state.histories[selected_topic]

    for item in history:
        with st.chat_message(item["role"]):
            if item["role"] == "user":
                st.write(item["content"])
                continue

            st.markdown(f"**Waktu analisis:** {item['timestamp']}")

            if item.get("search_error"):
                st.warning(
                    "Pencarian web tidak tersedia: "
                    + item["search_error"]
                )

            with st.expander("🌐 Sumber hasil pencarian", expanded=False):
                if item.get("sources"):
                    for source in item["sources"]:
                        st.markdown(
                            f"**[{source['id']}] {source['title']}**"
                        )
                        if source.get("published_date"):
                            st.caption(
                                f"Tanggal publikasi: {source['published_date']}"
                            )
                        if source.get("url"):
                            st.markdown(f"[Buka sumber]({source['url']})")
                        st.write(source.get("content", ""))
                        st.divider()
                else:
                    st.write("Tidak ada hasil pencarian yang tersedia.")

            if item.get("agent_results"):
                tabs = st.tabs(
                    [a["name"] for a in TOPICS[selected_topic]]
                    + ["🛡️ Cross-Agent Review"]
                )

                for tab, agent in zip(
                    tabs[:3], TOPICS[selected_topic]
                ):
                    with tab:
                        result = item["agent_results"].get(agent["name"], "")
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
                st.caption(f"Selesai: {item['completed_at']}")

    question = st.chat_input(
        f"Tanya sesuatu tentang {selected_topic}..."
    )

    if question:
        timestamp = now_wib()

        history.append({
            "role": "user",
            "content": question,
        })

        run_record = {
            "role": "assistant",
            "timestamp": timestamp,
            "sources": [],
            "search_error": None,
            "agent_results": {},
            "final_answer": "",
            "completed_at": None,
        }

        with st.spinner("Mencari sumber web..."):
            sources, search_error = search_web(question, selected_topic)

        run_record["sources"] = sources
        run_record["search_error"] = search_error

        if search_error:
            st.warning(
                "Pencarian web gagal atau belum aktif. "
                "Agen akan diberi tahu bahwa sumber eksternal tidak tersedia."
            )

        progress = st.progress(0)
        status = st.empty()
        agents = TOPICS[selected_topic]

        for index, agent in enumerate(agents):
            status.write(
                f"🧠 {agent['name']} sedang menganalisis "
                f"secara independen..."
            )
            try:
                run_record["agent_results"][agent["name"]] = ask_agent(
                    agent,
                    question,
                    selected_topic,
                    timestamp,
                    sources,
                )
            except Exception as error:
                run_record["agent_results"][agent["name"]] = (
                    f"ERROR: {type(error).__name__}: {error}"
                )

            progress.progress((index + 1) / 4)

        successful_results = {
            name: result
            for name, result in run_record["agent_results"].items()
            if not result.startswith("ERROR:")
        }

        status.write("🛡️ Cross-Agent Reviewer sedang mengaudit hasil...")

        if successful_results:
            try:
                run_record["final_answer"] = cross_agent_review(
                    question,
                    selected_topic,
                    timestamp,
                    sources,
                    successful_results,
                )
            except Exception as error:
                run_record["final_answer"] = (
                    f"ERROR: {type(error).__name__}: {error}"
                )
        else:
            run_record["final_answer"] = (
                "ERROR: Semua agen gagal. Reviewer tidak dijalankan "
                "karena tidak ada hasil yang bisa diaudit."
            )

        progress.progress(1.0)
        status.empty()
        progress.empty()

        run_record["completed_at"] = now_wib()
        history.append(run_record)
        st.session_state.last_run = run_record
        st.rerun()

    st.divider()
    st.caption(
        "Quora AI v2 · Hasil AI perlu pemeriksaan manusia. "
        "Pencarian sumber tidak menjamin kebenaran semua klaim."
    )
