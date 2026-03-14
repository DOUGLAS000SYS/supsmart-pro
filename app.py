import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
import urllib.parse

# --- 1. BANCO DE DADOS (PERSISTÊNCIA REAL) ---
def init_db():
    conn = sqlite3.connect('supsmart_pro.db', check_same_thread=False)
    c = conn.cursor()
    # Tabela de Resumo das Compras
    c.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY, data TEXT, total REAL, itens_qtd INTEGER)''')
    # Tabela de Detalhes (Itens de cada compra)
    c.execute('''CREATE TABLE IF NOT EXISTS itens_detalhes 
                 (compra_id INTEGER, nome TEXT, preco REAL, qtd REAL, cat TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- 2. UI ADAPTATIVA (SaaS MODERN STYLE) ---
st.set_page_config(page_title="SupSmart Pro", layout="wide", page_icon="✨")

# CSS para resolver o contraste no Modo Dark e Light
st.markdown("""
<style>
    @import url('https://rsms.me/inter/inter.css');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Cards que se adaptam ao tema (Glassmorphism suave) */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 20px !important;
        border-radius: 12px !important;
    }
    
    /* Ajuste de botões e inputs */
    .stButton>button { border-radius: 8px; font-weight: 600; }
    .stTextInput>div>div>input { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. GESTÃO DE ESTADO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- 4. CABEÇALHO E MÉTRICAS ---
st.title("SupSmart / Dashboard")

# Carrega dados do banco
df_compras = pd.read_sql("SELECT * FROM compras", conn)
total_carrinho = sum(i['Total'] for i in st.session_state.carrinho)
gasto_historico = df_compras['total'].sum() if not df_compras.empty else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("No Carrinho", f"R$ {total_carrinho:.2f}")
m2.metric("Itens Atuais", len(st.session_state.carrinho))
m3.metric("Gasto Total", f"R$ {gasto_historico:.2f}")
m4.metric("Compras", len(df_compras))

st.write("##")

# --- 5. NAVEGAÇÃO POR ABAS (AQUI ESTÁ O HISTÓRICO) ---
tab_atual, tab_hist, tab_analise = st.tabs(["🛒 Compra Atual", "📜 Histórico de Listas", "📈 Insights"])

# --- ABA 1: COMPRA ATUAL ---
with tab_atual:
    col_in, col_res = st.columns([1, 1.5])
    
    with col_in:
        with st.container(border=True):
            st.subheader("Adicionar Item")
            nome = st.text_input("Nome do Produto")
            c1, c2 = st.columns(2)
            with c1: qtd = st.number_input("Qtd", min_value=0.1, value=1.0)
            with c2: preco = st.number_input("Preço Unit.", min_value=0.0, step=0.01)
            cat = st.selectbox("Categoria", ["Alimentos", "Higiene", "Limpeza", "Bebidas", "Outros"])
            
            if st.button("Adicionar", use_container_width=True, type="primary"):
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
                
                if st.button("✅ FINALIZAR E SALVAR COMPRA", use_container_width=True):
                    # Salva no Banco de Dados
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
                st.info("Adicione itens para começar sua lista.")

# --- ABA 2: HISTÓRICO (OPÇÃO SOLICITADA) ---
with tab_hist:
    st.subheader("Histórico de Compras Realizadas")
    if not df_compras.empty:
        # Tabela com as compras
        st.dataframe(df_compras.sort_values(by='id', ascending=False), use_container_width=True, hide_index=True)
        
        st.write("---")
        st.subheader("🔍 Detalhes da Compra")
        id_busca = st.number_input("Informe o ID da compra para ver os itens:", min_value=1, step=1)
        if st.button("Ver Itens"):
            detalhes = pd.read_sql(f"SELECT nome as Item, preco as 'Preço', qtd as 'Qtd', cat as Categoria FROM itens_detalhes WHERE compra_id = {id_busca}", conn)
            if not detalhes.empty:
                st.table(detalhes)
            else:
                st.warning("Compra não encontrada.")
    else:
        st.warning("Você ainda não salvou nenhuma compra.")

# --- ABA 3: ANALYTICS ---
with tab_analise:
    if not df_compras.empty:
        fig = px.area(df_compras, x="data", y="total", title="Evolução de Gastos", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Dados insuficientes para gerar análises.")