import streamlit as st

# --- 1. CONFIGURAÇÃO PROFISSSIONAL ---
st.set_page_config(
    page_title="SupSmart Pro",
    page_icon="logo.png", # O seu escudo (Conceito 3)
    layout="centered"
)

# --- 2. INICIALIZAÇÃO DE MEMÓRIA (Session State) ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'home'

# --- 3. ESTILIZAÇÃO CUSTOMIZADA (O Roxo Premium) ---
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; font-weight: bold; background-color: #7B1FA2; color: white; }
    .titulo-principal { text-align: center; color: #4A148C; font-size: 40px; font-weight: 900; margin-bottom: 0px; }
    .frase-sucesso { text-align: center; font-style: italic; color: #6A1B9A; padding: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 4. LÓGICA DE NAVEGAÇÃO ---
def mudar_pagina(nome_da_pagina):
    st.session_state.pagina = nome_da_pagina
    st.rerun()

# --- TELA A: BOAS-VINDAS ---
if st.session_state.pagina == 'home':
    st.image("banner.png", use_container_width=True) # Sua imagem de capa
    st.markdown('<p class="titulo-principal">SupSmart Pro</p>', unsafe_allow_html=True)
    st.write("---")
    
    st.subheader("Bem-vindo ao seu controle total.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 MODO VISITANTE"):
            mudar_pagina('calculadora')
    with col2:
        if st.button("🌐 CONECTAR GOOGLE"):
            st.toast("Em breve: Sincronização em Nuvem!")

    st.info("O modo visitante salva seus dados apenas durante esta sessão.")

# --- TELA B: CALCULADORA (Onde a mágica acontece) ---
elif st.session_state.pagina == 'calculadora':
    if st.button("⬅️ Sair / Trocar Usuário"):
        mudar_pagina('home')

    st.title("🛒 Sua Lista de Precisão")
    
    # --- AQUI VOCÊ COLA O CÓDIGO DA CALCULADORA QUE DEU CERTO NO MERCADO ---
    st.write("Insira aqui seus inputs de nome, peso e preço...")
    
    # --- O BOTÃO FINAL COM A SUA FRASE ---
    if st.button("Finalizar Compra"):
        st.balloons()
        st.markdown("""
            <div style="border: 2px solid #7B1FA2; border-radius: 15px; background-color: #f3e5f5; padding: 15px; text-align: center;">
                <h4 style="color: #4A148C;">"Quem constrói a própria ferramenta, nunca fica à mercê da sorte."</h4>
            </div>
        """, unsafe_allow_html=True)