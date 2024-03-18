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

col1, col_empty, col2 = st.columns([1, 2, 1])

# Na primeira coluna, adicionar o logo do Cofeci
with col1:
    st.image('cofeci3.jpeg', width=100)  # Ajuste a largura conforme necessário

# Na segunda coluna, adicionar o logo do Rei
with col2:
    st.image('125.1_LOGO REI-01.png', width=100)  # Ajuste a largura conforme necessário



# Função para plotar o gráfico de barras
def plot_bar_chart_perg13(df):
    # Normalizando categorias específicas para "Negro"
    df['PERG.13'] = df['PERG.13'].replace({
        "Negro": "Negro",
        "Africano": "Negro",
        "Preto": "Negro",
        "Amarelo": "Amarelo",
        "AMARELO": "Amarelo"
    })

    # Consolidando categorias para "Não quis responder/Indiferente"
    categorias_indiferente = [
        "Não quis responder", "Não quis informar", "indiferente", "Indiferente", "Indiferente  ",
        "INDIFERNTE", "Não respondeu", "NÃO QUIS RESPONDER.", "Não informa",
        "não se identifica como nada", "Não se interessou em responder ao questionário",
        "99", "Não quis informar"
    ]
    
    df['PERG.13'] = df['PERG.13'].apply(lambda x: "Não quis responder/Indiferente" if x in categorias_indiferente else x)

    # Filtrando o DataFrame para manter somente as categorias desejadas
    categorias_desejadas = ["Branco", "Pardo", "Negro", "Não quis responder/Indiferente"]
    df_filtrado = df[df['PERG.13'].isin(categorias_desejadas)]

    # Contando a ocorrência das categorias normalizadas e convertendo para porcentagem
    df_agrupado = df_filtrado['PERG.13'].value_counts(normalize=True).reset_index()
    df_agrupado.columns = ['Resposta', 'Porcentagem']
    df_agrupado['Porcentagem'] *= 100

    # Cores especificadas
    cores = ['#05668d', '#028090', '#00a896', '#02c39a', '#ff9e00', '#00b4d8', '#0096c7', '#0077b6', '#023e8a', '#03045e']

    # Criando o gráfico de barras
    fig = px.bar(df_agrupado, x='Resposta', y='Porcentagem', title='Qual a sua etnia?',
                 text='Porcentagem', color='Resposta', color_discrete_sequence=cores)
    
    # Ajustes finais no gráfico
    fig.update_traces(texttemplate='%{text:.2s}%')
    fig.update_layout(xaxis_title="Categoria", yaxis_title="Porcentagem (%)", xaxis={'categoryorder':'total descending'})
    
    # Exibindo o gráfico
    st.plotly_chart(fig) 


def plot_bar_chart_perg14(df):
    # Profissões especificadas na lista fornecida
    profissoes_listadas = [
        "Não tem outra profissão",
        "Administrador(a)",
        "Advogado(a)",
        "Empresário(a)",
        "Funcionário público",
        "Aposentado",
        "Comerciante",
        "Engenheiro(a)",
        "Professor(a)"
    ]
    
    # Cria uma nova coluna 'Categoria' no DataFrame
    df['Categoria'] = df['PERG.14'].apply(lambda x: x if x in profissoes_listadas else "Outros")

    # Contagem de quantidades por categoria
    df_agrupado = df['Categoria'].value_counts(normalize=True).reset_index()
    df_agrupado.columns = ['Resposta', 'Porcentagem']

    # Convertendo a porcentagem para o formato de porcentagem no gráfico
    df_agrupado['Porcentagem'] *= 100

    # Cores da imagem enviada
    cores = ["#f94144", "#f3722c", "#f8961e", "#f9844a", "#f9c74f", "#90be6d", "#43aa8b", "#4d908e", "#577590", "#277da1"]

    # Criando o gráfico de barras com as cores especificadas
    fig = px.bar(df_agrupado, x='Resposta', y='Porcentagem', title='Possui outra profissão além de corretor?',
                 text='Porcentagem', color='Resposta', color_discrete_sequence=cores)

    # Ajustes finais no gráfico
    fig.update_layout(xaxis_title="Profissão", yaxis_title="Porcentagem (%)", xaxis={'categoryorder':'total descending'})
    fig.update_traces(texttemplate='%{text:.2f}%')

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
            "Selecione o Sexo dos Entrevistados:",
            options=options_sexo,
            default=st.session_state['selected_sexo']
        )
        st.session_state['selected_sexo'] = selected_sexo

        # Aplicando o filtro de sexo, caso alguma opção tenha sido selecionada
        if st.session_state['selected_sexo']:
            filtered_data = filtered_data[filtered_data['PERG.9'].isin(st.session_state['selected_sexo'])]

            # Aqui continuam as funções de plotagem ou exibição de dados que já estavam sendo utilizadas
            plot_bar_chart_perg13(filtered_data)
            plot_bar_chart_perg14(filtered_data)

else:
    st.write("Selecione os filtros para visualizar os dados.")