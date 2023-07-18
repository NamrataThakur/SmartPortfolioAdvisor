const express = require('express');
const sqlite3 = require('sqlite3').verbose();

const app = express();
const cors = require('cors');

app.use(cors());
app.use(express.json());

app.post('/stockportfolio', (req, res) => {
    console.log('in stockportfolio');
    const { date } = req.body;
    const db = new sqlite3.Database('../database/stocks.db', sqlite3.OPEN_READWRITE, (err) => {
        if (err) {
            console.error(err.message);
        } else {
            console.log('Connected to the stocks database.');
        }
    });
    db.serialize(() => {
        // db.each(`SELECT stocktickers,chromosome,max(sharpe) FROM garesults WHERE date='${day}'`, (err, row) => {
        db.each(
            'SELECT date,stocktickers,chromosome,max(sharpe) as sharpe,return,risk FROM garesults WHERE date is ?',
        [date],
        (err, row) => {
            if (err) {
                console.error(err.message);
            }
            res.send(row);
        },
);
    });
});

app.post('/stockportfoliolatest', (req, res) => {
    console.log('in stockportfolio');
    const { date } = req.body;
    const db = new sqlite3.Database('../database/stocks.db', sqlite3.OPEN_READWRITE, (err) => {
        if (err) {
            console.error(err.message);
        } else {
            console.log('Connected to the stocks database.');
        }
    });
    db.serialize(() => {
        // db.each(`SELECT stocktickers,chromosome,max(sharpe) FROM garesults WHERE date='${day}'`, (err, row) => {
        db.each(
           'SELECT max(a.date) as date ,stocktickers,chromosome,a.sharpe,a.return,a.risk FROM (SELECT date,stocktickers,chromosome,max(sharpe) as sharpe,return,risk FROM garesults group by date) as a',
        (err, row) => {
            if (err) {
                console.error(err.message);
            }
            res.send(row);
        },
);
    });
});

app.post('/stockforecast', (req, res) => {
    const { stock } = req.body;
    const db = new sqlite3.Database('../database/lstm_prediction.db', sqlite3.OPEN_READWRITE, (err) => {
        if (err) {
            console.error(err.message);
        } else {
            console.log('Connected to the lstm_prediction database.');
        }
    });
    db.serialize(() => {
        // db.each(`SELECT stocktickers,chromosome,max(sharpe) FROM garesults WHERE date='${day}'`, (err, row) => {
        db.each(
'SELECT group_concat(date) as date,group_concat(price) as price FROM predictions WHERE ticker is ?',
        [stock],
        (err, row) => {
            if (err) {
                console.error(err.message);
            }
            console.log(row);
            res.send(row);
        },
);
    });
});

app.post('/groupstockforecast', (req, res) => {
    const { stocks } = req.body;
    const db = new sqlite3.Database('../database/lstm_prediction.db', sqlite3.OPEN_READWRITE, (err) => {
        if (err) {
            console.error(err.message);
        } else {
            console.log('Connected to the lstm_prediction database.');
        }
    });
    let sql = 'SELECT group_concat(date) as date,group_concat(price) as price FROM predictions WHERE';
    for (let i = 0; i < stocks.length - 1; i++) {
        sql += ' ticker is ? OR';
    }
    sql += ' ticker is ?';
    db.serialize(() => {
        // db.each(`SELECT stocktickers,chromosome,max(sharpe) FROM garesults WHERE date='${day}'`, (err, row) => {
        db.each(
sql,
        stocks,
        (err, row) => {
            if (err) {
                console.error(err.message);
            }
            console.log(row);
            res.send(row);
        },
);
    });
});

app.listen(3001, () => {
    console.log('listening on port 3001');
});
