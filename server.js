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

// Define the endpoint to get top 50 tunes
app.get('/top-tunes', (req, res) => {
    const query = `
        SELECT t.tune_id, t.name, t.session_url, COUNT(tts.tune_id) AS tune_count
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


app.get('/sessions', (req, res) => {
    const query = `SELECT * FROM Session`;
    db.all(query, [], (err, rows) => {
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
