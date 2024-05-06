from neo4j_manager import Neo4jManager


def greedy_recommendations(manager: Neo4jManager, user_name):
    # Obtener películas que el usuario ha visto y gustado
    seen_movies = set(movie['movie_title'] for movie in manager.get_movies_by_user(user_name))
    liked_movies = set(movie['movie_title'] for movie in manager.get_liked_movies_by_user(user_name))

    # Encontrar usuarios que han visto o gustado las mismas películas
    related_users = set()
    for movie in seen_movies | liked_movies:
        for user in manager.get_users_by_movie(movie):
            if user['user_name'] != user_name:
                related_users.add(user['user_name'])

    # Recopilar películas vistas o gustadas por los usuarios relacionados
    potential_movies = {}
    for rel_user in related_users:
        user_seen = set(movie['movie_title'] for movie in manager.get_movies_by_user(rel_user))
        user_liked = set(movie['movie_title'] for movie in manager.get_liked_movies_by_user(rel_user))

        for movie in user_seen | user_liked:
            if movie not in seen_movies and movie not in liked_movies:
                if movie not in potential_movies:
                    potential_movies[movie] = 0
                potential_movies[movie] += 1

    # Ordenar las películas por el número de usuarios relacionados que las han visto o gustado
    recommended_movies = sorted(potential_movies.items(), key=lambda x: x[1], reverse=True)

    # Devolver solo los títulos de las películas como recomendaciones
    return [movie for movie, count in recommended_movies]
