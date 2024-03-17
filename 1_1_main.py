import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import hmac
from PIL import Image

# Função para verificar a senha
def check_password():
    def password_entered():
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

# Função para carregar os dados
@st.cache_data
def load_data():
    return pd.read_csv('cofeci.csv')

# Função para plotar o gráfico de barras
def plot_bar_chart_perg5(data):
    data['PERG.5'] = pd.to_numeric(data['PERG.5'], errors='coerce')
    data_filtered = data[data['PERG.5'] >= 20]
    
    max_age = data_filtered['PERG.5'].max()
    if pd.isna(max_age):
        max_bin = 30
    else:
        max_bin = int(max_age) + 10 - (int(max_age) % 10)
    
    bins = range(20, max_bin + 10, 10)
    labels = [f'{i} - {i + 9}' for i in bins[:-1]]
    
    data_filtered['Faixa Etária'] = pd.cut(data_filtered['PERG.5'], bins=bins, labels=labels, right=False)
    
    age_group_percentage = data_filtered['Faixa Etária'].value_counts(normalize=True).sort_index() * 100
    age_group_percentage_df = age_group_percentage.reset_index()
    age_group_percentage_df.columns = ['Faixa Etária', 'Porcentagem']

    color_map = {
        '20 - 29': '#07f49e',
        '30 - 39': '#11cc99',
        '40 - 49': '#1ba493',
        '50 - 59': '#257c8e',
        '60 - 69': '#2e5489',
        '70 - 79': '#382c83',
        '80 - 89': '#42047e',
    }

    fig = px.bar(age_group_percentage_df, x='Faixa Etária', y='Porcentagem', text='Porcentagem',
                 title='Porcentagem de Idade dos Entrevistados por Faixa Etária',
                 color='Faixa Etária', color_discrete_map=color_map)
    
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',
                      yaxis_title="Porcentagem (%)", xaxis_title="Faixa Etária")
    
    st.plotly_chart(fig)

# Função para plotar o gráfico de donut
def plot_donut_chart_perg9(data):
    values_df = data['PERG.9'].value_counts().reset_index()
    values_df.columns = ['Resposta', 'Quantidade']
    
    color_map = {
        'Masculino': '#1dbde6',
        'Feminino': '#f1515e'
    }
    
    fig = px.pie(values_df, values='Quantidade', names='Resposta', hole=0.4,
                 title='Sexo dos Entrevistados',
                 color='Resposta', color_discrete_map=color_map)
    
    fig.update_traces(textinfo='percent', insidetextfont=dict(color='white', size=14))
    
    st.plotly_chart(fig)

# Carregar os dados

data = load_data()

# Mapeamento de Regiões para Estados
regioes_estados = {
    'Centro-Oeste': ['Goiás (GO)', 'Mato Grosso (MT)', 'Mato Grosso do Sul (MS)', 'Distrito Federal (DF)'],
    'Nordeste': ['Alagoas (AL)', 'Bahia (BA)', 'Ceará (CE)', 'Maranhão (MA)', 'Paraíba (PB)', 'Pernambuco (PE)', 'Piauí (PI)', 'Rio Grande do Norte (RN)', 'Sergipe (SE)'],
    'Norte': ['Acre (AC)', 'Amapá (AP)', 'Amazonas (AM)', 'Pará (PA)', 'Rondônia (RO)', 'Roraima (RR)', 'Tocantins (TO)'],
    'Sudeste': ['Espírito Santo (ES)', 'Minas Gerais (MG)', 'Rio de Janeiro (RJ)', 'São Paulo (SP)'],
    'Sul': ['Paraná (PR)', 'Rio Grande do Sul (RS)', 'Santa Catarina (SC)'],
    'Brasil': []  
}
if 'password_correct' not in st.session_state:
    st.session_state['password_correct'] = False

if 'selected_regiao' not in st.session_state:
    st.session_state['selected_regiao'] = 'Selecione uma opção'

if 'selected_estado' not in st.session_state:
    st.session_state['selected_estado'] = []

