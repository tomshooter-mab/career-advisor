import time
import streamlit as st
from google import genai

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN WEB
# ---------------------------------------------------------
st.set_page_config(
    page_title="PathFinder AI - Career & Campus Advisor",
    page_icon="🎓",
    layout="wide"
)

# ---------------------------------------------------------
# 2. SISTEM LOGIN & SESSION STATE
# ---------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None  # 'guest' atau 'member'
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "users_db" not in st.session_state:
    st.session_state["users_db"] = {"siswa": "123456"}  # Database pengguna sementara

# ---------------------------------------------------------
# 3. HALAMAN LOGIN / REGISTER / GUEST MODE
# ---------------------------------------------------------
if not st.session_state["logged_in"]:
    st.title("🎓 PathFinder AI")
    st.caption("Platform Pemetaan Karir, Peluang Kampus, dan Analisis Portofolio Berbasis AI")
    st.markdown("---")

    col_login, col_guest = st.columns(2)

    # OPSI A: LOGIN / REGISTER (Member)
    with col_login:
        st.subheader("🔐 Akun Member")
        st.write("Masuk ke akun Anda untuk menyimpan riwayat analisis secara permanen.")
        
        tab_login, tab_register = st.tabs(["Masuk", "Daftar Akun"])
        
        with tab_login:
            user_in = st.text_input("Username:", key="login_user")
            pass_in = st.text_input("Password:", type="password", key="login_pass")
            if st.button("Masuk"):
                if user_in in st.session_state["users_db"] and st.session_state["users_db"][user_in] == pass_in:
                    st.session_state["logged_in"] = True
                    st.session_state["user_type"] = "member"
                    st.session_state["username"] = user_in
                    st.rerun()
                else:
                    st.error("Username atau password salah.")

        with tab_register:
            new_user = st.text_input("Username Baru:", key="reg_user")
            new_pass = st.text_input("Password Baru:", type="password", key="reg_pass")
            if st.button("Daftar"):
                if new_user and new_pass:
                    if new_user in st.session_state["users_db"]:
                        st.warning("Username sudah terdaftar.")
                    else:
                        st.session_state["users_db"][new_user] = new_pass
                        st.success("Akun berhasil dibuat! Silakan klik tab 'Masuk'.")
                else:
                    st.warning("Mohon isi username dan password.")

    # OPSI B: MODE TAMU (Akses Cepat)
    with col_guest:
        st.subheader("🚀 Mode Tamu (Akses Cepat)")
        st.write("Jelajahi fitur pemetaan karir dan rekomendasi kampus secara instan tanpa perlu pendaftaran.")
        st.info("💡 **Akses Cepat:** Mode ini cocok untuk Anda yang ingin langsung mencoba simulasi analisis AI.")
        
        guest_name = st.text_input("Nama / Panggilan:", placeholder="Contoh: Budi")
        if st.button("Lanjutkan sebagai Tamu ➡️"):
            st.session_state["logged_in"] = True
            st.session_state["user_type"] = "guest"
            st.session_state["username"] = guest_name if guest_name else "Pengunjung"
            st.rerun()

    st.stop()

# ---------------------------------------------------------
# 4. PEMBACAAN API KEY OTOMATIS (SECRETS)
# ---------------------------------------------------------
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        st.header("⚙️ Pengaturan Sistem")
        api_key = st.text_input("Masukkan Gemini API Key (Lokal):", type="password")

# ---------------------------------------------------------
# 5. DASHBOARD UTAMA
# ---------------------------------------------------------

# SIDEBAR NAVIGASI PROFIL
with st.sidebar:
    st.header("👤 Profil Pengguna")
    if st.session_state["user_type"] == "member":
        st.success(f"Member: **{st.session_state['username']}**")
    else:
        st.warning(f"Tamu: **{st.session_state['username']}**")
    
    if st.button("Keluar / Ganti Akun"):
        st.session_state["logged_in"] = False
        st.session_state["user_type"] = None
        st.session_state["username"] = ""
        st.rerun()

