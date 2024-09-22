import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import graphviz as gv
import matplotlib.colors as mcolors
import math

# ===============================
# Configuração da Página 
# ===============================
st.set_page_config(
    page_title="Processo",
    layout="wide"  
)

# ===============================
# Sidebar - Barra Lateral 
# ===============================
st.sidebar.markdown("""---""")

# Carregar a imagem na sidebar
image_path = 'app.png'
image = Image.open(image_path)
st.sidebar.image(image, width=190)

st.sidebar.markdown("""
    <h1 style='display: inline; font-size: 28px;'>MedFlow</h1>
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
        df = pd.read_excel(uploaded_file)
        data_dict[uploaded_file.name] = df

st.sidebar.markdown("""---""")

# ===================================
# Filtro interativo de datas para o arquivo amostra_dados_tempo_ciclo.xlsx
# ===================================
df_filtered = None  # Variável de controle para os gráficos

if 'amostra_dados_tempo_ciclo.xlsx' in data_dict:
    df_tempo_ciclo = data_dict['amostra_dados_tempo_ciclo.xlsx']

    # Certificar que a coluna 'Data' seja datetime
    df_tempo_ciclo['Data'] = pd.to_datetime(df_tempo_ciclo['Data'], format='%Y-%m-%d')

    # Definir o valor mínimo e máximo para o slider de datas
    min_date = df_tempo_ciclo['Data'].min().date()  
    max_date = df_tempo_ciclo['Data'].max().date()  

    # Filtro interativo de data
    selected_dates = st.sidebar.slider(
        'Selecione o intervalo de datas',
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        format='DD-MM-YYYY'
    )

    # Filtrar o dataframe com base nas datas selecionadas
    df_filtered = df_tempo_ciclo[(df_tempo_ciclo['Data'].dt.date >= selected_dates[0]) & 
                                 (df_tempo_ciclo['Data'].dt.date <= selected_dates[1])]

st.sidebar.markdown("""---""")

st.sidebar.markdown('##### Desenvolvido por [@FranciscoPena](https://www.linkedin.com/in/franciscobpena/) & [@DanielMeireles](https://www.linkedin.com/in/daniel-meireles-processos/) 🤓')

# ===============================
# Corpo principal da página - Upload das medições
# ===============================
st.header("🏥Visão Analítica por:")

# Criando as guias (tabs)
tab2, tab3 = st.tabs(['🔜 Etapas do Processo', '📊 Gráficos Complementares'])

# =====================================================
# Exibindo os gráficos na Tab2 - Etapas do Atendimento
# =====================================================

# ======================================================
# Container 1: Distribuição do Tempo por Etapa com Média
# ======================================================

if df_filtered is not None:
    with tab2:
        # Container 1: Distribuição do Tempo por Etapa com Média
        with st.container():
            st.subheader("Distribuição do Tempo por Etapa com Média")

            # Gráfico de boxplot com a data filtrada
            fig_box = px.box(df_filtered, x='Etapa', y='Tempo (Minutos)', title="Boxplot: Tempo por Etapa")

            # Adicionar linha de média
            media_tempo = df_filtered.groupby('Etapa')['Tempo (Minutos)'].mean().reset_index()

            for index, row in media_tempo.iterrows():
                fig_box.add_trace(go.Scatter(
                    x=[row['Etapa']], 
                    y=[row['Tempo (Minutos)']],
                    mode='markers',
                    marker=dict(color='red', size=10, symbol='line-ns-open'),
                    name=f"Média {row['Etapa']}"
                ))

            st.plotly_chart(fig_box)
            
# ======================================================
# Container 2: Sequenciamento e Headcount por Etapa
# ======================================================
        with st.container():
            st.subheader("Parametrize:")
        
            # Subtítulo para a sequência
            st.write("### Definir a sequência do processo")
        
            # Agrupar as etapas e calcular a média do Tempo (Minutos)
            media_tempo = df_filtered.groupby('Etapa')['Tempo (Minutos)'].mean().reset_index()
        
            # Interações para a sequência das etapas
            etapas = media_tempo['Etapa'].unique().tolist()
        
            sequencia_etapas = {}
            for etapa in etapas:
                sequencia_etapas[etapa] = st.number_input(f"Informe a posição na sequência para a etapa {etapa}:", min_value=1, step=1)
        
            # Subtítulo para o Headcount
            st.write("### Determinar quantidade de headcount por etapa")
        
            # Input interativo para quantidade de funcionários (Headcount)
            headcount_etapas = {}
            for etapa in etapas:
                headcount_etapas[etapa] = st.number_input(f"Quantidade de funcionários na etapa {etapa}:", min_value=1)
        
            # Verificar se os inputs foram preenchidos antes de gerar o diagrama
            if all(sequencia_etapas.values()) and all(headcount_etapas.values()):
                
                # Ordenar as etapas com base na sequência inserida
                etapas_ordenadas = sorted(sequencia_etapas.items(), key=lambda x: x[1])
        
                # Criar o diagrama de fluxo horizontal com gradação de cor para TC
                st.subheader("Diagrama de Fluxo com Headcount e Mapa de Calor por TC")
                dot = gv.Digraph(format='png')
                dot.attr(rankdir='LR')  # Define a orientação horizontal (Left to Right)
        
                # Mapear as cores para os tempos de ciclo (TC)
                norm = mcolors.Normalize(vmin=media_tempo['Tempo (Minutos)'].min(), vmax=media_tempo['Tempo (Minutos)'].max())
                cmap = mcolors.LinearSegmentedColormap.from_list("", ["#FFCCCC", "#FF0000"])  # De gradiente claro até vermelho
        
                # Adicionar as etapas, tempo de ciclo (TC), e Headcount ao diagrama
                for i, (etapa, pos) in enumerate(etapas_ordenadas):
                    tc = media_tempo[media_tempo['Etapa'] == etapa]['Tempo (Minutos)'].values[0]
                    headcount = headcount_etapas[etapa]
                    color = mcolors.to_hex(cmap(norm(tc)))  # Mapeia a cor baseada no valor de TC
                    dot.node(etapa, f"{etapa}\nTC: {tc:.2f} min\nHeadcount: {headcount}", style='filled', fillcolor=color)
                    if i > 0:
                        dot.edge(etapas_ordenadas[i-1][0], etapa)
        
                # Renderizar o diagrama
                st.graphviz_chart(dot)

# ======================================================
# Container 3: Taxa de Chegada de Pacientes por Etapa
# ======================================================
        with st.container():
            st.write("### Determinar a taxa de chegada (TCC - Pacientes/hora) por etapa")
        
            # Input interativo para taxa de chegada de pacientes por etapa
            taxa_chegada_etapas = {}
            for etapa in etapas:
                taxa_chegada_etapas[etapa] = st.number_input(f"Taxa de chegada de pacientes/hora na etapa {etapa}:", min_value=1)

# ======================================================
# Container 4: Desempenho do Processo
# ======================================================
        with st.container():
            st.subheader("Desempenho do Processo")

            # ======================================================
            # Dynamic Analytical Observation Below the Table
            # ======================================================
            # Justification for the chosen model in each stage
            st.write("### Modelos Utilizados:")
            st.write("""
            - Etapas com apenas 1 funcionário seguiram o modelo M/M/1.
            - Etapas com mais de um funcionário seguiram o modelo M/M/c, considerando múltiplos servidores.
            """)
        
            # Organizar as colunas da tabela de acordo com a sequência das etapas do Container 2
            colunas = [etapa[0] for etapa in etapas_ordenadas]
        
                        # Estruturar uma tabela interativa com as variáveis calculadas
            df_tabela = pd.DataFrame({
                'Etapa': colunas,  # Use a ordem das etapas definida pelo usuário
                'Headcount': [headcount_etapas[etapa] for etapa in colunas],
                'Headcount Necessário': [math.ceil(media_tempo[media_tempo['Etapa'] == etapa]['Tempo (Minutos)'].values[0] / (60 / taxa_chegada_etapas[etapa])) for etapa in colunas],
                'TCC': [taxa_chegada_etapas[etapa] for etapa in colunas],
                'TAF': [headcount_etapas[etapa] / media_tempo[media_tempo['Etapa'] == etapa]['Tempo (Minutos)'].values[0] * 60 for etapa in colunas],
                'Fator de Utilização (%)': [round((taxa_chegada_etapas[etapa] / (headcount_etapas[etapa] / media_tempo[media_tempo['Etapa'] == etapa]['Tempo (Minutos)'].values[0] * 60) * 100), 2) for etapa in colunas],
                'Clientes na Fila': [(taxa_chegada_etapas[etapa] / (headcount_etapas[etapa] / media_tempo[media_tempo['Etapa'] == etapa]['Tempo (Minutos)'].values[0] * 60)) * (taxa_chegada_etapas[etapa] / ((headcount_etapas[etapa] / media_tempo[media_tempo['Etapa'] == etapa]['Tempo (Minutos)'].values[0] * 60) - taxa_chegada_etapas[etapa])) for etapa in colunas],
                'Tempo na Fila (h)': [(taxa_chegada_etapas[etapa] / (headcount_etapas[etapa] / media_tempo[media_tempo['Etapa'] == etapa]['Tempo (Minutos)'].values[0] * 60)) * (1 / ((headcount_etapas[etapa] / media_tempo[media_tempo['Etapa'] == etapa]['Tempo (Minutos)'].values[0] * 60) - taxa_chegada_etapas[etapa])) for etapa in colunas],
                'Tempo na Fila (min)': [(taxa_chegada_etapas[etapa] / (headcount_etapas[etapa] / media_tempo[media_tempo['Etapa'] == etapa]['Tempo (Minutos)'].values[0] * 60)) * 60 for etapa in colunas],
            })
        
            df_tabela['Etapa'] = df_tabela['Etapa'].astype(str)  # Converter para string se necessário
        
            # Aplicar o estilo com gradiente de cor para Fator de Utilização e Clientes na Fila em vermelho
            styled_df = df_tabela.style.background_gradient(subset=['Fator de Utilização (%)', 'Clientes na Fila'], cmap="Reds")
            st.dataframe(styled_df)
        
            # Analyze the performance dynamically based on Fator de Utilização
            fator_utilizacao = df_tabela['Fator de Utilização (%)']
            clientes_fila = df_tabela['Clientes na Fila']
            st.subheader("Observação analítica:")   
            if fator_utilizacao.max() > 100:
                st.write("⚠️ **Alerta de Utilização**: Uma ou mais etapas têm Fator de Utilização acima de 100%, o que indica sobrecarga. Recomendamos aumentar o número de funcionários nessas etapas ou reduzir a taxa de chegada de pacientes.")
            elif fator_utilizacao.mean() > 85:
                st.write("✅ **Bom Aproveitamento**: A média do Fator de Utilização está alta (acima de 85%), o que indica um uso eficiente dos recursos. No entanto, monitore as filas para evitar gargalos.")
            else:
                st.write("🔍 **Oportunidade de Melhoria**: O Fator de Utilização está abaixo de 85% na maioria das etapas. Considere ajustar o número de funcionários para otimizar o atendimento.")
        
            # Analyze the number of clients in the queue
            if clientes_fila.max() > 10:
                st.write("⚠️ **Alerta de Fila**: Há mais de 10 clientes na fila em uma ou mais etapas. Isso sugere que o processo está gerando filas significativas. Reavalie a taxa de atendimento ou o número de funcionários.")
            elif clientes_fila.mean() >= 5:
                st.write("📊 **Monitoramento Necessário**: O número de clientes na fila está em um nível moderado (acima ou igual 5), o que pode indicar gargalos pontuais.")
            else:
                st.write("✅ **Bom Desempenho de Fila**: O número de clientes na fila está em um nível aceitável (abaixo de 5) em todas as etapas.")
                
# ======================================================
# Container 5: Diagrama de Fluxo
# ======================================================
        with st.container():
            st.subheader("Diagrama de Fluxo")
        
            # Criar o diagrama de fluxo horizontal com tempos na fila entre etapas
            dot = gv.Digraph(format='png')
            dot.attr(rankdir='LR')  # Define a orientação horizontal (Left to Right)
        
            # Mapear as cores para o tempo de fila (min) para os quadrados
            norm = mcolors.Normalize(vmin=df_tabela['Tempo na Fila (min)'].min(), vmax=df_tabela['Tempo na Fila (min)'].max())
            cmap = mcolors.LinearSegmentedColormap.from_list("", ["#FFCCCC", "#FF0000"])  # Gradiente vermelho para quadrados
        
            # Adicionar as etapas e o tempo de ciclo (TC) ao diagrama, destacando gargalos
            for i, (etapa, pos) in enumerate(etapas_ordenadas):
                tc = media_tempo[media_tempo['Etapa'] == etapa]['Tempo (Minutos)'].values[0]
                tempo_fila = df_tabela[df_tabela['Etapa'] == etapa]['Tempo na Fila (min)'].values[0]
                
                # Nome da etapa com TC (sem mapa de calor)
                dot.node(etapa, f"TC: {tc:.2f} min\n{etapa}", style='filled', fillcolor='white', fontsize="16", fontname="Helvetica-Bold")
        
                # Se não for a primeira etapa, adiciona o tempo de fila entre as etapas em um quadrado
                if i > 0:
                    etapa_anterior = etapas_ordenadas[i-1][0]
                    # Adicionar o tempo de fila entre as etapas em um quadrado, com mapa de calor
                    color = mcolors.to_hex(cmap(norm(tempo_fila)))
                    dot.node(f"fila_{i}", f"TE: {tempo_fila:.2f} min", shape='box', style='filled', fillcolor=color, fontsize="16", fontname="Helvetica-Bold")
                    dot.edge(etapa_anterior, f"fila_{i}")
                    dot.edge(f"fila_{i}", etapa)
        
            # Identificar e marcar o gargalo com a menor TAF (etapa roxa com texto "Gargalo")
            gargalo = df_tabela.loc[df_tabela['TAF'].idxmin()]
            dot.node(gargalo['Etapa'], f"{gargalo['Etapa']}\n(Gargalo)\nMenor TAF: {gargalo['TAF']:.2f} Pctes/h", style='filled', fillcolor='purple', fontsize="16", fontname="Helvetica-Bold")
        
            # Renderizar o diagrama
            st.graphviz_chart(dot)

else:
    st.warning("Você deve inserir os dados de acordo com o template 'amostra_dados_tempo_ciclo.xlsx' para visualizar os gráficos.")
# =====================================================
# Tab 3 - Métricas e Gráficos
# =====================================================
if df_filtered is not None:
    
    with tab3:
        with st.container():
            st.title("Métricas")
            
            # Criar duas colunas para as métricas
            col1, col2 = st.columns(2, gap="small")

            # =======================
            # Coluna 1: Leadtime em Minutos
            # =======================
            with col1:               
                # Somar todos os tempos de ciclo (TC) e tempos na fila (TE)
                leadtime_minutos = df_filtered['Tempo (Minutos)'].sum() + df_tabela['Tempo na Fila (min)'].sum()

                # Exibir resultado em minutos
                st.metric(label="Leadtime (Minutos)", value=f"{leadtime_minutos:.2f} min")

            # =======================
            # Coluna 2: Saídas por hora
            # =======================
            with col2: 
                # Calcular a menor TAF do processo
                menor_taf = df_tabela['TAF'].min()
                
                # Calcular saídas com base na menor TAF
                saida_por_hora = 1 / menor_taf if menor_taf > 0 else 0

                # Exibir o valor das saídas
                st.metric(label="Saídas (Paciente/hora)", value=f"{saida_por_hora:.2f} Pacientes/h")

            # Linha divisória
            st.markdown("""---""")
        
# ======================================================
# Container: Agregação de valor (Mapa de Árvore)
# ======================================================
        with st.container():
        
            # Calcular o Tempo Não Agregado de Valor (NAV) e Agregado de Valor (AV)
            NAV = df_tabela['Tempo na Fila (min)'].sum()  # Tempo Não Agregado de Valor
            AV = df_filtered['Tempo (Minutos)'].sum()     # Tempo Agregado de Valor
        
            # Calcular o Total do Leadtime e proporção TAV e TNAV
            leadtime_minutos = AV + NAV
            TAV_percent = (AV / leadtime_minutos) * 100 if leadtime_minutos > 0 else 0
            TNAV_percent = 100 - TAV_percent
        
            # Criar DataFrame para o Mapa de Árvore
            df_treemap = pd.DataFrame({
                'Tipo': ['Tempo Agregado de Valor (TAV)', 'Tempo Não Agregado de Valor (TNAV)'],
                'Tempo (minutos)': [AV, NAV],
                'Percentual': [TAV_percent, TNAV_percent]
            })
        
            # Criar o gráfico de Mapa de Árvore
            fig_treemap = px.treemap(
                df_treemap, 
                path=['Tipo'], 
                values='Tempo (minutos)', 
                color='Percentual',
                color_continuous_scale='RdBu',
                title="Mapa de Árvore: Proporção de Tempo Agregado vs Não Agregado"
            )
        
            # Exibir o gráfico
            st.plotly_chart(fig_treemap)
            
            # Linha divisória
            st.markdown("""---""")
        
# ======================================================
# Container 3: Gráfico de Barras (Tempo de Fila por Etapa)
# ======================================================
        with st.container():
            # Criar gráfico de barras com o Tempo de Fila (TE) por Etapa
            etapas_ordenadas = [etapa[0] for etapa in sequencia_etapas.items()]  # Etapas ordenadas conforme a interação do usuário
            df_fila_ordenada = df_tabela[df_tabela['Etapa'].isin(etapas_ordenadas)].sort_values(by='Etapa', key=lambda x: [sequencia_etapas[etapa] for etapa in x])
        
            fig_fila = px.bar(
                df_fila_ordenada, 
                x='Etapa', 
                y='Tempo na Fila (min)', 
                title="Tempo de Fila por Etapa (min)", 
                labels={'Tempo na Fila (min)': 'Tempo na Fila (min)', 'Etapa': 'Etapa'}
            )
        
            # Melhorar a legibilidade: ajustar a largura do gráfico e habilitar a rolagem horizontal
            fig_fila.update_layout(
                xaxis={'categoryorder': 'total ascending', 'tickangle': -45},
                height=500,  # Altura do gráfico
                width=1000,  # Largura ajustada para suportar rolagem
                margin=dict(l=40, r=40, t=40, b=120),  # Margens ajustadas
                xaxis_title="Etapa",
                yaxis_title="Tempo na Fila (min)",
                showlegend=False
            )
        
            # Exibir o gráfico de barras
            st.plotly_chart(fig_fila, use_container_width=True)
            
            # Linha divisória
            st.markdown("""---""")
        
# ======================================================
# Container 4: Gráfico de Barras (Fatores de Utilização por Etapa)
# ======================================================
        with st.container():
            # Ordenar etapas com base na sequência do usuário e preparar dados
            df_utilizacao_ordenada = df_tabela[df_tabela['Etapa'].isin(etapas_ordenadas)].sort_values(by='Etapa', key=lambda x: [sequencia_etapas[etapa] for etapa in x])
        
            # Criar gráfico de barras para Fator de Utilização
            fig_utilizacao = px.bar(
                df_utilizacao_ordenada, 
                x='Etapa', 
                y='Fator de Utilização (%)', 
                title="Fator de Utilização por Etapa (%)", 
                labels={'Fator de Utilização (%)': 'Fator de Utilização (%)', 'Etapa': 'Etapa'},
                text='Fator de Utilização (%)'
            )
        
            # Atualizar o layout para exibir os valores arredondados no gráfico e ajustar para rolagem horizontal
            fig_utilizacao.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            fig_utilizacao.update_layout(
                xaxis={'categoryorder': 'total ascending', 'tickangle': -45},
                height=500,  # Altura do gráfico
                width=1000,  # Largura ajustada para suportar rolagem
                margin=dict(l=40, r=40, t=40, b=120),  # Margens ajustadas
                xaxis_title="Etapa",
                yaxis_title="Fator de Utilização (%)",
                showlegend=False
            )
        
            # Exibir o gráfico
            st.plotly_chart(fig_utilizacao, use_container_width=True)

# ======================================================
# Rodapé
# ======================================================
st.markdown("""
    ---
    © 2024 LeanMasterAcademy 🦎. Todos os direitos reservados.
""")




