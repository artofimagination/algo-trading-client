FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -yqq \
    python3-pip \
    python3-tk \
    git

RUN pip install -U pip
RUN pip install jupyter
# Data science
RUN pip install pandas plotly python-dotenv requests ciso8601 tables flake8 
# GUI modules
RUN pip install pyautogui python-xlib

EXPOSE 8888
