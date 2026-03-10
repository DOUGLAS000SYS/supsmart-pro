import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import matplotlib.pyplot as plt

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="SupSmart Pro", page_icon="🛒", layout="centered")

if 'pagina' not in st.session_state: st.session_state.pagina = 'home'
if 'carrinho' not in st.session_state: st.session_state.carrinho = []

def mudar_pagina(nome):
    st.session_state.pagina = nome
    st.rerun()

# --- FUNÇÃO DO PDF ---
def exportar_pdf(df, total, orcamento):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "RESUMO DE COMPRA - SUPSMART PRO", ln=True, align="C")
        
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(90, 10, "Item", 1)
        pdf.cell(50, 10, "Segmento", 1)
        pdf.cell(50, 10, "Valor", 1, ln=True)
        
        pdf.set_font("Arial", "", 11)
        for _, row in df.iterrows():
            pdf.cell(90, 10, str(row['nome'])[:30], 1)
            pdf.cell(50, 10, str(row['segmento']), 1)
            pdf.cell(50, 10, f"R$ {row['valor']:.2f}", 1, ln=True)
            
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, f"TOTAL: R$ {total:.2f} | META: R$ {orcamento:.2f}", ln=True)

        # Gráfico de Pizza no PDF
        df_pizza = df.groupby("segmento")["valor"].sum()
        plt.figure(figsize=(6, 4))
        plt.pie(df_pizza, labels=df_pizza.index, autopct='%1.1f%%', startangle=140)
        
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        pdf.image(img_buf, x=50, y=pdf.get_y() + 10, w=110)
        plt.close()

        # Retorna o PDF como bytes (usando latin-1 para evitar erro de encoding)
        return pdf.output(dest='S').encode('latin-1', 'replace')
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")
        return None

# --- INTERFACE ---

# TELA 1: HOME (RESTAURADA)
if st.session_state.pagina == 'home':
    st.image("banner.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center;'>Bem-vindo ao SupSmart Pro</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 MODO VISITANTE", use_container_width=True):
            mudar_pagina('calculadora')
    with col2:
        if st.button("🌐 ENTRAR COM GOOGLE", use_container_width=True):
            st.toast("Em breve: Login Google!")
    
    st.markdown("---")
    st.caption("<p style='text-align:center;'>Douglas Dev | v5.2 Elite</p>", unsafe_allow_html=True)

# TELA 2: CALCULADORA (FOCO NO CLIENTE)
elif st.session_state.pagina == 'calculadora':
    st.markdown("<h4 style='text-align: center;'>🛒 SupSmart</h4>", unsafe_allow_html=True)
    
    orcamento = st.number_input("Defina seu limite (R$)", min_value=0.0, value=100.0)

    with st.form("add_item", clear_on_submit=True):
        col_a, col_b = st.columns([2, 1])
        with col_a: nome = st.text_input("📦 Produto")
        with col_b: seg = st.selectbox("🏷️ Tipo", ["Matinais", "Bebidas", "Açougue", "Limpeza", "Hortifruti", "Outros"])
        c1, c2 = st.columns(2)
        with c1: q = st.text_input("Qtd", "1")
        with c2: p = st.text_input("Preço", "0.00")
        if st.form_submit_button("ADICIONAR"):
            try:
                v = float(q.replace(',','.')) * float(p.replace(',','.'))
                st.session_state.carrinho.append({"nome": nome, "valor": v, "segmento": seg})
                st.rerun()
            except: st.error("Valor inválido!")

    total = sum(i['valor'] for i in st.session_state.carrinho)
    st.markdown(f"<h2 style='text-align: center;'>Total: R$ {total:.2f}</h2>", unsafe_allow_html=True)

    if st.session_state.carrinho:
        df_l = pd.DataFrame(st.session_state.carrinho)
        for i in st.session_state.carrinho:
            st.write(f"• **{i['nome']}**: R$ {i['valor']:.2f}")

        st.write("---")
        c_pdf, c_sair = st.columns(2)
        with c_pdf:
            pdf_bytes = exportar_pdf(df_l, total, orcamento)
            if pdf_bytes:
                st.download_button("📄 BAIXAR PDF + GRÁFICO", data=pdf_bytes, file_name="compra_supsmart.pdf", mime="application/pdf")
        with c_sair:
            if st.button("⬅️ VOLTAR / SAIR"):
                st.session_state.carrinho = []
                mudar_pagina('home')