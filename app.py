import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURAÇÃO E NOVO ESTILO CLEAN ---
st.set_page_config(page_title="SupSmart Pro", page_icon="📊", layout="centered")

# CSS para mudar totalmente o visual (Clean/Neumorfismo Light)
st.markdown("""
<style>
    /* Fundo Principal e Texto Base */
    .stApp { background-color: #F4F7F6; color: #333; }
    h1, h2, h3, h4 { color: #2C3E50; font-family: 'Poppins', sans-serif; }
    
    /* Novo Card de Item (Clean) */
    .item-card {
        background: white;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #2ECC71;
        margin-bottom: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        color: #333;
    }
    
    /* Cards de Status Superiores (Com Gradiente) */
    .stat-card {
        background: linear-gradient(135deg, #00B09B, #96C93D);
        color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center; margin-bottom: 10px;
    }
    
    /* Botões Limpos e Modernos */
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3em;
        background-color: #2ECC71; color: white; font-weight: bold;
        border: none; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #27AE60; border: none; color: white; }
    
    /* Inputs */
    input { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. LÓGICA DE DADOS ---
if 'pagina' not in st.session_state: st.session_state.pagina = 'home'
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'historico' not in st.session_state: st.session_state.historico = []

def mudar_pagina(nome):
    st.session_state.pagina = nome
    st.rerun()

# --- TELA 1: HOME (VISUAL REINVENTADO) ---
if st.session_state.pagina == 'home':
    st.image("banner.png", use_container_width=True)
    st.markdown("<h1 style='text-align: center;'>SupSmart Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7F8C8D;'>A inteligência financeira do seu mercado.</p>", unsafe_allow_html=True)
    st.write("##")
    
    # 1. CARDS DE STATUS (IGUAL À IMAGEM)
    col1, col2, col3 = st.columns(3)
    total_compra = sum(i['valor'] for i in st.session_state.carrinho)
    gasto_mensal = sum(h['total'] for h in st.session_state.historico) if st.session_state.historico else 0.0

    with col1:
        st.markdown(f'<div class="stat-card" style="background: linear-gradient(135deg, #27AE60, #2ECC71);">Total Compra<br><h3>R$ {total_compra:.2f}</h3></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card" style="background: linear-gradient(135deg, #2980B9, #3498DB);">Itens Lista<br><h3>{len(st.session_state.carrinho)}</h3></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card" style="background: linear-gradient(135deg, #8E44AD, #9B59B6);">Gasto Mensal<br><h3>R$ {gasto_mensal:.2f}</h3></div>', unsafe_allow_html=True)

    # 2. GRÁFICO NA HOME (Prioridade Visual)
    if st.session_state.carrinho:
        df_pizza = pd.DataFrame(st.session_state.carrinho)
        fig_pizza = px.pie(df_pizza, values='valor', names='segmento', hole=.4, title="Distribuição da Compra Atual")
        # Ajuste de cores para o visual clean
        fig_pizza.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pizza, use_container_width=True)

    st.write("##")
    
    # 3. BOTÕES DE AÇÃO
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 INICIAR NOVA COMPRA", use_container_width=True): mudar_pagina('calculadora')
    with c2:
        if st.button("📜 VER HISTÓRICO COMPRAS", use_container_width=True): mudar_pagina('historico')

    st.write("---")
    st.caption("<center>Douglas Dev System | v7.0 Clean Edition</center>", unsafe_allow_html=True)

# --- TELA 2: CALCULADORA (VISUAL CLEAN) ---
elif st.session_state.pagina == 'calculadora':
    st.markdown("### 🛒 Calculadora Inteligente")
    
    with st.container():
        orcamento = st.number_input("Quanto pretende gastar hoje? (R$)", min_value=0.0, value=100.0)
        
        with st.form("add_item", clear_on_submit=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                nome = st.text_input("📦 Produto", placeholder="Ex: Alcatra, Arroz...")
            with col2:
                tipo_medida = st.radio("Medida", ["Un", "Kg"], horizontal=True)
            with col3:
                qtd = st.number_input("Qtd / Peso", min_value=0.01, value=1.0, step=0.01)
                
            col4, col5 = st.columns(2)
            with col4:
                preco = st.number_input("Preço Unitário", min_value=0.0, value=0.0, step=0.01)
            with col5:
                seg = st.selectbox("🏷️ Segmento", ["Açougue", "Bebidas", "Limpeza", "Hortifruti", "Padaria", "Matinais", "Higiene", "Outros"])
            
            if st.form_submit_button("➕ ADICIONAR ITEM"):
                if nome:
                    st.session_state.carrinho.append({
                        "nome": nome, "qtd": qtd, "medida": tipo_medida, "valor": qtd * preco, "segmento": seg
                    })
                    st.rerun()

    # TOTAIS E SEMÁFORO (NOVO ESTILO)
    total = sum(item['valor'] for item in st.session_state.carrinho)
    progresso = min(total / orcamento, 1.0) if orcamento > 0 else 0
    # Cores Claras para o semáforo
    cor_bar = "#2ECC71" if progresso < 0.8 else "#F1C40F" if progresso < 1.0 else "#E74C3C"
    
    st.markdown(f"""
        <div style='background: {cor_bar}; padding: 15px; border-radius: 12px; text-align: center; margin-top: 10px; color: white;'>
            <h2 style='margin:0; color: white;'>Total: R$ {total:.2f}</h2>
            <small>Meta: R$ {orcamento:.2f}</small>
        </div>
    """, unsafe_allow_html=True)
    st.progress(progresso)

    # Lista de Itens Estilizada
    st.write("##")
    if st.session_state.carrinho:
        for item in reversed(st.session_state.carrinho):
            st.markdown(f"""
                <div class="item-card">
                    <div style="display: flex; justify-content: space-between;">
                        <b>{item['nome']}</b>
                        <span style="color: #27AE60; font-weight: bold;">R$ {item['valor']:.2f}</span>
                    </div>
                    <small style="color: #7F8C8D;">{item['segmento']} | {item['qtd']}{item['medida']} x R$ {item['valor']/item['qtd']:.2f}</small>
                </div>
            """, unsafe_allow_html=True)

        st.write("---")
        
        # FINALIZAR E SALVAR HISTÓRICO
        if st.button("✅ FINALIZAR COMPRA E SALVAR"):
            # Salva no histórico
            resumo = {
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "total": total,
                "itens": len(st.session_state.carrinho)
            }
            st.session_state.historico.append(resumo)
            # Limpa o carrinho
            st.session_state.carrinho = []
            st.balloons()
            st.success("Compra salva no histórico!")
            mudar_pagina('home')
            
        if st.button("🗑️ LIMPAR LISTA ATUAL"):
            st.session_state.carrinho = []
            st.rerun()

    if st.sidebar.button("⬅️ VOLTAR PARA HOME"): mudar_pagina('home')

# --- TELA 3: HISTÓRICO (VISUAL CLEAN) ---
elif st.session_state.pagina == 'historico':
    st.markdown("### 📜 Histórico de Compras")
    
    if not st.session_state.historico:
        st.info("Nenhuma compra finalizada ainda.")
    else:
        # Gráfico de Gasto Mensal (Barras)
        df_hist = pd.DataFrame(st.session_state.historico)
        fig_bar = px.bar(df_hist, x='data', y='total', title="Evolução do Gasto Mensal")
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
        fig_bar.update_traces(marker_color='#2980B9')
        st.plotly_chart(fig_bar, use_container_width=True)

        # Cards do Histórico
        for compa in reversed(st.session_state.historico):
            st.markdown(f"""
            <div class="item-card" style="border-left: 5px solid #2980B9;">
                <div style="display: flex; justify-content: space-between;">
                    <b>{compa['data']}</b>
                    <span style="font-weight: bold;">R$ {compa['total']:.2f}</span>
                </div>
                <small style="color: #7F8C8D;">{compa['itens']} itens</small>
            </div>
            """, unsafe_allow_html=True)
            
    if st.button("🗑️ LIMPAR TODO HISTÓRICO"):
        st.session_state.historico = []
        st.rerun()
        
    if st.sidebar.button("⬅️ VOLTAR PARA HOME"): mudar_pagina('home')