from seed import seed
from neo4j_manager import Neo4jManager


def main():
    manager = Neo4jManager()
    seed(manager)


if __name__ == "__main__":
    main()
