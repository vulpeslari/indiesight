import streamlit as st
import pandas as pd
import time
import csv
import base64

# Função para carregar o dataset CSV
def load_data1():
    try:
        data = pd.read_csv('dataset.csv', on_bad_lines='skip')

        if 'Username' not in data.columns or 'Game' not in data.columns:
            st.error("O arquivo CSV deve conter as colunas: 'Username' e 'Game'")
            return pd.DataFrame(columns=["Username", "Game"])
        return data
    except FileNotFoundError:
        st.warning("Arquivo CSV não encontrado.")
        return pd.DataFrame(columns=["Username", "Game"])

# Função para carregar as descrições dos jogos
def load_games_desc():
    games_desc = {}
    try:
        with open('games_desc.csv', mode='r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            headers = next(reader)
            for row in reader:
                print(f"Processing row: {row}")  # Debugging print
                if len(row) >= 3:
                    game_name, image_url, description = row[0], row[1], row[2]
                    games_desc[game_name] = {"image": image_url, "description": description}
                else:
                    st.warning(f"Formato incorreto na linha: {row}")
    except FileNotFoundError:
        st.warning("Arquivo games_desc.csv não encontrado.")
    except UnicodeDecodeError as e:
        st.error(f"Erro ao ler o arquivo: {e}")
    return games_desc

# Carregar as descrições dos jogos
games_desc = load_games_desc()

# Carregar o dataset de usuários e suas listas de jogos adquiridos
users_lists = load_data1()

def generate_Medium(games_list, dataset):
    medium_games = {
        "Single_Player": 0,
        "Multi_Player": 0,
        "Rouguelike": 0,
        "Terror": 0,
        "Visual_Novel": 0,
        "Resource_Managment": 0,
        "RPG": 0,
        "Combat": 0,
        "Simulator": 0,
        "Puzzle": 0,
        "Adventure": 0
    }

    for game in games_list:
        if game in dataset:
            for key in medium_games.keys():
                medium_games[key] += dataset[game][key]

    for key in medium_games:
        medium_games[key] = round(medium_games[key] / len(games_list), 2)

    return medium_games

def manhattan(array1, array2):
    distance = 0
    for key in array1.keys():
        if key in array2:
            distance += abs(array1[key] - array2[key])
    return distance

def recommend(username, user_list):
    # Filtrar lista de jogos do usuário
    user_games = user_list[user_list['Username'] == username]['Game'].tolist()

    if not user_games:
        return []

    medium_taste = generate_Medium(user_games, games_data)

    distances = {}
    for game_name, game_data in games_data.items():
        distances[game_name] = manhattan(medium_taste, game_data)

    # Normalizar as distâncias para calcular porcentagem de recomendação
    max_distance = max(distances.values())
    recommendations = {
        game_name: 100 - ((distance / max_distance) * 100) 
        for game_name, distance in distances.items()
    }

    # Ordenar recomendações por maior porcentagem
    sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
    return sorted_recommendations

# Função para carregar os dados dos jogos em um dicionário
def load_games_data():
    games_data = {}
    try:
        with open('Games_dataset.csv', mode='r') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Ignora o cabeçalho
            for row in reader:
                game_name, Single_Player, Multi_Player, Rouguelike, Terror, Visual_Novel, Resource_Managment, RPG, Combat, Simulator, Puzzle, Adventure = row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]
                games_data[game_name] = {
                    "Single_Player": int(Single_Player),
                    "Multi_Player": int(Multi_Player),
                    "Rouguelike": int(Rouguelike),
                    "Terror": int(Terror),
                    "Visual_Novel": int(Visual_Novel),
                    "Resource_Managment": int(Resource_Managment),
                    "RPG": int(RPG),
                    "Combat": int(Combat),
                    "Simulator": int(Simulator),
                    "Puzzle": int(Puzzle),
                    "Adventure": int(Adventure)
                }
    except FileNotFoundError:
        st.warning("Arquivo Games_dataset.csv não encontrado.")
    return games_data

# Carregar dados dos jogos
games_data = load_games_data()

# Função para adicionar à lista de um usuário
def add_rating(username, game):
    new_entry = pd.DataFrame({"Username": [username], "Game": [game]})
    new_entry.to_csv('dataset.csv', mode='a', header=False, index=False)

