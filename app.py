import streamlit as st
import pandas as pd
import sqlite3
import urllib.parse
from datetime import datetime, timedelta, timezone

# --- 1. CONFIGURAÇÃO DE APP PROFISSIONAL (LIMPEZA SaaS) ---
st.set_page_config(
    page_title="SupSmart Pro",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS para esconder menus do Streamlit e polir a interface
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { max-width: 1000px; margin: 0 auto; }
    </style>
""", unsafe_allow_html=True)

# --- 2. FUNÇÕES DE APOIO ---
def get_agora_br():
    fuso_br = timezone(timedelta(hours=-3))
    return datetime.now(fuso_br).strftime("%d/%m/%Y %H:%M")

def get_db_connection():
    conn = sqlite3.connect('supsmart_pro.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, total REAL, itens_qtd INTEGER, limite REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS itens_detalhes 
                 (compra_id INTEGER, nome TEXT, preco REAL, qtd REAL, cat TEXT, medida TEXT)''')
    
    # Reparo automático de colunas
    cursor.execute("PRAGMA table_info(compras)")
    colunas = [row[1] for row in cursor.fetchall()]
    if 'limite' not in colunas:
        cursor.execute("ALTER TABLE compras ADD COLUMN limite REAL DEFAULT 500.0")
    
    conn.commit()
    return conn

conn = get_db_connection()

# --- 3. LÓGICA DE ACESSO (TELA DE INÍCIO) ---
if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.markdown("<h1 style='text-align: center;'>🛒 SupSmart Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Sua lista de compras inteligente e profissional.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("---")
        if st.button("🚀 Entrar como Visitante", use_container_width=True):
            st.session_state.logado = True
            st.rerun()
        
        st.markdown('''
            <div style="background-color: white; color: #757575; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; border: 1px solid #ddd; opacity: 0.7;">
                <img src="https://rotulos.com.br/wp-content/uploads/2021/05/google-logo.png" width="18" style="margin-right: 10px; vertical-align: middle;">
                Login com Google (Em breve)
            </div>
        ''', unsafe_allow_html=True)
    st.stop()

# --- 4. APP PRINCIPAL (DASHBOARD) ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Menu lateral discreto para "Sair"
with st.sidebar:
    st.write("👤 Usuário: **Visitante**")
    if st.button("Sair / Logout"):
        st.session_state.logado = False
        st.rerun()

st.title("SupSmart / Dashboard")

# Orçamento e Métricas
limite_input = st.number_input("Definir Meta de Gasto (R$):", min_value=0.0, value=500.0)
total_carrinho = sum(i['Total'] for i in st.session_state.carrinho)

c1, c2 = st.columns(2)
c1.metric("Total no Carrinho", f"R$ {total_carrinho:.2f}")
c2.metric("Meta do Mês", f"R$ {limite_input:.2f}", delta=f"R$ {limite_input - total_carrinho:.2f} livres")

st.divider()

# Navegação por Abas
tab_compra, tab_hist = st.tabs(["🛒 Nova Compra", "📜 Histórico"])

with tab_compra:
    # Formulário de Entrada
    with st.form("add_item", clear_on_submit=True):
        col_n, col_m = st.columns([2, 1])
        nome = col_n.text_input("Nome do Produto")
        medida = col_m.radio("Tipo", ["Un", "Kg"], horizontal=True)
        
        col_q, col_p, col_cat = st.columns(3)
        qtd = col_q.number_input("Qtd", min_value=0.01, value=1.0)
        preco = col_p.number_input("Preço Unitário", min_value=0.0, step=0.01)
        cat = col_cat.selectbox("Categoria", ["Alimentos", "Limpeza", "Higiene", "Bebidas", "Outros"])
        
        if st.form_submit_button("➕ ADICIONAR ITEM", use_container_width=True):
            if nome and preco > 0:
                st.session_state.carrinho.append({
                    "Item": nome, "Qtd": qtd, "Preço": preco, 
                    "Total": qtd * preco, "Categoria": cat, "Medida": medida
                })
                st.rerun()

    if st.session_state.carrinho:
        st.write("### Itens Atuais")
        df_car = pd.DataFrame(st.session_state.carrinho)
        st.dataframe(df_car, use_container_width=True, hide_index=True)
        
        # WhatsApp Link Generation
        texto_wpp = f"🛒 *Lista SupSmart*\n"
        for i in st.session_state.carrinho:
            texto_wpp += f"- {i['Item']} ({i['Qtd']}{i['Medida']}): R$ {i['Total']:.2f}\n"
        texto_wpp += f"\n💰 *Total: R$ {total_carrinho:.2f}*"
        link_wpp = f"https://wa.me/?text={urllib.parse.quote(texto_wpp)}"
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("✅ SALVAR COMPRA", type="primary", use_container_width=True):
                cur = conn.cursor()
                data_br = get_agora_br()
                cur.execute("INSERT INTO compras (data, total, itens_qtd, limite) VALUES (?, ?, ?, ?)", 
                            (data_br, total_carrinho, len(st.session_state.carrinho), limite_input))
                c_id = cur.lastrowid
                for i in st.session_state.carrinho:
                    cur.execute("INSERT INTO itens_detalhes VALUES (?, ?, ?, ?, ?, ?)", 
                                (c_id, i['Item'], i['Preço'], i['Qtd'], i['Categoria'], i['Medida']))
                conn.commit()
                st.session_state.carrinho = []
                st.success("Salvo com sucesso!")
                st.rerun()
        with col_b2:
            st.markdown(f'<a href="{link_wpp}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;">Enviar p/ WhatsApp</div></a>', unsafe_allow_html=True)

with tab_hist:
    df_hist = pd.read_sql("SELECT * FROM compras ORDER BY id DESC", conn)
    if not df_hist.empty:
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        id_detalhe = st.number_input("Ver itens do ID:", min_value=1, step=1)
        if st.button("Ver Detalhes"):
            det = pd.read_sql(f"SELECT nome, preco, qtd, medida, cat FROM itens_detalhes WHERE compra_id = {int(id_detalhe)}", conn)
            st.table(det)