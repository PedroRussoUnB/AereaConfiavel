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
    st.markdown("<h3 style='text-align: center; color: #003366;'>Pedro Richetti Russo</h3>", unsafe_allow_html=True)
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

    st.markdown("#### Calcular o número máximo de vendas com risco limite")
    risco_limite_usuario = st.slider("Defina o risco máximo aceitável (%)", min_value=1, max_value=20, value=7)
    tabela_risco_limite = pd.DataFrame({
        "Passagens Vendidas": np.arange(capacidade, capacidade + 31),
        "Risco de Overbooking (%)": (1 - binom.cdf(capacidade, np.arange(capacidade, capacidade + 31), p)) * 100
    })
    limite_risco = tabela_risco_limite[tabela_risco_limite['Risco de Overbooking (%)'] <= risco_limite_usuario]['Passagens Vendidas'].max()
    if pd.notna(limite_risco):
        st.success(f"Máximo de passagens com risco ≤ {risco_limite_usuario}%: {limite_risco}")
    else:
        st.error("Nenhuma configuração atende ao limite de risco informado.")

    # Gráfico
    st.markdown("#### Variação da Probabilidade de Overbooking com Diferentes Quantidades Vendidas")
    venda_range = np.arange(capacidade, capacidade + 21)
    probs = 1 - binom.cdf(capacidade, venda_range, p)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=venda_range, y=probs, mode='lines+markers', line=dict(color='#003366')))
    fig.update_layout(title="Probabilidade de Overbooking (mais passageiros que assentos)",
                      xaxis_title="Número de Passagens Vendidas",
                      yaxis_title="Probabilidade (%)",
                      yaxis=dict(range=[0, 1]),
                      plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

    tabela = pd.DataFrame({"Passagens Vendidas": venda_range, "Risco de Overbooking (%)": (probs * 100).round(2)})
    st.write("### Tabela de Riscos por Quantidade de Vendas")
    st.dataframe(tabela)

    # Análise Financeira
    st.markdown("#### Avaliação Financeira de Venda de Passagens Adicionais")
    passagens_extra = st.slider("Quantas passagens além da capacidade vender?", min_value=1, max_value=30, value=10)
    custo_indenizacao = st.number_input("Custo médio por passageiro em overbooking (R$)", min_value=0, value=1000)
    receita_passagem = st.number_input("Receita por passagem extra vendida (R$)", min_value=0, value=500)

    risco_n = 1 - binom.cdf(capacidade, capacidade + passagens_extra, p)
    ganho_extra = receita_passagem * passagens_extra
    perda_esperada = risco_n * custo_indenizacao

    st.write(f"- Receita extra esperada: **R$ {ganho_extra:.2f}**")
    st.write(f"- Custo esperado com overbooking: **R$ {perda_esperada:.2f}**")

    if ganho_extra > perda_esperada:
        st.success("Compensa financeiramente vender essas passagens a mais.")
    else:
        st.warning("Não compensa — o risco supera o ganho.")

# -------------------------- ABA 2 - ROI DO NOVO SISTEMA --------------------------
with aba2:
    st.header("Análise de ROI do Novo Sistema de Previsão de Demanda")

    investimento = st.slider("Investimento inicial (R$)", min_value=10000, max_value=100000, value=50000, step=1000)
    receita_estimada = st.slider("Receita estimada com o novo sistema (R$)", min_value=40000, max_value=100000, value=80000, step=1000)
    custo_operacional = st.slider("Custo operacional anual (R$)", min_value=0, max_value=50000, value=10000, step=1000)

    lucro = receita_estimada - custo_operacional
    roi = (lucro / investimento) * 100
    st.write(f"### ROI Esperado: **{roi:.2f}%**")

    # Simulação Monte Carlo
    st.markdown("#### Simulação de Cenários com Receita Variável")
    media = receita_estimada
    desvio = st.slider("Desvio padrão da receita simulada", min_value=1000, max_value=30000, value=10000, step=1000)
    simulacoes = st.slider("Número de simulações Monte Carlo", min_value=100, max_value=10000, value=1000, step=100)

    receitas_simuladas = np.random.normal(loc=media, scale=desvio, size=simulacoes)
    lucros_simulados = receitas_simuladas - custo_operacional
    rois_simulados = (lucros_simulados / investimento) * 100

    limite_receita = st.slider("Defina um valor de referência para receita mínima aceitável (R$)", min_value=40000, max_value=100000, value=60000, step=1000)
    prob_receita_baixa = (receitas_simuladas < limite_receita).mean() * 100
    st.write(f"Probabilidade da receita ficar abaixo de R$ {limite_receita}: **{prob_receita_baixa:.2f}%**")

    fig = px.histogram(rois_simulados, nbins=30, title="Distribuição do ROI Simulado", labels={"value": "ROI (%)"})
    st.plotly_chart(fig, use_container_width=True)

    st.write("#### ROI em 3 cenários")
    st.write(f"- Otimista (percentil 90): {np.percentile(rois_simulados, 90):.2f}%")
    st.write(f"- Realista (média): {np.mean(rois_simulados):.2f}%")
    st.write(f"- Pessimista (percentil 10): {np.percentile(rois_simulados, 10):.2f}%")

# -------------------------- ABA 3 - DECISÃO FINAL --------------------------
with aba3:
    st.header("Decisão Estratégica Final")

    st.markdown("""
    Com base nas análises realizadas:

    - A **probabilidade de overbooking** pode ser gerenciada com ajustes finos no número de passagens vendidas e acompanhamento da taxa de comparecimento.
    - A **análise financeira** indica que vender além da capacidade pode gerar lucro **desde que o risco esperado de indenizações esteja sob controle**.
    - O **novo sistema de previsão** apresenta um ROI médio interessante, mas **com variações significativas** dependendo do comportamento da receita.

    ✅ **Você recomendaria a adoção imediata do sistema?**

    Selecione sua sugestão com base nos dados:
    """)

    decisao = st.radio("Baseado na simulação, qual seria sua decisão para a Aérea Confiável?", [
        "Adotar o sistema imediatamente",
        "Adotar com monitoramento e ajustes",
        "Adiar e revisar estratégia de vendas ou custos"
    ])

    st.write("---")
    st.subheader("Comentário Técnico-Financeiro")
    if decisao == "Adotar o sistema imediatamente":
        st.success("A análise de ROI médio e os percentis demonstram boa viabilidade. O sistema deve melhorar a eficiência de vendas e reduzir incertezas.")
    elif decisao == "Adotar com monitoramento e ajustes":
        st.info("A distribuição do ROI mostra riscos moderados. Recomendamos implantar o sistema com acompanhamento mensal e ajustes em estratégias de venda conforme os dados reais.")
    else:
        st.warning("Como a receita apresenta grande variabilidade e há risco elevado de prejuízo, sugerimos reavaliar os custos operacionais ou estratégias de venda antes de adotar o sistema.")
