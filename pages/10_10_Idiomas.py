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
    return pd.read_csv('cofeci2.csv')

col1, col_empty, col2 = st.columns([1, 2, 1])

# Na primeira coluna, adicionar o logo do Cofeci
with col1:
    st.image('cofeci3.jpeg', width=100)  # Ajuste a largura conforme necessário

# Na segunda coluna, adicionar o logo do Rei
with col2:
    st.image('125.1_LOGO REI-01.png', width=100)  # Ajuste a largura conforme necessário



# Função para plotar o gráfico de barras
def plot_bar_chart_perg26(df):
    # Criação de uma nova coluna para agrupar idiomas menos comuns como 'Outros'
    top_languages = df['PERG.26'].value_counts().nlargest(3).index.tolist()
    df['Idioma_Agrupado'] = df['PERG.26'].apply(lambda x: x if x in top_languages else 'Outros')

    # Contando a frequência dos idiomas agrupados
    language_counts = df['Idioma_Agrupado'].value_counts().reset_index()
    language_counts.columns = ['Idioma', 'Quantidade']

    # Calcular porcentagens
    total_respostas = language_counts['Quantidade'].sum()
    language_counts['Porcentagem'] = (language_counts['Quantidade'] / total_respostas) * 100

    # Criando o gráfico de barras
    fig = px.bar(language_counts, x='Idioma', y='Porcentagem', text='Porcentagem',
                 title='Qual Idioma você fala?', color='Idioma')
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(xaxis_title="Idioma", yaxis_title="Porcentagem",
                      uniformtext_minsize=8, uniformtext_mode='hide')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',
                      yaxis_title="Porcentagem (%)",
                      xaxis_title='',
                      legend=dict(
                          orientation="h",
                          yanchor="bottom",
                          y=-0.3, # Ajuste conforme necessário
                          xanchor="center",
                          x=0.5
                      ),
                      xaxis=dict(
                        tickmode='array',
                        tickvals=[]
                        ))
    st.plotly_chart(fig)


data = load_data()
data['PERG.5'] = data['PERG.5'].astype(str)
data['PERG.5'] = data['PERG.5'].str.extract('(\d+)')[0]  # Extrai apenas os dígitos
data = data[~data['PERG.5'].isnull()]  # Remove linhas onde a idade não pôde ser extraída
data['PERG.5'] = data['PERG.5'].astype(int)  # Converte para inteiro
data = data[(data['PERG.5'] > 0) & (data['PERG.5'] <= 120)]  # Filtra idades razoáveis


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

        data['PERG.5'] = data['PERG.5'].astype(int)

        # Adicionando o filtro de idade como antes
        options_idade = ['Todos', 'Menos de 35 anos', 'Mais de 35 anos']
        if 'selected_idade' not in st.session_state:
            st.session_state['selected_idade'] = 'Todos'

        selected_idade = st.sidebar.selectbox(
            "Selecione a Faixa Etária:",
            options=options_idade,
            index=options_idade.index(st.session_state['selected_idade'])
        )
        st.session_state['selected_idade'] = selected_idade

        # Aplicando o filtro de idade ao DataFrame
        if selected_idade == 'Menos de 35 anos':
            filtered_data = filtered_data[filtered_data['PERG.5'] < 35]
        elif selected_idade == 'Mais de 35 anos':
            filtered_data = filtered_data[filtered_data['PERG.5'] > 35]

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
            "Selecione o Sexo dos Entrevistados:",
            options=options_sexo,
            default=st.session_state['selected_sexo']
        )
        st.session_state['selected_sexo'] = selected_sexo

        # Aplicando o filtro de sexo, caso alguma opção tenha sido selecionada
        if st.session_state['selected_sexo']:
            filtered_data = filtered_data[filtered_data['PERG.9'].isin(st.session_state['selected_sexo'])]

            # Aqui continuam as funções de plotagem ou exibição de dados que já estavam sendo utilizadas
            plot_bar_chart_perg26(filtered_data)

else:
    st.write("Selecione os filtros para visualizar os dados.")
