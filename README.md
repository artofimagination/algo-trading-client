# py-algo-trading-client
Python based algo trading client, that allows to accomodate trading/signalling algorithms. 
At the moment it allows only connection to Binance platform, but feel free to implement your own wrapper.
!!This repo is under heavy development at the moment!!

# Setup
This setup assumes that VS code and docker are installed.

VS Code steps:
 - Install extensions Docker (Microsoft), Remote-containers (Microsoft)
 - Click in the green area in the bottom left corner (Open a Remote Window)
 - Don't forget to set your API keys in a freshly created ```.env``` file see ```.env.example``` as an example
 - NEVER PUSH THE ```.env``` IN YOUR REMOTE REPO. (I added it to gitignore to make it harder :) )
 - Reopen in container (Select from Dockerfile)
 - Run ```xhost local:docker``` in the host command line (this will allow the GUI forwarding from the container)
 - If all goes well, you just need press F5 and it should start build and then the application with Debug.

Jupyter notebook:
 - If you are using VS Code as well, just run ```jupyter notebook --allow-root``` in the VS Code terminal once the above steps are done
 - If you want to use the container but not VSCode run the following:
    - ```docker build -f Dockerfile -t trading_env:latest .```
    - ```docker run -it --env-file .env -p 8888:8888 -e DISPLAY=$DISPLAY -v /var/run/docker.sock:/var/run/docker.sock -v /tmp/.X11-unix:/tmp/.X11-unix trading_env:latest jupyter notebook --allow-root --no-browser --ip=0.0.0.0```

# How to use
Please open the ```tutorial.ipynb``` jupyter file to learn more.

There are various functions to support building a bot, please checkout ```api.ipynb``` for more info. (This doc is yet incomplete)
