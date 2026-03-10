import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import matplotlib.pyplot as plt

# --- 1. CONFIGURAÇÕES ---
st.set_page_config(page_title="SupSmart", page_icon="🛒", layout="centered")

if 'carrinho' not in st.session_state: st.session_state.carrinho = []

# --- 2. FUNÇÃO GERADORA DE PDF (COM GRÁFICO DENTRO) ---
def exportar_pdf(df, total, orcamento):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Simples
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "RESUMO DE COMPRA - SUPSMART", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 10, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    
    # Tabela de Itens
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
    pdf.cell(190, 10, f"TOTAL PAGO: R$ {total:.2f} (Meta: R$ {orcamento:.2f})", ln=True)
    
    # GERAÇÃO DO GRÁFICO PARA O PDF
    pdf.ln(10)
    pdf.cell(190, 10, "ANALISE DE GASTOS (POR SEGMENTO):", ln=True)
    
    # Criando o gráfico de pizza em memória (sem mostrar na tela do app)
    df_pizza = df.groupby("segmento")["valor"].sum()
    plt.figure(figsize=(6, 4))
    plt.pie(df_pizza, labels=df_pizza.index, autopct='%1.1f%%', startangle=140, colors=['#7B1FA2', '#FFC107', '#2E7D32', '#D32F2F', '#1976D2'])
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    
    # Inserindo a imagem do gráfico no PDF
    pdf.image(img_buf, x=50, y=pdf.get_y() + 5, w=110)
    plt.close()

    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 3. INTERFACE (DESIGN LIMPO) ---
st.markdown("<h3 style='text-align: center; color: #4A148C;'>SupSmart</h3>", unsafe_allow_html=True)

# ORÇAMENTO NO TOPO (A PRIMEIRA COISA)
orcamento = st.number_input("Quanto você pode gastar hoje? (R$)", min_value=0.0, value=100.0)

# FORMULÁRIO DE ENTRADA
with st.form("novo_item", clear_on_submit=True):
    col1, col2 = st.columns([2, 1])
    with col1: nome = st.text_input("📦 Nome do Produto")
    with col2: segmento = st.selectbox("🏷️ Tipo", ["Matinais", "Bebidas", "Açougue", "Limpeza", "Hortifruti", "Padaria", "Outros"])
    
    c1, c2 = st.columns(2)
    with c1: qtd = st.text_input("Quantidade", value="1")
    with c2: preco = st.text_input("Preço Unitário", value="0.00")
    
    if st.form_submit_button("ADICIONAR À LISTA"):
        try:
            valor_final = float(qtd.replace(',','.')) * float(preco.replace(',','.'))
            st.session_state.carrinho.append({"nome": nome, "valor": valor_final, "segmento": segmento})
            st.rerun()
        except: st.error("Erro nos valores!")

# EXIBIÇÃO DA LISTA E TOTALIZADORES
total = sum(item['valor'] for item in st.session_state.carrinho)
progresso = min(total / orcamento, 1.0) if orcamento > 0 else 0
cor = "green" if progresso < 0.7 else "orange" if progresso < 1.0 else "red"

st.markdown(f"<h2 style='text-align: center; color: {cor};'>Total: R$ {total:.2f}</h2>", unsafe_allow_html=True)
st.progress(progresso)

if st.session_state.carrinho:
    st.write("---")
    df_lista = pd.DataFrame(st.session_state.carrinho)
    
    for i, item in enumerate(st.session_state.carrinho):
        st.write(f"**{item['nome']}** ({item['segmento']}) - R$ {item['valor']:.2f}")

    st.write("---")
    
    # BOTÕES DE AÇÃO
    col_pdf, col_limpar = st.columns(2)
    
    with col_pdf:
        # GERA O PDF COM O GRÁFICO SÓ QUANDO CLICA
        dados_pdf = exportar_pdf(df_lista, total, orcamento)
        st.download_button("📄 GERAR PDF COM GRÁFICO", data=dados_pdf, file_name="compra_supsmart.pdf", mime="application/pdf")

    with col_limpar:
        if st.button("🗑️ LIMPAR TUDO"):
            st.session_state.carrinho = []
            st.rerun()