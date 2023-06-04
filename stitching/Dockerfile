FROM ubuntu:18.04

# ashlar dependencies

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        build-essential \
        ffmpeg \
        git \
        libfftw3-dev \
        libfftw3-double3 \
        libfftw3-long3 \
        libfftw3-single3 \
        openjdk-11-jdk-headless \
        python3-dev \
        python3-pip \
        python3-tk \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install -q -U \
    cython \
    numpy \
    pip

COPY ./stitching/libs/ashlar /tmp/ashlar/
RUN pip3 install /tmp/ashlar

ENV OMP_NUM_THREADS 4

## end of ashlar build

## start of stitching worker build
WORKDIR /app

COPY ./stitching/requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

## Copy shared utils
COPY ./docker_compose_libs/shared_utils /app/shared_utils/

COPY ./docker_compose_libs/celery_tasks/ /app/celery_tasks/
COPY ./stitching /app

#ENTRYPOINT celery -A stitching.main worker --concurrency=4 --loglevel=info -n stitching_worker.%h
#ENTRYPOINT python3 ./stitching/main.py
