# Projeto Desenvolvido na Data Science Academy

"""Pagina Home — Landing page principal da Tech Store Brasil."""

import streamlit as st


def dsa_render_home():
    """Renderiza a pagina Home."""

    # --- CSS customizado ---
    st.markdown("""
    <style>
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 0.3rem;
    }
    .hero-sub {
        font-size: 1.15rem;
        color: #888;
        margin-bottom: 2rem;
    }
    .bar-gradient {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        border-radius: 12px;
    }
    .metrics-bar {
        display: flex;
        justify-content: center;
        gap: 3rem;
        padding: 1.2rem 2rem;
    }
    .metric-item {
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #fff;
        margin: 0;
        line-height: 1.2;
    }
    .stat-label {
        font-size: 0.82rem;
        color: #ddd;
        margin: 0;
    }
    .feature-card {
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .feature-icon {
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    .feature-title {
        font-size: 1rem;
        font-weight: 600;
        color: #fff;
        margin-bottom: 0.3rem;
    }
    .feature-desc {
        font-size: 0.82rem;
        color: #ddd;
    }
    .step-number {
        display: inline-block;
        width: 32px;
        height: 32px;
        line-height: 32px;
        border-radius: 50%;
        background: #4A90D9;
        color: white;
        font-weight: 700;
        text-align: center;
        font-size: 0.9rem;
        margin-bottom: 0.4rem;
    }
    .cta-section {
        padding: 2.5rem 2rem;
        text-align: center;
        margin-top: 1.5rem;
    }
    .cta-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 0.3rem;
    }
    .cta-sub {
        font-size: 0.95rem;
        color: #ddd;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Hero ---
    st.markdown('<p class="hero-title">Tech Store Brasil</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">'
        'Eletrônicos de ponta com atendimento inteligente 24h. '
        'Cinco agentes de IA especializados prontos para ajudar você.'
        '</p>',
        unsafe_allow_html=True,
    )

    # --- Métricas ---
    st.markdown(
        '<div class="bar-gradient"><div class="metrics-bar">'
        '<div class="metric-item"><p class="stat-number">30+</p><p class="stat-label">Produtos no catálogo</p></div>'
        '<div class="metric-item"><p class="stat-number">5</p><p class="stat-label">Agentes de IA</p></div>'
        '<div class="metric-item"><p class="stat-number">24/7</p><p class="stat-label">Atendimento disponível</p></div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("")

    # --- Features ---
    st.markdown("#### O que diferencia este projeto?")
    f1, f2, f3, f4 = st.columns(4)

    features = [
        ("🛒", "Catálogo Completo - Portal de E-commerce",
         "Smartphones, notebooks, tablets, acessórios e smart home"),
        ("🤖", "IA Especializada",
         "Cada tipo de dúvida é atendido por um agente treinado para aquele assunto"),
        ("📚", "Base de Conhecimento",
         "Respostas fundamentadas nas políticas oficiais da loja via RAG"),
        ("👤", "Atendimento Humano",
         "Transferência para atendente com protocolo quando necessário"),
    ]

    for col, (icon, title, desc) in zip([f1, f2, f3, f4], features):
        with col:
            st.markdown(
                f'<div class="bar-gradient feature-card">'
                f'<div class="feature-icon">{icon}</div>'
                f'<div class="feature-title">{title}</div>'
                f'<div class="feature-desc">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("")

    # --- Como funciona ---
    st.markdown("#### Como funciona")
    s1, s2, s3, s4 = st.columns(4)

    steps = [
        ("1", "Você pergunta", "Sobre produtos, pedidos, trocas ou qualquer dúvida"),
        ("2", "Roteador classifica", "O agente roteador identifica a intenção da sua mensagem"),
        ("3", "Especialista responde", "O agente ideal é acionado com acesso a dados reais"),
        ("4", "Resposta precisa", "Você recebe uma resposta contextualizada em segundos"),
    ]

    for col, (num, title, desc) in zip([s1, s2, s3, s4], steps):
        with col:
            st.markdown(f'<div class="step-number">{num}</div>', unsafe_allow_html=True)
            st.markdown(f"**{title}**")
            st.caption(desc)

    st.markdown("")

    # --- CTA ---
    st.markdown(
        '<div class="bar-gradient cta-section">'
        '<p class="cta-title">Pronto para experimentar?</p>'
        '<p class="cta-sub">Converse com nossos Agentes de IA e veja a diferença de um atendimento personalizado com IA.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    _, center, _ = st.columns([2, 3, 2])
    with center:
        if st.button("Iniciar conversa com IA", type="primary", use_container_width=True):
            st.session_state["navigate_to"] = "Chat com IA"
            st.rerun()
