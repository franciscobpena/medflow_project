#==============================
# Bibliotecas
#==============================

import streamlit as st
from PIL import Image

#===============================
#Configuração da Página 
#===============================

st.set_page_config(
    page_title="Home",
    page_icon="👋",
    layout="wide"  
)

#===============================
# Sidebar - Barra Lateral 
#===============================
image = Image.open('app.png')
st.sidebar.image(image, width=190)
st.sidebar.markdown("""
    <h1 style='display: inline; font-size: 28px;'>MedFlow</h1>
    <h2 style='display: inline; font-size: 18px;'>➤</h2>
    """, unsafe_allow_html=True)
st.sidebar.markdown('### Simplificando fluxos, melhorando vidas')
st.sidebar.markdown("""---""")
st.sidebar.markdown('##### Desenvolvido por [@DanielMeireles](https://www.linkedin.com/in/daniel-meireles-processos/) & [@FranciscoPena](https://franciscobpena.github.io/porfolio_projetos/)')

#==================================
# Corpo principal da pagina - HOME
#==================================

st.title("🏥Aplicativo e Dashboard")

st.markdown(
    '<p style="font-size:15px;">Melhore os processos relacionados ao atendimento hospitalar</p>',
    unsafe_allow_html=True
)

st.markdown("---")

st.header("Como utilizar o App?")

st.subheader("Upload dos dados:")
st.markdown("""
- Seguir com a estrutura de dados recomendada neste repositório [Clique aqui](https://github.com/franciscobpena/medflow_project/tree/fc0885746f3df19ca2442b7aa21c09bb05e38131/dataset);
- Os 02 arquivos templates refere-se ao tempo de atendimento e chegadas de pacientes.""")

st.subheader("Visão - Entrada pacientes:")
st.markdown("""
- A partir do upload do arquivo "amostra_pacientes_hora.xlsx" você terá uma série de estatisticas e projeções 
que vão lhe auxiliar no entendimento do processo.""")

st.subheader("Visão - Desempenho dos processos:")
st.markdown("""
- Com base nas informações na visão “Desempenho do Processo’ você pode consultar uma série de informações referente ao processo e seu desempenho; 
- É fortemente indicado cruzar com informações factuais e contextuais para se tomar uma melhor decisão.
""")

st.subheader("Fundamentação técnica:")
st.markdown("""
- Estatística Inferencial;
- Teoria das Restrições;
- Lean e Ciência de Dados. 
""")

# ===============================
# Rodapé
# ===============================
st.markdown("""
    ---
    © 2024 LeanMasterAcademy 🦎. Todos os direitos reservados.
""")





  