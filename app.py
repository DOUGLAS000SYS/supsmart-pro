import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import urllib.parse
from datetime import datetime, timedelta, timezone

# --- 1. CONFIGURAÇÃO VISUAL PREMIUM ---
st.set_page_config(page_title="SupSmart Pro", page_icon="🛒", layout="wide", initial_sidebar_state="collapsed")

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.9)), 
                    url("https://raw.githubusercontent.com/DOUGLAS000SYS/supsmart-pro/main/image_290a27.jpg");
        background-size: cover; background-position: center;
    }}
    #MainMenu, footer, header {{visibility: hidden;}}
    .stButton>button {{
        background: linear-gradient(90deg, #2ecc71, #27ae60);
        color: white; border: none; border-radius: 10px; padding: 15px; font-weight: bold; width: 100%;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 2. CONEXÃO NUVEM (SUPABASE) ---
def get_db_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS compras (id SERIAL PRIMARY KEY, data TEXT, total REAL, itens_qtd INTEGER, limite REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS itens_detalhes (compra_id INTEGER, nome TEXT, preco REAL, qtd REAL, cat TEXT, medida TEXT)")
    conn.commit()
    cur.close() ; conn.close()

# --- 3. TELA DE ENTRADA ---
if 'logado' not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<br><br><h1 style='text-align: center; color: white;'>SupSmart Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: white;'>Transforme suas compras em uma experiência inteligente.</p>", unsafe_allow_html=True)
        if st.button("🚀 COMEÇAR AGORA GRÁTIS"):
            init_db()
            st.session_state.logado = True
            st.rerun()
    st.stop()

# --- 4. DASHBOARD (O APP EM SI) ---
st.title("🛒 Dashboard")
# ... (O resto da sua lógica de adicionar itens vai aqui)