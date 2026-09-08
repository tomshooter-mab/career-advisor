import streamlit as st
from google import genai
from google.genai import types

# ---------------------------------------------------------
# KONFIGURASI HALAMAN
# ---------------------------------------------------------
st.set_page_config(
    page_title="PathFinder AI - Career & Campus Advisor",
    page_icon="🎓",
    layout="wide"
)

# ---------------------------------------------------------
# INISIALISASI SESSION STATE (DATABASE SEDERHANA)
# ---------------------------------------------------------
# Menyimpan status login dan database akun sementara di memori
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None  # 'guest' atau 'member'
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "users_db" not in st.session_state:
    # Simulasi database user bawaan
    st.session_state["users_db"] = {"siswa": "123456"}

# ---------------------------------------------------------
# TAMPILAN 1: HALAMAN AUTENTIKASI (PILIH MASUK / GUEST)
# ---------------------------------------------------------
if not st.session_state["logged_in"]:
    st.title("🎓 PathFinder AI")
    st.write("Selamat datang! Silakan pilih metode masuk untuk memulai analisis karir & universitas.")
    st.markdown("---")

    col_login, col_guest = st.columns(2)

    # OPSI A: MASUK / BUAT AKUN (Untuk User Serius)
    with col_login:
        st.subheader("🔐 Akun Member")
        st.write("Simpan riwayat analisis dan portofolio kamu secara permanen.")

        tab_login, tab_register = st.tabs(["Masuk", "Buat Akun Baru"])

        with tab_login:
            username_input = st.text_input("Username / Email:", key="login_user")
            password_input = st.text_input("Password:", type="password", key="login_pass")
            if st.button("Masuk ke Akun"):
                if username_input in st.session_state["users_db"] and st.session_state["users_db"][
                    username_input] == password_input:
                    st.session_state["logged_in"] = True
                    st.session_state["user_type"] = "member"
                    st.session_state["username"] = username_input
                    st.success(f"Berhasil masuk! Selamat datang kembali, {username_input}.")
                    st.rerun()
                else:
                    st.error("Username atau password salah.")

        with tab_register:
            new_user = st.text_input("Buat Username / Email Baru:", key="reg_user")
            new_pass = st.text_input("Buat Password:", type="password", key="reg_pass")
            if st.button("Daftar Akun Baru"):
                if new_user and new_pass:
                    if new_user in st.session_state["users_db"]:
                        st.warning("Username sudah terdaftar. Silakan gunakan username lain.")
                    else:
                        st.session_state["users_db"][new_user] = new_pass
                        st.success("Akun berhasil dibuat! Silakan masuk di tab 'Masuk'.")
                else:
                    st.warning("Mohon isi username dan password.")

    # OPSI B: MODE GUEST (Untuk Uji Coba Cepat / Demo Juri)
    with col_guest:
        st.subheader("🚀 Mode Guest (Coba Instan)")
        st.write("Gunakan aplikasi langsung tanpa perlu mendaftar. Cocok untuk uji coba singkat.")
        st.info(
            "💡 **Catatan Mode Guest:** Hasil analisis dapat dilihat langsung tetapi tidak disimpan ke dalam riwayat akun.")

        guest_name = st.text_input("Nama Pengunjung (Opsional):", placeholder="Contoh: Pengunjung / Juri 1")
        if st.button("Lanjutkan sebagai Guest ➡️"):
            st.session_state["logged_in"] = True
            st.session_state["user_type"] = "guest"
            st.session_state["username"] = guest_name if guest_name else "Guest User"
            st.rerun()

    st.stop()  # Menghentikan eksekusi kode di bawah jika belum memilih masuk

# ---------------------------------------------------------
# TAMPILAN 2: HALAMAN UTAMA APLIKASI (SETELAH MASUK)
# ---------------------------------------------------------

