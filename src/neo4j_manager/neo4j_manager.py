from faker import Faker
import random
from py2neo import Graph
import os


class Neo4jManager:
    def __init__(self):
        _username = os.getenv("NEO4J_USER")
        _password = os.getenv("NEO4J_PASS")
        _host = os.getenv("NEO4J_HOST")
        self.graph = Graph(f"bolt://{_host}:7687", auth=(_username, _password))
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
        ORDER BY u.name
        """
        return self.graph.run(query).data()

    def get_movies_by_user(self, user_name):
        query = """
        MATCH (u:User {name: $user_name})-[:SAW]->(m:Movie)
        RETURN m.title AS movie_title
        """
        return self.graph.run(query, user_name=user_name).data()

    def get_liked_movies_by_user(self, user_name):
        query = """
        MATCH (u:User {name: $user_name})-[:LIKED]->(m:Movie)
        RETURN m.title AS movie_title
        """
        return self.graph.run(query, user_name=user_name).data()

    def get_users_by_movie(self, movie_title):
        query = """
        MATCH (u:User)-[:SAW]->(m:Movie {title: $movie_title})
        OPTIONAL MATCH (u)-[:LIKED]->(m:Movie {title: $movie_title})
        RETURN u.name AS user_name
        """
        return self.graph.run(query, movie_title=movie_title).data()

    def get_users_by_movies(self, movie_titles):
        query = """
        MATCH (u:User)-[:SAW]->(m:Movie)
        WHERE m.title IN $movie_titles
        OPTIONAL MATCH (u)-[:LIKED]->(m)
        RETURN u.name AS user_name, m.title AS movie_title
        """
        return self.graph.run(query, movie_titles=movie_titles).data()
