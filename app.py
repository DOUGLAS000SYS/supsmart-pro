# --- 5. LISTA DE COMPRAS (DASHBOARD) ---
st.markdown("### 📋 Itens na Lista")

# AQUI ESTAVA O ERRO: Adicione os dois-pontos no final da linha 96
if st.session_state.carrinho:
    df_c = pd.DataFrame(st.session_state.carrinho)
    st.dataframe(df_c[['nome', 'qtd', 'valor', 'cat']], use_container_width=True)
    
    col_f, col_l = st.columns(2)
    with col_f:
        if st.button("✅ FINALIZAR COMPRA", type="primary", use_container_width=True):
            salvar_compra(total_carrinho, st.session_state.carrinho)
            st.session_state.carrinho = []
            st.balloons()
            st.rerun()
    with col_l:
        if st.button("🗑️ LIMPAR LISTA", use_container_width=True):
            st.session_state.carrinho = []
            st.rerun()
else:
    st.info("Aguardando seu primeiro item para gerar o dashboard...")