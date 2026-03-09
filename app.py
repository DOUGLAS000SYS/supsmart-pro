import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="SupSmart Pro",
    page_icon="logo.png",
    layout="centered"
)

# --- 2. INICIALIZAÇÃO DE MEMÓRIA (Session State) ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'home'
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

def mudar_pagina(nome):
    st.session_state.pagina = nome
    st.rerun()

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #7B1FA2; color: white; font-weight: bold; }
    .titulo { text-align: center; color: #4A148C; }
    .card-item { border: 1px solid #ddd; padding: 10px; border-radius: 10px; margin-bottom: 5px; background: #fff; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DAS TELAS ---

# TELA 1: BOAS-VINDAS
if st.session_state.pagina == 'home':
    st.image("banner.png", use_container_width=True)
    st.markdown("<h1 class='titulo'>SupSmart Pro</h1>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 MODO VISITANTE"):
            mudar_pagina('calculadora')
    with col2:
        if st.button("🌐 CONECTAR GOOGLE"):
            st.toast("Em breve: Sincronização em Nuvem!")
    st.caption("Desenvolvido por Douglas | Versão 2.0")

# TELA 2: CALCULADORA (O Motor do Mercado)
elif st.session_state.pagina == 'calculadora':
    if st.sidebar.button("⬅️ Sair"):
        mudar_pagina('home')

    st.title("🛒 Lista de Precisão")
    
    # --- ENTRADA DE DADOS (Seu motor de agilidade) ---
    with st.container():
        produto = st.text_input("📦 Nome do Produto", placeholder="Ex: Arroz")
        col_tipo, col_val = st.columns([1, 1])
        
        with col_tipo:
            tipo = st.radio("Tipo", ["Unidade (x)", "Peso (KG)"])
        with col_val:
            qtd_txt = st.text_input("Qtd / Peso", value="1")
            prc_txt = st.text_input("Preço Unit / KG", placeholder="0,00")

    if st.button("➕ ADICIONAR AO CARRINHO"):
        try:
            # Converte vírgula para ponto para o código entender
            qtd = float(qtd_txt.replace(',', '.'))
            prc = float(prc_txt.replace(',', '.'))
            subtotal = qtd * prc
            
            st.session_state.carrinho.append({
                "nome": produto if produto else "Item s/ nome",
                "detalhe": f"{qtd} x R$ {prc:.2f}",
                "valor": subtotal
            })
            st.success(f"Adicionado: R$ {subtotal:.2f}")
        except:
            st.error("Ops! Digite números válidos nos campos de valor.")

    # --- EXIBIÇÃO DO CARRINHO ---
    st.write("---")
    total_geral = sum(item['valor'] for item in st.session_state.carrinho)
    
    st.metric("TOTAL NO CARRINHO", f"R$ {total_geral:.2f}")

    if st.session_state.carrinho:
        with st.expander("Ver itens da lista"):
            for idx, item in enumerate(st.session_state.carrinho):
                st.write(f"**{item['nome']}** - {item['detalhe']} = **R$ {item['valor']:.2f}**")
        
        if st.button("🗑️ Limpar Carrinho"):
            st.session_state.carrinho = []
            st.rerun()

    # BOTÃO FINAL
    if st.button("🏁 Finalizar Compra"):
        st.balloons()
        st.markdown(f"""
            <div style="border: 2px solid #7B1FA2; border-radius: 15px; background-color: #f3e5f5; padding: 15px; text-align: center;">
                <h2 style="color: #4A148C;">Total: R$ {total_geral:.2f}</h2>
                <p>"Quem constrói a própria ferramenta, nunca fica à mercê da sorte."</p>
            </div>
        """, unsafe_allow_html=True)