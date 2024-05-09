from utils import *
from search_algorithms import *
from datetime import timedelta


def main():
    # Display the main title of the app.
    st.title("Multi-page Streamlit App")

    # Define the menu options and add a sidebar select box for navigation.
    menu = ["Movies", "Scheduler"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Movies":
        # If "Movies" is selected, create a subheader and main title for the page.
        st.subheader("Movies Page")
        st.title("Neo4j Graph Visualization")

        # Initialize the Neo4j manager to interact with the graph database.
        manager = Neo4jManager()

        # Retrieve a sorted list of all available user names from the database.
        user_names = sorted([user['user_name'] for user in manager.get_all_users()])

        # Provide input fields in the sidebar for setting user, movie, and node limits.
        user_limit = st.sidebar.number_input("Select the user limit:", min_value=1, value=100)
        movies_limit = st.sidebar.number_input("Select the movie limit:", min_value=1, value=100)
        limit = st.sidebar.number_input("Select the node limit:", min_value=1, value=100)

        # Allow the user to select a specific username from the available options.
        selected_user = st.sidebar.selectbox("Select a user:", user_names)

        # (Optional) Seed the database (commented out here).
        # seed(manager)

        # Provide a sidebar select box to choose the recommendation algorithm.
        algorithm = st.sidebar.selectbox(
            "Choose the algorithm:",
            ("Beam Search", "Greedy Best-First Search", "Hill Climbing")
        )

        # Fetch the graph data from the Neo4j database using the specified limits.
        data = fetch_graph_data(manager, user_limit, movies_limit, limit)
        st.write(data)  # Display the fetched data.

        # Create three tabs for general graph, recommendations, and algorithm visualization.
        tab1, tab2, tab3 = st.tabs(["General Graph", "Recommendations", "Algorithm Visualization"])

        # In the first tab, visualize the general graph.
        with tab1:
            # Create a graph visualization for the selected user.
            path = create_vis(data, user_names, selected_user)
            # Render the graph in Streamlit.
            render_html_graph(path)

        # In the second tab, visualize recommendations based on the selected algorithm.
        with tab2:
            # Apply the appropriate recommendation algorithm based on user selection.
            if algorithm == "Beam Search":
                recommendations, graphs = beam_search_recommendations(manager, selected_user, 5)
            elif algorithm == "Greedy Best-First Search":
                recommendations, graphs = greedy_best_first_search_recommendations(manager, selected_user, 5)
            elif algorithm == "Hill Climbing":
                recommendations, graphs = hill_climbing_recommendations(manager, selected_user, 5)

            # Visualize the recommendation graph.
            path = visualize_recommendations(manager, selected_user, recommendations)
            render_html_graph(path)

        # In the third tab, visualize how the selected algorithm processed graph data.
        with tab3:
            st.header("Algorithm Visualization")
            # Visualize snapshots of the graph across algorithm layers.
            visualize_graph_snapshots(graphs)

    elif choice == "Scheduler":
        # If "Scheduler" is selected, provide the scheduler page's subheader and title.
        st.subheader("Scheduler")
        st.title("Generador de Horarios Escolares")

        # Display dictionaries of class schedules and class times (assuming they exist).
        st.write("Diccionario de Clases:")
        for clase, horarios_clase in clases.items():
            st.write(f"- {clase}: {', '.join(horarios_clase)}")

        st.write("Tiempo de clases:")
        for clase, tiempo_clase in tiempo_clases.items():
            st.write(f"- {clase}: {tiempo_clase}")

        # Provide an interface for randomly generating class schedules.
        st.header("Generador de Horario Aleatorio")
        st.write("Haz clic en el botón para generar un horario escolar aleatorio.")
        if st.button("Generar Horario Aleatorio"):
            mejor_horario = hill_climbing()  # Assume this function generates a schedule using hill climbing.
            st.write("Mejor horario encontrado:")
            for clase, horario in mejor_horario.items():
                st.write(f"{clase}: {horario}")

        # Provide an interface for assigning class schedules manually.
        st.header("Asignador de Horario de Clases")
        st.write("Haz clic en el botón para asignar horarios de clases.")
        if st.button("Asignar Horario de Clases"):
            # Example fixed schedule data.
            schedule = {
                "Lunes": [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00")],
                "Martes": [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00")],
                "Miércoles": [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00")],
                "Jueves": [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00")],
                "Viernes": [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00")],
            }

            # Example classes and their durations.
            classes = {
                "Matemáticas": timedelta(hours=2),
                "Historia": timedelta(hours=2),
                "Ciencias": timedelta(hours=2),
                "Literatura": timedelta(hours=2),
                "Física": timedelta(hours=2),
                "Química": timedelta(hours=2),
            }

            # Initialize the scheduler and assign schedules based on the provided data.
            scheduler = ClassScheduler(schedule, classes)
            class_schedule = scheduler.assign_class_schedule()

            # Display the best class schedule found.
            st.write("Mejor horario encontrado:")
            for class_name, (day, start_time, end_time) in class_schedule.items():
                st.write(f"{class_name}: {day} {start_time}-{end_time}")


# If this script is executed directly, invoke the main function.
if __name__ == "__main__":
    main()
