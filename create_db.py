import sqlite3

# Create Database
connection = sqlite3.connect('patterns.sqlite')
cursor = connection.cursor()

with open('create_db.sql', 'r') as f:
    text = f.read()
cursor.executescript(text)
cursor.close()
connection.close()