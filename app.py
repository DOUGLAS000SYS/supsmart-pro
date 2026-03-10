import streamlit as st
import urllib.parse

# --- 1. CONFIGURAÇÃO DA PÁGINA (Sempre a primeira coisa!) ---
st.set_page_config(
    page_title="SupSmart Pro",
    page_icon="logo.png",
    layout="centered"
)

# --- 2. INICIALIZAÇÃO DE MEMÓRIA (Session State) ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'home'
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

def mudar_pagina(nome):
    st.session_state.pagina = nome
    st.rerun()

# --- 3. ESTILO VISUAL (Roxo Premium) ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #7B1FA2; color: white; font-weight: bold; border: none; }
    .titulo { text-align: center; color: #4A148C; font-family: 'sans-serif'; }
    .metric-container { background-color: #f3e5f5; padding: 15px; border-radius: 15px; text-align: center; border: 1px solid #7B1FA2; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DAS TELAS ---

# TELA 1: BOAS-VINDAS
if st.session_state.pagina == 'home':
    st.image("banner.png", use_container_width=True)
    st.markdown("<h1 class='titulo'>SupSmart Pro</h1>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 MODO VISITANTE"):
            mudar_pagina('calculadora')
    with col2:
        if st.button("🌐 CONECTAR GOOGLE"):
            st.toast("Em breve: Sincronização em Nuvem!")
    st.caption("Desenvolvido por Douglas | Versão 2.0")

# TELA 2: CALCULADORA (O Motor do Mercado)
elif st.session_state.pagina == 'calculadora':
    if st.sidebar.button("⬅️ Voltar para Início"):
        mudar_pagina('home')

    st.title("🛒 Lista de Precisão")
    
    # --- ENTRADA DE DADOS ---
    with st.form("add_item", clear_on_submit=True):
        produto = st.text_input("📦 Nome do Produto", placeholder="Ex: Arroz")
        col_tipo, col_val = st.columns([1, 1])
        
        with col_tipo:
            tipo = st.radio("Tipo", ["Unidade (x)", "Peso (KG)"])
        with col_val:
            qtd_txt = st.text_input("Qtd / Peso", value="1")
            prc_txt = st.text_input("Preço Unit / KG", placeholder="0,00")
        
        enviar = st.form_submit_button("➕ ADICIONAR AO CARRINHO")

    if enviar:
        try:
            qtd = float(qtd_txt.replace(',', '.'))
            prc = float(prc_txt.replace(',', '.'))
            subtotal = qtd * prc
            
            st.session_state.carrinho.append({
                "nome": produto if produto else "Item s/ nome",
                "detalhe": f"{qtd} x R$ {prc:.2f}",
                "valor": subtotal
            })
            st.success(f"Adicionado: R$ {subtotal:.2f}")
        except:
            st.error("Erro! Use números e vírgula nos campos de valor.")

    # --- EXIBIÇÃO DO CARRINHO E TOTAL