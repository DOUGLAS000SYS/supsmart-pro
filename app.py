import streamlit as st
import pandas as pd
import urllib.parse

# --- 1. CONFIGURAÇÃO DE DESIGN (DARK MODE PREMIUM) ---
st.set_page_config(page_title="SupSmart Pro", page_icon="🛒", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .item-card {
        background: #1D2129;
        padding: 15px;
        border-radius: 12px;
        border-left: 6px solid #7B1FA2;
        margin-bottom: 10px;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.3);
    }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5em;
        background-color: #7B1FA2; color: white; font-weight: bold; border: none;
    }
    .stButton>button:hover { background-color: #9C27B0; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LÓGICA DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = 'home'
if 'carrinho' not in st.session_state: st.session_state.carrinho = []

def mudar_pagina(nome):
    st.session_state.pagina = nome
    st.rerun()

# --- TELA 1: HOME (RESTAURADA) ---
if st.session_state.pagina == 'home':
    st.image("banner.png", use_container_width=True)
    st.markdown("<h1 style='text-align: center;'>SupSmart Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #BBB;'>Inteligência em tempo real para suas compras.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 MODO VISITANTE"): mudar_pagina('calculadora')
    with col2:
        if st.button("🌐 ENTRAR COM GOOGLE"): st.toast("Em breve: Sincronização em nuvem!")
    
    st.write("---")
    st.caption("<center>Douglas Dev System | v6.0 Elite</center>", unsafe_allow_html=True)

# --- TELA 2: CALCULADORA (UNIDADE & KG) ---
elif st.session_state.pagina == 'calculadora':
    st.markdown("### 🛒 Minha Lista")
    
    orcamento = st.number_input("Defina sua meta de gasto (R$)", min_value=0.0, value=100.0)
    
    # --- FORMULÁRIO DE ENTRADA ---
    with st.container():
        st.write("---")
        with st.form("novo_item", clear_on_submit=True):
            nome = st.text_input("📦 Nome do Produto", placeholder="Ex: Alcatra, Arroz...")
            
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1: 
                tipo_medida = st.radio("Medida", ["Un", "Kg"], horizontal=True)
            with c2:
                # O step muda para 0.01 se for Kg para aceitar pesos quebrados
                qtd = st.number_input("Qtd / Peso", min_value=0.01, value=1.00, step=0.01 if tipo_medida == "Kg" else 1.0)
            with c3:
                preco = st.number_input("Preço", min_value=0.0, value=0.0, step=0.01)
            
            seg = st.selectbox("🏷️ Segmento", ["Açougue", "Bebidas", "Limpeza", "Hortifruti", "Padaria", "Matinais", "Outros"])
            
            if st.form_submit_button("➕ ADICIONAR ITEM"):
                valor_total_item = qtd * preco
                st.session_state.carrinho.append({
                    "nome": nome if nome else "Item",
                    "qtd": qtd, "medida": tipo_medida,
                    "preco": preco, "valor": valor_total_item, "segmento": seg
                })
                st.rerun()

    # --- TOTAIS E SEMÁFORO ---
    total = sum(item['valor'] for item in st.session_state.carrinho)
    progresso = min(total / orcamento, 1.0) if orcamento > 0 else 0
    cor_status = "#2E7D32" if progresso < 0.8 else "#FBC02D" if progresso < 1.0 else "#D32F2F"
    
    st.markdown(f"""
        <div style='background: {cor_status}; padding: 15px; border-radius: 12px; text-align: center; margin-top: 10px;'>
            <h2 style='margin:0; color: white;'>Total: R$ {total:.2f}</h2>
            <small style='color: white;'>Meta: R$ {orcamento:.2f}</small>
        </div>
    """, unsafe_allow_html=True)
    st.progress(progresso)

    # --- LISTA DE ITENS ---
    st.write("##")
    if st.session_state.carrinho:
        for i, item in enumerate(reversed(st.session_state.carrinho)):
            st.markdown(f"""
                <div class="item-card">
                    <div style="display: flex; justify-content: space-between;">
                        <b>{item['nome']}</b>
                        <span style="color: #9C27B0; font-weight: bold;">R$ {item['valor']:.2f}</span>
                    </div>
                    <small style="color: #888;">{item['segmento']} | {item['qtd']}{item['medida']} x R$ {item['preco']:.2f}</small>
                </div>
            """, unsafe_allow_html=True)

        # COMPARTILHAR WHATSAPP
        resumo_texto = f"🛒 *Resumo SupSmart*\nTotal: R$ {total:.2f}\nMeta: R$ {orcamento:.2f}"
        link_wa = f"https://wa.me/?text={urllib.parse.quote(resumo_texto)}"
        
        st.write("---")
        st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; height