import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- 1. BANCO DE DADOS (AUTO-REPARÁVEL) ---
def get_db_connection():
    conn = sqlite3.connect('supsmart_pro.db', check_same_thread=False)
    cursor = conn.cursor()
    # Criação das tabelas base
    cursor.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, total REAL, itens_qtd INTEGER, limite REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS itens_detalhes 
                 (compra_id INTEGER, nome TEXT, preco REAL, qtd REAL, cat TEXT, medida TEXT)''')
    
    # REPARO AUTOMÁTICO: Adiciona 'limite' se o banco for antigo
    cursor.execute("PRAGMA table_info(compras)")
    colunas = [row[1] for row in cursor.fetchall()]
    if 'limite' not in colunas:
        cursor.execute("ALTER TABLE compras ADD COLUMN limite REAL DEFAULT 500.0")
    
    conn.commit()
    return conn

conn = get_db_connection()

# --- 2. ESTILO SaaS PROFISSIONAL ---
st.set_page_config(page_title="SupSmart Pro", layout="wide")
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DASHBOARD ---
if 'carrinho' not in st.session_state: st.session_state.carrinho = []

st.title("SupSmart / Dashboard")

# Métricas com dados reais
df_compras = pd.read_sql("SELECT * FROM compras", conn)
total_atual = sum(i['Total'] for i in st.session_state.carrinho)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total no Carrinho", f"R$ {total_atual:.2f}")
col2.metric("Itens", len(st.session_state.carrinho))
col3.metric("Gasto do Mês", f"R$ {df_compras['total'].sum() if not df_compras.empty else 0:.2f}")
col4.metric("Previsão", f"R$ {(df_compras['total'].mean() if not df_compras.empty else 0) * 1.1:.2f}", "-2%")

# --- 4. INTERFACE ---
tab1, tab2 = st.tabs(["🛒 Mercado", "📜 Histórico"])

with tab1:
    c_in, c_list = st.columns([1, 1.5])
    with c_in:
        with st.form("novo_item", clear_on_submit=True):
            nome = st.text_input("Produto")
            med = st.radio("Tipo", ["Un", "Kg"], horizontal=True)
            q, p = st.columns(2)
            qtd = q.number_input("Qtd", min_value=0.01, value=1.0)
            preco = p.number_input("Preço", min_value=0.0, step=0.01)
            cat = st.selectbox("Categoria", ["Alimentos", "Limpeza", "Higiene", "Outros"])
            if st.form_submit_button("Adicionar"):
                if nome and preco > 0:
                    st.session_state.carrinho.append({
                        "Item": nome, "Qtd": qtd, "Preço": preco, 
                        "Total": qtd*preco, "Cat": cat, "Medida": med
                    })
                    st.rerun()
    with c_list:
        if st.session_state.carrinho:
            st.dataframe(pd.DataFrame(st.session_state.carrinho), use_container_width=True)
            if st.button("✅ FINALIZAR COMPRA", type="primary", use_container_width=True):
                cur = conn.cursor()
                agora = datetime.now().strftime("%d/%m/%Y %H:%M")
                cur.execute("INSERT INTO compras (data, total, itens_qtd, limite) VALUES (?, ?, ?, ?)", 
                            (agora, total_atual, len(st.session_state.carrinho), 500.0))
                c_id = cur.lastrowid
                for i in st.session_state.carrinho:
                    cur.execute("INSERT INTO itens_detalhes VALUES (?, ?, ?, ?, ?, ?)", 
                                (c_id, i['Item'], i['Preço'], i['Qtd'], i['Cat'], i['Medida']))
                conn.commit()
                st.session_state.carrinho = []
                st.balloons()
                st.rerun()

with tab2:
    if not df_compras.empty:
        st.dataframe(df_compras.sort_values(by='id', ascending=False), use_container_width=True, hide_index=True)
        id_ver = st.number_input("Ver Detalhes (ID):", min_value=1, step=1)
        if st.button("Buscar"):
            detalhes = pd.read_sql(f"SELECT nome as Item, preco as 'R$', qtd, medida as Tipo FROM itens_detalhes WHERE compra_id = {int(id_ver)}", conn)
            st.table(detalhes) if not detalhes.empty else st.error("ID não encontrado.")