import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA (O que aparece na aba do navegador) ---
st.set_page_config(
    page_title="SupSmart Pro",
    page_icon="logo.png",  # Seu escudo roxo!
    layout="centered"
)

# --- 2. GERENCIAMENTO DE NAVEGAÇÃO (Memória do App) ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'home'

def mudar_pagina(nome):
    st.session_state.pagina = nome
    st.rerun()

# --- 3. ESTILO VISUAL (Roxo Premium) ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-color: #7B1FA2;
        color: white;
        font-weight: bold;
        border: none;
    }
    .titulo {
        text-align: center;
        color: #4A148C;
        font-family: 'sans-serif';
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DAS TELAS ---

# TELA 1: BOAS-VINDAS
if st.session_state.pagina == 'home':
    st.image("banner.png", use_container_width=True)
    st.markdown("<h1 class='titulo'>SupSmart Pro</h1>", unsafe_allow_html=True)
    st.write("---")
    
    st.subheader("Seu controle total, do carrinho ao caixa.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 MODO VISITANTE"):
            mudar_pagina('calculadora')
    with col2:
        if st.button("🌐 CONECTAR GOOGLE"):
            st.toast("Em breve: Sincronização em Nuvem!")

    st.caption("Desenvolvido por Douglas | Versão 2.0 Profissional")

# TELA 2: CALCULADORA (Onde a mágica acontece)
elif st.session_state.pagina == 'calculadora':
    if st.sidebar.button("⬅️ Sair"):
        mudar_pagina('home')

    st.title("🛒 Sua Lista de Precisão")
    
    # ---------------------------------------------------------
    # ESPAÇO PARA O SEU CÓDIGO DO MERCADO (COLE ABAIXO)
    # ---------------------------------------------------------
    st.info("Sua calculadora está ativa!")
    
    # Exemplo de onde você coloca seus inputs e cálculos:
    # nome = st.text_input("Produto")
    # preco = st.number_input("Preço", min_value=0.0)
    
    # ---------------------------------------------------------
    
    # BOTÃO DE FINALIZAÇÃO COM A SUA FRASE DE PROSPERIDADE
    if st.button("Finalizar Compra"):
        st.balloons()
        st.markdown("""
            <div style="border: 2px solid #7B1FA2; border-radius: 15px; background-color: #f3e5f5; padding: 15px; text-align: center;">
                <h3 style="color: #4A148C;">"Quem constrói a própria ferramenta, nunca fica à mercê da sorte."</h3>
            </div>
        """, unsafe_allow_html=True)