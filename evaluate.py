import face_recognition
from util import loadImageEncoding, getFolders, fetch_face_library, predict, EVA_DIR
from database import fetch_evaluation_descriptors
import argparse

# ========== main ==========
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l", "--local", help="Use local data", action='store_true')

    args = parser.parse_args()
    local = args.local

    library = fetch_face_library()
    if local:
        # Get dataset folders
        eva_dataset_folders = getFolders(EVA_DIR)
        for label in eva_dataset_folders:
            data_dir = EVA_DIR + label + "/"
            imgs_enc = loadImageEncoding(data_dir)
            print(f"-----{label}-----")
            for img_enc in imgs_enc:
                result = predict(img_enc, library)
                print(result)
    else:
        data = fetch_evaluation_descriptors()
        total = len(data)
        err_cnt = 0
        for item in data:
            label = item[0]
            img_enc = list(item[1:])
            result = predict([img_enc], library)
            predict_name = result[0]["name"]
            predict_dist = result[0]["distance"]
            #print(f"{label}: {predict_name} {predict_dist}")
            if predict_name != label:
                err_cnt += 1
        err_rate = err_cnt / total
        print(f"Error rate: {err_rate}. Total:{total}")
