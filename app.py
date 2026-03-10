import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import matplotlib.pyplot as plt

# --- 1. CONFIGURAÇÕES ---
st.set_page_config(page_title="SupSmart", page_icon="🛒", layout="centered")

if 'pagina' not in st.session_state: st.session_state.pagina = 'home'
if 'carrinho' not in st.session_state: st.session_state.carrinho = []

def mudar_pagina(nome):
    st.session_state.pagina = nome
    st.rerun()

# --- 2. FUNÇÃO GERADORA DE PDF (CORRIGIDA) ---
def exportar_pdf(df, total, orcamento):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "RESUMO DE COMPRA - SUPSMART", ln=True, align="C")
        
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(90, 10, "Item", 1)
        pdf.cell(50, 10, "Segmento", 1)
        pdf.cell(50, 10, "Valor", 1, ln=True)
        
        pdf.set_font("Arial", "", 11)
        for _, row in df.iterrows():
            pdf.cell(90, 10, str(row['nome']), 1)
            pdf.cell(50, 10, str(row['segmento']), 1)
            pdf.cell(50, 10, f"R$ {row['valor']:.2f}", 1, ln=True)
            
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, f"TOTAL PAGO: R$ {total:.2f}", ln=True)
        
        # Gráfico no PDF
        df_pizza = df.groupby("segmento")["valor"].sum()
        plt.figure(figsize=(6, 4))
        plt.pie(df_pizza, labels=df_pizza.index, autopct='%1.1f%%', startangle=140)
        
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        pdf.image(img_buf, x=50, y=pdf.get_y() + 5, w=110)
        plt.close()

        return pdf.output(dest='S').encode('latin-1', 'replace')
    except Exception as e:
        return None

# --- 3. INTERFACE ---

# TELA 1: HOME (BOTÕES DE VOLTA)
if st.session_state.pagina == 'home':
    st.image("banner.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: #4A148C;'>Bem-vindo ao SupSmart</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 MODO VISITANTE", use_container_width=True):
            mudar_pagina('calculadora')
    with col2:
        if st.button("🌐 ENTRAR COM GOOGLE", use_container_width=True):
            st.toast("Em breve: Sincronização em nuvem!")
    
    st.caption("<p style='text-align:center;'>Douglas Dev | v5.1 Elite</p>", unsafe_allow_html=True)

# TELA 2: CALCULADORA
elif st.session_state.pagina == 'calculadora':
    st.markdown("<h3 style='text-align: center; color: #4A148C;'>SupSmart</h3>", unsafe_allow_html=True)
    
    orcamento = st.number_input("Quanto você pode gastar hoje? (R$)", min_value=0.0, value=100.0)

    with st.form("novo_item", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1: nome = st.text_input("📦 Nome do Produto")
        with col2: segmento = st.selectbox("🏷️ Tipo", ["Matinais", "Bebidas", "Açougue", "Limpeza", "Hortifruti", "Padaria", "Outros"])
        c1, c2 = st.columns(2)
        with c1: qtd = st.text_input("Quantidade", value="1")
        with c2: preco = st.text_input("Preço Unitário", value="0.00")
        if st.form_submit_button("ADICIONAR À LISTA"):
            try:
                v = float(qtd.replace(',','.')) * float(preco.replace(',','.'))
                st.session_state.carrinho.append({"nome": nome, "valor": v, "segmento": segmento})
                st.rerun()
            except: st.error("Erro nos valores!")

    total = sum(item['valor'] for item in st.session_state.carrinho)
    st.markdown(f"<h2 style='text-align: center;'>Total: R$ {total:.2f}</h2>", unsafe_allow_html=True)

    if st.session_state.carrinho:
        df_lista = pd.DataFrame(st.session_state.carrinho)
        for i, item in enumerate(st.session_state.carrinho):
            st.write(f"**{item['nome']}** ({item['segmento']}) - R$ {item['valor']:.2f}")

        st.write("---")
        
        c_pdf, c_limpar = st.columns(2)
        with c_pdf:
            pdf_bytes = exportar_pdf(df_lista, total, orcamento)
            if pdf_bytes:
                st.download_button("📄 GERAR PDF", data=pdf_bytes, file_name="compra.pdf", mime="application/pdf")
        with c_limpar:
            if st.button("🗑️ LIMPAR TUDO"):
                st.session_state.carrinho = []
                st.rerun()
    
    if st.sidebar.button("⬅️ Sair"): mudar_pagina('home')