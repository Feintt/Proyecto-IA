import os
import streamlit as st
from pyvis.network import Network
from neo4j_manager import Neo4jManager


def render_html_graph(path):
    if os.path.exists(path):
        with open(path) as file:
            html_content = file.read()
            st.components.v1.html(html_content, height=500)
    else:
        st.error("No se pudo encontrar el archivo de visualización del grafo.")


def create_vis(data, user_names, selected_user=None):
    nt = Network("800px", "1000px")
    for record in data:
        n_name = record['n_name']
        m_name = record['m_name']
        relationship_type = record['relationship_type']
        if n_name and m_name:
            if n_name == selected_user:
                nt.add_node(n_name, title=n_name, label=n_name, color="green")
            elif n_name in user_names:
                nt.add_node(n_name, title=n_name, label=n_name, color="red")
            else:
                nt.add_node(n_name, title=n_name, label=n_name, color="blue")

            if m_name == selected_user:
                nt.add_node(m_name, title=m_name, label=m_name, color="green")
            elif m_name in user_names:
                nt.add_node(m_name, title=m_name, label=m_name, color="red")
            else:
                nt.add_node(m_name, title=m_name, label=m_name, color="blue")

            nt.add_edge(n_name, m_name, title=relationship_type)

    path = "static/graph.html"
    nt.save_graph(path)
    return path


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