# HEADER UTAMA
st.title("🎓 PathFinder AI")
st.caption("Analisis Peluang PTN/PTS, Evaluasi Budget UKT, dan Rekomendasi Portofolio")
st.markdown("---")

# FORM INPUT DATA
st.subheader("📋 Form Data Pelajar & Target Akademik")
with st.form("student_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 Data Diri & Akademik")
        nama = st.text_input("Nama Lengkap / Inisial:", value=st.session_state["username"] if st.session_state["user_type"] == "member" else "")
        kelas = st.selectbox("Kelas / Jenjang Saat Ini:", ["SMA/SMK Kelas 10", "SMA/SMK Kelas 11", "SMA/SMK Kelas 12", "Gap Year"])
        rata_rapor = st.number_input("Rata-rata Nilai Rapor (Skala 100):", min_value=0.0, max_value=100.0, value=85.0, step=0.5)
        target_bidang = st.text_input("Target Bidang / Jurusan Impian:*", placeholder="Contoh: Teknik Informatika / Computer Science / Bisnis")

    with col2:
        st.markdown("### 💰 Biaya & Finansial")
        budget_kuliah = st.selectbox(
            "Budget Maksimal Biaya Kuliah (UKT / Semester):*",
            [
                "< Rp3.000.000 / semester (KIP-K / Beasiswa Penuh)",
                "Rp3.000.000 - Rp7.000.000 / semester",
                "Rp7.000.000 - Rp15.000.000 / semester",
                "Rp15.000.000 - Rp25.000.000 / semester",
                "> Rp25.000.000 / semester (Sanggup Mandiri/PTS Khusus)"
            ]
        )
        lokasi_favorit = st.text_input("Preferensi Wilayah Kampus:", placeholder="Contoh: Jawa Timur, Jawa Barat, Jabodetabek, atau Bebas")

    st.markdown("---")
    st.markdown("### 🏛️ Target Universitas Pilihan (Wajib 3 Pilihan)")
    uc1, uc2, uc3 = st.columns(3)
    with uc1:
        univ_1 = st.text_input("Pilihan 1 (Utama):*", placeholder="Contoh: BINUS Malang")
    with uc2:
        univ_2 = st.text_input("Pilihan 2 (Cadangan 1):*", placeholder="Contoh: Universitas Surabaya")
    with uc3:
        univ_3 = st.text_input("Pilihan 3 (Cadangan 2):*", placeholder="Contoh: Universitas Brawijaya")

    st.markdown("---")
    st.markdown("### 🛠️ Modal Skill & Portofolio Saat Ini")
    skill_dimiliki = st.text_area("Skill & Keahlian yang Dikuasai:*", placeholder="Contoh: Pemrograman Python, C++, logika matematika, Bahasa Inggris.", height=100)
    proyek_prestasi = st.text_area("Pengalaman Proyek / Karya / Aktivitas:", placeholder="Contoh: Proyek kalkulator Tkinter, proyek visualisasi data Python, lomba fisika, panitia sekolah.", height=100)

    submit_button = st.form_submit_button("🚀 Jalankan Analisis AI Completeness & Feasibility")