# Função de carregamento
def loading_screen():
    with st.spinner('Carregando...'):
        time.sleep(3)

# Função principal para a página
def main_page():
    # Exibir a logo e descrição antes das abas
    st.markdown(
    """
    <div style='text-align: center;'>
        <img src='data:image/png;base64,{}' width='400'>
        <p style='margin-top:20px;'><i>O <b>IndieSight</b> é um projeto de recomendação de jogos que são, 
            assim como nós, independentes. Nos ajude recomendando os jogos que mais gosta para 
            oferecer uma recomendação que não só é mais precisa, como é a sua cara!</i></p>
    </div>
    """.format(base64.b64encode(open("logo.png", "rb").read()).decode()),
    unsafe_allow_html=True
)
    
    # Criar abas após a descrição e logo
    tab1, tab2 = st.tabs(["Recomendar Jogos", "Ver Recomendações"])

    st.markdown(
    """
    <style>
        .stTabs>div>div>div>button {
            width: 100%;
            text-align: center;
            border: none;
            padding: 15px;
            font-size: 18px;
            font-weight: bold;
        }

        .stTabs>div>div>div>button:focus {
            outline: none;
        }
    </style>
    """, unsafe_allow_html=True
)

    # Aba 1: Recomendação de Jogos
    with tab1:
        st.header("Ajude recomendando um jogo!")
        
        username = st.text_input("Digite um nome de usuário:")
        
        if username:
            game_options = list(games_data.keys())
            game = st.selectbox("Escolha um jogo:", game_options)

            if st.button("Adicionar Recomendação"):
                add_rating(username, game)
                st.success(f"Recomendação de '{username}' adicionada com sucesso!")

    # Aba 2: Visualizar Recomendações
    with tab2:
        st.header("Jogos que são a sua cara!")
        
        username = st.selectbox("Escolha um usuário para recomendações:", users_lists['Username'].unique())

        st.markdown("---")

        if username:
            recommendations = recommend(username, users_lists)

            if not recommendations:
                st.warning("Nenhuma recomendação disponível para este usuário.")
            else:
                # Initialize session state for pagination
                if 'page' not in st.session_state:
                    st.session_state.page = 0

                # Pagination logic
                items_per_page = 10
                start_idx = st.session_state.page * items_per_page
                end_idx = start_idx + items_per_page
                paginated_recommendations = recommendations[start_idx:end_idx]

                for index, (game_name, recommendation_percentage) in enumerate(paginated_recommendations, start=start_idx + 1):
                    col1, col2 = st.columns([5, 1])
                    score_bg = "green" if recommendation_percentage > 75 else "orange" if 50 <= recommendation_percentage <= 75 else "red"

                    with col1:
                        # Exibir nome do jogo
                        st.markdown(f"""
                        <div style='padding: 10px; margin-bottom: 20px; font-size: 26px;'>
                            <strong>‣  {index}. {game_name}</strong>
                        </div>
                        """, unsafe_allow_html=True)

                        if game_name in games_desc:
                            # Exibir a imagem do jogo ao lado da descrição
                            colA, colB = st.columns([3, 4])
                            with colA:
                                st.image(games_desc[game_name]["image"], width=250)
                            with colB:
                                st.write(games_desc[game_name]["description"])

                    with col2:
                        # Exibir a pontuação de recomendação
                        score_bg = "green" if recommendation_percentage > 75 else "orange" if 50 <= recommendation_percentage <= 75 else "red"
                        st.markdown(f"""
                        <div style='text-align: center; background-color: {score_bg}; width: 100%; padding: 5px; border-radius: 5px;'>
                            <b>★ {recommendation_percentage:.1f}%</b>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("---")

                # Navigation buttons
                col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
                with col2:
                    if st.session_state.page > 0:
                        if st.button("⯇ Anterior"):
                            st.session_state.page -= 1
                with col4:
                    if end_idx < len(recommendations):
                        if st.button("Próximo ⯈"):
                            st.session_state.page += 1
        else:
            st.write("Escolha um usuário válido para ver as recomendações.")

# Exibir tela de carregamento e página principal
loading_screen()
main_page()
