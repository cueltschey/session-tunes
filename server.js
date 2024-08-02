const express = require('express');
const path = require('path');
const sqlite3 = require('sqlite3');

const db = new sqlite3.Database("./session.db");
const app = express();
const port = 3000;

app.use(express.static(path.join(__dirname, "dist")))

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
