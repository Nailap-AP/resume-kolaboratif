# utils/data_handler.py
import json
import os
import pandas as pd
from datetime import datetime

DATA_FILE = "data/research_data.json"

def load_research_data():
    """Memuat data penelitian dari file JSON"""
    try:
        # Coba baca dari file lokal
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        else:
            # Jika file tidak ada, buat file kosong
            os.makedirs("data", exist_ok=True)
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
            return []
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

def save_research_data(data):
    """Menyimpan data penelitian ke file JSON"""
    try:
        # Pastikan direktori ada
        os.makedirs("data", exist_ok=True)
        
        # Simpan ke file
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Juga buat backup dengan timestamp
        backup_file = f"data/research_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def export_to_csv(data, filename="research_export.csv"):
    """Ekspor data ke format CSV"""
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False

def import_from_json(file_path):
    """Impor data dari file JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error importing data: {e}")
        return None
