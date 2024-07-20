FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -yqq \
    python3-pip \
    python3-tk \
    git \
    python3-pyqt5.qtopengl \
    python3-pyqt5.qtwebengine \
    x11-apps

RUN pip install -U pip
RUN pip install jupyter
# Data science
RUN pip install pandas plotly python-dotenv requests ciso8601 tables flake8 jdc scipy numpy matplotlib scikit-learn
# GUI modules
RUN pip install pyautogui python-xlib pyqtgraph pyqt5 PyOpenGL
# Cryptograpy
RUN pip install pycryptodome
# clone binance API
RUN git clone https://github.com/binance/binance-connector-python.git /workspaces/algo-trading-client/src/trade_platforms/binance_connector_python
RUN ln -s /workspaces/algo-trading-client/src/trade_platforms/binance_connector_python/binance /workspaces/algo-trading-client/src/binance

EXPOSE 8888
