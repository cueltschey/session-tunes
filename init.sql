CREATE TABLE Session (
  session_id INTEGER PRIMARY KEY,
  location_id INTEGER,
  session_date DATE,
  start_time TIME,
  end_time TIME,
  description TEXT,
  FOREIGN KEY (location_id) REFERENCES Location(location_id)
);

CREATE TABLE Location (
  location_id INTEGER PRIMARY KEY,
  description TEXT,
  address VARCHAR(255),
  url VARCHAR(255)
);

CREATE TABLE SetTable (
  set_id INTEGER PRIMARY KEY,
  description TEXT
);

CREATE TABLE Tune (
  tune_id INTEGER PRIMARY KEY,
  name VARCHAR(255),
  abc_path VARCHAR(255),
  key VARCHAR(255),
  session_url VARCHAR(255)
);

CREATE TABLE SetToSession (
  session_id INTEGER,
  set_id INTEGER,
  set_index INTEGER,
  FOREIGN KEY (session_id) REFERENCES Session(session_id),
  FOREIGN KEY (set_id) REFERENCES SetTable(set_id)
);

CREATE TABLE TuneToSet (
  tune_id INTEGER,
  set_id INTEGER,
  tune_index INTEGER,
  FOREIGN KEY (tune_id) REFERENCES Tune(tune_id),
  FOREIGN KEY (set_id) REFERENCES SetTable(set_id)
);
