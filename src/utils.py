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
    options = ('{"configure": {"enabled": false}, "edges": {"color": {"inherit": true}, "smooth": {"enabled": true, '
               '"type": "dynamic"}}, "interaction": {"dragNodes": true, "hideEdgesOnDrag": false, "hideNodesOnDrag": '
               'false}, "physics": {"enabled": false, "stabilization": {"enabled": true, "fit": true, "iterations": '
               '1000, "onlyDynamicEdges": false, "updateInterval": 50}}}')
    nt.set_options(options)  # Desactivar las físicas
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


def visualize_recommendations(manager, selected_user, recommendations):
    # Crear una instancia de un gráfico de Pyvis
    nt = Network("800px", "800px")
    options = '{"configure": {"enabled": false}, "edges": {"color": {"inherit": true}, "smooth": {"enabled": true, "type": "dynamic"}}, "interaction": {"dragNodes": true, "hideEdgesOnDrag": false, "hideNodesOnDrag": false}, "physics": {"enabled": false, "stabilization": {"enabled": true, "fit": true, "iterations": 1000, "onlyDynamicEdges": false, "updateInterval": 50}}}'
    nt.set_options(options)

    # Añadir nodo para el usuario seleccionado
    nt.add_node(selected_user, title=selected_user, label=selected_user, color="green")

    # Añadir nodos para cada película recomendada y enlaces hacia el usuario seleccionado
    for movie in recommendations:
        nt.add_node(movie, title=movie, label=movie, color="blue")
        nt.add_edge(selected_user, movie, title="Recomendada", color="orange")

    # Guardar y mostrar el gráfico
    path = "static/recommendations_graph.html"
    nt.save_graph(path)
    return path


def fetch_graph_data(manager: Neo4jManager, user_limit=100, movie_limit=100, limit=100):
    # Consulta para obtener una cantidad limitada de usuarios y películas
    query = f"""
        MATCH (u:User)-[r:SAW|LIKED]->(m:Movie)
        RETURN u.name AS n_name, m.name AS m_name, type(r) AS relationship_type
        ORDER BY u.name, m.name, type(r)
        LIMIT {limit}
    """.format(limit=user_limit + movie_limit)
    try:
        data = manager.run_query(query)
        if not data:
            print("No data found with the given query.")
            return []
        return data
    except Exception as e:
        print(f"Error fetching graph data: {e}")
        return []
