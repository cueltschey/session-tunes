#!python3
r""" SessionDataManager.py - manage all database connections for session data

"""
import neo4j
import sqlite3


class SessionDataManager:
    def __init__(self, session_db, initialize_db=True):
        URI = "neo4j+s://a36f2166.databases.neo4j.io"
        AUTH = ("neo4j", "1Mik7YKwO1IdAxbZMrhMGG_bpidd1gGSBusyi2a23go")
        self.driver = neo4j.GraphDatabase.driver(URI, auth=AUTH)
        self.driver.verify_connectivity()
        if initialize_db:
            self.initialize_database()

        self.session_conn = sqlite3.connect(session_db)
        self.session_cursor = self.session_conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.driver.close()
        self.session_cursor.close()
        self.session_conn.close()

    def initialize_database(self):
        initialization_commands = [
            # Create constraints
            "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE l.location_id IS UNIQUE;",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE;",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (st:SetTable) REQUIRE st.set_id IS UNIQUE;",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Tune) REQUIRE t.tune_id IS UNIQUE;",
            # Create indexes
            "CREATE RANGE INDEX IF NOT EXISTS FOR (s:Session) ON (s.session_date);",
            "CREATE RANGE INDEX IF NOT EXISTS FOR (t:Tune) ON (t.the_session_tune_id);",
            # Define node properties (similar to table columns)
            "CREATE (:Location {location_id: 0, description: '', address: '', url: ''});",
            "CREATE (:Session {session_id: 0, session_date: date(), start_time: time(), end_time: time(), description: ''});",
            "CREATE (:SetTable {set_id: 0, description: ''});",
            "CREATE (:Tune {tune_id: 0, the_session_tune_id: 0, name: '', abc: '', tune_type: '', tune_meter: '', tune_mode: '', tune_url: ''});",
        ]
        with self.driver.session() as session:
            for command in initialization_commands:
                session.run(command)
            session.write_transaction(self._create_initial_location)

    @staticmethod
    def _create_initial_location(tx):
        query = (
            "MERGE (l:Location {location_id: 1}) "
            "SET l.description = $description, "
            "    l.address = $address, "
            "    l.url = $url"
        )
        tx.run(
            query,
            description="B.D.Riley Thursday Session at Mueller in Austin, Texas.",
            address="1905 Aldrich St #130, Austin, TX 78723",
            url="https://bdrileys.com/")

    def create_session(self, location_id, session_date, start_time, end_time, description):
        query = (
            "CREATE (s:Session {session_id: randomUUID(), "
            "location_id: $location_id, "
            "session_date: date($session_date), "
            "start_time: time($start_time), "
            "end_time: time($end_time), "
            "description: $description}) "
            "RETURN s.session_id as session_id"
        )
        with self.driver.session() as session:
            result = session.run(
                query,
                location_id=location_id,
                session_date=session_date,
                start_time=start_time,
                end_time=end_time,
                description=description)
            return result.single()["session_id"]

    def create_location(self, description, address, url):
        query = (
            "CREATE (l:Location {location_id: randomUUID(), "
            "description: $description, "
            "address: $address, "
            "url: $url}) "
            "RETURN l.location_id as location_id"
        )
        with self.driver.session() as session:
            result = session.run(
                query,
                description=description,
                address=address,
                url=url)
            return result.single()["location_id"]

    def read_or_create_set(self, description):
        query = (
            "MERGE (s:SetTable {description: $description}) "
            "ON CREATE SET s.set_id = randomUUID() "
            "RETURN s.set_id as set_id"
        )
        with self.driver.session() as session:
            result = session.run(
                query,
                description=description)
            return result.single()["set_id"]

    def create_tune(self, the_session_tune_id, name, abc, tune_type, tune_meter, tune_mode, tune_url):
        query = (
            "CREATE (t:Tune {tune_id: randomUUID(), "
            "the_session_tune_id: $the_session_tune_id, "
            "name: $name, "
            "abc: $abc, "
            "tune_type: $tune_type, "
            "tune_meter: $tune_meter, "
            "tune_mode: $tune_mode, "
            "tune_url: $tune_url}) "
            "RETURN t.tune_id as tune_id"
        )
        with self.driver.session() as session:
            result = session.run(
                query,
                the_session_tune_id=the_session_tune_id,
                name=name,
                abc=abc,
                tune_type=tune_type,
                tune_meter=tune_meter,
                tune_mode=tune_mode,
                tune_url=tune_url)
            return result.single()["tune_id"]

    def get_id_or_create_tune(self, the_session_tune_id, name, abc, tune_type, tune_meter, tune_mode, tune_url):
        query = (
            "MERGE (t:Tune {the_session_tune_id: $the_session_tune_id}) "
            "ON CREATE SET t.tune_id = randomUUID(), "
            "t.name = $name, "
            "t.abc = $abc, "
            "t.tune_type = $tune_type, "
            "t.tune_meter = $tune_meter, "
            "t.tune_mode = $tune_mode, "
            "t.tune_url = $tune_url "
            "RETURN t.tune_id as tune_id"
        )
        with self.driver.session() as session:
            result = session.run(
                query,
                the_session_tune_id=the_session_tune_id,
                name=name,
                abc=abc,
                tune_type=tune_type,
                tune_meter=tune_meter,
                tune_mode=tune_mode,
                tune_url=tune_url)
            return result.single()["tune_id"]


    def create_set_to_session(self, session_id, set_id, set_index):
        query = (
            "MATCH (s:Session {session_id: $session_id}), (st:SetTable {set_id: $set_id}) "
            "MERGE (s)-[r:INCLUDES {set_index: $set_index}]->(st) "
            "RETURN r.set_index as relationship_id"
        )
        with self.driver.session() as session:
            result = session.run(
                query,
                session_id=session_id,
                set_id=set_id,
                set_index=set_index)
            try:
                return result.single()["relationship_id"]
            except ResultConsumedError:
                # If the relationship already existed, return the set_index
                return set_index

    def create_tune_to_set(self, tune_id, set_id, tune_index):
        query = (
            "MATCH (t:Tune {tune_id: $tune_id}), (st:SetTable {set_id: $set_id}) "
            "MERGE (st)-[r:CONTAINS {tune_index: $tune_index}]->(t) "
            "RETURN r.tune_index as relationship_id"
        )
        with self.driver.session() as session:
            result = session.run(
                query,
                tune_id=tune_id,
                set_id=set_id,
                tune_index=tune_index)
            try:
                return result.single()["relationship_id"]
            except ResultConsumedError:
                # If the relationship already existed, return the tune_index
                return tune_index

    def get_tune_from_TheSession(self, tune_id):
        abc = ""
        tune_type = ""
        tune_meter = ""
        tune_mode = ""

        self.session_cursor.execute('SELECT abc, type, meter, mode FROM tunes WHERE tune_id = ?', (tune_id,))
        abc_result = self.session_cursor.fetchone()
        if abc_result:
            abc, tune_type, tune_meter, tune_mode = abc_result
        return abc, tune_type, tune_meter, tune_mode
