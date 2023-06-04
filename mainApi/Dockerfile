FROM python:3.8-slim

# FROM nvcr.io/nvidia/tensorflow:22.02-tf2-py3
# FROM tensorflow/tensorflow:1.6.0-gpu-py3
# set env variables
# FROM nvidia/cuda:11.5.0-base-ubuntu20.04

# RUN apt update
# RUN apt-get install -y python3 python3-pip

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ENV NVIDIA_VISIBLE_DEVICES all
# ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

# additional dependencies
# netcat used for checking for resources on the network before start, see start.sh for use
RUN apt-get update && \
    apt-get install -y netcat

# Install dependencies to solve dependency bug: openslide
RUN apt-get install -y openslide-tools && \
    apt install -y build-essential && \
    apt install -y default-jdk && \
    pip install --upgrade pip \
    pip install openslide-python \
    pip install numpy

WORKDIR /app

COPY ./mainApi/requirements.txt /app/requirements.txt

RUN pip install --upgrade -r /app/requirements.txt

EXPOSE 8000

COPY ./mainApi /app/mainApi/

RUN chmod -R 777 /app/mainApi/app/static

## Copy shared
COPY ./docker_compose_libs/shared_utils/ /app/shared_utils/
COPY ./docker_compose_libs/celery_tasks/ /app/celery_tasks/


