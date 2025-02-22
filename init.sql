CREATE TABLE Location (
  location_id INTEGER PRIMARY KEY,
  description TEXT,
  address VARCHAR(255),
  url VARCHAR(255)
);

CREATE TABLE Session (
  session_id INTEGER PRIMARY KEY,
  location_id INTEGER,
  session_date DATE,
  start_time TIME,
  end_time TIME,
  description TEXT,
  FOREIGN KEY (location_id) REFERENCES Location(location_id)
);

CREATE TABLE SetToSession (
  session_id INTEGER,
  set_id INTEGER,
  set_index INTEGER,
  FOREIGN KEY (session_id) REFERENCES Session(session_id),
  FOREIGN KEY (set_id) REFERENCES SetTable(set_id)
);

CREATE TABLE SetTable (
  set_id INTEGER PRIMARY KEY,
  description TEXT
);

CREATE TABLE TuneToSet (
  tune_id INTEGER,
  set_id INTEGER,
  tune_index INTEGER,
  FOREIGN KEY (tune_id) REFERENCES Tune(tune_id),
  FOREIGN KEY (set_id) REFERENCES SetTable(set_id)
);

CREATE TABLE Tune (
  tune_id INTEGER PRIMARY KEY,
  the_session_tune_id INTEGER,
  name VARCHAR(255),
  abc TEXT,
  tune_type VARCHAR(255),
  tune_meter VARCHAR(255),
  tune_mode VARCHAR(255),
  tune_url VARCHAR(255)
);