# SIDEBAR PENGATURAN & PROFIL
with st.sidebar:
    st.header("👤 Status Pengguna")
    if st.session_state["user_type"] == "member":
        st.success(f"Akun Member: **{st.session_state['username']}**")
    else:
        st.warning(f"Mode Guest: **{st.session_state['username']}**")

    if st.button("Keluar / Ganti Akun"):
        st.session_state["logged_in"] = False
        st.session_state["user_type"] = None
        st.session_state["username"] = ""
        st.rerun()

    st.markdown("---")
    st.header("⚙️ Pengaturan Sistem")
    api_key = st.text_input("Masukkan Gemini API Key:", type="password")
    st.markdown("[Dapatkan Gemini API Key Gratis](https://aistudio.google.com/)")

# HEADER UTAMA
st.title("🎓 PathFinder AI")
st.caption("Sistem Analisis Peluang Masuk PTN/PTS, Evaluasi Skill, dan Rekomendasi Portofolio Pelajar")
st.markdown("---")

# FORM INPUT PROFIL & PERTANYAAN WAJIB
st.subheader("📋 Form Data Pelajar & Target Akademik")
with st.form("student_analysis_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 👤 Data Diri & Akademik")
        nama = st.text_input("Nama Lengkap / Inisial:",
                             value=st.session_state["username"] if st.session_state["user_type"] == "member" else "")
        kelas = st.selectbox("Kelas / Jenjang Saat Ini:",
                             ["SMA/SMK Kelas 10", "SMA/SMK Kelas 11", "SMA/SMK Kelas 12", "Gap Year"])
        rata_rapor = st.number_input("Rata-rata Nilai Rapor Saat Ini (Skala 100):", min_value=0.0, max_value=100.0,
                                     value=85.0, step=0.5)
        target_bidang = st.text_input("Target Bidang Karir / Jurusan Impian:*",
                                      placeholder="Contoh: Computer Science / Teknik Informatika")

    with col2:
        st.markdown("### 💰 Biaya & Finansial")
        budget_kuliah = st.selectbox(
            "Budget Maksimal Biaya Kuliah (UKT / Per Semester):*",
            [
                "< Rp3.000.000 / semester (KIP-K / Beasiswa Penuh)",
                "Rp3.000.000 - Rp7.000.000 / semester",
                "Rp7.000.000 - Rp15.000.000 / semester",
                "Rp15.000.000 - Rp25.000.000 / semester",
                "> Rp25.000.000 / semester (Sanggup Mandiri/PTS Khusus)"
            ]
        )
        lokasi_favorit = st.text_input("Preferensi Wilayah Kampus:",
                                       placeholder="Contoh: Jawa Timur, Jabodetabek, atau Bebas")

    st.markdown("---")
    st.markdown("### 🏛️ Target Universitas Pilihan (Wajib 3 Pilihan)")
    uc1, uc2, uc3 = st.columns(3)
    with uc1:
        univ_1 = st.text_input("Pilihan 1 (Utama):*", placeholder="Contoh: ITS - Teknik Informatika")
    with uc2:
        univ_2 = st.text_input("Pilihan 2 (Cadangan 1):*", placeholder="Contoh: UB - Teknik Informatika")
    with uc3:
        univ_3 = st.text_input("Pilihan 3 (Cadangan 2):*", placeholder="Contoh: BINUS - Computer Science")

    st.markdown("---")
    st.markdown("### 🛠️ Modal Skill & Portofolio Saat Ini")
    skill_dimiliki = st.text_area("Skill & Keahlian yang Sudah Dikuasai (Sebutkan secara rinci):*",
                                  placeholder="Contoh: Dasar Python, logika Fisika, UI Tkinter.", height=100)
    proyek_prestasi = st.text_area("Pengalaman Proyek / Karya / Lomba yang Pernah Dibuat:",
                                   placeholder="Contoh: Kalkulator Python, ikutan OSK Fisika.", height=100)

    submit_button = st.form_submit_button("🚀 Jalankan Analisis AI Completeness & Feasibility")

