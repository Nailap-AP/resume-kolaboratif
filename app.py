import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

# Set page config pertama di script
st.set_page_config(
    page_title="Aplikasi Resume Kolaboratif",
    page_icon="📋",
    layout="wide"
)

# Setup database path
@st.cache_resource
def init_database():
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect('data/laporan.db', check_same_thread=False)
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS laporan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT NOT NULL,
            konten TEXT,
            kategori TEXT,
            status TEXT DEFAULT 'draft',
            dibuat_oleh TEXT,
            tanggal_dibuat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            terakhir_diupdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS pengguna (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nama TEXT,
            role TEXT DEFAULT 'viewer'
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS kolaborator (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            laporan_id INTEGER,
            user_id INTEGER,
            role TEXT,
            FOREIGN KEY (laporan_id) REFERENCES laporan(id),
            FOREIGN KEY (user_id) REFERENCES pengguna(id)
        )
    ''')
    
    # Insert default users if not exist
    default_users = [
        ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'Administrator', 'admin'),
        ('user1', hashlib.sha256('user123'.encode()).hexdigest(), 'User Satu', 'editor'),
        ('user2', hashlib.sha256('user123'.encode()).hexdigest(), 'User Dua', 'viewer')
    ]
    
    for username, pwd_hash, nama, role in default_users:
        c.execute('''
            INSERT OR IGNORE INTO pengguna (username, password_hash, nama, role)
            VALUES (?, ?, ?, ?)
        ''', (username, pwd_hash, nama, role))
    
    conn.commit()
    return conn

# Initialize database
conn = init_database()

# Authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    c = conn.cursor()
    c.execute('SELECT password_hash FROM pengguna WHERE username = ?', (username,))
    result = c.fetchone()
    
    if result and result[0] == hash_password(password):
        c.execute('SELECT id, username, nama, role FROM pengguna WHERE username = ?', (username,))
        user_data = c.fetchone()
        return user_data
    return None

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Login Page
def login_page():
    st.title("🔐 Login - Aplikasi Resume Kolaboratif")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            user_data = authenticate(username, password)
            if user_data:
                st.session_state.authenticated = True
                st.session_state.user_info = {
                    'id': user_data[0],
                    'username': user_data[1],
                    'nama': user_data[2],
                    'role': user_data[3]
                }
                st.session_state.page = 'dashboard'
                st.success(f"Selamat datang, {user_data[2]}!")
                st.rerun()
            else:
                st.error("Username atau password salah!")
    
    # Demo credentials
    with st.expander("Credential Demo"):
        st.write("**Admin:** username=`admin`, password=`admin123`")
        st.write("**Editor:** username=`user1`, password=`user123`")
        st.write("**Viewer:** username=`user2`, password=`user123`")

# Dashboard
def dashboard():
    st.title("📊 Dashboard")
    
    # User info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"👤 {st.session_state.user_info['nama']}")
    with col2:
        st.info(f"🎯 {st.session_state.user_info['role'].upper()}")
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.session_state.page = 'login'
            st.rerun()
    
    st.markdown("---")
    
    # Quick stats
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM laporan")
    total = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM laporan WHERE status = 'draft'")
    draft = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM laporan WHERE status = 'published'")
    published = c.fetchone()[0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Laporan", total)
    col2.metric("Draft", draft)
    col3.metric("Published", published)
    
    st.markdown("---")
    
    # Create new report button
    if st.session_state.user_info['role'] in ['admin', 'editor']:
        if st.button("📄 Buat Laporan Baru", type="primary"):
            st.session_state.page = 'create_report'
            st.rerun()
    
    # Recent reports
    st.subheader("📋 Laporan Terbaru")
    c.execute('''
        SELECT id, judul, kategori, status, dibuat_oleh, tanggal_dibuat 
        FROM laporan 
        ORDER BY tanggal_dibuat DESC 
        LIMIT 10
    ''')
    reports = c.fetchall()
    
    if reports:
        for report in reports:
            with st.expander(f"{report[1]} ({report[2]})"):
                st.write(f"**Status:** {report[3]}")
                st.write(f"**Dibuat oleh:** {report[4]}")
                st.write(f"**Tanggal:** {report[5]}")
                if st.button("Lihat Detail", key=f"view_{report[0]}"):
                    st.session_state.selected_report = report[0]
                    st.session_state.page = 'view_report'
                    st.rerun()
    else:
        st.info("Belum ada laporan. Buat laporan pertama Anda!")

# Create Report
def create_report():
    st.title("📄 Buat Laporan Baru")
    
    with st.form("report_form"):
        judul = st.text_input("Judul Laporan")
        kategori = st.selectbox("Kategori", ["Proyek", "Meeting", "Bulanan", "Lainnya"])
        konten = st.text_area("Isi Laporan", height=200)
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("💾 Simpan", type="primary")
        with col2:
            if st.form_submit_button("❌ Batal"):
                st.session_state.page = 'dashboard'
                st.rerun()
        
        if submit and judul and konten:
            c = conn.cursor()
            try:
                c.execute('''
                    INSERT INTO laporan (judul, kategori, konten, dibuat_oleh, status)
                    VALUES (?, ?, ?, ?, 'draft')
                ''', (judul, kategori, konten, st.session_state.user_info['username']))
                conn.commit()
                st.success("Laporan berhasil dibuat!")
                st.session_state.page = 'dashboard'
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

# View Report
def view_report():
    st.title("👁️ Detail Laporan")
    
    if 'selected_report' not in st.session_state:
        st.error("Tidak ada laporan yang dipilih")
        st.session_state.page = 'dashboard'
        st.rerun()
        return
    
    c = conn.cursor()
    c.execute('''
        SELECT judul, kategori, konten, status, dibuat_oleh, tanggal_dibuat 
        FROM laporan WHERE id = ?
    ''', (st.session_state.selected_report,))
    
    report = c.fetchone()
    
    if report:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(report[0])
        with col2:
            status_color = "🟢" if report[3] == 'published' else "🟡"
            st.write(f"{status_color} {report[3].upper()}")
        
        st.write(f"**Kategori:** {report[1]}")
        st.write(f"**Dibuat oleh:** {report[4]}")
        st.write(f"**Tanggal:** {report[5]}")
        
        st.markdown("---")
        st.subheader("Konten")
        st.write(report[2])
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Edit Laporan"):
                st.session_state.page = 'edit_report'
                st.rerun()
        with col2:
            if st.button("🔙 Kembali ke Dashboard"):
                st.session_state.page = 'dashboard'
                st.rerun()
    else:
        st.error("Laporan tidak ditemukan")
        st.session_state.page = 'dashboard'
        st.rerun()

# Main App
def main():
    # Check authentication
    if not st.session_state.authenticated:
        login_page()
    else:
        # Sidebar navigation
        with st.sidebar:
            st.title("📋 Menu")
            st.write(f"Halo, **{st.session_state.user_info['nama']}**!")
            st.markdown("---")
            
            pages = {
                "📊 Dashboard": "dashboard",
                "📄 Buat Laporan": "create_report",
                "👥 Kolaborator": "collaborators",
                "⚙️ Pengaturan": "settings"
            }
            
            for page_name, page_key in pages.items():
                if st.button(page_name, key=page_key, use_container_width=True):
                    st.session_state.page = page_key
                    st.rerun()
            
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_info = None
                st.session_state.page = 'login'
                st.rerun()
        
        # Main content area
        if st.session_state.page == 'dashboard':
            dashboard()
        elif st.session_state.page == 'create_report':
            create_report()
        elif st.session_state.page == 'view_report':
            view_report()
        elif st.session_state.page == 'edit_report':
            st.title("✏️ Edit Laporan")
            st.info("Fitur edit akan segera tersedia")
            if st.button("🔙 Kembali"):
                st.session_state.page = 'dashboard'
                st.rerun()
        elif st.session_state.page == 'collaborators':
            st.title("👥 Kelola Kolaborator")
            st.info("Fitur kolaborator akan segera tersedia")
            if st.button("🔙 Kembali"):
                st.session_state.page = 'dashboard'
                st.rerun()
        elif st.session_state.page == 'settings':
            st.title("⚙️ Pengaturan")
            st.info("Fitur pengaturan akan segera tersedia")
            if st.button("🔙 Kembali"):
                st.session_state.page = 'dashboard'
                st.rerun()

if __name__ == "__main__":
    main()
