import argparse
import face_recognition
import numpy as np
from prettytable import PrettyTable
import sys
import json
import random
from datetime import datetime
from lib.Postgres import Postgres

with open('config.json') as json_file:
    data = json.load(json_file)
    database_cfg = data["database"]
    host = database_cfg["host"]
    port = database_cfg["port"]
    user = database_cfg["user"]
    password = database_cfg["password"]
    databasest = database_cfg["database"]
    database = Postgres(host, port, user,
                        password, databasest)


def insert_descriptor(label, descriptors=[]):
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
    query = f"DELETE FROM descriptors WHERE id={pk}"
    data = database.exe_query(query)
    return data


def insert_label(label):
    dt = datetime.now()
    query = f"INSERT INTO labels (name, create_time) VALUES ('{label}','{dt}') ON CONFLICT DO NOTHING"
    data = database.exe_query(query)
    return data


def fetch_labels():
    query = f"SELECT name FROM labels"
    data = database.exe_query(query)
    return data


def fetch_valid_labels(thershold=20):
    query = f"SELECT name_id FROM descriptors GROUP BY name_id HAVING COUNT(1) > {thershold} ORDER BY name_id"
    data = database.exe_query(query)
    return data


def remove_label(label):
    query = f"DELETE FROM descriptors WHERE name_id in (SELECT id FROM labels WHERE name='{label}')"
    data = database.exe_query(query)
    query = f"DELETE FROM labels WHERE name in ('{label}')"
    data = database.exe_query(query)
    return data


def fetch_evaluation_descriptors():
    group_id_start = random.randrange(0, 80)
    group_id_end = group_id_start + 20
    columns = ""
    for x in range(128):
        columns += f", b.p{x}"
    query = f"SELECT name {columns} FROM labels a JOIN descriptors b ON a.id = b.name_id WHERE b.group_id BETWEEN {group_id_start} AND {group_id_end} ORDER BY a.name"
    data = database.exe_query(query)
    return data


def fetch_descriptors(label=""):
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
    if label == "":
        query = f"SELECT a.name, COUNT(1) FROM labels a JOIN descriptors b ON a.id = b.name_id GROUP BY a.name ORDER BY a.name"
    else:
        query = f"SELECT a.name, COUNT(1) FROM labels a JOIN descriptors b ON a.id = b.name_id WHERE a.name='{label}' GROUP BY a.name ORDER BY a.name"
    data = database.exe_query(query)

    return data


def create_table_labels():
    query = f"CREATE TABLE labels (id SERIAL PRIMARY KEY, name TEXT NOT NULL, create_time TIMESTAMP NOT NULL)"
    data = database.exe_query(query)
    query = f"CREATE INDEX idx_labels ON labels (name)"
    data = database.exe_query(query)
    return data


def create_table_tags():
    query = f"CREATE TABLE tags(id SERIAL PRIMARY KEY, name_id INTEGER REFERENCES labels(id), create_time TIMESTAMP NOT NULL, name TEXT NOT NULL)"
    data = database.exe_query(query)
    query = f"CREATE INDEX idx_tags ON labels (name)"
    data = database.exe_query(query)
    return data


def create_table_descriptors():
    columns = ""
    for x in range(128):
        columns += f", p{x} DOUBLE PRECISION"

    query = f"CREATE TABLE descriptors (id SERIAL PRIMARY KEY, name_id INTEGER REFERENCES labels(id), group_id INTEGER NOT NULL, create_time TIMESTAMP NOT NULL {columns})"
    data = database.exe_query(query)
    query = f"CREATE INDEX idx_descriptors ON descriptors (name_id)"
    data = database.exe_query(query)
    return data


def drop_table(table):
    query = f"DROP TABLE IF EXISTS {table} CASCADE"
    data = database.exe_query(query)
    return data


def clean_db():
    tabels = ["labels", "descriptors", "tags"]
    for tabel in tabels:
        drop_table(tabel)
    create_table_labels()
    create_table_tags()
    create_table_descriptors()

    return True


def summary():
    t = PrettyTable(['Name', 'Count'])
    summaries = count_descriptors()
    for row in summaries:
        name, count = row
        t.add_row([name, count])
    print(t)
    return True


def status():
    t = PrettyTable(['Name', 'Count', 'Mean', 'STD', 'Max', 'Min'])
    labels = count_descriptors()
    for label in labels:
        name, count = label
        if count <= 3:
            continue
        descriptors = fetch_descriptors(name)
        distances = []
        for idx1, d1 in enumerate(descriptors):
            d1 = [np.array(d1[2:])]
            for idx2, d2 in enumerate(descriptors):
                if idx2 <= idx1:
                    continue
                d2 = np.array(d2[2:])
                distance = face_recognition.face_distance(d1, d2)
                distances.append(distance)
        dMean = round(float(np.mean(distances)), 3)
        dStd = round(float(np.std(distances)), 3)
        dMax = round(float(np.max(distances)), 3)
        dMin = round(float(np.min(distances)), 3)
        t.add_row([name, len(descriptors), dMean, dStd, dMax, dMin])
    print(t)
    return True


# main
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cmd", help="'summary' / 'status' / 'fetch_descriptor' / 'fetch_evaluation_descriptors' / 'fetch_label' / 'insert_label' / 'insert_descriptor' / 'remove_descriptor' / 'remove_label' / 'clean_db'",
                        required=False,  type=str)
    parser.add_argument("-p", "--pk", help="primary key in descriptors",
                        required=False,  type=str)
    parser.add_argument("-t", "--label", help="person name",
                        required=False,  type=str)

    args = parser.parse_args()
    label = args.label
    cmd = args.cmd
    pk = args.pk

    if cmd == "insert_label":
        result = insert_label(label)
    elif cmd == "summary":
        result = summary()
    elif cmd == "status":
        result = status()
    elif cmd == "insert_descriptor":
        result = insert_descriptor(label)
    elif cmd == "remove_descriptor":
        result = remove_descriptor(pk)
    elif cmd == "remove_label":
        result = remove_label(label)
    elif cmd == "clean_db":
        result = clean_db()
    elif cmd == "fetch_label":
        result = fetch_labels()
    elif cmd == "fetch_descriptor":
        result = fetch_descriptors()
    elif cmd == "fetch_evaluation_descriptors":
        result = fetch_evaluation_descriptors()
    else:
        result = 'Unkown command'
    print(result)
