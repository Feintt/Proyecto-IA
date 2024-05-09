from neo4j_manager import Neo4jManager
from collections import defaultdict, deque
import networkx as nx


def beam_search_recommendations(manager, user_name, beam_width=5):
    seen_movies = set(movie['movie_title'] for movie in manager.get_movies_by_user(user_name))
    liked_movies = set(movie['movie_title'] for movie in manager.get_liked_movies_by_user(user_name))
    initial_movies = seen_movies | liked_movies
    layers = [initial_movies]
    current_recommendations = set()
    graphs = []  # Store NetworkX graphs for each layer

    G = nx.Graph()  # Initialize NetworkX Graph
    for movie in initial_movies:
        G.add_node(movie, label=movie, color='blue')

    for i in range(3):  # Example depth of 3 layers
        new_layer = defaultdict(int)
        layer_graph = nx.Graph()  # Graph for current layer

        for movie in layers[-1]:
            # Node style for current layer
            if i > 0: G.add_node(movie, label=movie, color='red')

            for user in manager.get_users_by_movie(movie):
                if user['user_name'] != user_name:
                    other_movies = set(m['movie_title'] for m in manager.get_movies_by_user(user['user_name']))
                    other_movies |= set(m['movie_title'] for m in manager.get_liked_movies_by_user(user['user_name']))
                    other_movies.difference_update(seen_movies)
                    other_movies.difference_update(liked_movies)

                    for new_movie in other_movies:
                        new_layer[new_movie] += 1
                        layer_graph.add_node(new_movie, label=new_movie, color='green')
                        layer_graph.add_edge(movie, new_movie, weight=1)

        if not new_layer:
            break

        top_movies = sorted(new_layer.items(), key=lambda x: x[1], reverse=True)[:beam_width]
        next_layer = set(movie for movie, _ in top_movies)
        layers.append(next_layer)
        current_recommendations.update(next_layer)

        # Combine layer graph with main graph
        G = nx.compose(G, layer_graph)
        graphs.append(G.copy())  # Store snapshot

    return list(current_recommendations), graphs


def hill_climbing_recommendations(manager: Neo4jManager, user_name, iterations=10):
    seen_movies = set(movie['movie_title'] for movie in manager.get_movies_by_user(user_name))
    liked_movies = set(movie['movie_title'] for movie in manager.get_liked_movies_by_user(user_name))
    candidate_movies = seen_movies | liked_movies
    current_recommendations = set()
    graphs = []  # To store the graph at each step

    G = nx.Graph()
    G.add_nodes_from(candidate_movies)

    for _ in range(iterations):
        new_recommendations = defaultdict(int)
        current_graph = G.copy()

        for movie in candidate_movies:
            related_users = manager.get_users_by_movie(movie)
            for user in related_users:
                if user['user_name'] != user_name:
                    other_movies = set(m['movie_title'] for m in manager.get_movies_by_user(user['user_name']))
                    other_movies |= set(m['movie_title'] for m in manager.get_liked_movies_by_user(user['user_name']))
                    other_movies.difference_update(seen_movies)
                    other_movies.difference_update(liked_movies)

                    for new_movie in other_movies:
                        new_recommendations[new_movie] += 1
                        current_graph.add_edge(movie, new_movie, weight=1)

        if not new_recommendations:
            break

        best_movie, _ = max(new_recommendations.items(), key=lambda item: item[1])
        candidate_movies = {best_movie}
        current_recommendations.add(best_movie)
        graphs.append(current_graph)

    return list(current_recommendations), graphs


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

