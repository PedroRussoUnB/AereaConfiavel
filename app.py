import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from scipy.stats import binom
from scipy.stats import norm
import plotly.express as px
from PIL import Image
import os
import warnings
warnings.filterwarnings("ignore")

# Configuração da página
st.set_page_config(page_title="Análise de Distribuições de Probabilidade",
                   layout="wide",
                   initial_sidebar_state="expanded")

# Estilo verde do slider
st.markdown("""
    <style>
    .stSlider > div > div > div > div > div > div {
        background-color: #4CAF50 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Carregar logotipo
caminho_imagem = os.path.join(os.path.dirname(__file__), "Logo", "unb_logo.png")
logo_unb = Image.open(caminho_imagem)

# Cabeçalho com logotipo e título
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image(logo_unb, use_container_width=True)
with col2:
    st.markdown("<h1 style='text-align: center; color: #003366;'>Análise de Distribuições de Probabilidade</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #003366;'>Pedro Richetti Russo e Daniel Vianna</h3>", unsafe_allow_html=True)
with col3:
    st.image(logo_unb, use_container_width=True)

st.markdown("---")

# Abas
aba1, aba2, aba3 = st.tabs(["Overbooking", "Simulação de ROI", "Decisão e Análise Final"])

# ------------------------------- ABA 1 - OVERBOOKING ------------------------------
with aba1:
    st.header("Simulação de Overbooking (Binomial)")

    st.markdown("#### Cálculo de Risco de Overbooking com Cenários Personalizáveis")

    capacidade = st.number_input("Capacidade do avião (número de assentos)", min_value=100, max_value=200, value=120)
    assentos_vendidos = st.slider("Número de passagens vendidas", min_value=capacidade, max_value=capacidade + 30, value=130)
    p = st.slider("Probabilidade de comparecimento (p)", min_value=0.80, max_value=1.00, value=0.88, step=0.01)

    risco = 1 - binom.cdf(capacidade, assentos_vendidos, p)
    st.write(f"### Probabilidade de mais de {capacidade} passageiros aparecerem: **{risco*100:.2f}%**")

    st.markdown("#### Defina o Limite Máximo de Risco Aceitável (%)")
    risco_maximo = st.slider("Risco Máximo (%)", min_value=1, max_value=20, value=7)

    venda_range = np.arange(capacidade, capacidade + 21)
    probs = 1 - binom.cdf(capacidade, venda_range, p)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=venda_range, y=probs, mode='lines+markers', line=dict(color='#003366')))

    # Linha horizontal indicando o limite de risco no eixo Y
    fig.add_hline(y=risco_maximo / 100, line=dict(color='red', width=2, dash='dash'),
                  annotation_text=f"Limite {risco_maximo}%", annotation_position="bottom right")

    fig.update_layout(title="Probabilidade de Overbooking (mais passageiros que assentos)",
                      xaxis_title="Número de Passagens Vendidas",
                      yaxis_title="Probabilidade (%)",
                      yaxis=dict(range=[0, 1]),
                      plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

    tabela = pd.DataFrame({"Passagens Vendidas": venda_range, "Risco de Overbooking (%)": (probs * 100).round(2)})
    st.write("### Tabela de Riscos por Quantidade de Vendas")
    st.dataframe(tabela)

    limite_risco = tabela[tabela['Risco de Overbooking (%)'] <= risco_maximo]['Passagens Vendidas'].max()
    if pd.notna(limite_risco):
        st.success(f"Número máximo de passagens a serem vendidas com risco ≤ {risco_maximo}%: {limite_risco}")
    else:
        st.error("Nenhuma configuração está abaixo do risco definido.")

    # Análise Financeira
    st.markdown("#### Avaliação Financeira de Vendas Acima da Capacidade")
    excesso = st.slider("Quantas passagens acima da capacidade você quer simular?", min_value=1, max_value=30, value=10)
    custo_indenizacao = st.number_input("Custo médio por passageiro em overbooking (R$)", min_value=0, value=1000)
    receita_passagem = st.number_input("Receita por passagem extra vendida (R$)", min_value=0, value=500)

    risco_extra = 1 - binom.cdf(capacidade, capacidade + excesso, p)
    ganho_extra = receita_passagem * excesso
    perda_esperada = risco_extra * custo_indenizacao
    st.write(f"- Receita extra esperada: **R$ {ganho_extra:.2f}**")
    st.write(f"- Custo esperado com overbooking: **R$ {perda_esperada:.2f}**")

    if ganho_extra > perda_esperada:
        st.success("Compensa financeiramente vender essas passagens a mais.")
    else:
        st.warning("Não compensa financeiramente — o risco é maior que o ganho.")


# -------------------------- ABA 2 - ROI DO NOVO SISTEMA --------------------------
with aba2:
    st.header("Análise de ROI do Novo Sistema de Previsão de Demanda")

    investimento = st.slider("Investimento inicial (R$)", min_value=10000, max_value=100000, value=50000, step=1000)
    receita_estimada = st.slider("Receita estimada com o novo sistema (R$)", min_value=40000, max_value=100000, value=80000, step=1000)
    custo_operacional = st.slider("Custo operacional anual (R$)", min_value=0, max_value=50000, value=10000, step=1000)

    lucro = receita_estimada - custo_operacional
    roi = (lucro / investimento) * 100
    st.session_state["roi_percent"] = roi  # Salva o ROI para ser acessado na aba 3

    st.write(f"### ROI Esperado: **{roi:.2f}%**")

    st.markdown("#### Simulação de Cenários com Receita Variável")
    media = receita_estimada
    desvio = st.slider("Desvio padrão da receita simulada", min_value=1000, max_value=30000, value=10000, step=1000)
    simulacoes = st.slider("Número de simulações Monte Carlo", min_value=100, max_value=10000, value=1000, step=100)
    receita_limite = st.number_input("Defina um limite mínimo de receita para análise de risco (R$)", value=60000)

    receitas_simuladas = np.random.normal(loc=media, scale=desvio, size=simulacoes)
    lucros_simulados = receitas_simuladas - custo_operacional
    rois_simulados = (lucros_simulados / investimento) * 100

    prob_receita_baixa = (receitas_simuladas < receita_limite).mean() * 100
    st.write(f"Probabilidade da receita ficar abaixo de R$ {receita_limite:,.2f}: **{prob_receita_baixa:.2f}%**")

    fig = px.histogram(rois_simulados, nbins=30, title="Distribuição do ROI Simulado", labels={"value": "ROI (%)"})
    st.plotly_chart(fig, use_container_width=True)

    st.write("#### ROI em 3 cenários")
    st.write(f"- Otimista (percentil 90): {np.percentile(rois_simulados, 90):.2f}%")
    st.write(f"- Realista (média): {np.mean(rois_simulados):.2f}%")
    st.write(f"- Pessimista (percentil 10): {np.percentile(rois_simulados, 10):.2f}%")


# -------------------------- ABA 3 - DECISÃO FINAL --------------------------
with aba3:
    st.header("Decisão Estratégica Final")

    roi_percent = st.session_state.get("roi_percent", None)

    if roi_percent is None:
        st.warning("⚠️ O ROI ainda não foi calculado. Volte para a aba anterior e forneça os dados.")
    else:
        st.success(f"✅ ROI calculado com os dados fornecidos: **{roi_percent:.2f}%**")

        st.markdown("### 🎯 Defina o ROI que você considera satisfatório")
        roi_esperado = st.slider("ROI desejado (%)", min_value=0.0, max_value=300.0, value=25.0, step=0.5)

        # Cálculo da diferença percentual
        diferenca = roi_percent - roi_esperado
        proporcao = diferenca / roi_esperado if roi_esperado != 0 else 0

        # Gerar comentários automáticos com base na diferença proporcional
        if proporcao >= 0.5:
            comentario = (
                f"O ROI obtido ({roi_percent:.2f}%) está significativamente acima do desejado ({roi_esperado:.2f}%). "
                "Isso demonstra excelente desempenho do sistema, indicando forte viabilidade financeira. "
                "A empresa pode considerar expandir o investimento, testar novas rotas com maior flexibilidade e investir em IA para refinar as previsões de demanda."
            )
        elif proporcao >= 0.1:
            comentario = (
                f"O ROI obtido ({roi_percent:.2f}%) está acima do ROI esperado ({roi_esperado:.2f}%), "
                "o que é um indicativo saudável de retorno. A adoção do sistema é recomendada, e ajustes finos, como melhorias em coleta de dados e redução de custos operacionais, podem aumentar ainda mais o desempenho."
            )
        elif -0.1 <= proporcao < 0.1:
            comentario = (
                f"O ROI calculado ({roi_percent:.2f}%) está próximo ou igual ao ROI esperado ({roi_esperado:.2f}%), "
                "o que mostra que o sistema atende às expectativas. A decisão pode ser pela adoção com monitoramento contínuo e controle de riscos, principalmente quanto à sazonalidade da demanda."
            )
        elif -0.3 <= proporcao < -0.1:
            comentario = (
                f"O ROI calculado ({roi_percent:.2f}%) está moderadamente abaixo do ROI esperado ({roi_esperado:.2f}%). "
                "Isso exige cautela: ajustes nos custos operacionais ou maior segmentação de marketing podem ser necessários para atingir o retorno desejado."
            )
        else:
            comentario = (
                f"O ROI calculado ({roi_percent:.2f}%) está bem abaixo do ROI desejado ({roi_esperado:.2f}%). "
                "A adoção do sistema não é recomendada neste momento. Sugere-se revisar o modelo de previsão, reduzir despesas ou buscar parcerias estratégicas para viabilizar o investimento."
            )

        st.markdown("---")
        st.subheader("📌 Recomendação Gerada Automaticamente:")
        st.info(comentario)