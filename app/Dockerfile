# Flask OpenCV DeepLearning Image
FROM continuumio/miniconda3:latest

# Working directory
WORKDIR /app

# Create the environment:
# COPY ["./app/boot.sh", "./app/environment.yml", "./app/wsgi.py", "./"]
COPY ["./boot.sh", "./environment.yml", "./wsgi.py", "./"]
# COPY ./app/src* ./src
COPY ./src* ./src
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
RUN echo "conda activate timeTracker" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]

RUN apt-get update && apt-get install --no-install-recommends -y \
    ffmpeg \
    libsm6 \
    libxext6 \
&& rm -rf /var/lib/apt/lists/*

# Demonstrate the environment is activated:
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"

# Expose port 
EXPOSE 5000

RUN chmod +x boot.sh

# User to security practice
# RUN useradd notroot
# USER notroot

# The code to run when container is started:
ENTRYPOINT ["./boot.sh"]