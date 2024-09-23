import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from statsmodels.tsa.holtwinters import ExponentialSmoothing 
from statsmodels.tsa.arima.model import ARIMA
import graphviz as gv
import matplotlib.colors as mcolors
import math

# ===============================
# Configuração da Página 
# ===============================
st.set_page_config(
    page_title="Entrada",
    layout="wide"  
)

# ===============================
# Sidebar - Barra Lateral 
# ===============================
st.sidebar.markdown("""---""")

# Usando o caminho absoluto para carregar a imagem
image_path = 'app.png'
image = Image.open(image_path)
st.sidebar.image(image, width=190)

st.sidebar.markdown("""
    <h1 style='display: inline; font-size: 28px;'>LeanFlow</h1>
    <h2 style='display: inline; font-size: 18px;'>➤</h2>
    """, unsafe_allow_html=True)
st.sidebar.markdown('### Simplificando fluxos, melhorando vidas')
st.sidebar.markdown("""---""")

# ===============================
# Upload dos arquivos
# ===============================
uploaded_files = st.sidebar.file_uploader("Upload de múltiplos arquivos", accept_multiple_files=True, type=["xlsx"])

# Mensagem condicional: se nenhum arquivo for carregado, exibe a mensagem
if not uploaded_files:
    st.warning("Faça o upload dos templates para que os gráficos sejam gerados.")

# Listar os arquivos enviados
data_dict = {}  # Dicionário para armazenar os DataFrames

if uploaded_files:
    st.sidebar.write("Arquivos enviados:")
    for uploaded_file in uploaded_files:
        st.sidebar.write(uploaded_file.name)
        # Ler o arquivo e armazenar no dicionário
        df = pd.read_excel(uploaded_file)
        data_dict[uploaded_file.name] = df

st.sidebar.markdown("""---""")

# ===================================
# Filtros interativos para a Tab 1
# ===================================
df_filtered = None  # Variável de controle para os gráficos

# Verificar se o arquivo "amostra_pacientes_hora.xlsx" foi carregado
if 'amostra_pacientes_hora.xlsx' in data_dict:
    df_pacientes_hora = data_dict['amostra_pacientes_hora.xlsx']

    # Certificar que a coluna 'Data' seja datetime
    df_pacientes_hora['Data'] = pd.to_datetime(df_pacientes_hora['Data'], format='%Y-%m-%d')

    # Definir o valor mínimo e máximo para o slider de datas
    min_date = df_pacientes_hora['Data'].min().date()  
    max_date = df_pacientes_hora['Data'].max().date()  

    # Filtro interativo de data
    selected_dates = st.sidebar.slider(
        'Selecione o intervalo de datas',
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        format='DD-MM-YYYY'
    )
    # Filtrar o dataframe com base nas datas selecionadas
    df_filtered = df_pacientes_hora[(df_pacientes_hora['Data'].dt.date >= selected_dates[0]) & 
                                    (df_pacientes_hora['Data'].dt.date <= selected_dates[1])]
else:
    st.warning("O arquivo 'amostra_pacientes_hora.xlsx' não foi carregado.")

st.sidebar.markdown("""---""")

st.sidebar.markdown('##### Desenvolvido por [@FranciscoPena](https://www.linkedin.com/in/franciscobpena/) & [@DanielMeireles](https://www.linkedin.com/in/daniel-meireles-processos/) 🤓')

# ===============================
# Corpo principal da página - Upload das medições
# ===============================
st.header("🏥Visão Analítica por:")

# Criando as guias (tabs)
tab1, = st.tabs(['🚶‍➡️ Entrada de Pacientes'])

# ============================
# Exibindo os gráficos na Tab1
# ============================
if 'amostra_pacientes_hora.xlsx' in data_dict and df_filtered is not None:
    with tab1:
        try:
            df_filtered['Hora'] = pd.to_datetime(df_filtered['Hora'], format='%H:%M:%S')
        except ValueError:
            df_filtered['Hora'] = pd.to_datetime(df_filtered['Hora'], format='%H:%M')

        df_filtered['Hora_Agrupada'] = df_filtered['Hora'].dt.strftime('%H:%M')

        # Agrupar os dados para somar a quantidade de pacientes por hora e por turno
        df_grouped = df_filtered.groupby(['Hora_Agrupada', 'Turno'])['Quantidade de Pacientes'].sum().reset_index()

        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                # Plotar gráfico de barras com dados consolidados
                fig_bar = px.bar(
                    df_grouped, 
                    x='Hora_Agrupada', 
                    y='Quantidade de Pacientes', 
                    color='Turno', 
                    title="Quantidade de Pacientes por Hora (Acumulado)",
                    labels={'Hora_Agrupada': 'Hora', 'Quantidade de Pacientes': 'Qtd Pacientes'},
                    category_orders={'Turno': ['1', '2', '3', '4']}
                )
                fig_bar.update_layout(
                    xaxis=dict(tickmode='linear', tick0=0, dtick=1),
                    xaxis_title="Hora",
                    yaxis_title="Quantidade de Pacientes",
                    legend_title="Turnos"
                )
                st.plotly_chart(fig_bar)

            with col2:
                fig_box = px.box(
                    df_filtered, 
                    x='Turno', 
                    y='Quantidade de Pacientes', 
                    title="Boxplot: Pacientes por Turno"
                )
                fig_box.update_layout(
                    xaxis_title="Turno", 
                    yaxis_title="Quantidade de Pacientes"
                )
                st.plotly_chart(fig_box)

        with st.container():
            st.subheader("Análise Exploratória dos Dados - EDA")

            def calcular_moda(x):
                modos = x.mode()
                if not modos.empty:
                    return modos.iloc[0]
                return None

            df_stats = df_filtered.groupby('Turno')['Quantidade de Pacientes'].agg(
                Moda=calcular_moda,
                Mediana='median',
                Media='mean',
                Desvio_Padrao='std'
            ).reset_index()

            df_stats_long = df_stats.melt(
                id_vars='Turno', 
                value_vars=['Moda', 'Mediana', 'Media', 'Desvio_Padrao'], 
                var_name='Estatística', 
                value_name='Valor'
            )

            fig_stats = px.bar(
                df_stats_long, 
                x='Turno', 
                y='Valor', 
                color='Estatística', 
                barmode='group',
                title="Estatísticas por Turno (Moda, Mediana, Média, Desvio Padrão)"
            )

            fig_stats.update_layout(
                xaxis_title="Turno",
                yaxis_title="Valor",
                legend_title="Estatísticas"
            )
            st.plotly_chart(fig_stats)

