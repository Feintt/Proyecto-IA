from faker import Faker
import random
from py2neo import Graph

graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

fake = Faker()


def generate_users(n):
    users = []
    for _ in range(n):
        users.append({
            "name": fake.name(),
            "age": random.randint(18, 70),
            "location": fake.city()
        })
    return users


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


def clear_database():
    graph.run("MATCH (n) DETACH DELETE n")


def seed():
    clear_database()

    users = generate_users(100)
    movies = generate_movies(50)

    for user in users:
        graph.run("CREATE (u:User {name: $name, age: $age, location: $location})", **user)

    for movie in movies:
        graph.run("CREATE (m:Movie {title: $title, year: $year, genre: $genre})", **movie)

    for user in users:
        seen_movies = random.sample(movies, k=random.randint(1, 10))
        for movie in seen_movies:
            graph.run("MATCH (u:User {name: $name}), (m:Movie {title: $title}) "
                      "CREATE (u)-[:SAW]->(m)", name=user['name'], title=movie['title'])
            if random.random() < 0.5:  # 50% probabilidad de gustar
                graph.run("MATCH (u:User {name: $name}), (m:Movie {title: $title}) "
                          "CREATE (u)-[:LIKED]->(m)", name=user['name'], title=movie['title'])
