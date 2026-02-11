#!/usr/bin/python3
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'information.db')

class DBConnect:
    def __init__(self):
        self._db = sqlite3.connect(DB_PATH)
        self._db.row_factory = sqlite3.Row
        self._db.execute('''create table if not exists Comp(
            ID integer primary key autoincrement, 
            Name varchar(255), 
            Gender varchar(255), 
            Comment text,
            CreatedAt datetime,
            Resolution text,
            Status varchar(50)
        )''')
        self._db.execute('''create table if not exists ResponseHistory(
            ID integer primary key autoincrement,
            CompID integer,
            Response text,
            Status varchar(50),
            CreatedAt datetime,
            FOREIGN KEY (CompID) REFERENCES Comp(ID)
        )''')
        self._db.commit()
        self._run_migrations()

    def _run_migrations(self):
        cursor = self._db.execute("PRAGMA table_info(Comp)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'CreatedAt' not in columns:
            self._db.execute('ALTER TABLE Comp ADD COLUMN CreatedAt datetime')
        if 'Resolution' not in columns:
            self._db.execute('ALTER TABLE Comp ADD COLUMN Resolution text')
        if 'Status' not in columns:
            self._db.execute("ALTER TABLE Comp ADD COLUMN Status varchar(50) DEFAULT 'Pending'")
        self._db.commit()

    def Add(self, name, gender, comment):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._db.execute('insert into Comp (Name, Gender, Comment, CreatedAt, Status) values (?,?,?,?,?)',
                         (name, gender, comment, now, 'Pending'))
        self._db.commit()
        return 'Your complaint has been submitted.'

    def ListRequest(self):
        cursor = self._db.execute('select * from Comp order by ID desc')
        return cursor

    def GetComplaint(self, comp_id):
        cursor = self._db.execute('select * from Comp where ID = ?', (comp_id,))
        return cursor.fetchone()

    def Resolve(self, comp_id, resolution, status):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._db.execute('insert into ResponseHistory (CompID, Response, Status, CreatedAt) values (?,?,?,?)',
                         (comp_id, resolution, status, now))
        self._db.execute('update Comp set Resolution = ?, Status = ? where ID = ?',
                         (resolution, status, comp_id))
        self._db.commit()

    def GetResponseHistory(self, comp_id):
        cursor = self._db.execute('select * from ResponseHistory where CompID = ? order by CreatedAt desc', (comp_id,))
        return cursor.fetchall()
