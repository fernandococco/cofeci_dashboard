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
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    password = st.text_input("Senha: ", type="password", key="password")
    
    # Habilitar o botão quando a senha for preenchida.
    password_entered_button = st.button("Enviar Senha", on_click=password_entered)

    if "password_correct" in st.session_state:
        st.error("Senha Incorreta. ")
    return False

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

def load_data():
    data = pd.read_csv('cofeci.csv')
    return data

col1, col_empty, col2 = st.columns([1, 2, 1])

# Na primeira coluna, adicionar o logo do Cofeci
with col1:
    st.image('cofeci3.jpeg', width=100)  # Ajuste a largura conforme necessário

# Na segunda coluna, adicionar o logo do Rei
with col2:
    st.image('125.1_LOGO REI-01.png', width=100)  # Ajuste a largura conforme necessário


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


# Carregar os dados
data = load_data()

# Filtro INICIAL por Estado (PERG.6), ordenado alfabeticamente
selected_perg_6 = st.sidebar.multiselect(
    'Selecione o Estado:', 
    sorted(data['PERG.6'].unique())  # Ordenando os estados em ordem alfabética
)

# Filtrar dados com base no estado selecionado para a próxima escolha
if selected_perg_6:
    filtered_data_by_perg_6 = data[data['PERG.6'].isin(selected_perg_6)]
    
    # Filtro por Interior ou Capital (PERG.7) usando st.radio
    # Incluindo 'Ambos' como uma opção para permitir seleção de todos os dados
    options_perg_7 = ['Ambos', 'Capital', 'Interior']
    selected_perg_7 = st.sidebar.radio("Selecione Interior ou Capital:", options=options_perg_7)

    # Aplicar filtros com base em Interior ou Capital
    if selected_perg_7 == 'Ambos':
        # Se 'Ambos' for selecionado, não filtrar por este critério
        final_filtered_data = filtered_data_by_perg_6
    else:
        # Se 'Capital' ou 'Interior' for selecionado, filtrar por esse critério
        final_filtered_data = filtered_data_by_perg_6[filtered_data_by_perg_6['PERG.7'] == selected_perg_7]
else:
    # Se nenhum estado for selecionado, criar um DataFrame vazio
    final_filtered_data = pd.DataFrame(columns=data.columns)

# Verificar se há dados filtrados para exibir
if not final_filtered_data.empty:
    # Chamadas para as funções de plotagem dos gráficos
    plot_bar_chart_perg5(final_filtered_data)
    plot_donut_chart_perg9(final_filtered_data)
else:
    st.write("Selecione os filtros para visualizar os dados.")
