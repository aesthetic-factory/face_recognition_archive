from tensorflow.keras.callbacks import ModelCheckpoint
import numpy as np
from sklearn.utils import shuffle
from database import fetch_descriptors
from tf_model import create_model, load_model_from_file

# Constants
MODEL_FILE_PATH = "./model.h5"
BATCH_SIZE = 1000  # depends on system memoey / GPU memory
EPOCHS = 100  # number of rounds for training


def prepare_dataset(descriptors):
    X = []
    Y = []
    cnt = 0
    for idx1, descriptor1 in enumerate(descriptors):
        name1 = descriptor1[1]
        img_enc1 = list(descriptor1[2:])
        for idx2, descriptor2 in enumerate(descriptors):
            cnt += 1
            if idx2 < idx1:
                continue
            name2 = descriptor2[1]
            img_enc2 = list(descriptor2[2:])
            attributes = []
            if cnt % 2 == 0:
                attributes.extend(img_enc1)
                attributes.extend(img_enc2)
            else:
                attributes.extend(img_enc2)
                attributes.extend(img_enc1)
            X.append(attributes)
            if name1 == name2:
                Y.append(1)
            else:
                Y.append(0)

    X = np.array(X).astype(np.float16)
    Y = np.array(Y).astype(np.float16)
    return X, Y


# main
if __name__ == '__main__':
    descriptors = fetch_descriptors()
    X, Y = prepare_dataset(descriptors)
    X, Y = shuffle(X, Y)
    X, Y = shuffle(X, Y)
    print(f"Dataset size:{len(X)} {len(Y)}")
    model = load_model_from_file(MODEL_FILE_PATH)
    if model == False:
        model = create_model(256, 1)
    model.summary()
    checkpoint = ModelCheckpoint(MODEL_FILE_PATH, monitor='val_binary_accuracy',
                                 verbose=0, save_best_only=True, mode='max')  # saves only the best ones

    model.fit(
        X, Y,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        shuffle=True,
        callbacks=[checkpoint],
        validation_split=0.15
    )
