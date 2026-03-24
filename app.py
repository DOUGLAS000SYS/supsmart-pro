import streamlit as st

# --- DESIGN STARTUP ---
st.set_page_config(page_title="SupSmart Pro", page_icon="🛒", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.8)), 
        url("https://raw.githubusercontent.com/DOUGLAS000SYS/supsmart-pro/main/image_290a27.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .stButton>button {
        background: linear-gradient(90deg, #2ecc71, #27ae60) !important;
        color: white !important;
        border: none !important;
        height: 3em !important;
        width: 100% !important;
        font-weight: bold !important;
    }
    h1, p {color: white !important; text-align: center;}
    </style>
""", unsafe_allow_html=True)

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
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)), 
        url("https://raw.githubusercontent.com/DOUGLAS000SYS/supsmart-pro/dev/image_290a27.jpg");
        background-size: cover; 
        background-position: center;
        background-attachment: fixed;
    }
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}
    </style>
""", unsafe_allow_html=True)

# 4. DASHBOARD
st.title("🛒 Dashboard Profissional")
st.success("Conectado ao Supabase!")
# O resto do seu código de itens entra aqui...