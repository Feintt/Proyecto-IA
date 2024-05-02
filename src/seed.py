from neo4j_manager import Neo4jManager
import random


def seed(manager: Neo4jManager):
    manager.clear_database()

    # Generar usuarios y películas
    users = manager.generate_users(100)
    movies = manager.create_movies(50)  # Asegúrate de que esto devuelva una lista

    # Insertar usuarios
    for user in users:
        manager.run_query("CREATE (u:User {name: $name, age: $age, location: $location})", **user)

    # Crear relaciones
    for user in users:
        seen_movies = random.sample(movies, k=random.randint(1, 10))
        for movie in seen_movies:
            manager.run_query("""
                MATCH (u:User {name: $name}), (m:Movie {title: $title})
                CREATE (u)-[:SAW]->(m)
            """, name=user['name'], title=movie['title'])
            if random.random() < 0.5:
                manager.run_query("""
                    MATCH (u:User {name: $name}), (m:Movie {title: $title})
                    CREATE (u)-[:LIKED]->(m)
                """, name=user['name'], title=movie['title'])
