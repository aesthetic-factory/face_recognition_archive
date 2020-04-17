import argparse
import face_recognition
import numpy as np
from prettytable import PrettyTable
from database import insert_descriptor, insert_label, remove_descriptor, remove_label, fetch_descriptors, fetch_labels, clean_db, count_descriptors


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
