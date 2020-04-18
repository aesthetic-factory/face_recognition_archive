import json
from multiprocessing import cpu_count

# database config
DB_HOST = ""
DB_PORT = ""
DS_USER = ""
DB_PASSWORD = ""
DB_DATABASE = ""

# directories config
DS_DIR = ""
DS_TRAIN_DIR = ""
DS_EVA_DIR = ""

# performance config
MAX_PROCESS = 2
JITTERS = 1

with open('config.json') as json_file:
    data = json.load(json_file)

    db_cfg = data["database"]
    DB_HOST = db_cfg["host"]
    DB_PORT = db_cfg["port"]
    DS_USER = db_cfg["user"]
    DB_PASSWORD = db_cfg["password"]
    DB_DATABASE = db_cfg["database"]

    dir_cfg = data["directories"]
    DS_DIR = dir_cfg["dataset"]
    DS_TRAIN_DIR = DS_DIR + "train/"
    DS_EVA_DIR = DS_DIR + "evaluate/"

    perf_cfg = data["performance"]
    MAX_PROCESS = cpu_count() if perf_cfg["max_process"] == -1 else perf_cfg["max_process"]
    JITTERS = perf_cfg["jitters"]

    if MAX_PROCESS < 2:
        MAX_PROCESS = 2
    if JITTERS < 1:
        JITTERS = 1
