from faker import Faker
import random
from py2neo import Graph

graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

fake = Faker()


# Generar datos para usuarios
def generate_users(n):
    users = []
    for _ in range(n):
        users.append({
            "name": fake.name(),
            "age": random.randint(18, 70),
            "location": fake.city()
        })
    return users


# Generar datos para películas
def generate_movies(n):
    genres = ["Action", "Comedy", "Drama", "Science Fiction", "Documentary"]
    movies = []
    for _ in range(n):
        movies.append({
            "title": fake.sentence(nb_words=3),
            "year": random.randint(1980, 2021),
            "genre": random.choice(genres)
        })
    return movies


def main():
    # Ejemplo de generación de datos
    users = generate_users(100)  # Generar 100 usuarios
    movies = generate_movies(50)  # Generar 50 películas

    # Imprime algunos ejemplos
    print(users[:5])  # Imprime los primeros 5 usuarios
    print(movies[:5])  # Imprime las primeras 5 películas

    # Insertar usuarios
    for user in users:
        graph.run("CREATE (u:User {name: $name, age: $age, location: $location})", **user)

    # Insertar películas
    for movie in movies:
        graph.run("CREATE (m:Movie {title: $title, year: $year, genre: $genre})", **movie)

    # Generar relaciones ficticias
    for user in users:
        seen_movies = random.sample(movies, k=random.randint(1, 10))  # Cada usuario ha visto 1-10 películas
        for movie in seen_movies:
            graph.run("MATCH (u:User {name: $name}), (m:Movie {title: $title}) "
                      "CREATE (u)-[:SAW]->(m)", name=user['name'], title=movie['title'])
            if random.random() < 0.5:  # 50% de probabilidad de que le haya gustado la película
                graph.run("MATCH (u:User {name: $name}), (m:Movie {title: $title}) "
                          "CREATE (u)-[:LIKED]->(m)", name=user['name'], title=movie['title'])


if "__main__" == __name__:
    main()
