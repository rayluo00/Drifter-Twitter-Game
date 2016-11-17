#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys

con = lite.connect('tweet.db')

# with con:

#     cur = con.cursor()
#     cur.execute("CREATE TABLE Cars(Id INT, Name TEXT, Price INT)")
#     cur.execute("INSERT INTO Cars VALUES(1,'Audi',52642)")
#     cur.execute("INSERT INTO Cars VALUES(2,'Mercedes',57127)")
#     cur.execute("INSERT INTO Cars VALUES(3,'Skoda',9000)")
#     cur.execute("INSERT INTO Cars VALUES(4,'Volvo',29000)")
#     cur.execute("INSERT INTO Cars VALUES(5,'Bentley',350000)")
#     cur.execute("INSERT INTO Cars VALUES(6,'Citroen',21000)")
#     cur.execute("INSERT INTO Cars VALUES(7,'Hummer',41400)")
#     cur.execute("INSERT INTO Cars VALUES(8,'Volkswagen',21600)")

with con:

    cur = con.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS Player;
        CREATE TABLE Player(id INTEGER primary key autoincrement, Name TEXT, Success INT, Total INT, TotalDay INT, LastDay TEXT);

        Insert Into Player (Name, Success, Total, TotalDay, LastDay) VALUES('@MrBot', 2, 10, 4, '05/24/2016');
        Insert Into Player (Name, Success, Total, TotalDay, LastDay) VALUES('@Driller', 3, 11, 1, '05/24/2016');
        Insert Into Player (Name, Success, Total, TotalDay, LastDay) VALUES('@Destroyer', 1, 10, 2, '05/23/2016');
        Insert Into Player (Name, Success, Total, TotalDay, LastDay) VALUES('@Player4', 2, 10, 4, '05/24/2016');
        Insert Into Player (Name, Success, Total, TotalDay, LastDay) VALUES('@Player2', 1, 17, 5, '05/25/2016');
        """)
    con.commit()
con.close()


        # Insert Into Player VALUES(2, '@Driller', 'goto A', 2, 4);
        # Insert Into Player VALUES(3, '@Destroyer', 'goto B', 1, 5);
        # Insert Into Player VALUES(4, '@Player4', 'goto C', 3, 10);
        # Insert Into Player VALUES(5, '@Player5', 'goto A', 5, 20);
        # Insert Into Player VALUES(6, '@Player6', 'goto K', 2, 3);
