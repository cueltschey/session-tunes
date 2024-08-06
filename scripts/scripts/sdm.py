import sqlite3

class SessionDataManager():
    def __init__(self, db_file, schema_file, session_db, initialize_db=True):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

        self.schema_file = schema_file
        if initialize_db:
            with open(schema_file, 'r') as f:
                schema = f.read()
                # _execute the SQL commands
                self.cursor.executescript(schema)
                self.conn.commit()
            # manually create the B.D.Riley's session as id 1.
            self.create_location(
                "B.D.Riley Thursday Session at Mueller in Austin, Texas.",
                "1905 Aldrich St #130, Austin, TX 78723",
                "https://bdrileys.com/")

        self.session_conn = sqlite3.connect(session_db)
        self.session_cursor = self.session_conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        #self.session_conn.commit() # maybe we should not do this, so that it is not possible to modify the data in TheSession-data repo.
        self.session_cursor.close()
        self.session_conn.close()

    def _execute(self, sql, params=None):
        try:
            if params:
                return self.cursor.execute(sql, params)
            else:
                return self.cursor.execute(sql)
        except sqlite3.Error as e:
            print(f"An SQL error occurred: {e}")
            raise

    # Session Table CRUD
    def create_session(self, location_id, session_date, start_time, end_time, description):
        sql = """INSERT INTO Session (location_id, session_date, start_time, end_time, description)
                 VALUES (?, ?, ?, ?, ?)"""
        self._execute(sql, (location_id, session_date, start_time, end_time, description))
        self.conn.commit()
        return self.cursor.lastrowid

    def read_session(self, session_id):
        sql = "SELECT * FROM Session WHERE session_id = ?"
        return self._execute(sql, (session_id,)).fetchone()

    def update_session(self, session_id, location_id, session_date, start_time, end_time, description):
        sql = """UPDATE Session SET location_id = ?, session_date = ?, start_time = ?,
                 end_time = ?, description = ? WHERE session_id = ?"""
        self._execute(sql, (location_id, session_date, start_time, end_time, description, session_id))
        self.conn.commit()

    def delete_session(self, session_id):
        sql = "DELETE FROM Session WHERE session_id = ?"
        self._execute(sql, (session_id,))
        self.conn.commit()

    # Location Table CRUD
    def create_location(self, description, address, url):
        sql = "INSERT INTO Location (description, address, url) VALUES (?, ?, ?)"
        self._execute(sql, (description, address, url))
        self.conn.commit()
        return self.cursor.lastrowid

    def read_location(self, location_id):
        sql = "SELECT * FROM Location WHERE location_id = ?"
        return self._execute(sql, (location_id,)).fetchone()

    def update_location(self, location_id, description, address, url):
        sql = "UPDATE Location SET description = ?, address = ?, url = ? WHERE location_id = ?"
        self._execute(sql, (description, address, url, location_id))
        self.conn.commit()

    def delete_location(self, location_id):
        sql = "DELETE FROM Location WHERE location_id = ?"
        self._execute(sql, (location_id,))
        self.conn.commit()

    # SetTable CRUD
    def create_set(self, description):
        sql = "INSERT INTO SetTable (description) VALUES (?)"
        self._execute(sql, (description,))
        self.conn.commit()
        return self.cursor.lastrowid

    def read_set(self, set_id):
        sql = "SELECT * FROM SetTable WHERE set_id = ?"
        return self._execute(sql, (set_id,)).fetchone()

    def update_set(self, set_id, description):
        sql = "UPDATE SetTable SET description = ? WHERE set_id = ?"
        self._execute(sql, (description, set_id))
        self.conn.commit()

    def delete_set(self, set_id):
        sql = "DELETE FROM SetTable WHERE set_id = ?"
        self._execute(sql, (set_id,))
        self.conn.commit()

    def read_or_create_set(self, description):
        read_sql = "SELECT set_id FROM SetTable WHERE description = ?"
        self._execute(read_sql, (description,))
        result = self.cursor.fetchone()
        if not result:
            create_sql = "INSERT INTO SetTable (description) VALUES (?)"
            self._execute(create_sql, (description,))
            set_id = self.cursor.lastrowid
        else:
            set_id = result[0]
        return set_id

    # Tune Table CRUD
    def create_tune(self, the_session_tune_id, name, abc, tune_type, tune_meter, tune_mode, tune_url):
        sql = """INSERT INTO Tune (the_session_tune_id, name, abc, tune_type, tune_meter, tune_mode, tune_url)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""
        self._execute(sql, (the_session_tune_id, name, abc, tune_type, tune_meter, tune_mode, tune_url))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_id_or_create_tune(self, the_session_tune_id, name, abc, tune_type, tune_meter, tune_mode, tune_url):
        get_id_sql = "SELECT tune_id FROM Tune WHERE the_session_tune_id = ?"
        self._execute(get_id_sql, (the_session_tune_id,))
        result = self.cursor.fetchone()
        if not result:
            return self.create_tune(the_session_tune_id, name, abc, tune_type, tune_meter, tune_mode, tune_url)
        return result[0]

    def read_tune(self, tune_id):
        sql = "SELECT * FROM Tune WHERE tune_id = ?"
        return self._execute(sql, (tune_id,)).fetchone()

    def update_tune(self, tune_id, the_session_tune_id, name, abc, tune_type, tune_meter, tune_mode, tune_url):
        sql = """UPDATE Tune SET , the_session_tune_id = ?, name = ?, abc = ?, tune_type = ?, tune_meter = ?,
                 tune_mode = ?, tune_url = ? WHERE tune_id = ?"""
        self._execute(sql, (the_session_tune_id, name, abc, tune_type, tune_meter, tune_mode, tune_url, tune_id))
        self.conn.commit()

    def delete_tune(self, tune_id):
        sql = "DELETE FROM Tune WHERE tune_id = ?"
        self._execute(sql, (tune_id,))
        self.conn.commit()

    # SetToSession Table CRUD
    def create_set_to_session(self, session_id, set_id, set_index):
        sql = "INSERT INTO SetToSession (session_id, set_id, set_index) VALUES (?, ?, ?)"
        self._execute(sql, (session_id, set_id, set_index))
        self.conn.commit()
        return self.cursor.lastrowid

    def read_set_to_session(self, session_id, set_id):
        sql = "SELECT * FROM SetToSession WHERE session_id = ? AND set_id = ?"
        return self._execute(sql, (session_id, set_id)).fetchone()

    def update_set_to_session(self, session_id, set_id, new_set_index):
        sql = "UPDATE SetToSession SET set_index = ? WHERE session_id = ? AND set_id = ?"
        self._execute(sql, (new_set_index, session_id, set_id))
        self.conn.commit()

    def delete_set_to_session(self, session_id, set_id):
        sql = "DELETE FROM SetToSession WHERE session_id = ? AND set_id = ?"
        self._execute(sql, (session_id, set_id))
        self.conn.commit()

    # TuneToSet Table CRUD
    def create_tune_to_set(self, tune_id, set_id, tune_index):
        sql = "INSERT INTO TuneToSet (tune_id, set_id, tune_index) VALUES (?, ?, ?)"
        self._execute(sql, (tune_id, set_id, tune_index))
        self.conn.commit()
        return self.cursor.lastrowid

    def read_tune_to_set(self, tune_id, set_id):
        sql = "SELECT * FROM TuneToSet WHERE tune_id = ? AND set_id = ?"
        return self._execute(sql, (tune_id, set_id)).fetchone()

    def update_tune_to_set(self, tune_id, set_id, new_tune_index):
        sql = "UPDATE TuneToSet SET tune_index = ? WHERE tune_id = ? AND set_id = ?"
        self._execute(sql, (new_tune_index, tune_id, set_id))
        self.conn.commit()

    def delete_tune_to_set(self, tune_id, set_id):
        sql = "DELETE FROM TuneToSet WHERE tune_id = ? AND set_id = ?"
        self._execute(sql, (tune_id, set_id))
        self.conn.commit()

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




