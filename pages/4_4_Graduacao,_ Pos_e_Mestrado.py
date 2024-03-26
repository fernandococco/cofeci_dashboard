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


def plot_bar_chart_perg18(df):
    # Categorias específicas para manter
    categorias_especificas = ["Administração", "Direito", "Engenharia", "Ciências Contábeis", "Pedagogia"]
    
    # Função para categorizar as respostas
    def categorizar_resposta(text):
        if text in categorias_especificas:
            return text
        elif text == "Não":
            return None  # Retorna None para as respostas "Não", que serão removidas
        else:
            return "Outros"
    
    # Aplica a função de categorização para cada resposta
    df['Categoria'] = df['PERG.18'].apply(categorizar_resposta)

    # Remove as entradas com categoria None (respostas "Não")
    df = df.dropna(subset=['Categoria'])

    # Contagem de quantidades por categoria e conversão para porcentagem
    df_agrupado = df['Categoria'].value_counts(normalize=True).reset_index()
    df_agrupado.columns = ['Categoria', 'Porcentagem']
    df_agrupado['Porcentagem'] *= 100
    
    # Cores para o gráfico
    cores = ['#FFA07A', '#20B2AA', '#778899', '#9370DB', '#3CB371', '#FFD700', '#4361ee']

    # Criando o gráfico de barras
    fig = px.bar(df_agrupado, x='Categoria', y='Porcentagem', title='Áreas de Formação',
                 text='Porcentagem', color='Categoria', color_discrete_sequence=cores)

    # Ajustes finais no gráfico
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
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


def plot_bar_chart_perg20(df):
    # Remover valores nulos da coluna "PERG.22"
    df = df.dropna(subset=['PERG.20'])

    # Definindo as categorias específicas para manter
    categorias_especificas = ["Direito", "Direito Imobiliário","Administração","Marketing","MBA"]
    
    # Função para agrupar as respostas
    def agrupar_respostas(valor):
        if valor in categorias_especificas:
            return valor
        else:
            return "Outros"
    
    # Aplicando a função de agrupamento na coluna de interesse
    df['Categoria'] = df['PERG.20'].apply(agrupar_respostas)
    
    # Contagem de quantidades por categoria e conversão para porcentagem
    df_agrupado = df['Categoria'].value_counts(normalize=True).reset_index()
    df_agrupado.columns = ['Categoria', 'Porcentagem']
    df_agrupado['Porcentagem'] *= 100  # Convertendo para porcentagem
    
    # Criando o gráfico de barras
    fig = px.bar(df_agrupado, x='Categoria', y='Porcentagem', title='Áreas de Pós-Graduação',
                 text='Porcentagem', color='Categoria')
    
    # Personalizando o texto nas barras para mostrar a porcentagem com duas casas decimais
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
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
    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)


def plot_bar_chart_perg22(df):
    # Remover valores nulos da coluna "PERG.22"
    df = df.dropna(subset=['PERG.22'])

    # Definindo as categorias específicas para manter
    categorias_especificas = ["MBA", "Administração"]
    
    # Função para agrupar as respostas
    def agrupar_respostas(valor):
        if valor in categorias_especificas:
            return valor
        else:
            return "Outros"
    
    # Aplicando a função de agrupamento na coluna de interesse
    df['Categoria'] = df['PERG.22'].apply(agrupar_respostas)
    
    # Contagem de quantidades por categoria e conversão para porcentagem
    df_agrupado = df['Categoria'].value_counts(normalize=True).reset_index()
    df_agrupado.columns = ['Categoria', 'Porcentagem']
    df_agrupado['Porcentagem'] *= 100  # Convertendo para porcentagem
    
    # Criando o gráfico de barras
    fig = px.bar(df_agrupado, x='Categoria', y='Porcentagem', title='Áreas de Mestrado',
                 text='Porcentagem', color='Categoria')
    
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
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
    
    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)


# Carregar os dados
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
            plot_bar_chart_perg18(filtered_data)
            plot_bar_chart_perg20(filtered_data)
            plot_bar_chart_perg22(filtered_data)

else:
    st.write("Selecione os filtros para visualizar os dados.")
