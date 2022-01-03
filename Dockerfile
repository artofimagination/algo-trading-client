FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -yqq \
    python3-pip \
    git

RUN pip install -U pip
RUN pip install jupyter
RUN pip install pandas plotly python-dotenv requests ciso8601