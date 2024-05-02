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

    def clear_database(self):
        self.graph.run("MATCH (n) DETACH DELETE n")

    def create_movies(self, n):
        genres = ["Action", "Comedy", "Drama", "Science Fiction", "Documentary"]
        movies = []
        for _ in range(n):
            movie = {
                "name": self.fake.sentence(nb_words=3),  # Usar esto como el nombre de la película
                "title": self.fake.sentence(nb_words=3),  # Y también como título
                "year": random.randint(1980, 2024),
                "genre": random.choice(genres)
            }
            self.create_movie_node(movie)
            movies.append(movie)  # Añadir el diccionario de la película a la lista
        return movies  # Devolver la lista de películas

    def create_movie_node(self, movie):
        query = """
        CREATE (m:Movie {name: $name, title: $title, year: $year, genre: $genre})
        RETURN m
        """
        return self.graph.run(query, movie).data()

    def run_query(self, query, **kwargs):
        if kwargs:
            return self.graph.run(query, kwargs)
        else:
            return self.graph.run(query)

    def get_random_user_name(self):
        # Esta consulta Cypher selecciona un nodo de usuario al azar y devuelve su nombre
        query = """
        MATCH (u:User)
        RETURN u.name AS name
        ORDER BY rand()
        LIMIT 1
        """
        result = self.graph.run(query).data()
        if result:
            return result[0]['name']
        else:
            return None  # Retorna None si no hay usuarios disponibles

    def get_all_users(self):
        query = """
        MATCH (u:User)
    RETURN u.name AS user_name
        """
        return self.graph.run(query).data()
