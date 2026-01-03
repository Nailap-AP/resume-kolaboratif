# app.py
import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys
from utils.data_handler import load_research_data, save_research_data

# Konfigurasi halaman
st.set_page_config(
    page_title="Resume Laporan Penelitian",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS kustom
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #1E40AF;
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .research-card {
        background-color: #F0F9FF;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-left: 5px solid #3B82F6;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
    }
    .stButton button {
        background-color: #3B82F6;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Sidebar untuk navigasi
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2103/2103655.png", width=100)
        st.title("📚 Menu Navigasi")
        
        menu = st.radio(
            "Pilih Halaman:",
            ["🏠 Dashboard", "📝 Input Data", "🔍 Lihat Penelitian", "📊 Analisis", "⚙️ Pengaturan"]
        )
        
        st.markdown("---")
        st.markdown("### Tentang Aplikasi")
        st.info(
            "Aplikasi ini membantu peneliti membuat resume laporan penelitian "
            "yang dapat disimpan di GitHub dan ditampilkan di Streamlit."
        )
        
        st.markdown("---")
        st.markdown("**Dibuat oleh:** Tim Penelitian")
        st.markdown("**Versi:** 1.0.0")

    # Halaman Dashboard
    if menu == "🏠 Dashboard":
        show_dashboard()
    
    # Halaman Input Data
    elif menu == "📝 Input Data":
        show_input_form()
    
    # Halaman Lihat Penelitian
    elif menu == "🔍 Lihat Penelitian":
        show_research_list()
    
    # Halaman Analisis
    elif menu == "📊 Analisis":
        show_analysis()
    
    # Halaman Pengaturan
    elif menu == "⚙️ Pengaturan":
        show_settings()

def show_dashboard():
    st.markdown('<h1 class="main-header">📊 Dashboard Resume Laporan Penelitian</h1>', unsafe_allow_html=True)
    
    # Load data penelitian
    research_data = load_research_data()
    
    if not research_data:
        st.warning("Belum ada data penelitian. Silakan tambah data di halaman 'Input Data'.")
        return
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Penelitian", len(research_data))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        completed = sum(1 for r in research_data if r.get('status') == 'Selesai')
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Penelitian Selesai", completed)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        ongoing = sum(1 for r in research_data if r.get('status') == 'Berjalan')
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Sedang Berjalan", ongoing)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        years = list(set(r.get('tahun', '') for r in research_data))
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Rentang Tahun", f"{min(years)} - {max(years)}" if years else "-")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Grafik status penelitian
    st.markdown('<h2 class="section-header">📈 Statistik Penelitian</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart status
        status_counts = {}
        for research in research_data:
            status = research.get('status', 'Tidak Diketahui')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Distribusi Status Penelitian",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bar chart tahun
        year_counts = {}
        for research in research_data:
            year = research.get('tahun', '')
            if year:
                year_counts[year] = year_counts.get(year, 0) + 1
        
        if year_counts:
            fig = px.bar(
                x=list(year_counts.keys()),
                y=list(year_counts.values()),
                title="Jumlah Penelitian per Tahun",
                labels={'x': 'Tahun', 'y': 'Jumlah'},
                color=list(year_counts.values()),
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Penelitian terbaru
    st.markdown('<h2 class="section-header">📋 Penelitian Terbaru</h2>', unsafe_allow_html=True)
    
    # Urutkan berdasarkan tanggal (terbaru)
    sorted_research = sorted(research_data, 
                           key=lambda x: x.get('tanggal_mulai', ''), 
                           reverse=True)[:5]
    
    for research in sorted_research:
        with st.container():
            st.markdown(f"""
            <div class="research-card">
                <h3 style="color: #1E40AF;">{research.get('judul', 'Judul Tidak Tersedia')}</h3>
                <p><strong>Peneliti:</strong> {research.get('peneliti_utama', '')}</p>
                <p><strong>Status:</strong> <span style="color: {'#10B981' if research.get('status') == 'Selesai' else '#F59E0B'}">{research.get('status', 'Tidak Diketahui')}</span></p>
                <p><strong>Tahun:</strong> {research.get('tahun', '')}</p>
                <p>{research.get('abstrak', '')[:200]}...</p>
            </div>
            """, unsafe_allow_html=True)

def show_input_form():
    st.markdown('<h1 class="main-header">📝 Input Data Penelitian Baru</h1>', unsafe_allow_html=True)
    
    with st.form("research_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            judul = st.text_input("Judul Penelitian*", placeholder="Masukkan judul penelitian")
            peneliti_utama = st.text_input("Peneliti Utama*", placeholder="Nama peneliti utama")
            institusi = st.text_input("Institusi*", placeholder="Universitas/Institusi")
            tahun = st.number_input("Tahun Penelitian*", min_value=2000, max_value=2030, value=2024)
            status = st.selectbox("Status Penelitian*", ["Berjalan", "Selesai", "Dalam Perencanaan"])
        
        with col2:
            tanggal_mulai = st.date_input("Tanggal Mulai")
            tanggal_selesai = st.date_input("Tanggal Selesai")
            bidang = st.multiselect(
                "Bidang Ilmu",
                ["Teknologi", "Kesehatan", "Pendidikan", "Pertanian", "Sosial", "Ekonomi", "Lainnya"]
            )
            sumber_dana = st.text_input("Sumber Dana", placeholder="Contoh: DIKTI, LPDP, Swasta")
        
        # Bagian abstrak dan metodologi
        abstrak = st.text_area("Abstrak*", placeholder="Ringkasan penelitian (maksimal 500 kata)", height=150)
        latar_belakang = st.text_area("Latar Belakang", placeholder="Latar belakang penelitian", height=100)
        metodologi = st.text_area("Metodologi*", placeholder="Metode penelitian yang digunakan", height=100)
        
        # Hasil dan kesimpulan
        col3, col4 = st.columns(2)
        with col3:
            hasil = st.text_area("Hasil Penelitian", placeholder="Temuan utama penelitian", height=100)
        with col4:
            kesimpulan = st.text_area("Kesimpulan", placeholder="Kesimpulan penelitian", height=100)
        
        # Link dan referensi
        link_publikasi = st.text_input("Link Publikasi", placeholder="URL jurnal/repositori")
        kata_kunci = st.text_input("Kata Kunci (pisahkan dengan koma)", placeholder="contoh: AI, Machine Learning, Data Science")
        
        # Upload file (opsional)
        uploaded_file = st.file_uploader("Upload Dokumen Pendukung (PDF/DOC)", type=['pdf', 'doc', 'docx'])
        
        # Tombol submit
        submitted = st.form_submit_button("💾 Simpan Data Penelitian")
        
        if submitted:
            if not judul or not peneliti_utama or not abstrak:
                st.error("Harap isi semua field yang wajib diisi (*)")
            else:
                # Load data yang ada
                research_data = load_research_data()
                
                # Buat data baru
                new_research = {
                    'id': len(research_data) + 1,
                    'judul': judul,
                    'peneliti_utama': peneliti_utama,
                    'institusi': institusi,
                    'tahun': tahun,
                    'status': status,
                    'tanggal_mulai': str(tanggal_mulai),
                    'tanggal_selesai': str(tanggal_selesai) if tanggal_selesai else None,
                    'bidang': bidang,
                    'sumber_dana': sumber_dana,
                    'abstrak': abstrak,
                    'latar_belakang': latar_belakang,
                    'metodologi': metodologi,
                    'hasil': hasil,
                    'kesimpulan': kesimpulan,
                    'link_publikasi': link_publikasi,
                    'kata_kunci': [k.strip() for k in kata_kunci.split(',')] if kata_kunci else [],
                    'tanggal_input': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Tambahkan ke data yang ada
                research_data.append(new_research)
                
                # Simpan data
                if save_research_data(research_data):
                    st.success("✅ Data penelitian berhasil disimpan!")
                    
                    # Tampilkan preview
                    with st.expander("Preview Data yang Disimpan"):
                        st.json(new_research)
                else:
                    st.error("❌ Gagal menyimpan data. Silakan coba lagi.")

def show_research_list():
    st.markdown('<h1 class="main-header">🔍 Daftar Penelitian</h1>', unsafe_allow_html=True)
    
    research_data = load_research_data()
    
    if not research_data:
        st.warning("Belum ada data penelitian.")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.selectbox("Filter Status", ["Semua", "Berjalan", "Selesai", "Dalam Perencanaan"])
    
    with col2:
        filter_year = st.selectbox("Filter Tahun", ["Semua"] + sorted(list(set(str(r.get('tahun', '')) for r in research_data)), reverse=True))
    
    with col3:
        search_term = st.text_input("Cari (Judul/Peneliti)")
    
    # Filter data
    filtered_data = research_data
    
    if filter_status != "Semua":
        filtered_data = [r for r in filtered_data if r.get('status') == filter_status]
    
    if filter_year != "Semua":
        filtered_data = [r for r in filtered_data if str(r.get('tahun')) == filter_year]
    
    if search_term:
        filtered_data = [
            r for r in filtered_data 
            if search_term.lower() in r.get('judul', '').lower() 
            or search_term.lower() in r.get('peneliti_utama', '').lower()
        ]
    
    # Tampilkan jumlah hasil
    st.info(f"Menampilkan {len(filtered_data)} dari {len(research_data)} penelitian")
    
    # Tampilkan daftar penelitian
    for idx, research in enumerate(filtered_data):
        with st.expander(f"{idx+1}. {research.get('judul', 'Judul Tidak Tersedia')}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Peneliti Utama:** {research.get('peneliti_utama', '')}")
                st.markdown(f"**Institusi:** {research.get('institusi', '')}")
                st.markdown(f"**Tahun:** {research.get('tahun', '')}")
                st.markdown(f"**Status:** {research.get('status', '')}")
                st.markdown(f"**Bidang:** {', '.join(research.get('bidang', []))}")
                
                st.markdown("---")
                st.markdown("**Abstrak:**")
                st.write(research.get('abstrak', ''))
            
            with col2:
                # Badge status
                status_color = {
                    'Selesai': 'success',
                    'Berjalan': 'warning',
                    'Dalam Perencanaan': 'info'
                }.get(research.get('status'), 'secondary')
                
                st.markdown(f'<span class="badge bg-{status_color}">{research.get("status")}</span>', 
                          unsafe_allow_html=True)
                
                # Tombol aksi
                if st.button("📋 Detail", key=f"detail_{idx}"):
                    st.session_state.selected_research = research
                
                if st.button("📥 Ekspor", key=f"export_{idx}"):
                    # Simpan sebagai JSON
                    json_str = json.dumps(research, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="Download JSON",
                        data=json_str,
                        file_name=f"research_{research.get('id')}.json",
                        mime="application/json"
                    )
            
            # Jika dipilih untuk detail
            if 'selected_research' in st.session_state and st.session_state.selected_research.get('id') == research.get('id'):
                st.markdown("---")
                st.markdown("### Detail Lengkap")
                
                tab1, tab2, tab3, tab4 = st.tabs(["📄 Info", "🔬 Metodologi", "📊 Hasil", "🔗 Link"])
                
                with tab1:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Latar Belakang:**")
                        st.write(research.get('latar_belakang', ''))
                    with col2:
                        st.markdown("**Sumber Dana:**")
                        st.write(research.get('sumber_dana', 'Tidak Tersedia'))
                
                with tab2:
                    st.markdown("**Metodologi:**")
                    st.write(research.get('metodologi', ''))
                
                with tab3:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Hasil Penelitian:**")
                        st.write(research.get('hasil', ''))
                    with col2:
                        st.markdown("**Kesimpulan:**")
                        st.write(research.get('kesimpulan', ''))
                
                with tab4:
                    if research.get('link_publikasi'):
                        st.markdown(f"[🔗 Link Publikasi]({research.get('link_publikasi')})")
                    else:
                        st.info("Tidak ada link publikasi tersedia")

def show_analysis():
    st.markdown('<h1 class="main-header">📊 Analisis Data Penelitian</h1>', unsafe_allow_html=True)
    
    research_data = load_research_data()
    
    if not research_data:
        st.warning("Belum ada data penelitian untuk dianalisis.")
        return
    
    # Konversi ke DataFrame untuk analisis lebih mudah
    df = pd.DataFrame(research_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Analisis tren tahunan
        st.markdown('<h3 class="section-header">📈 Tren Penelitian per Tahun</h3>', unsafe_allow_html=True)
        
        if 'tahun' in df.columns:
            yearly_counts = df['tahun'].value_counts().sort_index()
            fig = px.line(
                x=yearly_counts.index,
                y=yearly_counts.values,
                title="Jumlah Penelitian per Tahun",
                labels={'x': 'Tahun', 'y': 'Jumlah Penelitian'},
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Analisis bidang ilmu
        st.markdown('<h3 class="section-header">🔬 Distribusi Bidang Ilmu</h3>', unsafe_allow_html=True)
        
        # Hitung bidang ilmu
        bidang_counts = {}
        for bidang_list in df['bidang'].dropna():
            for bidang in bidang_list:
                bidang_counts[bidang] = bidang_counts.get(bidang, 0) + 1
        
        if bidang_counts:
            fig = px.bar(
                x=list(bidang_counts.keys()),
                y=list(bidang_counts.values()),
                title="Jumlah Penelitian per Bidang",
                labels={'x': 'Bidang Ilmu', 'y': 'Jumlah'},
                color=list(bidang_counts.values()),
                color_continuous_scale='Plasma'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Word cloud kata kunci
    st.markdown('<h3 class="section-header">🏷️ Kata Kunci Populer</h3>', unsafe_allow_html=True)
    
    # Ekstrak semua kata kunci
    all_keywords = []
    for keywords in df['kata_kunci'].dropna():
        all_keywords.extend(keywords)
    
    if all_keywords:
        from collections import Counter
        keyword_counts = Counter(all_keywords)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Buat bar chart untuk kata kunci
            top_keywords = keyword_counts.most_common(10)
            fig = px.bar(
                x=[k[0] for k in top_keywords],
                y=[k[1] for k in top_keywords],
                title="10 Kata Kunci Terpopuler",
                labels={'x': 'Kata Kunci', 'y': 'Frekuensi'},
                color=[k[1] for k in top_keywords]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Statistik Kata Kunci:**")
            st.metric("Total Kata Kunci", len(keyword_counts))
            st.metric("Kata Kunci Unik", len(set(all_keywords)))
            st.metric("Rata-rata per Penelitian", round(len(all_keywords)/len(df), 1))
    
    # Analisis timeline
    st.markdown('<h3 class="section-header">📅 Timeline Penelitian</h3>', unsafe_allow_html=True)
    
    if 'tanggal_mulai' in df.columns:
        # Coba konversi tanggal
        try:
            df['tanggal'] = pd.to_datetime(df['tanggal_mulai'])
            df['bulan_tahun'] = df['tanggal'].dt.to_period('M').astype(str)
            
            monthly_counts = df['bulan_tahun'].value_counts().sort_index()
            
            fig = px.area(
                x=monthly_counts.index,
                y=monthly_counts.values,
                title="Timeline Penelitian (per Bulan)",
                labels={'x': 'Bulan-Tahun', 'y': 'Jumlah Penelitian'}
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Data tanggal tidak dapat diproses untuk timeline")

def show_settings():
    st.markdown('<h1 class="main-header">⚙️ Pengaturan Aplikasi</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Pengaturan Umum", "Ekspor/Impor", "Bantuan"])
    
    with tab1:
        st.markdown("### Konfigurasi Aplikasi")
        
        # Pengaturan tema
        theme = st.selectbox("Tema Tampilan", ["Terang", "Gelap", "Otomatis"])
        
        # Bahasa
        language = st.selectbox("Bahasa", ["Indonesia", "English"])
        
        # Notifikasi
        email_notif = st.checkbox("Aktifkan notifikasi email")
        if email_notif:
            email_address = st.text_input("Alamat Email", placeholder="email@contoh.com")
        
        # Simpan pengaturan
        if st.button("Simpan Pengaturan"):
            st.success("Pengaturan berhasil disimpan!")
    
    with tab2:
        st.markdown("### Ekspor Data Penelitian")
        
        research_data = load_research_data()
        
        if research_data:
            # Ekspor sebagai JSON
            json_data = json.dumps(research_data, indent=2, ensure_ascii=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📥 Download Semua Data (JSON)",
                    data=json_data,
                    file_name=f"research_data_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            
            with col2:
                st.download_button(
                    label="📊 Download sebagai CSV",
                    data=pd.DataFrame(research_data).to_csv(index=False),
                    file_name=f"research_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            st.markdown("---")
            st.markdown("### Impor Data")
            
            uploaded_file = st.file_uploader("Upload file JSON data penelitian", type=['json'])
            
            if uploaded_file is not None:
                try:
                    imported_data = json.load(uploaded_file)
                    st.info(f"File berhasil diupload: {len(imported_data)} entri ditemukan")
                    
                    if st.button("Gabungkan dengan Data Saat Ini"):
                        # Gabungkan data
                        combined_data = research_data + imported_data
                        # Hapus duplikat berdasarkan ID
                        unique_data = []
                        seen_ids = set()
                        for item in combined_data:
                            if item['id'] not in seen_ids:
                                seen_ids.add(item['id'])
                                unique_data.append(item)
                        
                        if save_research_data(unique_data):
                            st.success(f"Data berhasil digabungkan! Total: {len(unique_data)} entri")
                        else:
                            st.error("Gagal menyimpan data gabungan")
                except Exception as e:
                    st.error(f"Error membaca file: {e}")
        else:
            st.warning("Tidak ada data untuk diekspor")
    
    with tab3:
        st.markdown("### Panduan Penggunaan")
        
        st.markdown("""
        #### Cara Menggunakan Aplikasi:
        
        1. **Input Data**: Tambahkan data penelitian baru melalui halaman "Input Data"
        2. **Lihat Data**: Periksa dan cari penelitian di halaman "Lihat Penelitian"
        3. **Analisis**: Lihat statistik dan tren di halaman "Analisis"
        4. **Ekspor**: Download data di halaman "Pengaturan > Ekspor/Impor"
        
        #### Fitur:
        - 📝 Input data penelitian lengkap
        - 🔍 Pencarian dan filter data
        - 📊 Visualisasi data interaktif
        - 📥 Ekspor data ke berbagai format
        - 💾 Simpan data ke file JSON
        
        #### Kontak:
        Jika mengalami masalah, silakan buat issue di repository GitHub.
        """)
        
        st.markdown("---")
        st.markdown("### Informasi Aplikasi")
        
        st.code(f"""
        Versi Aplikasi: 1.0.0
        Jumlah Data: {len(load_research_data())} penelitian
        Update Terakhir: {datetime.now().strftime('%d %B %Y')}
        """)

if __name__ == "__main__":
    main()
