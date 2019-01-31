import pathlib
import os
import datetime

from PyQt5 import QtSql

QSqlDatabase = QtSql.QSqlDatabase
QSqlQuery = QtSql.QSqlQuery


class DatabaseError(Exception):
    pass


conn = QSqlDatabase.addDatabase('QSQLITE', 'db')
path = pathlib.Path(os.path.abspath(__file__)).parent / 'db.sqlite'
conn.setDatabaseName(str(path))


def init():
    global conn
    if not conn.open():
        raise DatabaseError
    if 'outgones' not in conn.tables():
        minYear = datetime.MINYEAR
        maxYear = datetime.MAXYEAR
        query = QSqlQuery(conn)
        query.exec('CREATE TABLE outgones (\
            name TEXT NOT NULL,\
            day INTEGER NOT NULL CHECK(day >= 1 and day <= 31),\
            month INTEGER NOT NULL CHECK(month >= 1 and month <= 12),\
            year INTEGER NOT NULL CHECK(year >= {} and year <= {}),\
            category INTEGER NOT NULL CHECK(category >= 0 and category <= 11),\
            price REAL NOT NULL CHECK(price >= 0),\
            count INTEGER NOT NULL CHECK(count >= 1)\
        );'.format(minYear, maxYear))
        query.clear()
    conn.close()
