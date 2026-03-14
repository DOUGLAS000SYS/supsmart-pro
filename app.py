import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
import urllib.parse

# --- 1. BANCO DE DADOS ---
class DBManager:
    def __init__(self, db_name='supsmart_pro.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS compras (id INTEGER PRIMARY KEY, data TEXT, total REAL, itens INTEGER)')
        c.execute('CREATE TABLE IF NOT EXISTS itens_historico (nome TEXT, preco_unit REAL, data TEXT, categoria TEXT)')
        self.conn.commit()

    def salvar_compra(self, total, itens):
        c = self.conn.cursor()
        data = datetime.now().strftime("%d/%m/%Y")
        c.execute("INSERT INTO compras (data, total, itens) VALUES (?, ?, ?)", (data, total, len(itens)))
        for item in itens:
            c.execute("INSERT INTO itens_historico (nome, preco_unit, data, categoria) VALUES (?, ?, ?, ?)",
                      (item['Item'], item['Preço Unit'], data, item['Categoria']))
        self.conn.commit()

db = DBManager()

# --- 2. DESIGN SYSTEM (ESTILO LINEAR/NUBANK) ---
st.set_page_config(page_title="SupSmart", layout="wide", page_icon="✨")

st.markdown("""
<style>
    /* Importação de Fonte Moderna */
    @import url('https://rsms.me/inter/inter.css');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FBFBFC; }

    /* Estilização dos Cards Principais */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        padding: 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    
    /* Botões estilo Linear */
    .stButton>button {
        background-color: #111111;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #333333;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        color: white;
    }

    /* Inputs Estilizados */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        border-radius: 8px !important;
        border: 1px solid #E5E7EB !important;
    }

    /* Custom Header */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE ESTADO ---
if 'carrinho' not in st.session_state: st.session_state.carrinho = []

# --- 4. INTERFACE PRINCIPAL ---
st.markdown('<div class="header-container"><div><h1>SupSmart <span style="color:#888; font-weight:400;">/ Dashboard</span></h1></div></div>', unsafe_allow_html=True)

# Métricas de Alta Fidelidade
df_hist = pd.read_sql("SELECT * FROM compras", db.conn)
total_atual = sum(item['Total'] for item in st.session_state.carrinho)
gasto_acumulado = df_hist['total'].sum() if not df_hist.empty else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total no Carrinho", f"R$ {total_atual:.2f}")
m2.metric("Itens", len(st.session_state.carrinho))
m3.metric("Gasto do Mês", f"R$ {gasto_acumulado:.2f}")
m4.metric("Previsão", f"R$ {gasto_acumulado * 1.1:.2f}", delta="-2%")

st.write("##")

# Layout de Grid Moderno
col_left, col_right = st.columns([1.2, 2])

with col_left:
    with st.container(border=True):
        st.markdown("### 🛠️ Adicionar Item")
        nome = st.text_input("Nome do produto", placeholder="Ex: Café em grãos")
        
        c1, c2 = st.columns(2)
        with c1: qtd = st.number_input("Qtd", min_value=0.1, value=1.0)
        with c2: preco = st.number_input("Preço unitário", min_value=0.0, step=0.01)
        
        cat = st.selectbox("Categoria", ["Alimentos", "Higiene", "Limpeza", "Bebidas", "Outros"])
        
        if st.button("Adicionar à Lista", use_container_width=True):
            if nome and preco > 0:
                st.session_state.carrinho.append({
                    "Categoria": cat, "Item": nome, "Qtd": qtd, "Preço Unit": preco, "Total": qtd*preco
                })
                st.rerun()

with col_right:
    with st.container(border=True):
        st.markdown("### 📋 Checkout")
        if st.session_state.carrinho:
            df_c = pd.DataFrame(st.session_state.carrinho)
            st.dataframe(df_c, use_container_width=True, hide_index=True)
            
            c_fin, c_del = st.columns(2)
            with c_fin:
                if st.button("Finalizar Compra", type="primary", use_container_width=True):
                    db.salvar_compra(total_atual, st.session_state.carrinho)
                    st.session_state.carrinho = []
                    st.balloons()
                    st.rerun()
            with c_del:
                if st.button("Limpar Carrinho", use_container_width=True):
                    st.session_state.carrinho = []
                    st.rerun()
        else:
            st.markdown("<div style='text-align:center; padding: 40px; color:#888;'>Nenhum item adicionado ainda.</div>", unsafe_allow_html=True)

# --- 5. ANALYTICS (INSPIRADO NO LINEAR) ---
st.write("---")
st.markdown("### 📈 Insights de Consumo")
ca, cb = st.columns(2)

with ca:
    if st.session_state.carrinho:
        fig = px.bar(df_c, x="Item", y="Total", color="Categoria", 
                     title="Distribuição de Custos Atual", 
                     color_discrete_sequence=px.colors.qualitative.Prism)
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

with cb:
    if not df_hist.empty:
        fig_line = px.area(df_hist, x="data", y="total", title="Fluxo de Gastos Mensal",
                           color_discrete_sequence=['#111111'])
        fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_line, use_container_width=True)