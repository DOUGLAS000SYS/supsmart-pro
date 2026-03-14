import streamlit as st
import pandas as pd
import sqlite3
import urllib.parse
from datetime import datetime, timedelta, timezone

# --- 1. FUNÇÕES DE APOIO ---
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
    conn.commit()
    return conn

conn = get_db_connection()

# --- 2. TELA DE INÍCIO (LOGIN / VISITANTE) ---
if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.markdown("<h1 style='text-align: center;'>🛒 SupSmart Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Controle suas compras de forma inteligente</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("---")
        # Botão Visitante
        if st.button("🚀 Entrar como Visitante", use_container_width=True):
            st.session_state.logado = True
            st.rerun()
        
        # Simulação Botão Google (Visual)
        st.markdown('''
            <div style="background-color: white; color: #757575; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; border: 1px solid #ddd; cursor: not-allowed; opacity: 0.7;">
                <img src="https://rotulos.com.br/wp-content/uploads/2021/05/google-logo.png" width="18" style="margin-right: 10px; vertical-align: middle;">
                Fazer login com Google (Em breve)
            </div>
        ''', unsafe_allow_html=True)
        st.caption("Nota: O login com Google requer configuração de API.")
    st.stop() # Interrompe o código aqui até o usuário entrar

# --- 3. SE O USUÁRIO ESTIVER LOGADO, MOSTRA O APP ---
st.set_page_config(page_title="SupSmart Pro", layout="wide")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Botão de Sair na Sidebar
with st.sidebar:
    st.write(f"Conectado como: **Visitante**")
    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()

st.title("SupSmart / Dashboard")

# --- 4. MÉTRICAS E ORÇAMENTO ---
limite_input = st.number_input("Definir Meta de Gasto (R$):", min_value=0.0, value=500.0)
total_carrinho = sum(i['Total'] for i in st.session_state.carrinho)

c1, c2 = st.columns(2)
c1.metric("Total no Carrinho", f"R$ {total_carrinho:.2f}")
c2.metric("Meta", f"R$ {limite_input:.2f}", delta=f"Sobram: R$ {limite_input - total_carrinho:.2f}")

st.divider()

# --- 5. NAVEGAÇÃO ---
tab_mercado, tab_historico = st.tabs(["🛒 Comprar", "📜 Histórico"])

with tab_mercado:
    with st.form("add_item", clear_on_submit=True):
        col_nome, col_medida = st.columns([2, 1])
        nome = col_nome.text_input("Produto")
        medida = col_medida.radio("Tipo", ["Un", "Kg"], horizontal=True)
        
        col_q, col_p, col_c = st.columns(3)
        qtd = col_q.number_input("Qtd", min_value=0.01, value=1.0)
        preco = col_p.number_input("Preço Unitário", min_value=0.0, step=0.01)
        cat = col_c.selectbox("Categoria", ["Alimentos", "Limpeza", "Higiene", "Bebidas", "Outros"])
        
        if st.form_submit_button("➕ ADICIONAR ITEM"):
            if nome and preco > 0:
                st.session_state.carrinho.append({
                    "Item": nome, "Qtd": qtd, "Preço": preco, 
                    "Total": qtd * preco, "Categoria": cat, "Medida": medida
                })
                st.rerun()

    if st.session_state.carrinho:
        st.write("### Itens no Carrinho")
        df_car = pd.DataFrame(st.session_state.carrinho)
        st.dataframe(df_car, use_container_width=True, hide_index=True)
        
        # Link WhatsApp
        texto_wpp = f"🛒 *Lista de Compras - SupSmart*\n\n"
        for i in st.session_state.carrinho:
            texto_wpp += f"▪️ {i['Item']} ({i['Qtd']}{i['Medida']}) - R$ {i['Total']:.2f}\n"
        texto_wpp += f"\n💰 *Total: R$ {total_carrinho:.2f}*"
        texto_encoded = urllib.parse.quote(texto_wpp)
        link_wpp = f"https://wa.me/?text={texto_encoded}"
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ FINALIZAR COMPRA", type="primary", use_container_width=True):
                cur = conn.cursor()
                data_atual = get_agora_br()
                cur.execute("INSERT INTO compras (data, total, itens_qtd, limite) VALUES (?, ?, ?, ?)", 
                            (data_atual, total_carrinho, len(st.session_state.carrinho), limite_input))
                compra_id = cur.lastrowid
                for i in st.session_state.carrinho:
                    cur.execute("INSERT INTO itens_detalhes VALUES (?, ?, ?, ?, ?, ?)", 
                                (compra_id, i['Item'], i['Preço'], i['Qtd'], i['Categoria'], i['Medida']))
                conn.commit()
                st.session_state.carrinho = []
                st.success("Compra salva!")
                st.rerun()

        with col_btn2:
            st.markdown(f'''<a href="{link_wpp}" target="_blank" style="text-decoration: none;"><div style="background-color: #25D366; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;">WhatsApp</div></a>''', unsafe_allow_html=True)

with tab_historico:
    df_compras = pd.read_sql("SELECT * FROM compras ORDER BY id DESC", conn)
    if not df_compras.empty:
        st.dataframe(df_compras, use_container_width=True, hide_index=True)