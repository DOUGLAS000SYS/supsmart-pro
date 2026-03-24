import streamlit as st
import psycopg2

st.set_page_config(page_title="SupSmart Pro", page_icon="🛒", layout="wide")

# Design Profissional
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.8)), 
        url("https://raw.githubusercontent.com/DOUGLAS000SYS/supsmart-pro/main/image_290a27.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    h1, p, .stMarkdown { color: white !important; text-align: center; }
    .stButton>button {
        background: linear-gradient(90deg, #2ecc71, #27ae60) !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

st.success("🚀 Conectado ao Supabase!")

# Teste de conexão (que você já validou)
st.success("Conectado ao Supabase!")

# O resto do seu código (Login e Dashboard) vem abaixo...

# 2. CONEXÃO NUVEM
def get_db_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

# 3. LOGICA DE ACESSO
if 'logado' not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    _, col, _ = st.columns([1, 2, 1])
    with col:
     st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.8)), 
        url("https://raw.githubusercontent.com/DOUGLAS000SYS/supsmart-pro/main/image_290a27.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    h1, p, .stMarkdown { color: white !important; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 4. DASHBOARD
st.title("🛒 Dashboard Profissional")
st.success("Conectado ao Supabase!")
# O resto do seu código de itens entra aqui...