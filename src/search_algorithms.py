from neo4j_manager import Neo4jManager
from collections import defaultdict, deque


def beam_search_recommendations(manager: Neo4jManager, user_name, beam_width=5):
    # Obtain movies the user has seen or liked
    seen_movies = set(movie['movie_title'] for movie in manager.get_movies_by_user(user_name))
    liked_movies = set(movie['movie_title'] for movie in manager.get_liked_movies_by_user(user_name))

    # Initialize the search with movies seen or liked by the user
    initial_movies = seen_movies | liked_movies
    layers = [initial_movies]
    current_recommendations = set()

    # Perform beam search to the specified depth (number of layers)
    for _ in range(3):  # Example depth of 3 layers
        new_layer = defaultdict(int)
        for movie in layers[-1]:
            # Find users who have seen or liked this movie
            for user in manager.get_users_by_movie(movie):
                if user['user_name'] != user_name:
                    # Consider movies seen or liked by these users
                    other_seen = set(m['movie_title'] for m in manager.get_movies_by_user(user['user_name']))
                    other_liked = set(m['movie_title'] for m in manager.get_liked_movies_by_user(user['user_name']))
                    new_movies = other_seen | other_liked

                    # Filter out movies already seen or liked by the original user
                    new_movies.difference_update(seen_movies)
                    new_movies.difference_update(liked_movies)

                    # Count potential new recommendations
                    for new_movie in new_movies:
                        new_layer[new_movie] += 1

        # If no new movies were found, stop the search
        if not new_layer:
            break

        # Sort new movies based on counts and keep the top 'beam_width' movies
        top_movies = sorted(new_layer.items(), key=lambda x: x[1], reverse=True)[:beam_width]
        layers.append(set(movie for movie, count in top_movies))
        current_recommendations.update(layers[-1])

    return list(current_recommendations)


def hill_climbing_recommendations(manager: Neo4jManager, user_name, iterations=10):
    # Obtain initial movies the user has seen or liked
    seen_movies = set(movie['movie_title'] for movie in manager.get_movies_by_user(user_name))
    liked_movies = set(movie['movie_title'] for movie in manager.get_liked_movies_by_user(user_name))
    candidate_movies = seen_movies | liked_movies

    # Initialize current recommendations
    current_recommendations = set()

    # Start hill climbing to find better recommendations iteratively
    for _ in range(iterations):
        new_recommendations = defaultdict(int)

        # Explore each candidate movie to find related users and their liked or seen movies
        for movie in candidate_movies:
            related_users = manager.get_users_by_movie(movie)
            for user in related_users:
                if user['user_name'] != user_name:
                    other_seen = set(m['movie_title'] for m in manager.get_movies_by_user(user['user_name']))
                    other_liked = set(m['movie_title'] for m in manager.get_liked_movies_by_user(user['user_name']))
                    new_movies = other_seen | other_liked

                    # Update scores for new movies
                    for new_movie in new_movies:
                        if new_movie not in seen_movies and new_movie not in liked_movies:
                            new_recommendations[new_movie] += 1

        # Select the best movie from new recommendations if better than the current
        if not new_recommendations:
            break  # No better moves, stop the iteration

        # Find the movie with the highest count of new recommendations
        best_movie, _ = max(new_recommendations.items(), key=lambda item: item[1])
        candidate_movies = {best_movie}
        current_recommendations.add(best_movie)

    return list(current_recommendations)


def greedy_best_first_search_recommendations(manager: Neo4jManager, user_name, top_k=5):
    # Start with movies the user has seen or liked
    seen_movies = set(movie['movie_title'] for movie in manager.get_movies_by_user(user_name))
    liked_movies = set(movie['movie_title'] for movie in manager.get_liked_movies_by_user(user_name))

    # Merge sets for initial exploration
    explore_queue = deque(seen_movies | liked_movies)
    explored_movies = set()  # To avoid re-exploring the same movies

    # Dictionary to store movie scores based on user endorsements
    movie_scores = defaultdict(int)

    while explore_queue and len(movie_scores) < top_k:
        current_movie = explore_queue.popleft()
        explored_movies.add(current_movie)

        # Find users who have liked or seen the current movie
        related_users = manager.get_users_by_movie(current_movie)
        for user in related_users:
            if user['user_name'] != user_name:
                other_movies = set(m['movie_title'] for m in manager.get_movies_by_user(user['user_name']))
                other_movies |= set(m['movie_title'] for m in manager.get_liked_movies_by_user(user['user_name']))

                # Add unexplored movies to the queue and increment their score
                for movie in other_movies:
                    if movie not in seen_movies and movie not in liked_movies and movie not in explored_movies:
                        if movie not in explore_queue:
                            explore_queue.append(movie)
                        movie_scores[movie] += 1

    # Sort movies by scores and select the top k
    recommended_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [movie for movie, _ in recommended_movies]
