import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "banco_dados.db")

def create_table_if_not_exists():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnpj TEXT UNIQUE NOT NULL,
            razao_social TEXT,
            form_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_client_data(cnpj, razao_social, data_dict):
    create_table_if_not_exists()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    form_data_json = json.dumps(data_dict, ensure_ascii=False)
    
    cursor.execute('''
        INSERT INTO clients (cnpj, razao_social, form_data, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(cnpj) DO UPDATE SET
            razao_social=excluded.razao_social,
            form_data=excluded.form_data,
            updated_at=CURRENT_TIMESTAMP
    ''', (cnpj, razao_social, form_data_json))
    
    conn.commit()
    conn.close()

def load_client_data(cnpj):
    create_table_if_not_exists()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT form_data FROM clients WHERE cnpj = ?', (cnpj,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return json.loads(row[0])
    return None

def get_all_saved_cnpjs():
    create_table_if_not_exists()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT cnpj, razao_social FROM clients ORDER BY updated_at DESC')
    rows = cursor.fetchall()
    
    conn.close()
    return rows
