import os
import streamlit as st
from pyvis.network import Network
from neo4j_manager import Neo4jManager
import streamlit
import time
from datetime import datetime, timedelta
import random
import heapq
import streamlit.components.v1 as components


def time_tracker(func):
    """A decorator that displays the execution time of the function it wraps in Streamlit."""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)  # Execute the wrapped function
        end_time = time.time()
        execution_time = end_time - start_time
        st.write(
            f"Execution time of {func.__name__}: {execution_time:.4f} seconds")  # Use Streamlit to display the execution time
        return result

    return wrapper


def render_html_graph(path):
    if os.path.exists(path):
        with open(path) as file:
            html_content = file.read()
            st.components.v1.html(html_content, height=500)
    else:
        st.error("No se pudo encontrar el archivo de visualización del grafo.")


def create_vis(data, user_names, selected_user=None):
    # Create static directory of it does not exist
    if not os.path.exists("static"):
        os.makedirs("static")

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
        streamlit.write(movie)
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


clases = {
    'Matemáticas': ['Lunes 8:00-10:00', 'Miércoles 10:00-12:00'],
    'Historia': ['Lunes 10:00-12:00', 'Jueves 8:00-10:00'],
    'Ciencias': ['Martes 8:00-10:00', 'Viernes 10:00-12:00'],
    'Literatura': ['Martes 10:00-12:00', 'Miércoles 8:00-10:00'],
    'Física': ['Miércoles 14:00-16:00', 'Viernes 8:00-10:00'],
    'Química': ['Jueves 10:00-12:00', 'Viernes 14:00-16:00']
}

# Definición de las restricciones de disponibilidad de los profesores
disponibilidad_profesores = {
    'Profesor1': ['Lunes 8:00-12:00', 'Martes 8:00-12:00', 'Miércoles 8:00-12:00'],
    'Profesor2': ['Lunes 10:00-14:00', 'Martes 10:00-14:00', 'Miércoles 10:00-14:00'],
    'Profesor3': ['Martes 14:00-18:00', 'Jueves 14:00-18:00', 'Viernes 14:00-18:00'],
    'Profesor4': ['Lunes 14:00-18:00', 'Miércoles 14:00-18:00', 'Viernes 10:00-14:00'],
    'Profesor5': ['Lunes 8:00-12:00', 'Miércoles 8:00-12:00', 'Viernes 8:00-12:00'],
}
tiempo_clases = {
    "Matemáticas": "2 horas",
    "Historia": "2 horas",
    "Ciencias": "2 horas",
    "Literatura": "2 horas",
    "Física": "2 horas",
    "Química": "2 horas",
}


def generar_horario_inicial():
    horario = {}
    for clase in clases.keys():
        horario[clase] = random.choice(clases[clase])
    return horario

    # Función para evaluar la calidad de un horario


def evaluar_horario(horario):
    # Por simplicidad, evaluamos simplemente la disponibilidad de los profesores
    for clase, horario_clase in horario.items():
        for profesor, horarios_disponibles in disponibilidad_profesores.items():
            if horario_clase not in horarios_disponibles:
                return False
    return True

    # Función de hill climbing para mejorar el horario


def hill_climbing():
    horario_actual = generar_horario_inicial()
    mejor_horario = horario_actual.copy()

    while True:
        vecino = horario_actual.copy()
        clase_a_cambiar = random.choice(list(clases.keys()))
        nuevo_horario = random.choice(clases[clase_a_cambiar])
        vecino[clase_a_cambiar] = nuevo_horario

        if evaluar_horario(vecino):
            mejor_horario = vecino.copy()

        if random.random() < 0.1:
            break

        horario_actual = vecino.copy()

    return mejor_horario

    # Clase para asignar horarios de clases


class ClassScheduler:
    def __init__(self, schedule, classes):
        self.schedule = schedule
        self.classes = classes
        self.start_time = datetime.strptime("00:00", "%H:%M")
        self.visited_slots = set()  # Conjunto para mantener los nodos visitados

    def calculate_remaining_time(self, current_time, event_time):
        if current_time < event_time:
            return event_time - current_time
        else:
            return timedelta(days=1) - (current_time - event_time)

    def heuristic(self, current_time, remaining_classes):
        # Simple heuristic: estimated time to schedule remaining classes
        return sum([class_duration.total_seconds() for class_duration in remaining_classes])

    def find_earliest_available_slot(self, current_time):
        earliest_slot = None
        min_remaining_time = timedelta(days=1)

        for day, slots in self.schedule.items():
            for start_time, end_time in slots:
                slot = (day, start_time)
                if slot not in self.visited_slots:
                    start = datetime.strptime(start_time, "%H:%M")
                    if start >= current_time:
                        remaining_time = self.calculate_remaining_time(current_time, start)
                        if remaining_time < min_remaining_time:
                            earliest_slot = (day, start_time)
                            min_remaining_time = remaining_time

        return earliest_slot

    def assign_class_schedule(self):
        current_time = self.start_time
        remaining_classes = [(duration, class_name) for class_name, duration in self.classes.items()]
        heapq.heapify(remaining_classes)
        class_schedule = {}

        for day in self.schedule:  # Iterar sobre todos los días disponibles
            current_time = self.start_time  # Reiniciar el tiempo al principio del día
            while remaining_classes:
                current_slot = self.find_earliest_available_slot(current_time)

                if current_slot:
                    current_day, start_time = current_slot
                    duration, class_name = heapq.heappop(remaining_classes)
                    end_time = datetime.strptime(start_time, "%H:%M") + duration

                    class_schedule[class_name] = (current_day, start_time, end_time.strftime("%H:%M"))
                    current_time = end_time
                    # Marcar el slot como visitado
                    self.visited_slots.add(current_slot)
                else:
                    break

        return class_schedule


def visualize_graph_snapshots(graphs):
    tmp_dir = 'tmp'
    os.makedirs(tmp_dir, exist_ok=True)  # Ensure the directory exists

    # Clear the tmp directory of old files
    for file in os.listdir(tmp_dir):
        os.remove(os.path.join(tmp_dir, file))

    for i, graph in enumerate(graphs):
        file_path = os.path.join(tmp_dir, f"graph_{i}.html")
        # Create the network visualizations
        nt = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
        nt.barnes_hut()  # Set the physics layout of the network

        # Add nodes and edges
        for node, ndata in graph.nodes(data=True):
            nt.add_node(node, title=node, label=node, color=ndata.get('color', 'blue'))
        for source, target, edata in graph.edges(data=True):
            weight = edata.get('weight', 1)
            nt.add_edge(source, target, value=weight)

        # Show physics control buttons
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
    components.html(html_content, height=800, scrolling=True)  # Enable scrolling within the iframe
