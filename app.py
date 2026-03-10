import streamlit as st
import urllib.parse

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SupSmart Pro", page_icon="logo.png", layout="centered")

# --- 2. MEMÓRIA ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'home'
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

def mudar_pagina(nome):
    st.session_state.pagina = nome
    st.rerun()

# --- 3. ESTILO ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #7B1FA2; color: white; font-weight: bold; }
    .metric-container { background-color: #f3e5f5; padding: 15px; border-radius: 15px; text-align: center; border: 1px solid #7B1FA2; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- TELA 1: HOME ---
if st.session_state.pagina == 'home':
    st.image("banner.png", use_container_width=True)
    st.markdown("<h1 style='text-align:center; color:#4A148C;'>SupSmart Pro</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 MODO VISITANTE"):
            mudar_pagina('calculadora')
    with col2:
        if st.button("🌐 CONECTAR GOOGLE"):
            st.toast("Em breve!")

# --- TELA 2: CALCULADORA (REPARE QUE ESTÁ NO MESMO NÍVEL DO IF ACIMA) ---
elif st.session_state.pagina == 'calculadora':
    if st.sidebar.button("⬅️ Sair"):
        mudar_pagina('home')

    st.title("🛒 Lista de Precisão")
    
    with st.form("meu_formulario", clear_on_submit=True):
        produto = st.text_input("📦 Produto")
        c1, c2 = st.columns(2)
        with c1:
            qtd_txt = st.text_input("Qtd", value="1")
        with c2:
            prc_txt = st.text_input("Preço", placeholder="0,00")
        enviar = st.form_submit_button("➕ ADICIONAR")

    if enviar:
        try:
            q = float(qtd_txt.replace(',', '.'))
            p = float(prc_txt.replace(',', '.'))
            st.session_state.carrinho.append({"nome": produto, "valor": q * p})
            st.success("Adicionado!")
        except:
            st.error("Erro nos números!")

    # TOTAL (ESTÁ FORA DO FORMULÁRIO!)
    st.write("---")
    total = sum(item['valor'] for item in st.session_state.carrinho)
    
    st.markdown(f"""<div class="metric-container">
        <p style="margin:0; color:#4A148C;">TOTAL ACUMULADO</p>
        <h1 style="margin:0; color:#7B1FA2;">R$ {total:.2f}</h1>
    </div>""", unsafe_allow_html=True)

    if st.session_state.carrinho:
        # WHATSAPP
        texto = f"🛒 *Resumo SupSmart Pro*\n\n"
        for i in st.session_state.carrinho:
            texto += f"• {i['nome']}: R$ {i['valor']:.2f}\n"
        texto += f"\n💰 *TOTAL: R$ {total:.2f}*"
        
        link = f"https://wa.me/?text={urllib.parse.quote(texto)}"
        
        st.write("")
        st.markdown(f"""<a href="{link}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">
                ENVIAR PARA WHATSAPP ✅
            </div>
        </a>""", unsafe_allow_html=True)
        
        if st.button("🗑️ Limpar"):
            st.session_state.carrinho = []
            st.rerun()