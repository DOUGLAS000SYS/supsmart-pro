import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime

# --- 1. BANCO DE DADOS COM AUTO-FIX ---
def get_db_connection():
    conn = sqlite3.connect('supsmart_pro.db', check_same_thread=False)
    # Garante a criação das tabelas com a estrutura correta
    conn.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, total REAL, itens_qtd INTEGER)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS itens_detalhes 
                 (compra_id INTEGER, nome TEXT, preco REAL, qtd REAL, cat TEXT)''')
    
    # AUTO-FIX: Verifica se a coluna itens_qtd existe (evita o OperationalError)
    try:
        conn.execute("SELECT itens_qtd FROM compras LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("ALTER TABLE compras ADD COLUMN itens_qtd INTEGER DEFAULT 0")
        
    conn.commit()
    return conn

conn = get_db_connection()

# --- 2. UI ADAPTATIVA (SaaS DESIGN) ---
st.set_page_config(page_title="SupSmart Pro", layout="wide")

st.markdown("""
<style>
    @import url('https://rsms.me/inter/inter.css');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Cards que funcionam em qualquer tema */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }
    /* Forçar visibilidade dos textos nas métricas */
    [data-testid="stMetricLabel"] p { color: #888 !important; }
    [data-testid="stMetricValue"] { color: inherit !important; font-weight: 700 !important; }
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
m1.metric("Carrinho", f"R$ {total_carrinho:.2f}")
m2.metric("Itens", len(st.session_state.carrinho))
m3.metric("Gasto Total", f"R$ {gasto_hist:.2f}")
m4.metric("Compras", len(df_compras))

# --- 5. OPERAÇÃO ---
tab_loja, tab_hist = st.tabs(["🛒 Mercado", "📜 Histórico"])

with tab_loja:
    c_in, c_res = st.columns([1, 1.5])
    with c_in:
        with st.form("add_item", clear_on_submit=True):
            nome = st.text_input("Produto")
            q1, q2 = st.columns(2)
            with q1: qtd = st.number_input("Qtd", min_value=0.1, value=1.0)
            with q2: preco = st.number_input("Preço", min_value=0.0, step=0.01)
            cat = st.selectbox("Categoria", ["Alimentos", "Higiene", "Limpeza", "Bebidas", "Outros"])
            if st.form_submit_button("Adicionar"):
                if nome and preco > 0:
                    st.session_state.carrinho.append({"Categoria": cat, "Item": nome, "Qtd": qtd, "Preço Unit": preco, "Total": qtd*preco})
                    st.rerun()

    with c_res:
        if st.session_state.carrinho:
            st.dataframe(pd.DataFrame(st.session_state.carrinho), use_container_width=True, hide_index=True)
            if st.button("✅ FINALIZAR COMPRA", use_container_width=True, type="primary"):
                cur = conn.cursor()
                data_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                cur.execute("INSERT INTO compras (data, total, itens_qtd) VALUES (?, ?, ?)", 
                            (data_str, total_carrinho, len(st.session_state.carrinho)))
                compra_id = cur.lastrowid
                for i in st.session_state.carrinho:
                    cur.execute("INSERT INTO itens_detalhes VALUES (?, ?, ?, ?, ?)", 
                                (compra_id, i['Item'], i['Preço Unit'], i['Qtd'], i['Categoria']))
                conn.commit()
                st.session_state.carrinho = []
                st.balloons()
                st.rerun()
        else:
            st.info("Adicione produtos para começar.")

with tab_hist:
    if not df_compras.empty:
        st.dataframe(df_compras.sort_values(by='id', ascending=False), use_container_width=True, hide_index=True)
        st.write("---")
        id_ver = st.number_input("Ver detalhes da compra (ID):", min_value=1, step=1)
        if st.button("Ver Itens"):
            detalhes = pd.read_sql(f"SELECT nome, preco, qtd FROM itens_detalhes WHERE compra_id = {id_ver}", conn)
            st.table(detalhes) if not detalhes.empty else st.warning("ID não encontrado.")
    else:
        st.info("Nenhuma compra salva.")