import face_recognition
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from multiprocessing import Pool, cpu_count
from util import loadImageEncoding, getFolders, fetch_face_library, predict, EVA_DIR

# Constant
MAX_PROCESS = 12  # cpu_count()
BUFFER_SIZE = 60

fontpath = "./wt002.ttf"
font = ImageFont.truetype(fontpath, 12)
library = fetch_face_library()


def process_frame(frame):
    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = frame[:, :, ::-1]

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(
        rgb_frame, face_locations, model="large")

    face_names = []
    predictions = predict(face_encodings, library)
    for prediction in predictions:
        face_names.append(prediction['name'])

    # Label the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        if not name:
            continue

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        frame = draw_text(frame, name, left + 10, bottom + 10)
    return frame, face_locations, face_names


def draw_text(frame, name, pos_x, pos_y):
    # Add text
    img_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(img_pil)
    draw.text((pos_x, pos_y),  name,
              font=font)  # fill=(0, 0, 255, 0)
    frame = np.array(img_pil)
    return frame


def process_frame_buffer(frame_buffer):
    with Pool(MAX_PROCESS) as p:  # multi-process pool size
        results = p.map(
            process_frame, frame_buffer)
        frame_array = []
        locations_array = []
        names_array = []
        for res in results:
            frame_array.append(res[0])
            locations_array.append(res[1])
            names_array.append(res[2])
        for frame, locations, names in zip(frame_array, locations_array, names_array):
            output_movie.write(frame)


# ========== main ==========
if __name__ == '__main__':

    # Open the input movie file
    input_movie = cv2.VideoCapture("video.mp4")
    length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))
    v_width = int(input_movie.get(cv2.CAP_PROP_FRAME_WIDTH))
    v_height = int(input_movie.get(cv2.CAP_PROP_FRAME_HEIGHT))
    v_fps = int(input_movie.get(cv2.CAP_PROP_FPS))

    # Create an output movie file (make sure resolution/frame rate matches input video!)
    fourcc = cv2.VideoWriter_fourcc(*'AVC1')
    output_movie = cv2.VideoWriter(
        'output.mp4', fourcc, v_fps, (v_width, v_height))

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    frame_number = 0

    frame_buffer = []
    while True:
        # Grab a single frame of video
        ret, frame = input_movie.read()
        frame_number += 1

        # Quit when the input video file ends
        if not ret or frame_number > 300:
            if len(frame_buffer):
                process_frame_buffer(frame_buffer)
                frame_buffer = []
                print("Writing frame {} / {}".format(frame_number, length))
            break

        frame_buffer.append(frame)
        if len(frame_buffer) == BUFFER_SIZE:
            process_frame_buffer(frame_buffer)
            frame_buffer = []
            print("Writing frame {} / {}".format(frame_number, length))

        # Write the resulting image to the output video file

    # All done!
    input_movie.release()
    cv2.destroyAllWindows()
