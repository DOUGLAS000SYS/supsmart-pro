import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime

# --- 1. BANCO DE DADOS (VERSÃO ROBUSTA) ---
def get_db_connection():
    conn = sqlite3.connect('supsmart_pro.db', check_same_thread=False)
    # Criar tabelas com estrutura final
    conn.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, total REAL, itens_qtd INTEGER)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS itens_detalhes 
                 (compra_id INTEGER, nome TEXT, preco REAL, qtd REAL, cat TEXT, medida TEXT)''')
    
    # Auto-fix para garantir que a coluna itens_qtd existe
    try:
        conn.execute("SELECT itens_qtd FROM compras LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("ALTER TABLE compras ADD COLUMN itens_qtd INTEGER DEFAULT 0")
    conn.commit()
    return conn

conn = get_db_connection()

# --- 2. UI/UX (SaaS DARK/LIGHT ADAPTIVE) ---
st.set_page_config(page_title="SupSmart Pro", layout="wide", page_icon="🛒")

st.markdown("""
<style>
    @import url('https://rsms.me/inter/inter.css');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Cards Adaptativos */
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

# --- 3. GESTÃO DE ESTADO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- 4. DASHBOARD ---
st.title("SupSmart / Dashboard")

try:
    df_compras = pd.read_sql("SELECT * FROM compras", conn)
except:
    df_compras = pd.DataFrame(columns=['id', 'data', 'total', 'itens_qtd'])

total_carrinho = sum(i['Total'] for i in st.session_state.carrinho)
gasto_hist = df_compras['total'].sum() if not df_compras.empty else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("No Carrinho", f"R$ {total_carrinho:.2f}")
m2.metric("Itens", len(st.session_state.carrinho))
m3.metric("Gasto Acumulado", f"R$ {gasto_hist:.2f}")
m4.metric("Total Listas", len(df_compras))

# --- 5. NAVEGAÇÃO ---
tab_loja, tab_hist = st.tabs(["🛒 Calculadora Mercado", "📜 Histórico de Gastos"])

with tab_loja:
    c_in, c_res = st.columns([1, 1.5])
    
    with c_in:
        with st.form("form_mercado", clear_on_submit=True):
            st.subheader("Novo Item")
            nome = st.text_input("Produto")
            
            # Opção Unidade ou Kg
            medida = st.radio("Medida", ["Un", "Kg"], horizontal=True)
            
            c1, c2 = st.columns(2)
            with c1: 
                qtd = st.number_input("Qtd/Peso", min_value=0.01, value=1.00, step=0.01)
            with c2: 
                preco = st.number_input("Preço Unit/Kg", min_value=0.0, step=0.01)
                
            cat = st.selectbox("Categoria", ["Alimentos", "Açougue", "Higiene", "Limpeza", "Bebidas", "Outros"])
            
            if st.form_submit_button("Adicionar Item"):
                if nome and preco > 0:
                    st.session_state.carrinho.append({
                        "Categoria": cat, "Item": nome, "Qtd": qtd, 
                        "Medida": medida, "Preço": preco, "Total": qtd * preco
                    })
                    st.rerun()

    with c_res:
        st.subheader("Lista Atual")
        if st.session_state.carrinho:
            df_atual = pd.DataFrame(st.session_state.carrinho)
            st.dataframe(df_atual, use_container_width=True, hide_index=True)
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("✅ FINALIZAR COMPRA", use_container_width=True, type="primary"):
                    cur = conn.cursor()
                    data_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                    cur.execute("INSERT INTO compras (data, total, itens_qtd) VALUES (?, ?, ?)", 
                                (data_str, total_carrinho, len(st.session_state.carrinho)))
                    compra_id = cur.lastrowid
                    for i in st.session_state.carrinho:
                        cur.execute("INSERT INTO itens_detalhes VALUES (?, ?, ?, ?, ?, ?)", 
                                    (compra_id, i['Item'], i['Preço'], i['Qtd'], i['Categoria'], i['Medida']))
                    conn.commit()
                    st.session_state.carrinho = []
                    st.balloons()
                    st.rerun()
            with col_b2:
                if st.button("🗑️ LIMPAR", use_container_width=True):
                    st.session_state.carrinho = []
                    st.rerun()
        else:
            st.info("Adicione itens para ver o total.")

with tab_hist:
    st.subheader("Compras Passadas")
    if not df_compras.empty:
        st.dataframe(df_compras.sort_values(by='id', ascending=False), use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("🔍 Detalhes da Compra")
        id_ver = st.number_input("ID da compra:", min_value=1, step=1)
        
        if st.button("Ver Detalhes"):
            detalhes = pd.read_sql(f"SELECT nome, preco, qtd, medida, cat FROM itens_detalhes WHERE compra_id = {id_ver}", conn)
            if not detalhes.empty:
                st.table(detalhes)
            else:
                st.warning("ID não encontrado no histórico.")
    else:
        st.info("Nenhuma compra salva até o momento.")