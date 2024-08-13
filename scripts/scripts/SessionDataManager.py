#!python3
r""" SessionDataManager.py - manage all database connections for session data

"""
from neo4j import GraphDatabase


class SessionDataManager:
    def __init__(self, db_file, schema_file, initialize_db=True):
        self.driver = GraphDatabase.driver(f"file:///{db_file}")
        self.schema_file = schema_file
        if initialize_db:
            self.initialize_database()

    def close(self):
        self.driver.close()

    def initialize_database(self):
        with open(self.schema_file, 'r') as f:
            schema = f.read()

        with self.driver.session() as session:
            session.run(schema)
            session.write_transaction(self._create_initial_location)

    @staticmethod
    def _create_initial_location(tx):
        query = (
            "MERGE (l:Location {location_id: 1}) "
            "SET l.description = $description, "
            "    l.address = $address, "
            "    l.url = $url"
        )
        tx.run(query,
               description="B.D.Riley Thursday Session at Mueller in Austin, Texas.",
               address="1905 Aldrich St #130, Austin, TX 78723",
               url="https://bdrileys.com/")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
