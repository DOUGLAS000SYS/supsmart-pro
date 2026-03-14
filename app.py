import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- 1. BANCO DE DADOS (CONEXÃO SEGURA) ---
def get_db_connection():
    conn = sqlite3.connect('supsmart_pro.db', check_same_thread=False)
    cursor = conn.cursor()
    # Tabela principal de compras
    cursor.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, total REAL, itens_qtd INTEGER)''')
    # Tabela de detalhes dos itens
    cursor.execute('''CREATE TABLE IF NOT EXISTS itens_detalhes 
                 (compra_id INTEGER, nome TEXT, preco REAL, qtd REAL, cat TEXT, medida TEXT)''')
    conn.commit()
    return conn

conn = get_db_connection()

# --- 2. DESIGN ADAPTATIVO (DARK MODE FRIENDLY) ---
st.set_page_config(page_title="SupSmart Pro", layout="wide", page_icon="🛒")

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

# --- 3. ESTADO DO CARRINHO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- 4. DASHBOARD ---
st.title("SupSmart / Dashboard")

# Carregar dados para as métricas
try:
    df_compras = pd.read_sql("SELECT * FROM compras", conn)
except:
    df_compras = pd.DataFrame(columns=['id', 'data', 'total', 'itens_qtd'])

total_carrinho = sum(i['Total'] for i in st.session_state.carrinho)
gasto_total = df_compras['total'].sum() if not df_compras.empty else 0.0

m1, m2, m3 = st.columns(3)
m1.metric("No Carrinho", f"R$ {total_carrinho:.2f}")
m2.metric("Itens", len(st.session_state.carrinho))
m3.metric("Total Histórico", f"R$ {gasto_total:.2f}")

tab_mercado, tab_historico = st.tabs(["🛒 Mercado", "📜 Histórico"])

with tab_mercado:
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        with st.form("form_item", clear_on_submit=True):
            st.subheader("Adicionar Produto")
            nome = st.text_input("Nome do Item")
            tipo = st.radio("Tipo", ["Un", "Kg"], horizontal=True)
            c_q, c_p = st.columns(2)
            qtd = c_q.number_input("Qtd/Peso", min_value=0.01, value=1.0)
            preco = c_p.number_input("Preço", min_value=0.0, step=0.01)
            cat = st.selectbox("Categoria", ["Alimentos", "Higiene", "Limpeza", "Bebidas", "Outros"])
            
            if st.form_submit_button("Adicionar ao Carrinho"):
                if nome and preco > 0:
                    st.session_state.carrinho.append({
                        "Item": nome, "Qtd": qtd, "Preço": preco, 
                        "Total": qtd * preco, "Medida": tipo, "Cat": cat
                    })
                    st.rerun()

    with col2:
        st.subheader("Itens no Carrinho")
        if st.session_state.carrinho:
            df_atual = pd.DataFrame(st.session_state.carrinho)
            st.dataframe(df_atual, use_container_width=True, hide_index=True)
            
            if st.button("✅ FINALIZAR E SALVAR COMPRA", type="primary", use_container_width=True):
                cur = conn.cursor()
                agora = datetime.now().strftime("%d/%m/%Y %H:%M")
                # Salva a compra principal
                cur.execute("INSERT INTO compras (data, total, itens_qtd) VALUES (?, ?, ?)", 
                            (agora, total_carrinho, len(st.session_state.carrinho)))
                compra_id = cur.lastrowid
                # Salva os itens detalhados
                for i in st.session_state.carrinho:
                    cur.execute("INSERT INTO itens_detalhes VALUES (?, ?, ?, ?, ?, ?)", 
                                (compra_id, i['Item'], i['Preço'], i['Qtd'], i['Cat'], i['Medida']))
                conn.commit()
                st.session_state.carrinho = []
                st.balloons()
                st.rerun()
        else:
            st.info("O carrinho está vazio.")

with tab_historico:
    st.subheader("Lista de Compras Salvas")
    if not df_compras.empty:
        st.dataframe(df_compras.sort_values(by='id', ascending=False), use_container_width=True, hide_index=True)
        st.divider()
        st.subheader("🔍 Detalhes da Compra")
        id_busca = st.number_input("Digite o ID da compra para ver os itens:", min_value=1, step=1)
        if st.button("Ver Itens"):
            detalhes = pd.read_sql(f"SELECT nome as Item, preco as 'Preço', qtd as Qtd, medida as Tipo FROM itens_detalhes WHERE compra_id = {int(id_busca)}", conn)
            if not detalhes.empty:
                st.table(detalhes)
            else:
                st.warning(f"Nenhum item encontrado para o ID {id_busca}.")
    else:
        st.info("Ainda não há compras no histórico.")