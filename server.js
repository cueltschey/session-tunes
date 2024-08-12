const path = require('path');
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, "dist")))

// Set up SQLite database connection
const db = new sqlite3.Database('mueller.db', (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        console.log('Connected to the SQLite database.');
    }
});

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



// GET all tunes in a given set
app.get('/set', (req, res) => {
    const set_id = req.query.set_id
    if(!set_id){
      res.status(401).send("set_id required")
      return
    }
    const query = `
          SELECT DISTINCT t.*
          FROM Tune t
          JOIN TuneToSet ts ON t.tune_id = ts.tune_id
          WHERE ts.set_id = ?
          ORDER BY ts.tune_index ASC;    
    `;
    db.all(query, [set_id], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});

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



// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

// Close the database connection when the server is stopped
process.on('SIGINT', () => {
    db.close((err) => {
        if (err) {
            console.error('Error closing the database ' + err.message);
        }
        console.log('Database connection closed.');
        process.exit(0);
    });
});
