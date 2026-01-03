# 📋 Aplikasi Resume Kolaboratif

Aplikasi web untuk membuat laporan secara kolaboratif dengan fitur multi-pengguna, version control, dan komentar.

## 🌐 Live Demo
Aplikasi dapat diakses di: [https://resume-kolaboratif.streamlit.app](https://resume-kolaboratif.streamlit.app)

## 🚀 Fitur Utama
- ✅ **Autentikasi Multi-User** dengan role-based access control
- ✅ **Buat & Edit Laporan** dengan version history
- ✅ **Kolaborasi Real-time** (simulasi)
- ✅ **Komentar & Diskusi** pada setiap laporan
- ✅ **Dashboard** dengan statistik lengkap
- ✅ **Filter & Pencarian** laporan
- ✅ **Ekspor Data** ke format JSON

## 👥 Role & Hak Akses
- **Admin**: Full access ke semua fitur
- **Editor**: Buat dan edit laporan
- **Reviewer**: Review dan approve laporan
- **Viewer**: Hanya melihat laporan

## 🔧 Teknologi yang Digunakan
- **Streamlit** - Framework web application
- **SQLite** - Database penyimpanan
- **Pandas** - Data manipulation
- **Python** - Backend programming

## 📦 Instalasi Lokal

```bash
# Clone repository
git clone https://github.com/username/resume-kolaboratif.git
cd resume-kolaboratif

# Install dependencies
pip install -r requirements.txt

# Run aplikasi
streamlit run app.py