# ================================
# Previsão de Séries Temporais
# ================================
if 'amostra_pacientes_hora.xlsx' in data_dict:  # Verificar se o arquivo foi carregado
    with st.container():
        if 'Data' in df_pacientes_hora.columns and 'Quantidade de Pacientes' in df_pacientes_hora.columns:
            df_volumetria = df_pacientes_hora[['Data', 'Quantidade de Pacientes']].copy()
            df_volumetria['Data'] = pd.to_datetime(df_volumetria['Data'], format='%Y-%m-%d')
            df_volumetria = df_volumetria.groupby('Data').sum().reset_index()
            df_volumetria.columns = ['ds', 'y']
            
            # Treinamento do modelo ARIMA
            model = ARIMA(df_volumetria['y'], order=(5, 1, 0))  # Ajuste a ordem conforme necessário
            model_fit = model.fit()

            # Fazer previsão para os próximos 30 dias
            forecast = model_fit.forecast(steps=30)
            
            # Criar novas datas para os próximos 30 dias
            future_dates = pd.date_range(start=df_volumetria['ds'].iloc[-1], periods=30, freq='D')

            # Gráfico dos dados reais e previsão
            fig_forecast = go.Figure()

            # Dados reais
            fig_forecast.add_trace(go.Scatter(x=df_volumetria['ds'], y=df_volumetria['y'],
                                              mode='lines', name='Dados Reais', line=dict(color='blue')))

            # Previsão
            fig_forecast.add_trace(go.Scatter(x=future_dates, y=forecast,
                                              mode='lines', name='Previsão', line=dict(color='orange', dash='dash')))

            # Layout do gráfico
            fig_forecast.update_layout(
                title="Análise Temporal e Projeção para Próximos 30 Dias",
                xaxis_title="Data",
                yaxis_title="Quantidade de Pacientes",
                legend_title="Linhas",
                hovermode="x unified"
            )

            # Exibir o gráfico no Streamlit
            st.plotly_chart(fig_forecast)
        else:
            st.warning("A coluna 'Data' ou 'Quantidade de Pacientes' não foi encontrada.")

# ======================================================
# Previsão de Pacientes por Turno para os Próximos 30 Dias
# ======================================================
if 'amostra_pacientes_hora.xlsx' in data_dict:  # Verificar se o arquivo foi carregado
    with st.container():
        if 'Turno' in df_pacientes_hora.columns:
            # Agrupar os dados por data e turno
            df_turno = df_pacientes_hora.groupby(['Data', 'Turno'])['Quantidade de Pacientes'].sum().reset_index()
            
            fig_forecast_turno = go.Figure()

            # Treinar o modelo ARIMA para cada turno
            for turno in df_turno['Turno'].unique():
                df_turno_filtrado = df_turno[df_turno['Turno'] == turno]
                
                # Treinamento para o modelo ARIMA por turno
                model_turno = ARIMA(df_turno_filtrado['Quantidade de Pacientes'], order=(5, 1, 0))
                model_fit_turno = model_turno.fit()

                # Fazer previsão para os próximos 30 dias
                forecast_turno = model_fit_turno.forecast(steps=30)
                
                # Criar novas datas para os próximos 30 dias
                future_turno_dates = pd.date_range(start=df_turno_filtrado['Data'].iloc[-1], periods=30, freq='D')

                # Gráfico com os dados reais e previsão por turno
                fig_forecast_turno.add_trace(go.Scatter(x=df_turno_filtrado['Data'], y=df_turno_filtrado['Quantidade de Pacientes'],
                                                        mode='lines', name=f'Dados Reais Turno {turno}', line=dict(color='blue')))
                fig_forecast_turno.add_trace(go.Scatter(x=future_turno_dates, y=forecast_turno,
                                                        mode='lines', name=f'Previsão Turno {turno}', line=dict(dash='dash')))

            # Layout do gráfico
            fig_forecast_turno.update_layout(
                title="Previsão de Pacientes por Turno para os Próximos 30 Dias",
                xaxis_title="Data",
                yaxis_title="Quantidade de Pacientes",
                legend_title="Turnos",
                hovermode="x unified"
            )

            # Exibir o gráfico
            st.plotly_chart(fig_forecast_turno)
        else:
            st.warning("Os dados não contêm a coluna 'Turno'.")

# ======================================================
# Rodapé
# ======================================================
st.markdown("""
    ---
    © 2024 LeanMasterAcademy 🦎. Todos os direitos reservados.
""")


