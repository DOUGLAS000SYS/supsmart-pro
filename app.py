import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
import urllib.parse

# --- 1. BANCO DE DATOS (A MENTE DO APP) ---
def init_db():
    conn = sqlite3.connect('supsmart_data.db')
    c = conn.cursor()
    # Tabela de Compras Finalizadas
    c.execute('''CREATE TABLE IF NOT EXISTS historico 
                 (id INTEGER PRIMARY KEY, data TEXT, total REAL, itens INTEGER)''')
    # Tabela de Inteligência de Preços (Média por item)
    c.execute('''CREATE TABLE IF NOT EXISTS precos_brutos 
                 (produto TEXT, preco_unit REAL, data TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- 2. CONFIGURAÇÃO DE UI (ESTILO APPLE DASHBOARD) ---
st.set_page_config(page_title="SupSmart Pro", layout="wide")

st.markdown("""
<style>
    .main { background-color: #F2F4F7; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; color: #1E1E1E; }
    .stDataFrame { background-color: white; border-radius: 10px; }
    .block-container { padding-top: 2rem; }
    .stButton>button { border-radius: 8px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE NEGÓCIO ---
if 'carrinho' not in st.session_state: st.session_state.carrinho = []

def salvar_compra(total, lista_itens):
    c = conn.cursor()
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    # Salva no histórico geral
    c.execute("INSERT INTO historico (data, total, itens) VALUES (?, ?, ?)", 
              (data_hoje, total, len(lista_itens)))
    # Salva cada preço para inteligência futura
    for item in lista_itens:
        c.execute("INSERT INTO precos_brutos (produto, preco_unit, data) VALUES (?, ?, ?)",
                  (item['nome'], item['preco'], data_hoje))
    conn.commit()

def buscar_media(produto):
    df_p = pd.read_sql(f"SELECT AVG(preco_unit) as media FROM precos_brutos WHERE produto='{produto}'", conn)
    return df_p['media'].iloc[0] if not df_p.empty else None

# --- 4. DASHBOARD (O "AGORA") ---
st.title("📊 SupSmart Dashboard")

total_carrinho = sum(i['valor'] for i in st.session_state.carrinho)
df_hist = pd.read_sql("SELECT * FROM historico", conn)
gasto_mensal = df_hist['total'].sum() if not df_hist.empty else 0.0

m1, m2, m3 = st.columns(3)
m1.metric("Total Atual", f"R$ {total_carrinho:.2f}")
m2.metric("Itens no Carrinho", len(st.session_state.carrinho))
m3.metric("Gasto Acumulado", f"R$ {gasto_mensal:.2f}", delta=f"{len(df_hist)} Compras")

st.divider()

# --- 5. OPERAÇÃO EM COLUNAS ---
col_add, col_list = st.columns([1, 1.5])

with col_add:
    st.subheader("➕ Novo Item")
    with st.form("input_form", clear_on_submit=True):
        nome = st.text_input("Nome do Produto (Ex: Arroz)")
        c1, c2 = st.columns(2)
        with c1: qtd = st.number_input("Qtd", min_value=0.01, value=1.0)
        with c2: preco = st.number_input("Preço Unitário", min_value=0.0, step=0.01)
        cat = st.selectbox("Categoria", ["Alimentos", "Limpeza", "Higiene", "Bebidas", "Outros"])
        
        # Inteligência de Preço Instantânea
        if nome:
            media = buscar_media(nome)
            if media and preco > 0:
                diff = ((preco - media) / media) * 100
                if diff > 5: st.error(f"⚠️ {diff:.1f}% mais caro que a sua média!")
                elif diff < -5: st.success(f"✅ {abs(diff):.1f}% mais barato que a média!")
        
        if st.form_submit_button("ADICIONAR"):
            if nome and preco > 0:
                st.session_state.carrinho.append({"nome": nome, "preco": preco, "qtd": qtd, "valor": qtd*preco, "cat": cat})
                st.rerun()

with col_list:
    st.subheader("📝 Itens na Lista")
    if st.session_state.carrinho