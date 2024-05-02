from seed import seed
from neo4j_manager import Neo4jManager
from utils import *


def main():
    # Streamlit app title
    st.title("Neo4j Graph Visualization")

    # Initialize Neo4jManager
    manager = Neo4jManager()

    # Seed the database with some data
    # seed(manager)

    # Get all usernames
    user_names = [user['user_name'] for user in manager.get_all_users()]

    # Select a user
    selected_user = st.selectbox("Selecciona un usuario:", user_names)

    # Fetch graph data
    data = fetch_graph_data(manager)

    path = create_vis(data, user_names, selected_user)
    render_html_graph(path)


if __name__ == "__main__":
    main()
