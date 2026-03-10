import streamlit as st
import urllib.parse
import time
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SupSmart Pro", page_icon="logo.png", layout="centered")

# Inicialização de memória (Carrinho e Histórico)
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'home'
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'historico' not in st.session_state:
    st.session_state.historico = []

def mudar_pagina(nome):
    st.session_state.pagina = nome
    st.rerun()

# --- 2. ESTILO CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #7B1FA2; color: white; font-weight: bold; }
    .item-card { background-color: white; padding: 12px; border-radius: 10px; border-left: 6px solid #7B1FA2; margin-bottom: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); color: black; }
    .hist-card { background-color: #f0f2f6; padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 4px solid #4A148C; font-size: 14px; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: GAVETA DE HISTÓRICO ---
with st.sidebar:
    st.title("📂 Memória")
    if st.button("⬅️ Voltar ao Início"): mudar_pagina('home')
    
    st.write("---")
    st.subheader("📜 Compras Passadas")
    if st.session_state.historico:
        for comp in reversed(st.session_state.historico):
            with st.expander(f"📅 {comp['data']}"):
                st.write(f"**Total: R$ {comp['total']:.2f}**")
                for it in comp['itens']:
                    st.markdown(f"<div class='hist-card'>{it}</div>", unsafe_allow_html=True)
        if st.button("🗑️ Limpar Histórico"):
            st.session_state.historico = []
            st.rerun()
    else:
        st.info("Nenhuma compra salva ainda.")

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
    st.caption("<p style='text-align:center;'>Versão 4.0 Pro | Douglas Dev</p>", unsafe_allow_html=True)

# --- TELA 2: CALCULADORA ---
elif st.session_state.pagina == 'calculadora':
    st.title("🛒 Lista de Precisão")
    
    # 🎯 CONFIGURAÇÃO DE ORÇAMENTO
    with st.expander("🎯 DEFINIR META DE GASTO", expanded=True):
        orcamento = st.number_input("Qual o limite de hoje? (R$)", min_value=1.0, value=100.0, step=10.0)

    # 📦 FORMULÁRIO DE ENTRADA
    with st.form("add_item", clear_on_submit=True):
        produto = st.text_input("📦 Nome do Produto")
        col1, col2 = st.columns(2)
        with col1: qtd_txt = st.text_input("Qtd/Peso", value="1")
        with col2: prc_txt = st.text_input("Preço Unitário", placeholder="0,00")
        enviar = st.form_submit_button("➕ ADICIONAR")

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
        except: st.error("⚠️ Use apenas números e vírgula.")

    # 📊 CÁLCULOS E SEMÁFORO
    total = sum(item['valor'] for item in st.session_state.carrinho)
    progresso = min(total / orcamento, 1.0) if orcamento > 0 else 0
    
    if progresso < 0.7: cor, msg = "#2E7D32", "✅ DENTRO DA META"
    elif progresso < 1.0: cor, msg = "#FBC02D", "⚠️ ATENÇÃO: QUASE LÁ"
    else: cor, msg = "#D32F2F", "🚨 LIMITE ULTRAPASSADO!"

    # 🎨 PAINEL DE STATUS
    st.markdown(f"""
        <div style="background-color: {cor}; padding: 20px; border-radius: 15px; text-align: center; color: white; margin-top: 10px;">
            <p style="margin:0; font-weight:bold;">{msg}</p>
            <h1 style="margin:0;">R$ {total:.2f}</h1>
            <p style="margin:0; opacity: 0.8;">Meta: R$ {orcamento:.2f}</p>
        </div>
    """, unsafe_allow_html=True)
    st.progress(progresso)

    # 📝 LISTA DE ITENS E FERRAMENTAS
    if st.session_state.carrinho:
        st.write("### 📝 Itens na Lista:")
        for i in st.session_state.carrinho:
            st.markdown(f"""
                <div class="item-card">
                    <strong>{i['nome']}</strong><br>
                    {i['detalhe']} = <strong>R$ {i['valor']:.2f}</strong>
                </div>
            """, unsafe_allow_html=True)

        st.write("---")
        
        # WHATSAPP
        resumo = f"🛒 *Resumo SupSmart Pro*\n\n"
        for i in st.session_state.carrinho:
            resumo += f"• {i['nome']}: R$ {i['valor']:.2f}\n"
        resumo += f"\n💰 *TOTAL: R$ {total:.2f}*"
        
        link_wa = f"https://wa.me/?text={urllib.parse.quote(resumo)}"
        st.markdown(f"""<a href="{link_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; margin-bottom:10px;">ENVIAR LISTA ✅</div></a>""", unsafe_allow_html=True)
        
        # 🏁 FINALIZAR COMPRA (COM SALVAMENTO NO HISTÓRICO)
        if st.button("🏁 FINALIZAR COMPRA"):
            # Salva no histórico antes de limpar
            nova_compra = {
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "total": total,
                "itens": [f"{it['nome']} - R$ {it['valor']:.2f}" for it in st.session_state.carrinho]
            }
            st.session_state.historico.append(nova_compra)
            
            st.balloons()
            st.success(f"Excelente! Compra salva no histórico: R$ {total:.2f}")
            time.sleep(2)
            st.session_state.carrinho = []
            st.rerun()
            
        if st.sidebar.button("🗑️ Limpar Carrinho Atual"):
            st.session_state.carrinho = []
            st.rerun()
    else:
        st.info("Carrinho vazio. Comece a adicionar itens!")