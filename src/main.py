from utils import *
from search_algorithms import *


def main():
    # Streamlit app title
    st.title("Neo4j Graph Visualization")

    # Initialize Neo4jManager
    manager = Neo4jManager()

    # Seed the database with some data
    # seed(manager)

    # Get all usernames
    user_names = sorted([user['user_name'] for user in manager.get_all_users()])

    # Select a user
    selected_user = st.selectbox("Selecciona un usuario:", user_names)

    # Field to input the limit of nodes
    user_limit = st.number_input("Selecciona el límite de usuarios:", min_value=1, value=100)

    # Field to input the limit of movies
    movies_limit = st.number_input("Selecciona el límite de películas:", min_value=1, value=100)

    # Field to input the limit of all nodes
    limit = st.number_input("Selecciona el límite de nodos:", min_value=1, value=100)

    # Fetch graph data
    data = fetch_graph_data(manager, user_limit, movies_limit, limit)

    # Create and render the graph
    path = create_vis(data, user_names, selected_user)
    render_html_graph(path)

    # Display recommendations
    recommendations = greedy_recommendations(manager, selected_user)[:5]

    path = visualize_recommendations(manager, selected_user, recommendations)
    render_html_graph(path)

    # Display greedy traversal
    path = visualize_greedy_traversal(manager, selected_user)
    render_html_graph(path)


if __name__ == "__main__":
    main()
