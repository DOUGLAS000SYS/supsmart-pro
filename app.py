import streamlit as st
import urllib.parse

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="SupSmart Pro", page_icon="logo.png", layout="centered")

if 'pagina' not in st.session_state: st.session_state.pagina = 'home'
if 'carrinho' not in st.session_state: st.session_state.carrinho = []

def mudar_pagina(n): 
    st.session_state.pagina = n
    st.rerun()

# Estilo dos Cards
st.markdown("<style>.stButton>button { width: 100%; border-radius: 10px; background-color: #7B1FA2; color: white; font-weight: bold; } .item-card { background-color: white; padding: 12px; border-radius: 10px; border-left: 6px solid #7B1FA2; margin-bottom: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); color: black; }</style>", unsafe_allow_html=True)

# --- HOME ---
if st.session_state.pagina == 'home':
    st.image("banner.png", use_container_width=True)
    st.markdown("<h1 style='text-align:center; color:#4A148C;'>SupSmart Pro</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("🚀 MODO VISITANTE"): mudar_pagina('calculadora')
    with c2: 
        if st.button("🌐 CONECTAR GOOGLE"): st.toast("Em breve!")

# --- CALCULADORA ---
elif st.session_state.pagina == 'calculadora':
    if st.sidebar.button("⬅️ Sair"): mudar_pagina('home')
    st.title("🛒 Lista de Precisão")
    
    # META DE GASTO
    with st.expander("🎯 CONFIGURAR ORÇAMENTO", expanded=True):
        orcamento = st.number_input("Quanto pretende gastar? (R$)", min_value=1.0, value=100.0)

    # FORMULÁRIO
    with st.form("add", clear_on_submit=True):
        prod = st.text_input("📦 Produto")
        c1, c2 = st.columns(2)
        with c1: q_t = st.text_input("Qtd", value="1")
        with c2: p_t = st.text_input("Preço", placeholder="0,00")
        if st.form_submit_button("➕ ADICIONAR"):
            try:
                q, p = float(q_t.replace(',','.')), float(p_t.replace(',','.'))
                st.session_state.carrinho.append({"n": prod if prod else "Item", "v": q*p, "d": f"{q}x R${p:.2f}"})
                st.rerun()
            except: st.error("Erro nos números!")

    # LÓGICA DO SEMÁFORO
    total = sum(i['v'] for i in st.session_state.carrinho)
    prog = min(total/orcamento, 1.0) if orcamento > 0 else 0
    
    if prog < 0.7: cor, msg = "#2E7D32", "✅ DENTRO DA META"
    elif prog < 1.0: cor, msg = "#FBC02D", "⚠️ QUASE NO LIMITE"
    else: cor, msg = "#D32F2F", "🚨 LIMITE ULTRAPASSADO!"

    # PAINEL DE STATUS
    st.markdown(f"""
        <div style='background-color:{cor}; padding:20px; border-radius:15px; text-align:center; color:white;'>
            <p style='margin:0;'>{msg}</p>
            <h1 style='margin:0;'>R$ {total:.2f}</h1>
            <small>Sua meta: R$ {orcamento:.2f}</small>
        </div>
    """, unsafe_allow_html=True)
    st.progress(prog)

    # LISTA DE ITENS
    if st.session_state.carrinho:
        st.write("### 📝 Itens na Lista")
        for i in st.session_state.carrinho:
            st.markdown(f"<div class='item-card'><b>{i['n']}</b><br>{i['d']} = <b>R$ {i['v']:.2f}</b></div>", unsafe_allow_html=True)
        
        # WHATSAPP
        texto = f"🛒 *Resumo SupSmart Pro*\nTotal: R$ {total:.2f}\nMeta: R$ {orcamento:.2f}"
        link = f"https://wa.me/?text={urllib.parse.quote(texto)}"
        st.markdown(f"<a href='{link}' target='_blank' style='text-decoration:none;'><div style='background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;'>ENVIAR WHATSAPP ✅</div></a>", unsafe_allow_html=True)
        
        if st.sidebar.button("🗑️ Limpar Lista"):
            st.session_state.carrinho = []
            st.rerun()