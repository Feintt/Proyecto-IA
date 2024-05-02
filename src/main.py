from seed import seed
from neo4j_manager import Neo4jManager
from search_algorithms import recommend_movies
import streamlit as st
from pyvis.network import Network
import os


def fetch_graph_data(manager: Neo4jManager):
    # Consulta para obtener solo los nodos y relaciones más relevantes
    query = """
    MATCH (n)-[r]->(m)
    WHERE n.name IS NOT NULL AND m.name IS NOT NULL
    RETURN n.name AS n_name, m.name AS m_name, type(r) AS relationship_type
    LIMIT 100
    """
    try:
        data = manager.run_query(query)
        if not data:
            print("No data found with the given query.")
            return []
        return data
    except Exception as e:
        print(f"Error fetching graph data: {e}")
        return []


def create_vis(data):
    nt = Network("500px", "500px")
    for record in data:
        n_name = record['n_name']
        m_name = record['m_name']
        relationship_type = record['relationship_type']
        if n_name and m_name:
            nt.add_node(n_name, title=n_name, label=n_name)
            nt.add_node(m_name, title=m_name, label=m_name)
            nt.add_edge(n_name, m_name, title=relationship_type)
    path = "graph.html"
    nt.save_graph(path)
    return path


def main():
    manager = Neo4jManager()
    # seed(manager)

    random_user = manager.get_random_user_name()
    recommendations = recommend_movies(manager, random_user)
    print(f"Recomendaciones para {random_user}:")
    for movie in recommendations:
        print(movie)

    st.title("Neo4j Graph Visualization")
    data = fetch_graph_data(manager)
    path = create_vis(data)
    if os.path.exists(path):
        with open(path, "r") as file:
            html_content = file.read()
            st.components.v1.html(html_content, height=500)
    else:
        st.error("No se pudo encontrar el archivo de visualización del grafo.")


if __name__ == "__main__":
    main()
