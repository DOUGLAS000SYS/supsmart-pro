# BOTÃO FINAL E COMPARTILHAMENTO
    if st.button("🏁 Finalizar Compra"):
        st.balloons()
        
        # 1. Criar o texto para o WhatsApp
        texto_whats = f"🛒 *Resumo da Compra - SupSmart Pro*\n\n"
        for item in st.session_state.carrinho:
            texto_whats += f"• {item['nome']}: R$ {item['valor']:.2f}\n"
        texto_whats += f"\n💰 *TOTAL: R$ {total_geral:.2f}*"
        texto_whats += f"\n\n_\"Quem constrói a própria ferramenta, nunca fica à mercê da sorte.\"_"
        
        # 2. Gerar o link (Codificado para URL)
        import urllib.parse
        msg_codificada = urllib.parse.quote(texto_whats)
        link_whatsapp = f"https://wa.me/?text={msg_codificada}"

        # 3. Mostrar o Resumo e o Botão de Compartilhar
        st.markdown(f"""
            <div style="border: 2px solid #7B1FA2; border-radius: 15px; background-color: #f3e5f5; padding: 15px; text-align: center; margin-bottom: 10px;">
                <h2 style="color: #4A148C;">Total: R$ {total_geral:.2f}</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Botão verde estilo WhatsApp
        st.markdown(f"""
            <a href="{link_whatsapp}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #25D366; color: white; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 18px;">
                    Send to WhatsApp ✅
                </div>
            </a>
        """, unsafe_allow_html=True)