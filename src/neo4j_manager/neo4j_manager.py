from faker import Faker
import random
from py2neo import Graph
import os


class Neo4jManager:
    def __init__(self):
        # Get credentials and host information for connecting to the Neo4j database.
        _username = os.getenv("NEO4J_USER")
        _password = os.getenv("NEO4J_PASS")
        _host = os.getenv("NEO4J_HOST")
        # Establish a connection to the Neo4j database using credentials and host.
        self.graph = Graph(f"bolt://{_host}:7687", auth=(_username, _password))
        # Initialize the Faker library to generate random user data.
        self.fake = Faker()

    def generate_users(self, n):
        # Generate `n` users with random names, ages, and locations.
        users = []
        for _ in range(n):
            users.append({
                "name": self.fake.name(),
                "age": random.randint(18, 70),
                "location": self.fake.city()
            })
        return users  # Return a list of generated user dictionaries.

    def clear_database(self):
        # Delete all nodes and relationships in the database.
        self.graph.run("MATCH (n) DETACH DELETE n")

    def create_movies(self, n):
        # Generate `n` random movie nodes with specific genres.
        genres = ["Action", "Comedy", "Drama", "Science Fiction", "Documentary"]
        movies = []
        for _ in range(n):
            # Generate a movie dictionary with random attributes.
            movie = {
                "name": self.fake.sentence(nb_words=3),
                "title": self.fake.sentence(nb_words=3),
                "year": random.randint(1980, 2024),
                "genre": random.choice(genres)
            }
            # Create a movie node in the Neo4j database using the dictionary data.
            self.create_movie_node(movie)
            movies.append(movie)  # Add the movie to the list of created movies.
        return movies  # Return the list of created movies.

    def create_movie_node(self, movie):
        # Cypher query for creating a single movie node with specified properties.
        query = """
        CREATE (m:Movie {name: $name, title: $title, year: $year, genre: $genre})
        RETURN m
        """
        # Execute the query and return the created node's data.
        return self.graph.run(query, movie).data()

    def run_query(self, query, **kwargs):
        # Execute a Cypher query with or without additional keyword arguments.
        if kwargs:
            return self.graph.run(query, kwargs)
        else:
            return self.graph.run(query)

    def get_random_user_name(self):
        # Cypher query to fetch a random user's name from the database.
        query = """
        MATCH (u:User)
        RETURN u.name AS name
        ORDER BY rand()
        LIMIT 1
        """
        # Execute the query and return the name if a user node exists.
        result = self.graph.run(query).data()
        if result:
            return result[0]['name']
        else:
            return None  # Return None if no users are available.

    def get_all_users(self):
        # Cypher query to fetch all user names, ordered alphabetically.
        query = """
        MATCH (u:User)
        RETURN u.name AS user_name
        ORDER BY u.name
        """
        return self.graph.run(query).data()

    def get_movies_by_user(self, user_name):
        # Fetch movie titles watched by a specified user.
        query = """
        MATCH (u:User {name: $user_name})-[:SAW]->(m:Movie)
        RETURN m.title AS movie_title
        """
        return self.graph.run(query, user_name=user_name).data()

    def get_liked_movies_by_user(self, user_name):
        # Fetch movie titles liked by a specified user.
        query = """
        MATCH (u:User {name: $user_name})-[:LIKED]->(m:Movie)
        RETURN m.title AS movie_title
        """
        return self.graph.run(query, user_name=user_name).data()

    def get_users_by_movie(self, movie_title):
        # Fetch user names who have watched or liked a specific movie.
        query = """
        MATCH (u:User)-[:SAW]->(m:Movie {title: $movie_title})
        OPTIONAL MATCH (u)-[:LIKED]->(m:Movie {title: $movie_title})
        RETURN u.name AS user_name
        """
        return self.graph.run(query, movie_title=movie_title).data()

    def get_users_by_movies(self, movie_titles):
        # Fetch users and corresponding movie titles for a list of movies.
        query = """
        MATCH (u:User)-[:SAW]->(m:Movie)
        WHERE m.title IN $movie_titles
        OPTIONAL MATCH (u)-[:LIKED]->(m)
        RETURN u.name AS user_name, m.title AS movie_title
        """
        return self.graph.run(query, movie_titles=movie_titles).data()
