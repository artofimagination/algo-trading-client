# py-algo-trading-client
Python based algo trading client, to do the money making for you.
At the moment it connects to FTX trading platform, throught the python API.
See the [API doc](https://docs.ftx.us/#overview)
!!This repo is under heavy development at the moment!!

# Setup
The setup is tailored to VS Code, but, if you just fire up the Docker container from the ```Dockerfile```
you can use any IDE.
 
 VS Code steps:
 - Install extensions Docker (Microsoft), Remote-containers (Microsoft)
 - Click in the green area in the bottom left corner (Open a Remote Window)
 - Reopen in container (Select from Dockerfile)
 - If all goes well, you just need press F5 and it should start build and then the application with Debug.
 - Don't forget to set your API keys in a freshly created ```.env``` file see ```.env.example``` as an example
 - NEVER PUSH THE ```.env``` IN YOUR REMOTE REPO. (I added it to gitignore to make it harder :) )

Jupyter notebook:
 - If you are using VS Code as well, just run ```jupyter notebook --allow-root``` in the VS Code terminal once the above steps are done
 - If you want to use the container but not VSCode run the following:
    - ```docker build -f Dockerfile -t trading_env:latest .```
    - ```docker run -it --env-file .env -p 8888:8888 -e DISPLAY=$DISPLAY -v /var/run/docker.sock:/var/run/docker.sock -v /tmp/.X11-unix:/tmp/.X11-unix trading_env:latest jupyter notebook --allow-root --no-browser --ip=0.0.0.0```
