import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
import urllib.parse

# --- 1. BANCO DE DATOS (CONEXÃO RESILIENTE) ---
def get_db_connection():
    conn = sqlite3.connect('supsmart_pro.db', check_same_thread=False)
    # Garante que as tabelas existam com a estrutura correta
    conn.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  data TEXT, 
                  total REAL, 
                  itens_qtd INTEGER)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS itens_detalhes 
                 (compra_id INTEGER, 
                  nome TEXT, 
                  preco REAL, 
                  qtd REAL, 
                  cat TEXT)''')
    conn.commit()
    return conn

conn = get_db_connection()

# --- 2. UI ADAPTATIVA (SaaS DESIGN SYSTEM) ---
st.set_page_config(page_title="SupSmart Pro", layout="wide", page_icon="✨")

st.markdown("""
<style>
    @import url('https://rsms.me/inter/inter.css');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Cards Glassmorphism - Funcionam em Dark e Light Mode */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        padding: 15px !important;
        border-radius: 12px !important;
    }
    
    /* Correção de visibilidade das métricas */
    [data-testid="stMetricValue"] { font-weight: 700 !important; }
    [data-testid="stMetricLabel"] p { color: #888 !important; font-size: 0.9rem !important; }

    /* Estilização de botões */
    .stButton>button { border-radius: 8px; font-weight: 600; transition: 0.2s; }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE ESTADO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- 4. MÉTRICAS DO DASHBOARD ---
st.title("SupSmart / Dashboard")

# Carregamento seguro dos dados para as métricas
try:
    df_compras = pd.read_sql("SELECT * FROM compras", conn)
except:
    df_compras = pd.DataFrame(columns=['id', 'data', 'total', 'itens_qtd'])

total_carrinho = sum(i['Total'] for i in st.session_state.carrinho)
gasto_historico = df_compras['total'].sum() if not df_compras.empty else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("No Carrinho", f"R$ {total_carrinho:.2f}")
m2.metric("Itens Atuais", len(st.session_state.carrinho))
m3.metric("Gasto Histórico", f"R$ {gasto_historico:.2f}")
m4.metric("Compras", len(df_compras))

st.write("##")

# --- 5. NAVEGAÇÃO POR ABAS ---
tab_atual, tab_hist, tab_analise = st.tabs(["🛒 Compra Atual", "📜 Histórico de Listas", "📈 Insights"])

# ABA: COMPRA ATUAL
with tab_atual:
    col_in, col_res = st.columns([1, 1.5])
    
    with col_in:
        with st.container(border=True):
            st.subheader("Adicionar Item")
            with st.form("form_add", clear_on_submit=True):
                nome = st.text_input("Produto")
                c1, c2 = st.columns(2)
                with c1: qtd = st.number_input("Qtd/Peso", min_value=0.01, value=1.0)
                with c2: preco = st.number_input("Preço Unit.", min_value=0.0, step=0.01)
                cat = st.selectbox("Categoria", ["Alimentos", "Higiene", "Limpeza", "Bebidas", "Outros"])
                
                if st.form_submit_button("Adicionar ao Carrinho"):
                    if nome and preco > 0:
                        st.session_state.carrinho.append({
                            "Categoria": cat, "Item": nome, "Qtd": qtd, "Preço Unit": preco, "Total": qtd*preco
                        })
                        st.rerun()

    with col_res:
        with st.container(border=True):
            st.subheader("Carrinho")
            if st.session_state.carrinho:
                df_temp = pd.DataFrame(st.session_state.carrinho)
                st.dataframe(df_temp, use_container_width=True, hide_index=True)
                
                if st.button("✅ FINALIZAR E SALVAR COMPRA", type="primary", use_container_width=True):
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
                
                # Botão para limpar carrinho sem salvar
                if st.button("🗑️ Limpar Lista"):
                    st.session_state.carrinho = []
                    st.rerun()
            else:
                st.info("O carrinho está vazio.")

# ABA: HISTÓRICO
with tab_hist:
    st.subheader("Listas Finalizadas")
    if not df_compras.empty:
        st.dataframe(df_compras.sort_values(by='id', ascending=False), use_container_width=True, hide_index=True)
        
        st.write("---")
        st.subheader("🔍 Detalhes da Compra")
        id_busca = st.number_input("ID da Compra:", min_value=1, step=1)
        if st.button("Ver Itens Comprados"):
            detalhes = pd.read_sql(f"SELECT nome as Item, preco as 'R$', qtd as Qtd, cat as Categoria FROM itens_detalhes WHERE compra_id = {id_busca}", conn)
            if not detalhes.empty:
                st.table(detalhes)
            else:
                st.warning("Nenhum item encontrado para este ID.")
    else:
        st.info("Nenhuma compra salva no histórico.")

# ABA: INSIGHTS
with tab_analise:
    if not df_compras.empty:
        fig = px.area(df_compras, x="data", y="total", title="Histórico de Gastos (R$)", markers=True)
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Dados insuficientes para gerar gráficos.")