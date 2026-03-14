import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- 1. BANCO DE DADOS (AUTO-REPARÁVEL) ---
def get_db_connection():
    conn = sqlite3.connect('supsmart_pro.db', check_same_thread=False)
    # Criação das tabelas base
    conn.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, total REAL, itens_qtd INTEGER)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS itens_detalhes 
                 (compra_id INTEGER, nome TEXT, preco REAL, qtd REAL, cat TEXT, medida TEXT)''')
    
    # REPARO AUTOMÁTICO: Adiciona colunas se elas não existirem
    cursor = conn.cursor()
    colunas_compras = [row[1] for row in cursor.execute("PRAGMA table_info(compras)")]
    if 'itens_qtd' not in colunas_compras:
        cursor.execute("ALTER TABLE compras ADD COLUMN itens_qtd INTEGER DEFAULT 0")
        
    colunas_detalhes = [row[1] for row in cursor.execute("PRAGMA table_info(itens_detalhes)")]
    if 'medida' not in colunas_detalhes:
        cursor.execute("ALTER TABLE itens_detalhes ADD COLUMN medida TEXT DEFAULT 'Un'")
        
    conn.commit()
    return conn

conn = get_db_connection()

# --- 2. ESTILO ADAPTATIVO (NUBANK/LINEAR STYLE) ---
st.set_page_config(page_title="SupSmart Pro", layout="wide")

st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }
    [data-testid="stMetricLabel"] p { color: #888 !important; }
    [data-testid="stMetricValue"] { font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGICA DO APP ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

st.title("SupSmart / Dashboard")

# Métricas
df_compras = pd.read_sql("SELECT * FROM compras", conn)
total_carrinho = sum(i['Total'] for i in st.session_state.carrinho)
m1, m2, m3 = st.columns(3)
m1.metric("No Carrinho", f"R$ {total_carrinho:.2f}")
m2.metric("Itens", len(st.session_state.carrinho))
m3.metric("Gasto Total", f"R$ {df_compras['total'].sum() if not df_compras.empty else 0:.2f}")

tab_loja, tab_hist = st.tabs(["🛒 Mercado", "📜 Histórico"])

with tab_loja:
    c1, c2 = st.columns([1, 1.5])
    with c1:
        with st.form("add_item", clear_on_submit=True):
            nome = st.text_input("Produto")
            medida = st.radio("Tipo", ["Un", "Kg"], horizontal=True)
            col_a, col_b = st.columns(2)
            qtd = col_a.number_input("Qtd", min_value=0.01, value=1.0)
            preco = col_b.number_input("Preço", min_value=0.0, step=0.01)
            if st.form_submit_button("Adicionar"):
                if nome and preco > 0:
                    st.session_state.carrinho.append({
                        "Item": nome, "Qtd": qtd, "Preço": preco, 
                        "Total": qtd*preco, "Medida": medida, "Cat": "Geral"
                    })
                    st.rerun()
    with c2:
        if st.session_state.carrinho:
            st.dataframe(pd.DataFrame(st.session_state.carrinho), use_container_width=True)
            if st.button("✅ FINALIZAR COMPRA", type="primary", use_container_width=True):
                cur = conn.cursor()
                dt = datetime.now().strftime("%d/%m/%Y %H:%M")
                cur.execute("INSERT INTO compras (data, total, itens_qtd) VALUES (?, ?, ?)", (dt, total_carrinho, len(st.session_state.carrinho)))
                c_id = cur.lastrowid
                for i in st.session_state.carrinho:
                    cur.execute("INSERT INTO itens_detalhes VALUES (?, ?, ?, ?, ?, ?)", (c_id, i['Item'], i['Preço'], i['Qtd'], i['Cat'], i['Medida']))
                conn.commit()
                st.session_state.carrinho = []
                st.balloons()
                st.rerun()

with tab_hist:
    if not df_compras.empty:
        st.dataframe(df_compras.sort_values(by='id', ascending=False), use_container_width=True, hide_index=True)
        st.divider()
        id_ver = st.number_input("Ver Detalhes (ID):", min_value=1, step=1)
        if st.button("Buscar Itens"):
            detalhes = pd.read_sql(f"SELECT nome, preco, qtd, medida FROM itens_detalhes WHERE compra_id = {id_ver}", conn)
            if not detalhes.empty:
                st.table(detalhes)
            else:
                st.error("ID não encontrado.")