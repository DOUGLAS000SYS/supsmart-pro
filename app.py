import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURAÇÃO E ESTILO (CORREÇÃO DE CORES) ---
st.set_page_config(page_title="SupSmart Pro", page_icon="📊", layout="centered")

st.markdown("""
<style>
    /* Fundo e Texto Principal */
    .stApp { background-color: #F4F7F6; color: #333; }
    
    /* CORREÇÃO DOS INPUTS: Texto escuro para ser visível no fundo claro */
    input, select, textarea { color: #333 !important; background-color: white !important; }
    label { color: #2C3E50 !important; font-weight: bold !important; }

    /* Cards de Status (Inspirados na imagem) */
    .stat-card {
        color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center; margin-bottom: 10px;
    }
    
    /* Cards de Itens na Lista */
    .item-card {
        background: white; padding: 15px; border-radius: 12px;
        border-left: 5px solid #2ECC71; margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. LÓGICA DE NAVEGAÇÃO E DADOS ---
if 'pagina' not in st.session_state: st.session_state.pagina = 'home'
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'historico' not in st.session_state: st.session_state.historico = []

def mudar_pagina(nome):
    st.session_state.pagina = nome
    st.rerun()

# --- TELA 1: PAINEL HOME ---
if st.session_state.pagina == 'home':
    st.image("banner.png", use_container_width=True)
    st.markdown("<h1 style='text-align: center;'>Painel Inteligente</h1>", unsafe_allow_html=True)
    
    # Linha de Cards (Status da Compra)
    c1, c2, c3 = st.columns(3)
    total_atual = sum(i['valor'] for i in st.session_state.carrinho)
    gasto_total_hist = sum(h['total'] for h in st.session_state.historico)

    with c1:
        st.markdown(f'<div class="stat-card" style="background: linear-gradient(135deg, #27AE60, #2ECC71);">Total Atual<br><h3>R$ {total_atual:.2f}</h3></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card" style="background: linear-gradient(135deg, #2980B9, #3498DB);">Itens<br><h3>{len(st.session_state.carrinho)}</h3></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card" style="background: linear-gradient(135deg, #8E44AD, #9B59B6);">Histórico<br><h3>R$ {gasto_total_hist:.2f}</h3></div>', unsafe_allow_html=True)

    # Gráfico de Categorias (Plotly)
    if st.session_state.carrinho:
        df = pd.DataFrame(st.session_state.carrinho)
        fig = px.pie(df, values='valor', names='segmento', hole=.4, title="Distribuição de Gastos")
        st.plotly_chart(fig, use_container_width=True)

    st.write("##")
    if st.button("🚀 INICIAR / CONTINUAR COMPRA"): mudar_pagina('calculadora')
    if st.button("📜 VER HISTÓRICO COMPLETO"): mudar_pagina('historico')

# --- TELA 2: CALCULADORA ---
elif st.session_state.pagina == 'calculadora':
    st.markdown("### 🛒 Calculadora de Mercado")
    
    with st.form("novo_item", clear_on_submit=True):
        nome = st.text_input("📦 Nome do Produto")
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1: tipo = st.radio("Medida", ["Un", "Kg"], horizontal=True)
        with c2: qtd = st.number_input("Qtd/Peso", min_value=0.01, value=1.0, step=0.01)
        with c3: preco = st.number_input("Preço Unit/Kg", min_value=0.0, value=0.0, step=0.01)
        seg = st.selectbox("🏷️ Categoria", ["Açougue", "Hortifruti", "Limpeza", "Bebidas", "Padaria", "Outros"])
        
        if st.form_submit_button("➕ ADICIONAR ITEM"):
            if nome:
                st.session_state.carrinho.append({"nome": nome, "valor": qtd * preco, "segmento": seg, "qtd": qtd, "med": tipo})
                st.rerun()

    # Totalizador
    total = sum(i['valor'] for i in st.session_state.carrinho)
    st.markdown(f"<div style='background: #2ECC71; color: white; padding: 15px; border-radius: 10px; text-align: center;'><h2>Total: R$ {total:.2f}</h2></div>", unsafe_allow_html=True)

    # Exibição dos Itens
    for item in reversed(st.session_state.carrinho):
        st.markdown(f'<div class="item-card"><b>{item["nome"]}</b><br><small>{item["qtd"]}{item["med"]} - R$ {item["valor"]:.2f}</small></div>', unsafe_allow_html=True)

    if st.button("✅ FINALIZAR E SALVAR COMPRA"):
        if st.session_state.carrinho:
            st.session_state.historico.append({"data": datetime.now().strftime("%d/%m %H:%M"), "total": total})
            st.session_state.carrinho = []
            st.success("Compra salva!")
            mudar_pagina('home')

    if st.sidebar.button("⬅️ VOLTAR"): mudar_pagina('home')

# --- TELA 3: HISTÓRICO ---
elif st.session_state.pagina == 'historico':
    st.markdown("### 📜 Suas Últimas Compras")
    for h in reversed(st.session_state.historico):
        st.markdown(f'<div class="item-card" style="border-left-color: #2980B9;"><b>{h["data"]}</b><br>Total: R$ {h["total"]:.2f}</div>', unsafe_allow_html=True)
    
    if st.sidebar.button("⬅️ VOLTAR"): mudar_pagina('home')