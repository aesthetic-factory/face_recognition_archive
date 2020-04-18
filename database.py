import sys
import random
from datetime import datetime
from lib.Postgres import Postgres
from config import DB_HOST, DB_PORT, DS_USER, DB_PASSWORD, DB_DATABASE

database = None


def setup_connection():
    global database
    if database != None:
        return True
    database = Postgres(DB_HOST, DB_PORT, DS_USER,
                        DB_PASSWORD, DB_DATABASE)


def insert_descriptor(label, descriptors=[]):
    setup_connection()
    dt = datetime.now()
    columns = ""
    values = ""
    for x in range(128):
        columns += f", p{x}"
        values += f", {descriptors[x]}"
    group_id = random.randrange(0, 100)
    query = f"INSERT INTO descriptors (name_id, group_id, create_time {columns}) VALUES ((SELECT id FROM labels WHERE name='{label}'),{group_id},'{dt}' {values})"
    data = database.exe_query(query)
    return data


def remove_descriptor(pk):
    setup_connection()
    query = f"DELETE FROM descriptors WHERE id={pk}"
    data = database.exe_query(query)
    return data


def insert_label(label):
    dt = datetime.now()
    query = f"INSERT INTO labels (name, create_time) VALUES ('{label}','{dt}') ON CONFLICT DO NOTHING"
    setup_connection()
    data = database.exe_query(query)
    return data


def fetch_labels():
    setup_connection()
    query = f"SELECT name FROM labels"
    data = database.exe_query(query)
    return data


def fetch_valid_labels(thershold=20):
    setup_connection()
    query = f"SELECT name_id FROM descriptors GROUP BY name_id HAVING COUNT(1) > {thershold} ORDER BY name_id"
    data = database.exe_query(query)
    return data


def remove_label(label):
    setup_connection()
    query = f"DELETE FROM descriptors WHERE name_id in (SELECT id FROM labels WHERE name='{label}')"
    data = database.exe_query(query)
    query = f"DELETE FROM labels WHERE name in ('{label}')"
    data = database.exe_query(query)
    return data


def fetch_evaluation_descriptors():
    setup_connection()
    group_id_start = random.randrange(0, 75)
    group_id_end = group_id_start + 25
    columns = ""
    for x in range(128):
        columns += f", b.p{x}"
    query = f"SELECT name {columns} FROM labels a JOIN descriptors b ON a.id = b.name_id WHERE b.group_id BETWEEN {group_id_start} AND {group_id_end} ORDER BY a.name"
    data = database.exe_query(query)
    return data


def fetch_descriptors(label=""):
    setup_connection()
    columns = ""
    for x in range(128):
        columns += f", b.p{x}"
    if label == "":
        query = f"SELECT b.id, name {columns} FROM labels a JOIN descriptors b ON a.id = b.name_id ORDER BY a.name"
    else:
        query = f"SELECT b.id, name {columns} FROM labels a JOIN descriptors b ON a.id = b.name_id WHERE a.name='{label}' ORDER BY a.name"
    data = database.exe_query(query)
    return data


def count_descriptors(label=""):
    setup_connection()
    if label == "":
        query = f"SELECT a.name, COUNT(1) FROM labels a JOIN descriptors b ON a.id = b.name_id GROUP BY a.name ORDER BY a.name"
    else:
        query = f"SELECT a.name, COUNT(1) FROM labels a JOIN descriptors b ON a.id = b.name_id WHERE a.name='{label}' GROUP BY a.name ORDER BY a.name"
    data = database.exe_query(query)

    return data


def create_table_labels():
    setup_connection()
    query = f"CREATE TABLE labels (id SERIAL PRIMARY KEY, name TEXT NOT NULL, create_time TIMESTAMP NOT NULL)"
    data = database.exe_query(query)
    query = f"CREATE INDEX idx_labels ON labels (name)"
    data = database.exe_query(query)
    return data


def create_table_tags():
    setup_connection()
    query = f"CREATE TABLE tags(id SERIAL PRIMARY KEY, name_id INTEGER REFERENCES labels(id), create_time TIMESTAMP NOT NULL, name TEXT NOT NULL)"
    data = database.exe_query(query)
    query = f"CREATE INDEX idx_tags ON labels (name)"
    data = database.exe_query(query)
    return data


def create_table_descriptors():
    setup_connection()
    columns = ""
    for x in range(128):
        columns += f", p{x} DOUBLE PRECISION"

    query = f"CREATE TABLE descriptors (id SERIAL PRIMARY KEY, name_id INTEGER REFERENCES labels(id), group_id INTEGER NOT NULL, create_time TIMESTAMP NOT NULL {columns})"
    data = database.exe_query(query)
    query = f"CREATE INDEX idx_descriptors ON descriptors (name_id)"
    data = database.exe_query(query)
    return data


def drop_table(table):
    setup_connection()
    query = f"DROP TABLE IF EXISTS {table} CASCADE"
    data = database.exe_query(query)
    return data


def clean_db():
    setup_connection()
    tabels = ["labels", "descriptors", "tags"]
    for tabel in tabels:
        drop_table(tabel)
    create_table_labels()
    create_table_tags()
    create_table_descriptors()

    return True
