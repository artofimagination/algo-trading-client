# py-algo-trading-client
Python based algo trading client, to do the money making for you.
At the moment it connects to FTX trading platform, throught the python API.

# Setup
The setup is tayloired to VS Code, but, if you just fire up the Docker container from the ```Dockerfile```
you can use any IDE.
 
 VS Code steps:
 - Install extensions Docker (Microsoft), Remote-containers (Microsoft), Python (Microsoft)
 - Click in the green area in the bottom left corner (Open a Remote Window)
 - Reopen in container (Select from Dockerfile)
 - Run ```xhost local:docker``` in the host command line (this is needed to run the GUI from docker)
 - If all goes well, you just need press F5 and it should start build and then the application with Debug.
 - Don't forget to set your API keys in a freshly created ```.env``` file see ```.env.example``` as an example
 - NEVER PUSH THE ```.env``` IN YOUR REMOTE REPO. (I added it to gitignore to make it harder :) )

