from faker import Faker
import random
from py2neo import Graph


class Neo4jManager:
    def __init__(self):
        self.graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))
        self.fake = Faker()

    def generate_users(self, n):
        users = []
        for _ in range(n):
            users.append({
                "name": self.fake.name(),
                "age": random.randint(18, 70),
                "location": self.fake.city()
            })
        return users

    def generate_movies(self, n):
        genres = ["Action", "Comedy", "Drama", "Science Fiction", "Documentary"]
        movies = []
        for _ in range(n):
            movies.append({
                "title": self.fake.sentence(nb_words=3),
                "year": random.randint(1980, 2024),
                "genre": random.choice(genres)
            })
        return movies

    def clear_database(self):
        self.graph.run("MATCH (n) DETACH DELETE n")

    def run_query(self, query, **kwargs):
        if kwargs:
            return self.graph.run(query, kwargs)
        else:
            return self.graph.run(query)
