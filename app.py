import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
import urllib.parse

# --- 1. BANCO DE DADOS (A MENTE DO APP) ---
def init_db():
    conn = sqlite3.connect('supsmart_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS historico 
                 (id INTEGER PRIMARY KEY, data TEXT, total REAL, itens INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS precos_brutos 
                 (produto TEXT, preco_unit REAL, data TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- 2. CONFIGURAÇÃO DE UI (ESTILO DASHBOARD PROFISSIONAL) ---
st.set_page_config(page_title="SupSmart Pro", layout="wide", page_icon="📊")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F8F9FA; color: #333; }
    
    /* Input Style Correction */
    input, select, textarea { color: #333 !important; background-color: white !important; }
    label { color: #2C3E50 !important; font-weight: bold !important; }

    .metric-card {
        background: white; padding: 20px; border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center;
        border: 1px solid #EEE;
    }
    .stButton>button {
        border-radius: 10px; height: 3.5em; font-weight: bold; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE DADOS ---
if 'carrinho' not in st.session_state: st.session_state.carrinho = []

def salvar_compra(total, lista_itens):
    c = conn.cursor()
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.execute("INSERT INTO historico (data, total, itens) VALUES (?, ?, ?)", 
              (data_hoje, total, len(lista_itens)))
    for item in lista_itens:
        c.execute("INSERT INTO precos_brutos (produto, preco_unit, data) VALUES (?, ?, ?)",
                  (item['nome'], item['preco'], data_hoje))
    conn.commit()

def buscar_media(produto):
    query = f"SELECT AVG(preco_unit) as media FROM precos_brutos WHERE produto=?"
    df_p = pd.read_sql(query, conn, params=(produto,))
    return df_p['media'].iloc[0] if not df_p.empty else None

# --- 4. DASHBOARD SUPERIOR ---
st.title("📊 SupSmart Pro")
st.caption("Controle de Mercado & Inteligência de Preços")

total_carrinho = sum(i['valor'] for i in st.session_state.carrinho)
df_hist = pd.read_sql("SELECT * FROM historico", conn)
gasto_total = df_hist['total'].sum() if not df_hist.empty else 0.0

m1, m2, m3, m4 = st.columns(4)
with m1: st.markdown(f'<div class="metric-card"><small>CARRINHO</small><br><h2 style="color:#2ECC71;">R$ {total_carrinho:.2f}</h2></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="metric-card"><small>ITENS</small><br><h2>{len(st.session_state.carrinho)}</h2></div>', unsafe_allow_html=True)
with m3: st.markdown(f'<div class="metric-card"><small>HISTÓRICO</small><br><h2 style="color:#3498DB;">R$ {gasto_total:.2f}</h2></div>', unsafe_allow_html=True)
with m4: st.markdown(f'<div class="metric-card"><small>COMPRAS</small><br><h2>{len(df_hist)}</h2></div>', unsafe_allow_html=True)

st.write("---")

# --- 5. OPERAÇÃO (CARRINHO E ANÁLISE) ---
col_add, col_list = st.columns([1, 1.5])

with col_add:
    st.subheader("➕ Adicionar Item")
    with st.form("input_form", clear_on_submit=True):
        nome = st.text_input("Produto (Ex: Arroz)")
        c1, c2 = st.columns(2)
        with c1: qtd = st.number_input("Qtd/Peso", min_value=0.01, value=1.0)
        with c2: preco = st.number_input("Preço Unit/Kg", min_value=0.0, step=0.01)
        cat = st.selectbox("Categoria", ["Alimentos", "Limpeza", "Higiene", "Bebidas", "Outros"])
        
        if nome:
            media = buscar_media(nome)
            if media and preco > 0:
                diff = ((preco - media) / media) * 100
                if diff > 5: st.warning(f"⚠️ {diff:.1f}%