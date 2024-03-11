import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import hmac
from PIL import Image

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    password = st.text_input("Senha: ", type="password", key="password")
    st.button("Enviar Senha", on_click=password_entered)

    if "password_correct" in st.session_state:
        st.error("Senha Incorreta.")

    return False

if not check_password():
    st.stop()

def load_data():
    data = pd.read_csv('cofeci.csv')
    return data

col1, col_empty, col2 = st.columns([1, 2, 1])

with col1:
    st.image('cofeci3.jpeg', width=100)

with col2:
    st.image('125.1_LOGO REI-01.png', width=100)





def plot_bar_chart_perg5(data):
    # Garantir que a coluna 'PERG.5' é numérica e filtrar para idades >= 20
    data['PERG.5'] = pd.to_numeric(data['PERG.5'], errors='coerce')
    data_filtered = data[data['PERG.5'] >= 20]
    
    # Definir os bins para agrupamento de idade de 10 em 10 anos, começando de 20
    max_age = data_filtered['PERG.5'].max()
    if pd.isna(max_age):
        max_bin = 30  # Valor padrão se não houver dados válidos, começando a contagem a partir de 20
    else:
        max_bin = int(max_age) + 10 - (int(max_age) % 10)
    
    bins = range(20, max_bin + 10, 10)
    labels = [f'{i} - {i + 9}' for i in bins[:-1]]
    
    # Agrupar as idades em faixas
    data_filtered['Faixa Etária'] = pd.cut(data_filtered['PERG.5'], bins=bins, labels=labels, right=False)
    
    # Calcular a porcentagem de respostas para cada faixa etária e ordenar pelo índice (Faixa Etária)
    age_group_percentage = data_filtered['Faixa Etária'].value_counts(normalize=True).sort_index() * 100
    age_group_percentage_df = age_group_percentage.reset_index()
    age_group_percentage_df.columns = ['Faixa Etária', 'Porcentagem']

    # Mapeamento de cores para cada faixa etária
    color_map = {
        '20 - 29': '#07f49e',
        '30 - 39': '#11cc99',
        '40 - 49': '#1ba493',
        '50 - 59': '#257c8e',
        '60 - 69': '#2e5489',
        '70 - 79': '#382c83',
        '80 - 89': '#42047e',
    }

    # Criar um gráfico de barras usando Plotly Express
    fig = px.bar(age_group_percentage_df, x='Faixa Etária', y='Porcentagem', text='Porcentagem',
                 title='Porcentagem de Idade dos Entrevistados por Faixa Etária',
                 color='Faixa Etária', color_discrete_map=color_map)  # Aplicando o mapeamento de cores
    
    # Formatar o texto da porcentagem no gráfico
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',
                      yaxis_title="Porcentagem (%)", xaxis_title="Faixa Etária")
    
    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)


def plot_donut_chart_perg9(data):
    # Contar os valores únicos na coluna 'PERG.9' e resetar o índice para transformar em DataFrame
    values_df = data['PERG.9'].value_counts().reset_index()
    values_df.columns = ['Resposta', 'Quantidade']
    
    # Definir mapeamento de cores para as respostas
    color_map = {
        'Masculino': '#1dbde6',
        'Feminino': '#f1515e'
    }
    
    # Criar um gráfico de rosca usando Plotly Express
    fig = px.pie(values_df, values='Quantidade', names='Resposta', hole=0.4,
                 title='Sexo dos Entrevistados',
                 color='Resposta', color_discrete_map=color_map)
    
    # Atualizar os traços para mostrar apenas a porcentagem, em cor branca
    fig.update_traces(textinfo='percent', insidetextfont=dict(color='white', size=14))
    
    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)

data = load_data()

# Filtro por Região do Brasil
selected_regiao = st.sidebar.selectbox(
    'Selecione a Região:', 
    ['Selecione uma opção', 'Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul'],
    index=0
)

# Mapeamento de Regiões para Estados (exemplo genérico, ajuste conforme necessário)
regioes_estados = {
    'Centro-Oeste': ['Goiás (GO)', 'Mato Grosso (MT)', 'Mato Grosso do Sul (MS)', 'Distrito Federal (DF)'],
    'Nordeste': ['Alagoas (AL)', 'Bahia (BA)', 'Ceará (CE)', 'Maranhão (MA)', 'Paraíba (PB)', 'Pernambuco (PE)', 'Piauí (PI)', 'Rio Grande do Norte (RN)', 'Sergipe (SE)'],
    'Norte': ['Acre (AC)', 'Amapá (AP)', 'Amazonas (AM)', 'Pará (PA)', 'Rondônia (RO)', 'Roraima (RR)', 'Tocantins (TO)'],
    'Sudeste': ['Espírito Santo (ES)', 'Minas Gerais (MG)', 'Rio de Janeiro (RJ)', 'São Paulo (SP)'],
    'Sul': ['Paraná (PR)', 'Rio Grande do Sul (RS)', 'Santa Catarina (SC)'],
    'Brasil': []  # Vazio para selecionar todos os estados
}

# Atualizar o filtro de Estados com base na região selecionada
if selected_regiao != 'Selecione uma opção':
    if selected_regiao == 'Brasil':
        estados_opcoes = sorted(data['PERG.6'].unique())
    else:
        estados_opcoes = regioes_estados[selected_regiao]
    selected_estado = st.sidebar.multiselect('Selecione o Estado:', estados_opcoes, default=estados_opcoes)
else:
    selected_estado = []

if selected_estado:
    filtered_data = data[data['PERG.6'].isin(selected_estado)]
    
    # Filtro por Interior ou Capital (PERG.7)
    options_perg_7 = ['Ambos', 'Capital', 'Interior']
    selected_perg_7 = st.sidebar.radio("Selecione Interior ou Capital:", options=options_perg_7)
    
    if selected_perg_7 != 'Ambos':
        filtered_data = filtered_data[filtered_data['PERG.7'] == selected_perg_7]
    
    # Filtro por Escolaridade (PERG.16)
    escolaridade_opcoes = ['Todos'] + sorted(filtered_data['PERG.16'].dropna().astype(str).unique().tolist())
    selected_escolaridade = st.sidebar.selectbox("Selecione a Escolaridade:", escolaridade_opcoes, index=0)
    
    if selected_escolaridade != 'Todos':
        filtered_data = filtered_data[filtered_data['PERG.16'].astype(str) == selected_escolaridade]
    
    # Aqui você pode chamar as funções para exibir os gráficos com filtered_data
    plot_bar_chart_perg5(filtered_data)
    plot_donut_chart_perg9(filtered_data)
else:
    st.write("Selecione os filtros para visualizar os dados.")


