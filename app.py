import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- 1. BANCO DE DADOS (BLINDADO & AUTO-REPARÁVEL) ---
def get_db_connection():
    conn = sqlite3.connect('supsmart_pro.db', check_same_thread=False)
    cursor = conn.cursor()
    # Tabela principal de compras
    cursor.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, total REAL, itens_qtd INTEGER, limite REAL)''')
    # Tabela de detalhes dos itens
    cursor.execute('''CREATE TABLE IF NOT EXISTS itens_detalhes 
                 (compra_id INTEGER, nome TEXT, preco REAL, qtd REAL, cat TEXT, medida TEXT)''')
    conn.commit()
    return conn

conn = get_db_connection()

# --- 2. DESIGN SYSTEM (SaaS MODERNO) ---
st.set_page_config(page_title="SupSmart Pro", layout="wide", page_icon="🛒")

st.markdown("""
<style>
    @import url('https://rsms.me/inter/inter.css');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Cards de Métricas Estilo Linear */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 12px !important;
        padding: 15px !important;
        transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover { transform: translateY(-2px); }
    [data-testid="stMetricLabel"] p { color: #888 !important; font-size: 0.85rem !important; }
    [data-testid="stMetricValue"] { font-weight: 700 !important; font-size: 1.5rem !important; }

    /* Estilização de Abas e Botões */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 40px; white-space: pre-wrap; background-color: rgba(128, 128, 128, 0.05);
        border-radius: 8px; padding: 5px 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE ESTADO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- 4. DASHBOARD & MÉTRICAS ---
st.title("SupSmart / Dashboard")

try:
    df_compras = pd.read_sql("SELECT * FROM compras", conn)
except:
    df_compras = pd.DataFrame(columns=['id', 'data', 'total', 'itens_qtd', 'limite'])

total_carrinho = sum(i['Total'] for i in st.session_state.carrinho)
gasto_historico = df_compras['total'].sum() if not df_compras.empty else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("🛒 No Carrinho", f"R$ {total_carrinho:.2f}")
m2.metric("📦 Itens Atuais", len(st.session_state.carrinho))
m3.metric("💰 Gasto Histórico", f"R$ {gasto_historico:.2f}")
m4.metric("📊 Compras Feitas", len(df_compras))

# --- 5. BARRA DE ORÇAMENTO (NOVA FUNCIONALIDADE) ---
with st.sidebar:
    st.header("⚙️ Configurações")
    limite = st.number_input("Definir Limite de Gastos (R$)", min_value=0.0, value=500.0, step=50.0)
    
    # Cálculo de progresso
    if limite > 0:
        progresso = min(total_carrinho / limite, 1.0)
        cor_barra = "green" if progresso < 0.8 else "orange" if progresso < 1.0 else "red"
        st.markdown(f"**Orçamento:** {progresso*100:.1f}%")
        st.progress(progresso)
        if progresso >= 1.0:
            st.error("⚠️ Você atingiu seu limite!")

# --- 6. NAVEGAÇÃO ---
tab_mercado, tab_historico = st.tabs(["🛒 Calculadora de Mercado", "📜 Histórico Inteligente"])

with tab_mercado:
    col_input, col_resumo = st.columns([1, 1.5])
    
    with col_input:
        with st.form("add_item_form", clear_on_submit=True):
            st.subheader("➕ Novo Item")
            nome = st.text_input("Nome do Produto", placeholder="Ex: Café")
            tipo = st.radio("Medida", ["Un", "Kg"], horizontal=True)
            
            c_q, c_p = st.columns(2)
            qtd = c_q.number_input("Qtd/Peso", min_value=0.01, value=1.00)
            preco = c_p.number_input("Preço Unit/Kg", min_value=0.00, step=0.01)
            cat = st.selectbox("Categoria", ["Alimentos", "Açougue", "Limpeza", "Higiene", "Bebidas", "Outros"])
            
            if st.form_submit_button("Adicionar à Lista", use_container_width=True):
                if nome and preco > 0:
                    st.session_state.carrinho.append({
                        "Item": nome, "Qtd": qtd, "Tipo": tipo,
                        "Preço": preco, "Total": qtd * preco, "Cat": cat
                    })
                    st.rerun()

    with col_resumo:
        st.subheader("📋 Lista de Compras")
        if st.session_state.carrinho:
            df_carrinho = pd.DataFrame(st.session_state.carrinho)
            st.dataframe(df_carrinho, use_container_width=True, hide_index=True)
            
            c_b1, c_b2 = st.columns(2)
            if c_b1.button("✅ FINALIZAR COMPRA", type="primary", use_container_width=True):
                cur = conn.cursor()
                agora = datetime.now().strftime("%d/%m/%Y %H:%M")
                cur.execute("INSERT INTO compras (data, total, itens_qtd, limite) VALUES (?, ?, ?, ?)", 
                            (agora, total_carrinho, len(st.session_state.carrinho), limite))
                compra_id = cur.lastrowid
                for i in st.session_state.carrinho:
                    cur.execute("INSERT INTO itens_detalhes VALUES (?, ?, ?, ?, ?, ?)", 
                                (compra_id, i['Item'], i['Preço'], i['Qtd'], i['Cat'], i['Tipo']))
                conn.commit()
                st.session_state.carrinho = []
                st.balloons()
                st.rerun()
                
            if c_b2.button("🗑️ LIMPAR TUDO", use_container_width=True):
                st.session_state.carrinho = []
                st.rerun()
        else:
            st.info("Adicione itens para começar a calcular.")

with tab_historico:
    st.subheader("💾 Compras Realizadas")
    if not df_compras.empty:
        # Exibe o histórico de compras
        st.dataframe(df_compras.sort_values(by='id', ascending=False), use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("🔍 Detalhes da Compra")
        id_selecionado = st.number_input("Insira o ID para ver os itens:", min_value=1, step=1)
        
        if st.button("Ver Detalhes dos Itens"):
            detalhes = pd.read_sql(f"SELECT nome as Item, preco as 'Preço', qtd as Qtd, medida as Tipo, cat as Categoria FROM itens_detalhes WHERE compra_id = {int(id_selecionado)}", conn)
            if not detalhes.empty:
                st.table(detalhes)
            else:
                st.warning("Nenhum detalhe encontrado para este ID.")
    else:
        st.info("Ainda não existem compras salvas no banco de dados.")