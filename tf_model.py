import os.path as path

# tensorflow
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import BatchNormalization, Activation, Dropout
from tensorflow.keras.layers import Input, Dense, LSTM
from tensorflow.keras.models import Model, load_model, save_model


def create_model(inputs_shape, outputs_shape):  # create a model
    main_input = Input(shape=inputs_shape, name='main_input')
    lay1 = Dense(inputs_shape, activation='selu')(main_input)
    lay1 = Dropout(0.5)(lay1)
    lay1 = BatchNormalization()(lay1)

    # lay2 = Dense(64, activation='selu')(lay1)
    # lay2 = Dropout(0.5)(lay2)
    # lay2 = BatchNormalization()(lay2)

    lay3 = Dense(32, activation='relu')(lay1)
    lay3 = Dropout(0.5)(lay3)
    lay3 = BatchNormalization()(lay3)

    output = Dense(outputs_shape, activation='sigmoid')(lay3)

    model = Model(inputs=main_input, outputs=output)
    # Compile model
    model.compile(
        loss='binary_crossentropy',
        optimizer="adam",
        metrics=['binary_accuracy']
    )
    return model


def load_model_from_file(model_file_path):
    if path.exists(model_file_path):
        model = load_model(model_file_path)
        return model
    else:
        return False