# ---------------------------------------------------------
# 6. PEMPROSESAN GOOGLE GEMINI API (SDK GOOGLE-GENAI)
# ---------------------------------------------------------
if submit_button:
    if not api_key:
        st.error("❌ Layanan AI belum siap. Konfigurasi Gemini API Key belum terdeteksi.")
    elif not target_bidang or not univ_1 or not univ_2 or not univ_3 or not skill_dimiliki:
        st.warning("⚠️ Mohon lengkapi semua kolom yang bertanda bintang (*).")
    else:
        # Urutan Fallback Model:
        # Menjajal seri 3.x terlebih dahulu, lalu otomatis beralih ke 2.x jika server overload (503) atau kehabisan kuota (429)
        models_to_try = [
            'gemini-3.6-flash',
            'gemini-3.1-pro-preview',
            'gemini-2.5-flash',
            'gemini-2.0-flash',
            'gemini-1.5-flash'
        ]
        
        response_text = None
        used_model_name = None
        errors_log = []

        with st.spinner("AI sedang menganalisis data universitas, budget, dan skill gap..."):
            try:
                client = genai.Client(api_key=api_key)
                
                system_prompt = """
                Kamu adalah Konsultan Karir, Pengamat Penerimaan Mahasiswa Baru, dan Advisor Portofolio Akademik profesional.
                Berikan analisis objektif, rasional, dan konstruktif dalam bahasa Indonesia yang baik dengan format Markdown berikut:
                
                ## 📊 1. Evaluasi Kecocokan Bidang (Field Alignment Score)
                - **Tingkat Kecocokan:** [Beri persentase 0-100%]
                - **Analisis Kualitatif:** Keselarasan antara minat, skill saat ini, dan target karir.

                ## 🏛️ 2. Analisis Peluang Diterima & Kelayakan Biaya (University Feasibility)
                Evaluasi ketiga universitas target berdasarkan persaingan, modal skill/nilai, dan budget:
                - **Pilihan 1: [Nama Univ 1]**
                  - *Estimasi Peluang Diterima:* [Tinggi / Sedang / Cenderung Berisiko / Sangat Sulit]
                  - *Analisis Skill vs Persaingan:* Apakah modal skill & nilai memadai?
                  - *Kesesuaian Budget:* Apakah perkiraan UKT sesuai rentang budget?
                - **Pilihan 2: [Nama Univ 2]**
                  - *Estimasi Peluang Diterima:* [Tinggi / Sedang / Cenderung Berisiko / Sangat Sulit]
                  - *Analisis Skill vs Persaingan:* ...
                  - *Kesesuaian Budget:* ...
                - **Pilihan 3: [Nama Univ 3]**
                  - *Estimasi Peluang Diterima:* [Tinggi / Sedang / Cenderung Berisiko / Sangat Sulit]
                  - *Analisis Skill vs Persaingan:* ...
                  - *Kesesuaian Budget:* ...

                ## 🔄 3. Opsi Alternatif Cadangan (Rencana Kontingensi)
                - **2 Alternatif Universitas/Jurusan Lain** yang sejenis, passing grade aman, dan pas dengan budget serta skill saat ini.

                ## 🛠️ 4. Skill Gap & Rencana Portofolio
                - **Skill Gap:** 3 skill utama yang MASIH KURANG dan WAJIB dipelajari.
                - **3 Ide Proyek Portofolio Nyata:** (Tingkat Dasar, Menengah, Lanjutan)

                ## ⚡ 5. Langkah Nyata Pekan Ini (Action Plan)
                - 3 tindakan konkret minggu ini.
                """

                user_payload = f"""
                Data Pengguna:
                - Nama: {nama if nama else 'Pengguna'}
                - Kelas: {kelas}
                - Nilai Rapor: {rata_rapor}
                - Target Bidang: {target_bidang}
                - Budget Kuliah: {budget_kuliah}
                - Preferensi Lokasi: {lokasi_favorit if lokasi_favorit else 'Bebas'}
                
                Target Universitas:
                - Pilihan 1: {univ_1}
                - Pilihan 2: {univ_2}
                - Pilihan 3: {univ_3}
                
                Modal Skill & Portofolio:
                - Skill: {skill_dimiliki}
                - Proyek/Pengalaman: {proyek_prestasi if proyek_prestasi else 'Belum ada'}
                """

                full_prompt = f"{system_prompt}\n\n{user_payload}"

                for model_name in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=full_prompt,
                        )
                        response_text = response.text
                        used_model_name = model_name
                        break
                    except Exception as e:
                        errors_log.append(f"**{model_name}**: {str(e)}")
                        time.sleep(2)  # Jeda 2 detik untuk menghindari lonjakan panggilan API secara berurutan
                        continue

            except Exception as e:
                st.error(f"Gagal menginisialisasi Client GenAI: {e}")

            if response_text:
                st.success(f"🎉 Analisis Selesai (Menggunakan Engine: `{used_model_name}`)!")
                st.markdown(response_text)
            else:
                st.error("❌ Gagal terhubung ke layanan Gemini. Detail kendala pada seluruh model:")
                for err in errors_log:
                    st.write(f"- {err}")
