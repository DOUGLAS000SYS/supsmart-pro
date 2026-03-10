import streamlit as st
import urllib.parse
import time
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SupSmart Pro", page_icon="🛒", layout="centered")

if 'pagina' not in st.session_state: st.session_state.pagina = 'home'
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'historico' not in st.session_state: st.session_state.historico = []

def mudar_pagina(nome):
    st.session_state.pagina = nome
    st.rerun()

# --- FUNÇÃO GERADORA DE PDF (Com Resumo de Gastos) ---
def gerar_pdf_com_analise(carrinho, total, orcamento):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Relatório de Compra Inteligente", ln=True, align="C")
    pdf.ln(5)
    
    # Resumo rápido
    pdf.set_font("Arial", "", 12)
    pdf.cell(190, 8, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.cell(190, 8, f"Total Pago: R$ {total:.2f}", ln=True)
    pdf.cell(190, 8, f"Meta Estipulada: R$ {orcamento:.2f}", ln=True)
    pdf.ln(10)

    # Tabela de Itens
    pdf.set_font("Arial", "B", 10)
    pdf.cell(80, 8, "Item", 1)
    pdf.cell(50, 8, "Segmento", 1)
    pdf.cell(60, 8, "Subtotal", 1, ln=True)
    
    pdf.set_font("Arial", "", 10)
    df = pd.DataFrame(carrinho)
    for index, row in df.iterrows():
        pdf.cell(80, 8, row['nome'], 1)
        pdf.cell(50, 8, row['segmento'], 1)
        pdf.cell(60, 8, f"R$ {row['valor']:.2f}", 1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "Distribuição por Segmento (Onde foi seu dinheiro):", ln=True)
    
    # Análise de Segmentos (Substitui o gráfico visual por dados precisos no PDF)
    df_agrupado = df.groupby("segmento")["valor"].sum().reset_index()
    for _, row in df_agrupado.iterrows():
        perc = (row['valor'] / total) * 100
        pdf.set_font("Arial", "", 11)
        pdf.cell(190, 8, f"- {row['segmento']}: R$ {row['valor']:.2f} ({perc:.1f}%)", ln=True)

    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 2. ESTILO CSS (Design Clean) ---
st.markdown("""
    <style>
    .main-title { font-size: 24px !important; color: #4A148C; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .stButton>button { border-radius: 8px; height: 3em; font-weight: bold; }
    .card { background-color: #f9f9f9; padding: 15px; border-radius: 10px; border-left: 5px solid #7B1FA2; margin-bottom: 10px; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# --- TELA CALCULADORA ---
if st.session_state.pagina == 'calculadora':
    st.markdown('<p class="main-title">🛒 SupSmart Pro</p>', unsafe_allow_html=True)
    
    # ORÇAMENTO DE VOLTA NA TELA PRINCIPAL
    orcamento = st.number_input("Quanto pretende gastar hoje? (R$)", min_value=1.0, value=100.0)
    
    with st.form("form_item", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        with c1: prod = st.text_input("📦 Nome do Produto")
        with c2: seg = st.selectbox("🏷️ Segmento", ["Matinais", "Bebidas", "Açougue", "Limpeza", "Higiene", "Hortifruti", "Padaria", "Outros"])
        
        c3, c4 = st.columns(2)
        with c3: q_t = st.text_input("Quantidade", "1")
        with c4: p_t = st.text_input("Preço Unitário", "0.00")
        
        if st.form_submit_button("➕ ADICIONAR ITEM"):
            try:
                v = float(q_t.replace(',','.')) * float(p_t.replace(',','.'))
                st.session_state.carrinho.append({"nome": prod, "valor": v, "segmento": seg})
                st.rerun()
            except: st.error("⚠️ Digite valores válidos.")

    # TOTAIS E SEMÁFORO
    total = sum(i['valor'] for i in st.session_state.carrinho)
    prog = min(total / orcamento, 1.0) if orcamento > 0 else 0
    cor_bar = "green" if prog < 0.7 else "orange" if prog < 1.0 else "red"
    
    st.subheader(f"Total: R$ {total:.2f}")
    st.progress(prog)

    # LISTA DE ITENS
    if st.session_state.carrinho:
        for i in st.session_state.carrinho:
            st.markdown(f'<div class="card"><b>{i["nome"]}</b> ({i["segmento"]})<br>Subtotal: R$ {i["valor"]:.2f}</div>', unsafe_allow_html=True)

        st.write("---")
        
        # OPÇÕES DE FINALIZAÇÃO
        col_wa, col_pdf = st.columns(2)
        
        with col_wa:
            texto_wa = f"🛒 *Resumo SupSmart*\nTotal: R$ {total:.2f}"
            link = f"https://wa.me/?text={urllib.parse.quote(texto_wa)}"
            st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; height:3em; background:#25D366; color:white; border:none; border-radius:8px; font-weight:bold;">ENVIAR WHATSAPP</button></a>', unsafe_allow_html=True)
        
        with col_pdf:
            pdf_data = gerar_pdf_com_analise(st.session_state.carrinho, total, orcamento)
            st.download_button("📄 GERAR PDF", data=pdf_data, file_name="compra_supsmart.pdf", mime="application/pdf")

        if st.button("🏁 FINALIZAR COMPRA E LIMPAR"):
            st.session_state.historico.append({"data": datetime.now().strftime("%d/%m"), "total": total})
            st.session_state.carrinho = []
            st.balloons()
            time.sleep(2)
            st.rerun()
    
    if st.sidebar.button("⬅️ Sair"): mudar_pagina('home')

else:
    st.image("banner.png", use_container_width=True)
    st.markdown('<p class="main-title">Bem-vindo ao SupSmart Pro</p>', unsafe_allow_html=True)
    if st.button("🚀 INICIAR NOVA LISTA"): mudar_pagina('calculadora')