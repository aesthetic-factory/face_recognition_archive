FROM python:3.8.2-slim-buster
LABEL maintainer="tragedyhk <alex99hk@gmail.com>"

# Install basic CLI tools etc.
RUN apt-get update && apt-get install -y --fix-missing --no-install-recommends \
        build-essential \
        cmake \
        git-core \
        software-properties-common
        

# Install Python packages
RUN pip3 install --upgrade setuptools
RUN pip3 install face_recognition numpy opencv-python argparse psycopg2 prettytable

# Clean up commands
RUN apt-get autoremove -y && apt-get clean && \
    rm -rf /usr/local/src/*

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR "/root"
CMD ["/bin/bash"]

# Sample commands to use docker

# Build image
# docker build -t face_recognition . --no-cache

# Run a container
# docker run -it --name faceRecognition -v ~/Dev/face_recognition:/root/project face_recognition

# Stop container
# docker container stop faceRecognition

# Restart and attach container
# docker restart faceRecognition
# docker attach faceRecognition

# Remove docker
# docker container rm faceRecognition

# Remove image
# docker image rm face_recognition

