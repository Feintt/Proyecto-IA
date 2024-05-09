from utils import *
from search_algorithms import *
from datetime import timedelta


def main():
    st.title("Multi-page Streamlit App")
    menu = ["Movies", "Scheduler"]
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


if __name__ == "__main__":
    main()
