const path = require('path');
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const app = express();
const PORT = process.env.PORT || 3000;
const neo4j = require('neo4j-driver');

app.use(express.static(path.join(__dirname, "dist")))

// Set up SQLite database connection
const db = new sqlite3.Database('mueller.db', (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        console.log('Connected to the SQLite database.');
    }
});

// Neo4j database connection
const neo4jUri = 'neo4j+s://a36f2166.databases.neo4j.io';
const neo4jUser = 'neo4j';
const neo4jPassword = '1Mik7YKwO1IdAxbZMrhMGG_bpidd1gGSBusyi2a23go';
const driver = neo4j.driver(neo4jUri, neo4j.auth.basic(neo4jUser, neo4jPassword));

// Test Neo4j connection
const session = driver.session();
session.run('RETURN 1 AS result')
    .then(() => {
        console.log('Connected to the Neo4j database.');
        session.close();
    })
    .catch(error => {
        console.error('Error connecting to Neo4j:', error);
        session.close();
    });


// bugbug: update to use session
// GET the top 50 tunes
app.get('/top-tunes', (req, res) => {
    const query = `
        SELECT t.tune_id, t.name, t.tune_url, COUNT(tts.tune_id) AS tune_count
        FROM Tune t
        JOIN TuneToSet tts ON t.tune_id = tts.tune_id
        GROUP BY t.tune_id, t.name
        ORDER BY tune_count DESC
        LIMIT 50;
    `;

    db.all(query, [], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});

// bugbug: update to use session
// GET all sessions
app.get('/sessions', (req, res) => {
    const query = `SELECT * FROM Session`;
    db.all(query, [], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});

// bugbug: update to use session
// GET all sets for a given session
app.get('/session', (req, res) => {
    const session_id = req.query.session_id
    if(!session_id){
      res.status(401).send("session_id required")
      return
    }
    const query = `
          SELECT s.*
          FROM SetTable s
          JOIN SetToSession st ON s.set_id = st.set_id
          WHERE st.session_id = ? AND s.set_id != 1;
          ORDER BY st.set_index ASC
      `;
    db.all(query, [session_id], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});

// bugbug: update to use session
// GET all sets
app.get('/sets', (req, res) => {
    const set_id = req.query.set_id
    if(!set_id){
      res.status(401).send("set_id required")
      return
    }
    const query = `SELECT * FROM SetTable WHERE set_id = ?`;
    db.all(query, [set_id], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});

// bugbug: update to use session
// GET all sets in a range of dates
app.get('/sets-in-range', (req, res) => {
    const start_date = req.query.start
    const end_date = req.query.end
    const key_str = req.query.key
    if(!start_date || !end_date){
      res.status(401).send("range required")
      return
    }
    const query = `
          SELECT s.*
          FROM SetTable s
          JOIN SetToSession st ON s.set_id = st.set_id
          JOIN Session ses ON st.session_id = ses.session_id
          WHERE ses.session_date BETWEEN ? AND ?
          ORDER BY st.set_index ASC;
    `;
    if(key_str && key_str != 'all'){
    const query = `
            SELECT s.*
            FROM SetTable s
            JOIN SetToSession st ON s.set_id = st.set_id
            JOIN Session ses ON st.session_id = ses.session_id
            JOIN TuneToSet tts ON tts.set_id = s.set_id
            JOIN Tune t ON t.tune_id = tts.tune_id
            WHERE ses.session_date BETWEEN ? AND ? AND t.tune_mode = ?
            ORDER BY st.set_index ASC;
      `;
      db.all(query, [start_date, end_date, key_str], (err, rows) => {
            if (err) {
                return res.status(500).json({ error: err.message });
            }
            res.json(rows);
        });
      return
    }

    db.all(query, [start_date, end_date], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});

// bugbug: update to use session
// GET all tunes in a given set
app.get('/set', (req, res) => {
    const set_id = req.query.set_id
    if(!set_id){
      res.status(401).send("set_id required")
      return
    }
    const query = `
          SELECT t.name, t.tune_id, t.name, t.tune_url, t.abc, COUNT(ts.tune_id) as tune_count
          FROM Tune t
          JOIN TuneToSet ts ON t.tune_id = ts.tune_id
          WHERE ts.set_id = ?
          GROUP BY t.name, t.tune_id, t.tune_url
          ORDER BY ts.tune_index ASC;    
    `;
    db.all(query, [set_id], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});

// bugbug: update to use session
// GET all sets of a given tune
app.get('/tune', (req, res) => {
    const tune_id = req.query.tune_id
    if(!tune_id){
      res.status(401).send("tune_id required")
      return
    }
    const query = `
          SELECT DISTINCT s.*
          FROM SetTable s
          JOIN TuneToSet ts ON s.set_id = ts.set_id
          WHERE ts.tune_id = ?
          ORDER BY ts.tune_index ASC;    
    `;
    db.all(query, [tune_id], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});


// bugbug: update to use session
// GET all sets in a range of dates
app.get('/tunes-in-range', (req, res) => {
    const start_date = req.query.start
    const end_date = req.query.end
    const key_str = req.query.key
    if(!start_date || !end_date){
      res.status(401).send("range required")
      return
    }
    const query = `
          SELECT t.name, t.tune_id, t.name, t.tune_url, COUNT(tts.tune_id) as tune_count
          FROM Tune t
          JOIN TuneToSet tts ON t.tune_id = tts.tune_id
          JOIN SetTable s ON s.set_id = tts.set_id
          JOIN SetToSession st ON s.set_id = st.set_id
          JOIN Session ses ON st.session_id = ses.session_id
          WHERE ses.session_date BETWEEN ? AND ?
          GROUP BY t.name, t.tune_id, t.tune_url
          ORDER BY tune_count DESC;
    `;

    if(key_str && key_str != 'all'){
    const query = `
          SELECT DISTINCT t.name, t.tune_id, t.name, t.tune_url
          FROM Tune t
          JOIN TuneToSet tts ON t.tune_id = tts.tune_id
          JOIN SetTable s ON s.set_id = tts.set_id
          JOIN SetToSession st ON s.set_id = st.set_id
          JOIN Session ses ON st.session_id = ses.session_id
          WHERE ses.session_date BETWEEN ? AND ? AND t.tune_mode = ?
          ORDER BY st.set_index ASC;
    `;
    db.all(query, [start_date, end_date, key_str], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
    return

    }

    db.all(query, [start_date, end_date], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});

// bugbug: update to use session
// GET all sessions in a range of dates
app.get('/sessions-in-range', (req, res) => {
    const start_date = req.query.start
    const end_date = req.query.end
    if(!start_date || !end_date){
      res.status(401).send("range required")
      return
    }
    const query = `
          SELECT *
          FROM Session s
          WHERE s.session_date BETWEEN ? AND ?
          ORDER BY s.session_date DESC;
    `;
    db.all(query, [start_date, end_date], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});


// bugbug: update to use session
app.get('/abc', (req, res) => {
    const tune_id = req.query.tune_id
    if(!tune_id){
      res.status(401).send("tune_id required")
      return
    }
    const query = `
          SELECT * From Tune
          WHERE tune_id = ?
    `;
    db.all(query, [tune_id], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});

app.get('/tune-info', (req, res) => {
    const tuneName = req.query.tuneName
    if(!tuneName){
      res.status(401).send("tuneName required")
      return
    }
    const query = `
          SELECT * From Tune
          WHERE name = ?
    `;
    db.all(query, [tuneName], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});

app.get('/set-info', (req, res) => {
    const setName = req.query.setName
    if(!setName){
      res.status(401).send("tuneName required")
      return
    }
    const query = `
          SELECT * From SetTable
          WHERE description = ?
    `;
    db.all(query, [setName], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});




app.get('/graph/tune', async (req, res) => {
  try {
    const tuneName = req.query.tuneName;
    const result = await driver.executeQuery(
      `
      MATCH (s:SetTable)-[:CONTAINS]->(t:Tune {name: $tuneName})
      WITH t, COLLECT(s) AS sets
      WITH t, sets[0..30] AS limitedSets
      MATCH (s)-[:CONTAINS]->(otherTune:Tune)
      WHERE s IN limitedSets
      RETURN t, limitedSets, COLLECT(otherTune) AS otherTunes
      `,
      { tuneName },
      { database: 'neo4j' }  // Specify the database if needed
    );

    const nodes = [];
    const edges = [];

    result.records.forEach(record => {
      const tuneNode = record.get('t').properties;
      nodes.push({
        id: tuneNode.tune_id,
        label: tuneNode.name,
        color: {background: 'yellow', border: "black"}
      });

      const sets = record.get('limitedSets');
      sets.forEach(set => {
        const setNode = set.properties;
        if (!nodes.find(n => n.id === setNode.set_id)) {
          nodes.push({
            id: setNode.set_id,
            label: setNode.description,
            color: {background: '#aaddaa', border: "black"}
          });
        }
      });

      const otherTunes = record.get('otherTunes').filter(tune => tune.properties.tune_id != tuneNode.tune_id);
      otherTunes.forEach(otherTune => {
        const otherTuneNode = otherTune.properties;
        if (!nodes.find(n => n.id === otherTuneNode.tune_id)) {
          nodes.push({
            id: otherTuneNode.tune_id,
            label: otherTuneNode.name,
            color: { background: '#aaaadd', border: "black" }
          });
        }
        nodes.filter(n => n.label.includes(otherTuneNode.name) && n.label != otherTuneNode.name).forEach(set => {
          if(!edges.find(e => e.to === set.id && e.from === otherTuneNode.tune_id)){
            edges.push({ from: otherTuneNode.tune_id, to: set.id });
          }
        });
      });

      sets.forEach(set => {
        const setNode = set.properties;
        edges.push({ from: tuneNode.tune_id, to: setNode.set_id});
      });
    });

    res.json({ nodes, edges });
  } catch (error) {
    console.error('Error fetching data:', error);
    res.status(500).send('Error fetching data');
  }
});


app.get('/graph/set', async (req, res) => {
  try {
    const setDescription = req.query.setName;
    const result = await driver.executeQuery(
      `
      MATCH (s:SetTable {description: $setDescription})-[:CONTAINS]->(t:Tune)
      WITH s, COLLECT(t) AS tunes
      WITH s, tunes[0..30] AS limitedTunes
      MATCH (otherSet:SetTable)-[:CONTAINS]->(t)
      WHERE t IN limitedTunes
      RETURN s, limitedTunes, COLLECT(otherSet) AS otherSets
      `,
      { setDescription },
      { database: 'neo4j' }  // Specify the database if needed
    );

    const nodes = [];
    const edges = [];

    result.records.forEach(record => {
      const setNode = record.get('s').properties;
      nodes.push({
        id: setNode.set_id,
        label: setNode.description,
        color: {background: 'yellow', border: "black"}
      });

      const tunes = record.get('limitedTunes');
      tunes.forEach(tune => {
        const tuneNode = tune.properties;
        if (!nodes.find(n => n.id === tuneNode.tune_id)) {
          nodes.push({
            id: tuneNode.tune_id,
            label: tuneNode.name,
            color: {background: '#aaddaa', border: "black"}
          });
        }
      });

      const otherTunes = record.get('otherSets').filter(set => set.properties.set_id != setNode.set_id);
      otherTunes.forEach(otherSet => {
        const otherSetNode = otherSet.properties;
        if (otherSetNode.description.includes(",") && !nodes.find(n => n.id === otherSetNode.set_id)) {
          nodes.push({
            id: otherSetNode.set_id,
            label: otherSetNode.description,
            color: { background: '#aaaadd', border: "black" }
          });
        }
        nodes.filter(n => otherSetNode.description.includes(n.label) && n.label != otherSetNode.description).forEach(set => {
          if(!edges.find(e => e.to === set.id && e.from === otherSetNode.set_id)){
            edges.push({ from: otherSetNode.set_id, to: set.id });
          }
        });
      });

      tunes.forEach(tune => {
        const tuneNode = tune.properties;
        edges.push({ from: tuneNode.tune_id, to: setNode.set_id});
      });
    });

    res.json({ nodes, edges });
  } catch (error) {
    console.error('Error fetching data:', error);
    res.status(500).send('Error fetching data');
  }
});



// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

// Cleanup on server shutdown
process.on('SIGINT', async () => {
    console.log('Closing database connections...');
    await driver.close();
    db.close((err) => {
        if (err) {
            console.error('Error closing SQLite database:', err.message);
        } else {
            console.log('Closed the SQLite database connection.');
        }
        process.exit(0);
    });
});
