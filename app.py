import streamlit as st
import urllib.parse
import time
import plotly.express as px
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SupSmart Pro", page_icon="logo.png", layout="centered")

if 'pagina' not in st.session_state: st.session_state.pagina = 'home'
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'historico' not in st.session_state: st.session_state.historico = []

def mudar_pagina(nome):
    st.session_state.pagina = nome
    st.rerun()

# --- FUNÇÃO PARA GERAR PDF ---
def gerar_pdf(carrinho, total, orcamento, df_agrupado):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "SupSmart Pro - Relatório de Compra", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 10, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(10)

    # Resumo Financeiro
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, f"Total da Compra: R$ {total:.2f}", ln=True)
    pdf.cell(190, 10, f"Orçamento Estipulado: R$ {orcamento:.2f}", ln=True)
    pdf.ln(5)

    # Lista de Itens
    pdf.set_font("Arial", "B", 11)
    pdf.cell(90, 10, "Produto", 1)
    pdf.cell(50, 10, "Segmento", 1)
    pdf.cell(50, 10, "Valor", 1, ln=True)
    
    pdf.set_font("Arial", "", 10)
    for item in carrinho:
        pdf.cell(90, 10, item['nome'], 1)
        pdf.cell(50, 10, item['segmento'], 1)
        pdf.cell(50, 10, f"R$ {item['valor']:.2f}", 1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "Análise de Gastos por Segmento:", ln=True)
    
    # Adicionando os dados do gráfico em formato de texto no PDF
    for index, row in df_agrupado.iterrows():
        percentual = (row['valor'] / total) * 100
        pdf.set_font("Arial", "", 10)
        pdf.cell(190, 8, f"- {row['segmento']}: R$ {row['valor']:.2f} ({percentual:.1f}%)", ln=True)

    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 2. ESTILO CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #7B1FA2; color: white; font-weight: bold; }
    .item-card { background-color: white; padding: 12px; border-radius: 10px; border-left: 6px solid #7B1FA2; margin-bottom: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- TELA CALCULADORA ---
if st.session_state.pagina == 'calculadora':
    st.title("🛒 SupSmart Pro - Inteligente")
    
    with st.sidebar:
        if st.button("⬅️ Início"): mudar_pagina('home')
        st.write("---")
        st.subheader("📜 Histórico")
        for h in reversed(st.session_state.historico): st.caption(f"{h['data']} - R$ {h['total']:.2f}")

    orcamento = st.sidebar.number_input("Meta de Gasto (R$)", min_value=1.0, value=100.0)

    with st.form("add_item", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1: produto = st.text_input("📦 Item")
        with col2: segmento = st.selectbox("🏷️ Segmento", ["Matinais", "Bebidas", "Açougue", "Limpeza", "Higiene", "Hortifruti", "Outros"])
        c1, c2 = st.columns(2)
        with c1: q_t = st.text_input("Qtd", "1")
        with c2: p_t = st.text_input("Preço", "0.00")
        if st.form_submit_button("➕ ADICIONAR"):
            try:
                val = float(q_t.replace(',','.')) * float(p_t.replace(',','.'))
                st.session_state.carrinho.append({"nome": produto, "valor": val, "segmento": segmento})
                st.rerun()
            except: st.error("Erro nos valores")

    total = sum(i['valor'] for i in st.session_state.carrinho)
    st.metric("Total Atual", f"R$ {total:.2f}", delta=f"{total-orcamento:.2f}" if total > orcamento else None, delta_color="inverse")

    if st.session_state.carrinho:
        df = pd.DataFrame(st.session_state.carrinho)
        df_agrupado = df.groupby("segmento")["valor"].sum().reset_index()
        
        # Gráfico de Pizza
        fig = px.pie(df_agrupado, values='valor', names='segmento', hole=.4, title="Distribuição de Gastos")
        st.plotly_chart(fig, use_container_width=True)
        
        # Gerar o PDF
        pdf_bytes = gerar_pdf(st.session_state.carrinho, total, orcamento, df_agrupado)
        
        st.download_button(
            label="📄 BAIXAR RELATÓRIO PDF",
            data=pdf_bytes,
            file_name=f"compra_{datetime.now().strftime('%d_%m_%Y')}.pdf",
            mime="application/pdf"
        )

        if st.button("🏁 FINALIZAR COMPRA"):
            st.session_state.historico.append({"data": datetime.now().strftime("%d/%m/%Y"), "total": total})
            st.session_state.carrinho = []
            st.balloons()
            time.sleep(2)
            st.rerun()
else:
    st.image("banner.png", use_container_width=True)
    if st.button("🚀 INICIAR"): mudar_pagina('calculadora')