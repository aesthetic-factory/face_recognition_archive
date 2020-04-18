import face_recognition
import glob
import math
import numpy as np
from multiprocessing import Pool
from os.path import basename
from database import fetch_descriptors, fetch_labels, fetch_valid_labels
from config import MAX_PROCESS, JITTERS

# Constant
TOL_DISTANCE = 0.5  # 0.44


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
            name = label["name"]
            # results = face_recognition.compare_faces(
            #     label["descriptors"], face, TOL_DISTANCE=TOL_DISTANCE)

            # distances = face_recognition.face_distance(
            #     label["descriptors"], face)

            # customized weighted distance
            distances = face_distance(label["descriptors"], face)
            real_avg_dist = np.mean(distances)
            if real_avg_dist < TOL_DISTANCE:
                predict_names.append(
                    {'name': name,  "distance": real_avg_dist})
                found = True

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
