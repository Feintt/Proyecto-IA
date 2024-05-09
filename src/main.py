from utils import *
from search_algorithms import *
import streamlit.components.v1 as components
from pyvis.network import Network
import networkx as nx
import os
from seed import seed
from datetime import datetime, timedelta
import random
import heapq

clases = {
            'Matemáticas': ['Lunes 8:00-10:00', 'Miércoles 10:00-12:00'],
            'Historia': ['Lunes 10:00-12:00', 'Jueves 8:00-10:00'],
            'Ciencias': ['Martes 8:00-10:00', 'Viernes 10:00-12:00'],
            'Literatura': ['Martes 10:00-12:00', 'Miércoles 8:00-10:00'],
            'Física': ['Miércoles 14:00-16:00', 'Viernes 8:00-10:00'],
            'Química': ['Jueves 10:00-12:00', 'Viernes 14:00-16:00']
        }

         #Definición de las restricciones de disponibilidad de los profesores
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

        # Función para generar un horario inicial aleatorio
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
    st.title("Multi-page Streamlit App")
    menu = ["Movies", "Scheduler", "Contact"]
    choice = st.sidebar.selectbox("Navigation", menu)
    if choice == "Movies":
        st.subheader("Movies Page")
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
        # Add content for the home page

    elif choice == "Scheduler":
        st.subheader("Scheduler")
         # Definir la interfaz de usuario con Streamlit
        st.title("Generador de Horarios Escolares")
        st.write("Diccionario de Clases:")
        for clase, horarios_clase in clases.items():
            st.write(f"- {clase}: {', '.join(horarios_clase)}")
        st.write("tiempo de clases:")
        for clase, tiempo_clase in tiempo_clases.items():
            st.write(f"- {clase}: {tiempo_clase}")
        st.header("Generador de Horario Aleatorio")
        st.write("Haz clic en el botón para generar un horario escolar aleatorio.")
        if st.button("Generar Horario Aleatorio"):
            mejor_horario = hill_climbing()
            st.write("Mejor horario encontrado:")
            for clase, horario in mejor_horario.items():
                st.write(f"{clase}: {horario}")

            st.header("Asignador de Horario de Clases")
            st.write("Haz clic en el botón para asignar horarios de clases.")
            if st.button("Asignar Horario de Clases"):
                # Ejemplo de horarios
                schedule = {
                    "Lunes": [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00")],
                    "Martes": [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00")],
                    "Miercoles": [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00")],
                    "Jueves": [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00")],
                    "Viernes": [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00")],
                }

                # Diccionario de clases con duraciones
                classes = {
                    "Matemáticas": timedelta(hours=2),
                    "Historia": timedelta(hours=2),
                    "Ciencias": timedelta(hours=2),
                    "Literatura": timedelta(hours=2),
                    "Física": timedelta(hours=2),
                    "Química": timedelta(hours=2),
                }

                scheduler = ClassScheduler(schedule, classes)
                class_schedule = scheduler.assign_class_schedule()
                st.write("Mejor horario encontrado:")
                for class_name, (day, start_time, end_time) in class_schedule.items():
                    st.write(f"{class_name}: {day} {start_time}-{end_time}")


    elif choice == "Contact":
        st.subheader("Contact Page")
    # Streamlit app title



if __name__ == "__main__":
    main()
