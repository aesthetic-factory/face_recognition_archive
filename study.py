import argparse
import numpy as np
from prettytable import PrettyTable
from lib.Postgres import Postgres
import json
import random


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


def get_samples_id(thershold=20):
    query = f"SELECT name_id FROM descriptors GROUP BY name_id HAVING COUNT(1) > {thershold} AND COUNT(1) < 150 ORDER BY name_id"
    data = database.exe_query(query)
    result = []
    for i in data:
        result.append(i[0])
    return result


def fetch_label_stat(col=0, id=24):
    query = f"SELECT stddev(p{col}) FROM public.descriptors"
    all_std = database.exe_query(query)[0][0]
    query = f"SELECT stddev(p{col}) FROM public.descriptors WHERE name_id={id}"
    this_std = database.exe_query(query)[0][0]
    ratio = float(all_std)/float(this_std)
    return ratio, this_std, all_std


ids = get_samples_id()
print(ids)
ratios = []
for x in range(128):
    ratios.append(0)
for i in ids:
    t = PrettyTable(['id', 'ratio', 'this', 'all'])
    for x in range(128):
        ratio, this_std, all_std = fetch_label_stat(x, i)
        ratios[x] += ratio / len(ids)
        if ratio > 3:
            t.add_row([x, ratio, this_std, all_std])
    # print(t)

t = PrettyTable(['id', 'ratio', 'low ratio', 'high ratio'])
total = 0
for x in range(128):
    total += ratios[x]
print(f"Average: {total / 128}")
average = total / 128
weights = []
for x in range(128):
    ratio = ratios[x]
    diff = round(abs(ratio - average) / average, 3)
    if diff > 0.22:
        weights.append(2)
    elif diff <= 0.02:
        weights.append(0.5)
    else:
        weights.append(1)
    if diff > 0.22:
        t.add_row([x, diff, '', 'x'])
    elif diff <= 0.02:
        t.add_row([x, diff, 'x', ''])
print(t)
print(weights)
# id: 34,49,80,111
