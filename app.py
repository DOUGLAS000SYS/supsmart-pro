import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="SupSmart Pro", page_icon="🛒", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    .item-card {
        background: #1D2129; padding: 15px; border-radius: 12px;
        border-left: 6px solid #7B1FA2; margin-bottom: 10px;
    }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3em;
        background-color: #7B1FA2; color: white; font-weight: bold;
    }
    .historico-card {
        background: #262730; padding: 10px; border-radius: 8px;
        border-bottom: 1px solid #444; margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. INICIALIZAÇÃO DE MEMÓRIA ---
if 'pagina' not in st.session_state: st.session_state.pagina = 'home'
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'historico' not in st.session_state: st.session_state.historico = []

def mudar_pagina(nome):
    st.session_state.pagina = nome
    st.rerun()

# --- TELA 1: HOME ---
if st.session_state.pagina == 'home':
    st.image("banner.png", use_container_width=True)
    st.markdown("<h1 style='text-align: center;'>SupSmart Pro</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 INICIAR LISTA"): mudar_pagina('calculadora')
    with col2:
        if st.button("📜 VER HISTÓRICO"): mudar_pagina('historico')

# --- TELA 2: CALCULADORA ---
elif st.session_state.pagina == 'calculadora':
    st.markdown("### 🛒 Calculadora Elite")
    orcamento = st.number_input("Meta de Gasto (R$)", min_value=0.0, value=100.0)
    
    with st.form("novo_item", clear_on_submit=True):
        nome = st.text_input("📦 Produto")
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1: tipo_medida = st.radio("Medida", ["Un", "Kg"], horizontal=True)
        with c2: qtd = st.number_input("Qtd/Peso", min_value=0.01, value=1.0, step=0.01)
        with c3: preco = st.number_input("Preço", min_value=0.0, value=0.0, step=0.01)
        
        if st.form_submit_button("➕ ADICIONAR"):
            if nome:
                st.session_state.carrinho.append({
                    "nome": nome, "qtd": qtd, "medida": tipo_medida, "valor": qtd * preco
                })
                st.rerun()

    total = sum(i['valor'] for i in st.session_state.carrinho)
    st.markdown(f"<h2 style='text-align: center;'>Total: R$ {total:.2f}</h2>", unsafe_allow_html=True)

    # Lista de itens atual
    for item in reversed(st.session_state.carrinho):
        st.markdown(f"""<div class="item-card"><b>{item['nome']}</b><br>
        {item['qtd']}{item['medida']} - R$ {item['valor']:.2f}</div>""", unsafe_allow_html=True)

    st.write("---")
    if st.button("✅ FINALIZAR COMPRA"):
        if st.session_state.carrinho:
            # Salva no histórico com data e hora
            resumo = {
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "total": total,
                "itens": len(st.session_state.carrinho)
            }
            st.session_state.historico.append(resumo)
            st.session_state.carrinho = [] # Limpa o carrinho
            st.success("Compra finalizada e salva no histórico!")
            mudar_pagina('home')

    if st.sidebar.button("⬅️ VOLTAR"): mudar_pagina('home')

# --- TELA 3: HISTÓRICO ---
elif st.session_state.pagina == 'historico':
    st.markdown("### 📜 Histórico de Compras")
    
    if not st.session_state.historico:
        st.info("Nenhuma compra finalizada ainda.")
    else:
        for compa in reversed(st.session_state.historico):
            st.markdown(f"""
            <div class="historico-card">
                <small>{compa['data']}</small><br>
                <b>Total: R$ {compa['total']:.2f}</b> | {compa['itens']} itens
            </div>
            """, unsafe_allow_html=True)
            
    if st.button("🗑️ LIMPAR HISTÓRICO"):
        st.session_state.historico = []
        st.rerun()
        
    if st.sidebar.button("⬅️ VOLTAR"): mudar_pagina('home')