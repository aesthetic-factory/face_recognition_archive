import face_recognition
from multiprocessing import Pool
from database import insert_descriptor, insert_label
from util import loadImageEncoding, getFolders, TRAIN_DIR


def train_batch(label):
    print(f"Training '{label}'")
    data_dir = TRAIN_DIR + label + "/"
    insert_label(label)
    imgs_enc = loadImageEncoding(data_dir)
    for img_enc in imgs_enc:
        for face_enc in img_enc:
            if len(face_enc):
                insert_descriptor(label, face_enc)
    face_encoding_library.extend(imgs_enc)


# ========== main ==========
if __name__ == '__main__':
    # Get dataset folders
    train_dataset_folders = getFolders(TRAIN_DIR)

    face_encoding_library = []
    for label in train_dataset_folders:
        train_batch(label)