# PROSES DAN OUTPUT GEMINI API
if submit_button:
    if not api_key:
        st.error("❌ Silakan masukkan Gemini API Key di sidebar terlebih dahulu.")
    elif not target_bidang or not univ_1 or not univ_2 or not univ_3 or not skill_dimiliki:
        st.warning("⚠️ Mohon lengkapi semua kolom yang bertanda bintang (*).")
    else:
        try:
            client = genai.Client(api_key=api_key)

            system_prompt = """
            Kamu adalah Konsultan Karir, Pengamat Penerimaan Mahasiswa Baru, dan Advisor Portofolio Akademik profesional.
            Tugasmu adalah menganalisis data calon mahasiswa dan memberikan masukan yang jujur, rasional, berbasis data, serta konstruktif.

            Gunakan format Markdown dengan struktur laporan sebagai berikut:

            ## 📊 1. Evaluasi Kecocokan Bidang (Field Alignment Score)
            - **Tingkat Kecocokan:** [Beri persentase 0-100%]
            - **Analisis Kualitatif:** Penjelasan apakah minat, skill saat ini, dan target karirnya sudah selaras.

            ## 🏛️ 2. Analisis Peluang Diterima & Kelayakan Biaya (University Feasibility)
            Evaluasi ketiga universitas target berdasarkan persaingan, modal skill/nilai, dan budget:
            - **Pilihan 1: [Nama Univ 1]**
              - *Estimasi Peluang Diterima:* [Tinggi / Sedang / Cenderung Berisiko / Sangat Sulit]
              - *Analisis Skill vs Persaingan:* Apakah modal skill & nilai rapor memadai?
              - *Kesesuaian Budget:* Apakah perkiraan UKT sesuai rentang budget?
            - **Pilihan 2: [Nama Univ 2]**
              - *Estimasi Peluang Diterima:* ...
              - *Analisis Skill vs Persaingan:* ...
              - *Kesesuaian Budget:* ...
            - **Pilihan 3: [Nama Univ 3]**
              - *Estimasi Peluang Diterima:* ...
              - *Analisis Skill vs Persaingan:* ...
              - *Kesesuaian Budget:* ...

            ## 🔄 3. Opsi Alternatif Cadangan (Rencana Kontingensi)
            Jika opsi di atas terlalu berisiko atau melebihi budget:
            - **2 Alternatif Universitas/Jurusan Lain** yang sejenis dan lebih aman sesuai budget serta skill.

            ## 🛠️ 4. Skill Gap & Rencana Portofolio
            - **Skill Gap:** 3 skill utama yang MASIH KURANG dan WAJIB dipelajari.
            - **3 Ide Proyek Portofolio Nyata:** (Tingkat Dasar, Menengah, Lanjutan)

            ## ⚡ 5. Langkah Nyata Pekan Ini (Action Plan)
            3 tindakan konkret minggu ini.
            """

            user_payload = f"""
            Data Murid:
            - Nama: {nama if nama else 'Murid'}
            - Kelas: {kelas}
            - Rata-rata Nilai Rapor: {rata_rapor}
            - Target Bidang / Karir: {target_bidang}
            - Budget Biaya Kuliah: {budget_kuliah}
            - Preferensi Lokasi: {lokasi_favorit if lokasi_favorit else 'Bebas'}

            Target Universitas:
            - Pilihan 1: {univ_1}
            - Pilihan 2: {univ_2}
            - Pilihan 3: {univ_3}

            Modal & Portofolio Saat Ini:
            - Skill yang Dikuasai: {skill_dimiliki}
            - Pengalaman Proyek/Prestasi: {proyek_prestasi if proyek_prestasi else 'Belum ada'}
            """

            with st.spinner(
                    "AI sedang menganalisis tingkat persaingan universitas, kelayakan budget, dan skill gap..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_payload,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.4
                    )
                )

                st.success("🎉 Analisis Portofolio & Kelayakan Kampus Selesai!")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"Terjadi kesalahan teknis: {e}")