if 'selected_perg_7' not in st.session_state:
    st.session_state['selected_perg_7'] = 'Ambos'

if 'selected_escolaridade' not in st.session_state:
    st.session_state['selected_escolaridade'] = 'Todos'

if 'selected_sexo' not in st.session_state:
    st.session_state['selected_sexo'] = ['Masculino', 'Feminino']


# Filtro por Região do Brasil
# Salvando a seleção anterior para detectar mudanças
previous_regiao = st.session_state['selected_regiao']
selected_regiao = st.sidebar.selectbox(
    'Selecione a Região:', 
    ['Selecione uma opção', 'Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul'],
    index=['Selecione uma opção', 'Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul'].index(st.session_state['selected_regiao'])
)
st.session_state['selected_regiao'] = selected_regiao

# Atualizar o filtro de Estados com base na região selecionada
estados_opcoes = []
if selected_regiao != 'Selecione uma opção':
    # Determinando as opções de estado com base na região selecionada
    if selected_regiao == 'Brasil':
        estados_opcoes = sorted(data['PERG.6'].unique())
    else:
        estados_opcoes = regioes_estados[selected_regiao]

    # Atualizando os estados selecionados para todos da nova região se a região mudou
    if selected_regiao != previous_regiao:
        st.session_state['selected_estado'] = estados_opcoes

    # Permitindo ao usuário fazer uma seleção manual dos estados
    selected_estado = st.sidebar.multiselect(
        'Selecione o Estado:',
        estados_opcoes,
        default=st.session_state['selected_estado']
    )
    if selected_estado:
        st.session_state['selected_estado'] = selected_estado

    # Aplicando o filtro de estado
    if st.session_state['selected_estado']:
        filtered_data = data[data['PERG.6'].isin(st.session_state['selected_estado'])]

        # Filtro de interior/capital
        options_perg_7 = ['Ambos', 'Capital', 'Interior']
        selected_perg_7 = st.sidebar.radio(
            "Selecione Interior ou Capital:",
            options=options_perg_7,
            index=options_perg_7.index(st.session_state['selected_perg_7'])
        )
        st.session_state['selected_perg_7'] = selected_perg_7

        if st.session_state['selected_perg_7'] != 'Ambos':
            filtered_data = filtered_data[filtered_data['PERG.7'] == st.session_state['selected_perg_7']]

        # Atualizando o filtro de escolaridade para multiselect e removendo a opção 'Todos'
        escolaridade_opcoes = sorted(filtered_data['PERG.16'].dropna().astype(str).unique().tolist())
        # Garantindo que os valores padrão estejam nas opções disponíveis
        if not set(st.session_state['selected_escolaridade']).issubset(set(escolaridade_opcoes)):
            st.session_state['selected_escolaridade'] = escolaridade_opcoes

        selected_escolaridade = st.sidebar.multiselect(
            "Selecione a Escolaridade:",
            escolaridade_opcoes,
            default=st.session_state['selected_escolaridade']
        )
        st.session_state['selected_escolaridade'] = selected_escolaridade

        # Aplicando o filtro de escolaridade
        if st.session_state['selected_escolaridade']:
            filtered_data = filtered_data[filtered_data['PERG.16'].astype(str).isin(st.session_state['selected_escolaridade'])]

        options_sexo = ['Masculino', 'Feminino']
        selected_sexo = st.sidebar.multiselect(
            "Selecione o sexo dos entrevistados:",
            options=options_sexo,
            default=st.session_state['selected_sexo']
        )
        st.session_state['selected_sexo'] = selected_sexo

        # Aplicando o filtro de sexo, caso alguma opção tenha sido selecionada
        if st.session_state['selected_sexo']:
            filtered_data = filtered_data[filtered_data['PERG.9'].isin(st.session_state['selected_sexo'])]

            # Aqui continuam as funções de plotagem ou exibição de dados que já estavam sendo utilizadas
            plot_bar_chart_perg5(filtered_data)
            plot_donut_chart_perg9(filtered_data)

else:
    st.write("Selecione os filtros para visualizar os dados.")
