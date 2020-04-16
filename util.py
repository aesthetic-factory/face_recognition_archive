import face_recognition
import glob
import math
import numpy as np
from multiprocessing import Pool, cpu_count
from os.path import basename
from database import fetch_descriptors, fetch_labels, fetch_valid_labels

# Constant
DATASET_DIR = "C:/Dev/Dataset/"
TRAIN_DIR = DATASET_DIR + "train/"
EVA_DIR = DATASET_DIR + "evaluate/"
ACCEPT_SCORE = 0.63
TOL_DISTANCE = 0.45  # 0.44
IDEAL_DISTANCE = 0.36  # 0.33
MAX_PROCESS = 14  # cpu_count()
JITTERS = 25


def getImagePath(folderPath):
    types = ('*.png', '*.jpg', '*.jiff')  # the tuple of file types
    files_list = []
    for files in types:
        files_list.extend(glob.glob(folderPath + files))
    return files_list


def getFolders(datasetPath):  # return folder name
    folder_list = []
    folder_list.extend(glob.glob(datasetPath+"/*"))
    return [basename(folder) for folder in folder_list]


def imageProcessor(img_path):
    face_encodings = []
    try:
        # Load the jpg files into numpy arrays
        image = face_recognition.load_image_file(img_path)

        # Get the face encodings for each face in each image file
        # Since there could be more than one face in each image, it returns a list of encodings.
        # But since I know each image only has one face, I only care about the first encoding in each image, so I grab index 0.
        face_encodings = face_recognition.face_encodings(
            image, num_jitters=JITTERS, model="large")
    except Exception as e:
        # In case of corrupted file
        print(f"Error {img_path}")
        pass
    return face_encodings


def loadImageEncoding(data_dir):
    img_paths = getImagePath(data_dir)
    face_encodings = []
    with Pool(MAX_PROCESS) as p:  # multi-process pool size
        face_encodings = p.map(imageProcessor, img_paths)
    return face_encodings


def fetch_face_library():
    labels = fetch_labels()
    library = []
    for label in labels:
        name = label[0]
        descriptors = fetch_descriptors(name)
        data = {}
        data["name"] = name
        data["descriptors"] = []
        for d in descriptors:
            data["descriptors"].append(d[2:])  # first 2 are, pk, name
        library.append(data)
    return library


def euclideanDistance(x, y, weights):
    distance = math.sqrt(
        sum([w*(a - b) ** 2 for a, b, w in zip(x, y, weights)]))
    return distance


def face_distance(descriptors, face):
    weights = [1] * 128
    # weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 2, 0.5, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 1, 1, 1, 1, 1, 2, 1, 2, 0.5, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 0.5, 0.5, 1, 1, 1, 1, 2, 1, 1, 0.5, 1, 1, 1, 1, 1, 2, 1, 0.5, 1, 2, 1, 1, 1, 1, 0.5, 2, 0.5, 1, 2, 1, 0.5, 1, 1, 1, 1, 1, 1, 2, 1,
    #            0.5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 0.5, 0.5, 0.5, 1, 1, 1, 1, 1, 1]

    distances = []
    for descriptor in descriptors:
        distance = euclideanDistance(descriptor, face, weights)
        distances.append(distance)
    return distances


def predict(img_enc, library):
    predicts = []
    for face in img_enc:
        found = False
        predict_names = []
        for label in library:

            # results = face_recognition.compare_faces(
            #     label["descriptors"], face, TOL_DISTANCE=TOL_DISTANCE)

            # distances = face_recognition.face_distance(
            #     label["descriptors"], face)

            distances = face_distance(label["descriptors"], face)

            matched = []
            matched_distances = []
            for d in distances:
                if d < TOL_DISTANCE:
                    matched.append(True)
                    matched_distances.append(d)
                else:
                    matched.append(False)
            if len(matched_distances) == 0:
                continue
            name = label["name"]

            avg_dist = np.mean(matched_distances)
            real_avg_dist = np.mean(distances)
            if avg_dist < TOL_DISTANCE:
                predict_names.append(
                    {'name': name,  "distance": real_avg_dist})
                found = True

            # match = matched.count(True)
            # total = len(matched)
            # upbound = 5
            # if total > 10 and total <= 15:
            #     upbound = 10
            # elif total > 15 and total <= 20:
            #     upbound = 15
            # else:
            #     upbound = 20
            # score = np.amin([upbound, match]) / upbound
            # penalty = (total - match) / total
            # compensated_score = score - penalty * \
            #     0.7 - (real_avg_dist-IDEAL_DISTANCE)*4

            # if compensated_score > ACCEPT_SCORE:
            #     predict_names.append(
            #         {'name': name, 'score': compensated_score, "distance": real_avg_dist, 'match_distance': avg_dist})
            #     found = True
                # print(
                #     f"{name}: {compensated_score}. score:{score} penalty:{penalty} avg_dist:{avg_dist}")

        if not found:
            predict_names.append(
                {'name': 'unkown', 'score': 0, "distance": 1})
        else:
            def sort_distance(json):
                return json['distance']
            predict_names.sort(key=sort_distance, reverse=False)

        predict_names = predict_names[:1]
        predicts.extend(predict_names)
    return predicts
