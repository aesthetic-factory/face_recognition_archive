import os
import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint
import numpy as np
from sklearn.utils import shuffle
import argparse
from util import loadImageEncoding, getFolders, fetch_face_library, predict, EVA_DIR
from database import fetch_descriptors, fetch_labels, fetch_evaluation_descriptors
from tf_model import load_model_from_file

# Constants
MODEL_FILE_PATH = "./model.h5"
EVA_DIR = "C:/Dev/Dataset/evaluate/"
BATCH_SIZE = 800  # depends on system memoey / GPU memory
EPOCHS = 100  # number of rounds for training

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# tf.get_logger().setLevel('ERROR')


def prepare_dataset(descriptors, img_enc2):
    X = []
    Names = []
    for descriptor in descriptors:
        name = descriptor[1]
        img_enc1 = list(descriptor[2:])
        attributes = []

        attributes.extend(img_enc1)
        attributes.extend(img_enc2)
        X.append(attributes)
        Names.append(name)

    X = np.array(X).astype(np.float16)
    return X, Names


def most_frequent(List):
    return max(set(List), key=List.count)


def predict_tf(img_enc, descriptors, model):
    predicts = []
    for face_enc in img_enc:
        X, Names = prepare_dataset(descriptors, list(face_enc))
        predict_results = model.predict(X)
        predict_names = []
        for match, name in zip(predict_results, Names):
            if match > 0.53:
                predict_names.append(name)
        if len(predict_names) == 0:
            predicts.append('Unkown')
        else:
            t = most_frequent(predict_names)
            if predict_names.count(t) > 5:
                predicts.append(t)
            else:
                predicts.append('Unkown')
    return predicts


# main
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l", "--local", help="Use local data", action='store_true')

    args = parser.parse_args()
    local = args.local
    descriptors = fetch_descriptors()
    model = load_model_from_file(MODEL_FILE_PATH)
    if local:
        eva_dataset_folders = getFolders(EVA_DIR)
        for label in eva_dataset_folders:
            labels = fetch_labels()
            data_dir = EVA_DIR + label + "/"
            imgs_enc = loadImageEncoding(data_dir)
            print(f"-----{label}-----")
            for img_enc in imgs_enc:
                predicts = predict_tf(img_enc, descriptors, model)
                print(predicts)

    else:
        data = fetch_evaluation_descriptors()
        total = len(data)
        err_cnt = 0
        print(f"----- START -----")
        for item in data:
            label = item[0]
            img_enc = list(item[1:])
            predicts = predict_tf([img_enc], descriptors, model)

            if predicts[0] != label:  # always 1 face in a row in db record
                err_cnt += 1
        err_rate = err_cnt / total
        print(f"Error rate: {err_rate}. Total:{total}")
