import streamlit as st
from datetime import datetime, timedelta
import urllib.parse

# Configuração da Página
st.set_page_config(page_title="SupSmart Pro", layout="centered", page_icon="🛒")

# Design Premium com Suporte a Modo Escuro
st.markdown('''
<style>
    :root { --bg-color: #F8F9FD; --card-bg: white; --text-main: #4A148C; }
    @media (prefers-color-scheme: dark) {
        :root { --bg-color: #121212; --card-bg: #1E1E1E; --text-main: #E1BEE7; }
    }
    .stApp { background-color: var(--bg-color); }
    .title-text { color: var(--text-main); font-weight: 800; font-size: 32px; text-align: center; }
    .card-inter { 
        background: linear-gradient(135deg, #6A1B9A 0%, #4A148C 100%); 
        color: white !important; padding: 25px; border-radius: 24px; 
        box-shadow: 0 10px 25px rgba(74, 20, 140, 0.3); margin-bottom: 20px;
    }
    .item-card {
        background: var(--card-bg); padding: 12px 16px; border-radius: 16px; 
        margin-bottom: 8px; display: flex; justify-content: space-between; 
        align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        border: 1px solid rgba(128,128,128,0.1);
    }
    .stButton>button { border-radius: 14px !important; font-weight: bold !important; height: 45px; }
</style>
''', unsafe_allow_html=True)

# Inicialização
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'historico' not in st.session_state: st.session_state.historico = []

# --- SIDEBAR: HISTÓRICO ---
st.sidebar.title("📚 Histórico")
busca = st.sidebar.text_input("🔍 Pesquisar", placeholder="Ex: Carne")
hist_filtrado = st.session_state.historico
if busca:
    hist_filtrado = [c for c in st.session_state.historico if any(busca.lower() in it['n'].lower() for it in c['itens'])]

for compra in hist_filtrado:
    with st.sidebar.expander(f"🛒 {compra['data']} (R$ {compra['total']:.2f})"):
        for it in compra['itens']:
            st.write(f"- {it['n']} ({it['q']}x R$ {it['p']:.2f})")

# --- CORPO PRINCIPAL ---
st.markdown('<div class="title-text">SupSmart Pro</div>', unsafe_allow_html=True)

orc = st.number_input("Orçamento R$", value=300.0)
gasto = sum(item['subtotal'] for item in st.session_state.carrinho)
saldo = orc - gasto
progresso = min(gasto / orc, 1.0) if orc > 0 else 0

st.markdown(f'''
<div class="card-inter">
    <p style="margin:0; font-size:12px; opacity:0.8; color:white !important;">TOTAL NO CARRINHO</p>
    <h1 style="margin:0; font-size:40px; color:white !important;">R$ {gasto:.2f}</h1>
    <div style="background:rgba(255,255,255,0.2); height:6px; border-radius:10px; margin: 15px 0;">
        <div style="background:white; width:{progresso*100}%; height:100%; border-radius:10px;"></div>
    </div>
    <p style="margin:0; color:white !important; font-size:14px;">Saldo: <b>R$ {saldo:.2f}</b></p>
</div>
''', unsafe_allow_html=True)

# Entrada
with st.container():
    nome = st.text_input("Produto", placeholder="Nome do item")
    col_q, col_p = st.columns(2)
    q_in = col_q.text_input("Qtd/Peso")
    p_in = col_p.text_input("Preço Unit/KG")
    
    if st.button("➕ ADICIONAR ITEM", use_container_width=True):
        try:
            q = float(q_in.replace(',','.')) if q_in else 1.0
            p = float(p_in.replace(',','.')) if p_in else 0.0
            if p > 0:
                st.session_state.carrinho.insert(0, {"n": nome or "Item", "q": q, "p": p, "subtotal": q*p})
                st.rerun()
            else: st.warning("Insira um preço.")
        except: st.error("Use apenas números.")

st.write("---")

# Lista
for i, item in enumerate(st.session_state.carrinho):
    col_i, col_d = st.columns([5, 1])
    with col_i:
        st.markdown(f'<div class="item-card"><span style="color:var(--text-main)">{item["n"]} (x{item["q"]})</span><b style="color:var(--text-main)">R$ {item["subtotal"]:.2f}</b></div>', unsafe_allow_html=True)
    with col_d:
        if st.button("✕", key=f"del_{i}"):
            st.session_state.carrinho.pop(i)
            st.rerun()

# Finalizar
if st.session_state.carrinho:
    if st.button("✅ FINALIZAR COMPRA", use_container_width=True):
        fuso_br = datetime.now() - timedelta(hours=3)
        agora = fuso_br.strftime("%d/%m/%Y %H:%M")
        st.session_state.historico.insert(0, {"data": agora, "itens": list(st.session_state.carrinho), "total": gasto})
        st.session_state.carrinho = []
        st.success("Compra Finalizada!")
        st.rerun()

    texto_whats = f"*Resumo SupSmart Pro*\n\n"
    for it in st.session_state.carrinho:
        texto_whats += f"• {it['n']}: R$ {it['subtotal']:.2f}\n"
    texto_whats += f"\n*Total: R$ {gasto:.2f}*"
    link_whats = f"https://wa.me/?text={urllib.parse.quote(texto_whats)}"
    st.markdown(f'''<a href="{link_whats}" target="_blank" style="text-decoration:none;">
        <div style="background-color:#25D366; color:white; padding:12px; border-radius:12px; text-align:center; font-weight:bold;">📲 ENVIAR PARA WHATSAPP</div>
    </a>''', unsafe_allow_html=True)
