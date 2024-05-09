from utils import *
from search_algorithms import *
import streamlit.components.v1 as components
from pyvis.network import Network
import networkx as nx
import os
from seed import seed


def visualize_graph_snapshots(graphs):
    tmp_dir = 'tmp'
    os.makedirs(tmp_dir, exist_ok=True)  # Ensure the directory exists

    for i, graph in enumerate(graphs):
        file_path = os.path.join(tmp_dir, f"graph_{i}.html")
        if True:  # Only create if it doesn't already exist
            nt = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
            nt.barnes_hut()  # Set the physics layout of the network

            # Iterate over all nodes and edges in the NetworkX graph
            for node, ndata in graph.nodes(data=True):
                nt.add_node(node, title=node, label=node, color=ndata.get('color', 'blue'))

            for source, target, edata in graph.edges(data=True):
                weight = edata.get('weight', 1)
                nt.add_edge(source, target, value=weight)

            # Add neighbor data to node hover data
            neighbor_map = nt.get_adj_list()
            for node in nt.nodes:
                node["title"] += " Neighbors:<br>" + "<br>".join(neighbor_map[node["id"]])
                node["value"] = len(neighbor_map[node["id"]])

            # Show physics control buttons in the network visualization
            nt.show_buttons(filter_=['physics'])

            # Save the network to an HTML file
            nt.save_graph(file_path)

    # Display logic using Streamlit with navigation
    if 'current_graph_index' not in st.session_state:
        st.session_state.current_graph_index = 0

    col1, col2 = st.columns(2)
    with col1:
        if st.button('Previous'):
            if st.session_state.current_graph_index > 0:
                st.session_state.current_graph_index -= 1
    with col2:
        if st.button('Next'):
            if st.session_state.current_graph_index < len(graphs) - 1:
                st.session_state.current_graph_index += 1

    current_index = st.session_state.current_graph_index
    file_path = os.path.join(tmp_dir, f"graph_{current_index}.html")
    with open(file_path) as file:
        html_content = file.read()
    components.html(html_content, height=800)


def main():
    # Streamlit app title
    st.title("Neo4j Graph Visualization")

    # Initialize Neo4jManager
    manager = Neo4jManager()

    # Get all usernames
    user_names = sorted([user['user_name'] for user in manager.get_all_users()])

    # Input fields for limits
    user_limit = st.sidebar.number_input("Select the user limit:", min_value=1, value=100)
    movies_limit = st.sidebar.number_input("Select the movie limit:", min_value=1, value=100)
    limit = st.sidebar.number_input("Select the node limit:", min_value=1, value=100)

    # Select a user
    selected_user = st.sidebar.selectbox("Select a user:", user_names)

    # Seed the database
    # seed(manager)

    # Algorithm selection
    algorithm = st.sidebar.selectbox(
        "Choose the algorithm:",
        ("Beam Search", "Greedy Best-First Search", "Hill Climbing")
    )

    # Fetch and show graph data
    data = fetch_graph_data(manager, user_limit, movies_limit, limit)
    st.write(data)

    # Visualization tabs
    tab1, tab2, tab3 = st.tabs(["General Graph", "Recommendations", "Algorithm Visualization"])

    with tab1:
        path = create_vis(data, user_names, selected_user)
        render_html_graph(path)  # Assuming this function embeds the HTML in Streamlit

    with tab2:
        # Display recommendations based on the selected algorithm
        if algorithm == "Beam Search":
            recommendations, graphs = beam_search_recommendations(manager, selected_user, 5)
        elif algorithm == "Greedy Best-First Search":
            recommendations, graphs = greedy_best_first_search_recommendations(manager, selected_user, 5)
        elif algorithm == "Hill Climbing":
            recommendations, graphs = hill_climbing_recommendations(manager, selected_user, 5)

        path = visualize_recommendations(manager, selected_user, recommendations)
        render_html_graph(path)  # Render recommendations in the second tab

    with tab3:
        st.header("Algorithm Visualization")
        visualize_graph_snapshots(graphs)


if __name__ == "__main__":
    main()
