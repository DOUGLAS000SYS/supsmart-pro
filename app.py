import streamlit as st
import urllib.parse
import time

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SupSmart Pro", page_icon="logo.png", layout="centered")

# Inicialização de memória do app
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'home'
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

def mudar_pagina(nome):
    st.session_state.pagina = nome
    st.rerun()

# --- 2. ESTILO CSS (O DESIGN LISO) ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #7B1FA2; color: white; font-weight: bold; }
    .item-card { background-color: white; padding: 12px; border-radius: 10px; border-left: 6px solid #7B1FA2; margin-bottom: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); color: black; }
    .finalizar-btn>div>button { background-color: #2E7D32 !important; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- TELA 1: HOME ---
if st.session_state.pagina == 'home':
    st.image("banner.png", use_container_width=True)
    st.markdown("<h1 style='text-align:center; color:#4A148C;'>SupSmart Pro</h1>", unsafe_allow_html=True)
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 MODO VISITANTE"): mudar_pagina('calculadora')
    with c2:
        if st.button("🌐 CONECTAR GOOGLE"): st.toast("Em breve: Nuvem!")
    st.caption("<p style='text-align:center;'>Desenvolvido por Douglas | Versão 3.0 Elite</p>", unsafe_allow_html=True)

# --- TELA 2: CALCULADORA (O MONSTRO) ---
elif st.session_state.pagina == 'calculadora':
    if st.sidebar.button("⬅️ Sair do App"): mudar_pagina('home')
    
    st.title("🛒 Lista de Precisão")
    
    # DEFINIR META DE GASTO
    with st.expander("🎯 CONFIGURAR ORÇAMENTO", expanded=True):
        orcamento = st.number_input("Qual o seu limite hoje? (R$)", min_value=1.0, value=100.0, step=10.0)

    # FORMULÁRIO DE ENTRADA
    with st.form("add_item", clear_on_submit=True):
        produto = st.text_input("📦 Nome do Produto (Ex: Arroz)")
        col1, col2 = st.columns(2)
        with col1: qtd_txt = st.text_input("Qtd/Peso", value="1")
        with col2: prc_txt = st.text_input("Preço Unitário", placeholder="0,00")
        enviar = st.form_submit_button("➕ ADICIONAR AO CARRINHO")

    if enviar:
        try:
            q = float(qtd_txt.replace(',', '.'))
            p = float(prc_txt.replace(',', '.'))
            st.session_state.carrinho.append({
                "nome": produto if produto else "Item", 
                "valor": q * p, 
                "detalhe": f"{q}x R$ {p:.2f}"
            })
            st.rerun()
        except: st.error("⚠️ Por favor, use apenas números e vírgula.")

    # CÁLCULOS E SEMÁFORO DE CORES
    total = sum(item['valor'] for item in st.session_state.carrinho)
    progresso = min(total / orcamento, 1.0) if orcamento > 0 else 0
    
    if progresso < 0.7: 
        cor, msg = "#2E7D32", "✅ DENTRO DA META"
    elif progresso < 1.0: 
        cor, msg = "#FBC02D", "⚠️ ATENÇÃO: QUASE LÁ"
    else: 
        cor, msg = "#D32F2F", "🚨 LIMITE ULTRAPASSADO!"

    # PAINEL DE STATUS DINÂMICO
    st.markdown(f"""