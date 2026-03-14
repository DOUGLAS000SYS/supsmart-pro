import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta, timezone

# --- 1. FUNÇÕES DE APOIO ---
def get_agora_br():
    fuso_br = timezone(timedelta(hours=-3))
    return datetime.now(fuso_br).strftime("%d/%m/%Y %H:%M")

def get_db_connection():
    conn = sqlite3.connect('supsmart_pro.db', check_same_thread=False)
    cursor = conn.cursor()
    # Tabela de Compras
    cursor.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, total REAL, itens_qtd INTEGER, limite REAL)''')
    # Tabela de Detalhes
    cursor.execute('''CREATE TABLE IF NOT EXISTS itens_detalhes 
                 (compra_id INTEGER, nome TEXT, preco REAL, qtd REAL, cat TEXT, medida TEXT)''')
    
    # Reparo automático de colunas para evitar erros das imagens
    cursor.execute("PRAGMA table_info(compras)")
    colunas = [row[1] for row in cursor.fetchall()]
    if 'limite' not in colunas:
        cursor.execute("ALTER TABLE compras ADD COLUMN limite REAL DEFAULT 500.0")
    
    conn.commit()
    return conn

conn = get_db_connection()

# --- 2. CONFIGURAÇÃO UI ---
st.set_page_config(page_title="SupSmart Pro", layout="wide")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

st.title("SupSmart / Dashboard")

# --- 3. ÁREA DE ORÇAMENTO (DIRETA) ---
limite_input = st.number_input("Definir Meta de Gasto (R$):", min_value=0.0, value=500.0)
total_carrinho = sum(i['Total'] for i in st.session_state.carrinho)

c1, c2 = st.columns(2)
c1.metric("Total no Carrinho", f"R$ {total_carrinho:.2f}")
c2.metric("Meta", f"R$ {limite_input:.2f}", delta=f"Sobram: R$ {limite_input - total_carrinho:.2f}")

st.divider()

# --- 4. ENTRADA DE DADOS (VISÍVEL) ---
tab_mercado, tab_historico = st.tabs(["🛒 Comprar", "📜 Histórico"])

with tab_mercado:
    with st.form("add_item", clear_on_submit=True):
        col_nome, col_medida = st.columns([2, 1])
        nome = col_nome.text_input("Produto")
        medida = col_medida.radio("Tipo", ["Un", "Kg"], horizontal=True)
        
        col_q, col_p, col_c = st.columns(3)
        qtd = col_q.number_input("Qtd", min_value=0.01, value=1.0)
        preco = col_p.number_input("Preço Unitário", min_value=0.0, step=0.01)
        cat = col_c.selectbox("Categoria", ["Alimentos", "Limpeza", "Higiene", "Bebidas", "Outros"])
        
        if st.form_submit_button("➕ ADICIONAR ITEM"):
            if nome and preco > 0:
                st.session_state.carrinho.append({
                    "Item": nome, "Qtd": qtd, "Preço": preco, 
                    "Total": qtd * preco, "Categoria": cat, "Medida": medida
                })
                st.rerun()

    if st.session_state.carrinho:
        st.write("### Itens no Carrinho")
        df_car = pd.DataFrame(st.session_state.carrinho)
        st.dataframe(df_car, use_container_width=True)
        
        if st.button("✅ FINALIZAR COMPRA", type="primary", use_container_width=True):
            cur = conn.cursor()
            data_atual = get_agora_br()
            
            # Salva na tabela compras
            cur.execute("INSERT INTO compras (data, total, itens_qtd, limite) VALUES (?, ?, ?, ?)", 
                        (data_atual, total_carrinho, len(st.session_state.carrinho), limite_input))
            compra_id = cur.lastrowid
            
            # Salva na tabela detalhes (evita KeyError das imagens)
            for i in st.session_state.carrinho:
                cur.execute("INSERT INTO itens_detalhes VALUES (?, ?, ?, ?, ?, ?)", 
                            (compra_id, i['Item'], i['Preço'], i['Qtd'], i['Categoria'], i['Medida']))
            
            conn.commit()
            st.session_state.carrinho = []
            st.success(f"Compra finalizada em {data_atual}!")
            st.balloons()
            st.rerun()

with tab_historico:
    df_compras = pd.read_sql("SELECT * FROM compras ORDER BY id DESC", conn)
    if not df_compras.empty:
        st.dataframe(df_compras, use_container_width=True, hide_index=True)
        
        id_ver = st.number_input("Ver Detalhes (ID):", min_value=1, step=1)
        if st.button("Buscar Itens"):
            detalhes = pd.read_sql(f"SELECT nome as Item, preco as 'R$', qtd, medida as Tipo FROM itens_detalhes WHERE compra_id = {int(id_ver)}", conn)
            if not detalhes.empty:
                st.table(detalhes)
            else:
                st.error("Nenhum item encontrado para este ID.")