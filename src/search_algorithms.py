from neo4j_manager import Neo4jManager
from collections import defaultdict, deque
import networkx as nx
from utils import time_tracker


@time_tracker
def beam_search_recommendations(manager, user_name, beam_width=5):
    # Retrieve the list of movies seen by the specified user and store their titles in a set.
    seen_movies = set(movie['movie_title'] for movie in manager.get_movies_by_user(user_name))

    # Retrieve the list of movies liked by the user and store their titles in another set.
    liked_movies = set(movie['movie_title'] for movie in manager.get_liked_movies_by_user(user_name))

    # Combine both sets to form a collection of all initial movies, whether seen or liked by the user.
    initial_movies = seen_movies | liked_movies

    # Initialize the search layers starting with the set of all initial movies.
    layers = [initial_movies]

    # Set to hold the final recommendations.
    current_recommendations = set()

    # List to store NetworkX graph snapshots for visualization purposes.
    graphs = []

    # Create an empty NetworkX graph.
    G = nx.Graph()

    # Add each initial movie as a node in the graph and label it.
    for movie in initial_movies:
        G.add_node(movie, label=movie, color='blue')

    # Save a copy of the graph state as the initial layer.
    graphs.append(G.copy())

    # Repeat the following steps for a predetermined number of layers (3 in this case).
    for i in range(3):
        # Initialize a new layer for counting recommendations.
        new_layer = defaultdict(int)

        # Create a new graph specifically for the current layer's visualization.
        layer_graph = nx.Graph()

        # Iterate over all movies in the last layer.
        for movie in layers[-1]:
            # If not the initial layer, add the movie node to the primary graph with a different color.
            if i > 0:
                G.add_node(movie, label=movie, color='red')

            # Retrieve all users who watched this movie.
            for user in manager.get_users_by_movie(movie):
                # Avoid considering the target user themselves.
                if user['user_name'] != user_name:
                    # Collect movies watched or liked by these users.
                    other_movies = set(m['movie_title'] for m in manager.get_movies_by_user(user['user_name']))
                    other_movies |= set(m['movie_title'] for m in manager.get_liked_movies_by_user(user['user_name']))

                    # Remove movies already seen or liked by the target user.
                    other_movies.difference_update(seen_movies)
                    other_movies.difference_update(liked_movies)

                    # Increment the count for each new movie that could be recommended.
                    for new_movie in other_movies:
                        new_layer[new_movie] += 1

                        # Add the new movie node to the layer graph and create an edge with the current movie.
                        layer_graph.add_node(new_movie, label=new_movie, color='green')
                        layer_graph.add_edge(movie, new_movie, weight=1)

        # If no new recommendations were found, exit the loop.
        if not new_layer:
            break

        # Sort the new movies by their counts and select only up to the beam width.
        top_movies = sorted(new_layer.items(), key=lambda x: x[1], reverse=True)[:beam_width]

        # Extract the movie titles from the sorted list.
        next_layer = set(movie for movie, _ in top_movies)

        # Add this layer to the layers list and update the recommendations set.
        layers.append(next_layer)
        current_recommendations.update(next_layer)

        # Combine the new layer graph with the primary graph.
        G = nx.compose(G, layer_graph)

        # Save a snapshot of the graph after processing each layer.
        graphs.append(G.copy())

    # Return the final list of recommendations and the collection of graphs.
    return list(current_recommendations), graphs


@time_tracker
def hill_climbing_recommendations(manager: Neo4jManager, user_name, iterations=10):
    # Retrieve all the movies that the target user has watched.
    seen_movies = set(movie['movie_title'] for movie in manager.get_movies_by_user(user_name))

    # Retrieve all the movies that the target user has explicitly liked.
    liked_movies = set(movie['movie_title'] for movie in manager.get_liked_movies_by_user(user_name))

    # Combine both sets to obtain the initial list of candidate movies.
    candidate_movies = seen_movies | liked_movies

    # Initialize a set to store the recommendations.
    current_recommendations = set()

    # List to store graph states for visualization purposes.
    graphs = []

    # Create a NetworkX graph and add all initial candidate movies as nodes.
    G = nx.Graph()
    G.add_nodes_from(candidate_movies)

    # Iterate a specified number of times to simulate the hill climbing process.
    for _ in range(iterations):
        # Initialize a defaultdict to track counts of new movie recommendations.
        new_recommendations = defaultdict(int)

        # Create a copy of the main graph for visualization at this stage.
        current_graph = G.copy()

        # Iterate through each candidate movie to find related users and their movies.
        for movie in candidate_movies:
            # Get all users who have watched this specific movie.
            related_users = manager.get_users_by_movie(movie)

            # For each related user, gather other movies they have watched or liked.
            for user in related_users:
                # Ignore the target user themselves.
                if user['user_name'] != user_name:
                    other_movies = set(m['movie_title'] for m in manager.get_movies_by_user(user['user_name']))
                    other_movies |= set(m['movie_title'] for m in manager.get_liked_movies_by_user(user['user_name']))

                    # Exclude the movies already seen or liked by the target user.
                    other_movies.difference_update(seen_movies)
                    other_movies.difference_update(liked_movies)

                    # Increment the count for each new movie that is not already in the user's list.
                    for new_movie in other_movies:
                        new_recommendations[new_movie] += 1

                        # Add an edge between the current movie and this new recommendation.
                        current_graph.add_edge(movie, new_movie, weight=1)

        # If no new recommendations were found in this iteration, exit the loop.
        if not new_recommendations:
            break

        # Find the movie with the highest recommendation count.
        best_movie, _ = max(new_recommendations.items(), key=lambda item: item[1])

        # Reset the candidate set to only include this best movie, simulating a hill climbing step.
        candidate_movies = {best_movie}

        # Add this movie to the set of recommendations.
        current_recommendations.add(best_movie)

        # Save the current state of the graph.
        graphs.append(current_graph)

    # Return the final recommendations and the graph states collected over the iterations.
    return list(current_recommendations), graphs


@time_tracker
def greedy_best_first_search_recommendations(manager: Neo4jManager, user_name, top_k=5):
    seen_movies = set(movie['movie_title'] for movie in manager.get_movies_by_user(user_name))
    liked_movies = set(movie['movie_title'] for movie in manager.get_liked_movies_by_user(user_name))
    explore_queue = deque(seen_movies | liked_movies)
    explored_movies = set()
    movie_scores = defaultdict(int)
    graphs = []  # To store the graph at each step

    G = nx.Graph()
    G.add_nodes_from(explore_queue)

    while explore_queue and len(movie_scores) < top_k:
        current_movie = explore_queue.popleft()
        explored_movies.add(current_movie)
        current_graph = G.copy()

        related_users = manager.get_users_by_movie(current_movie)
        for user in related_users:
            if user['user_name'] != user_name:
                other_movies = set(m['movie_title'] for m in manager.get_movies_by_user(user['user_name']))
                other_movies |= set(m['movie_title'] for m in manager.get_liked_movies_by_user(user['user_name']))

                for movie in other_movies:
                    if movie not in seen_movies and movie not in liked_movies and movie not in explored_movies:
                        if movie not in explore_queue:
                            explore_queue.append(movie)
                        movie_scores[movie] += 1
                        current_graph.add_node(movie, label=movie)
                        current_graph.add_edge(current_movie, movie)

        graphs.append(current_graph)

    recommended_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [movie for movie, _ in recommended_movies], graphs
