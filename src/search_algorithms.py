from neo4j_manager import Neo4jManager


def recommend_movies(manager: Neo4jManager, user_name):
    # Primero, obtén las películas que el usuario ya vio y le gustaron
    liked_movies_query = """
    MATCH (u:User {name: $name})-[:LIKED]->(m:Movie)
    RETURN m.genre as genre
    """
    liked_genres = manager.run_query(liked_movies_query, name=user_name)
    liked_genres = [record["genre"] for record in liked_genres]

    # Ahora, encuentra películas que no ha visto y calcula la puntuación basada en la similitud de género
    recommendations_query = """
    MATCH (m:Movie)
    WHERE NOT EXISTS ((:User {name: $name})-[:SAW]->(m))
    RETURN m.title as title, m.genre as genre
    """
    all_unseen_movies = manager.run_query(recommendations_query, name=user_name)
    unseen_movies = [(record["title"], record["genre"]) for record in all_unseen_movies]

    # Calcula la puntuación de recomendación basada en la similitud de género
    movie_scores = []
    for title, genre in unseen_movies:
        score = liked_genres.count(genre)  # Contar cuántas veces el género aparece en los gustados
        movie_scores.append((title, genre, score))

    # Ordena las películas basadas en la puntuación de similitud descendente
    movie_scores.sort(key=lambda x: x[2], reverse=True)  # Ordenar por puntuación de similitud

    # Devuelve los títulos de las películas con las mejores puntuaciones
    return [title for title, genre, score in movie_scores[:10]]  # Top 10 recomendaciones
