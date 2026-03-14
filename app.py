import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- 1. BANCO DE DADOS (AUTO-REPARO INTEGRADO) ---
def get_db_connection():
    conn = sqlite3.connect('supsmart_pro.db', check_same_thread=False)
    cursor = conn.cursor()
    # Tabelas base
    cursor.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, total REAL, itens_qtd INTEGER, limite REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS itens_detalhes 
                 (compra_id INTEGER, nome TEXT, preco REAL, qtd REAL, cat TEXT, medida TEXT)''')
    
    # Adição automática de colunas faltantes para evitar OperationalError
    cursor.execute("PRAGMA table_info(compras)")
    colunas = [row[1] for row in cursor.fetchall()]
    if 'limite' not in colunas:
        cursor.execute("ALTER TABLE compras ADD COLUMN limite REAL DEFAULT 0.0")
    
    conn.commit()
    return conn

conn = get_db_connection()

# --- 2. UX & MELHORIAS VISUAIS (SaaS MODERN) ---
st.set_page_config(page_title="SupSmart Pro", layout="wide", page_icon="🛒")

# CSS para cards estilo "Glassmorphism" e métricas legíveis
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 700 !important; }
    .main { background-color: #0e1117; }
</style>
""", unsafe_allow_html=True)

# --- 3. INTELIGÊNCIA DE DADOS & ESTADO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

st.title("SupSmart / Dashboard")

# Busca dados para Inteligência de Dados
df_hist = pd.read_sql("SELECT * FROM compras", conn)
total_carrinho = sum(i['Total'] for i in st.session_state.carrinho)

# Métricas Estilo SaaS
m1, m2, m3, m4 = st.columns(4)
m1.metric("🛒 No Carrinho", f"R$ {total_carrinho:.2f}")
m2.metric("📦 Itens", len(st.session_state.carrinho))
m3.metric("💰 Total Gasto", f"R$ {df_hist['total'].sum() if not df_hist.empty else 0:.2f}")

# Inteligência: Previsão baseada na média (Feature SaaS)
media = df_hist['total'].mean() if not df_hist.empty else 0
m4.metric("📈 Previsão Próxima", f"R$ {media * 1.05:.2f}", help="Baseado no seu histórico + 5% de inflação estimada")

# --- 4. NOVAS FUNCIONALIDADES ---
tab_loja, tab_hist = st.tabs(["🛒 Mercado", "📊 Análise de Gastos"])

with tab_loja:
    c1, c2 = st.columns([1, 1.5])
    with c1:
        with st.form("form_add", clear_on_submit=True):
            st.subheader("Adicionar Item")
            nome = st.text_input("Produto")
            tipo = st.radio("Unidade", ["Un", "Kg"], horizontal=True)
            col_a, col_b = st.columns(2)
            qtd = col_a.number_input("Qtd", min_value=0.01, value=1.0)
            preco = col_b.number_input("Preço", min_value=0.0, step=0.01)
            cat = st.selectbox("Categoria", ["Alimentos", "Limpeza", "Higiene", "Bebidas", "Outros"])
            
            if st.form_submit_button("Adicionar ao Carrinho", use_container_width=True):
                if nome and preco > 0:
                    # Alinhamento do dicionário para evitar KeyError
                    st.session_state.carrinho.append({
                        "Item": nome, "Qtd": qtd, "Preço": preco, 
                        "Total": qtd*preco, "Cat": cat, "Medida": tipo
                    })
                    st.rerun()

    with c2:
        if st.session_state.carrinho:
            st.dataframe(pd.DataFrame(st.session_state.carrinho), use_container_width=True, hide_index=True)
            if st.button("✅ FINALIZAR COMPRA", type="primary", use_container_width=True):
                cur = conn.cursor()
                dt = datetime.now().strftime("%d/%m/%Y %H:%M")
                cur.execute("INSERT INTO compras (data, total, itens_qtd) VALUES (?, ?, ?)", 
                            (dt, total_carrinho, len(st.session_state.carrinho)))
                compra_id = cur.lastrowid
                for i in st.session_state.carrinho:
                    cur.execute("INSERT INTO itens_detalhes VALUES (?, ?, ?, ?, ?, ?)", 
                                (compra_id, i['Item'], i['Preço'], i['Qtd'], i['Cat'], i['Medida']))
                conn.commit()
                st.session_state.carrinho = []
                st.balloons()
                st.rerun()

with tab_hist:
    if not df_hist.empty:
        st.subheader("Histórico de Compras")
        st.dataframe(df_hist.sort_values(by='id', ascending=False), use_container_width=True, hide_index=True)
        
        st.divider()
        id_ver = st.number_input("Detalhes da Compra (ID):", min_value=1, step=1)
        if st.button("Ver Itens"):
            detalhes = pd.read_sql(f"SELECT nome, preco, qtd, medida FROM itens_detalhes WHERE compra_id = {int(id_ver)}", conn)
            if not detalhes.empty:
                # Correção do erro da imagem image_b5b048: st.table fora de expressões lógicas puras
                st.table(detalhes)
            else:
                st.error("Compra não encontrada.")