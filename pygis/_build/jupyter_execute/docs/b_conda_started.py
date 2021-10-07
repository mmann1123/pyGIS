#!/usr/bin/env python
# coding: utf-8

# (conda_started)=
# 
# ----------------
# 
# ```{admonition} Learning Objectives
# - Learn the basics of Docker
# - Pull, run, and update a container set up for geospatial modeling
# ```
# ```{admonition} Review
# * [A normal intro to python environments](b_getting_started)
# ```
# ----------------
# 
# # Setting up Python for Geospatial on Mac, Windows, and Linux
# Geospatial analysis requires a pretty broad set of python modules and with it, comes a lot of dependencies. And to be honest, the only thing Python doesn't do well with, is dependencies. Luckily we have a few tricks up our sleeves to help you get to work fast. 
# 
# 
# ## Docker for Geospatial Python - GDAL Included
# Docker allows us to essentially package and share operating systems with specific modifications. Importantly for us this includes libraries and dependencies that are difficult to install otherwise (I'm looking at you GDAL). Before we start you should familiarize yourself with the basic concepts behind Docker, please read the following: [a simple intro to Docker concepts](https://docs.microsoft.com/en-us/dotnet/architecture/microservices/container-docker-introduction/docker-defined)
# 
# To get this done we will be accessing [DockerHub](https://hub.docker.com/), which allows coders like us to store their Docker images. We will be downloading an image of the Linux operating system (Ubuntu, which is "debian-based"), that already has GDAL built for us. Once we "pull" a copy of the image of this operating system we will open it as "a container". This "container" is a running instance of the "image" that we can run our applications on, and customize for our use case.  Read some more on ["images" vs "containers" etc here](https://docs.microsoft.com/en-us/dotnet/architecture/microservices/container-docker-introduction/docker-containers-images-registries).
# 
# ### Install Docker
# Follow the instructions for installing Docker on your system, take your time, and make sure you understand what you are doing before you do it!
# 
# 
# ````{tabbed} Mac
# ```python
# https://docs.docker.com/desktop/mac/install/
# ```
# ````
# ````{tabbed} Windows
# ```python
# https://docs.docker.com/desktop/windows/install/
# ```
# ````
# ````{tabbed} Linux
# ```python
# # click on your platform
# https://docs.docker.com/engine/install/#server
# ```
# ````
# 
# ### Pull and Run a Linux Image with GDAL
# Now we are going to get an Ubuntu image running that already has GDAL installed. We are going to pull the lastest build of our image from [OSGEO's docker hub page](https://github.com/OSGeo/gdal/tree/master/gdal/docker).
# 
# First open a terminal or powershell, type the following:
# 
# ````{tabbed} Mac
# ```
# # download the image
# docker pull osgeo/gdal:ubuntu-full-latest
# 
# # list your images 
# docker images -a 
# 
# # run osgeo/gdal image, but link my volume /your_folder_to_share_with_image:/location_on_container_to_access_it
# # here I am linking my <user_name> home folder to the containers home folder
# # important: update the <user_name> portion with your windows user name
# docker run -v /Users/<user_name>:/home  -it osgeo/gdal:ubuntu-full-latest
# ```
# ````
# ````{tabbed} Windows
# ```
# # download the image
# docker pull osgeo/gdal:ubuntu-full-latest
# 
# # list your images 
# docker images -a 
# 
# # run osgeo/gdal image, but link my volume /your_folder_to_share_with_image:/location_on_container_to_access_it
# # here I am linking my <user_name> home folder to the containers home folder
# # important: update the <user_name> portion with your windows user name
# docker run -v C:/Users/<user_name>:/home  -it osgeo/gdal:ubuntu-full-latest
# ```
# ````
# ````{tabbed} Linux
# ```
# # download the image
# sudo docker pull osgeo/gdal:ubuntu-full-latest
# 
# # list your images 
# sudo docker images -a 
# 
# # Run osgeo/gdal image, but link my volume /your_folder_to_share_with_image:/location_on_container_to_access_it
# # here I am linking my home folder to the containers home folder
# sudo docker run -v /home:/home  -it osgeo/gdal:ubuntu-full-latest
# ```
# ````
# 
# Your command prompt in the terminal window should now say something funny like `root@b0c5ab799195:/# `. You are now INSIDE your running docker container, which is running Ubuntu linux. 
# 
# Just to demonstrate this is really linux, let's ask the system what OS is running:
# ````{tabbed} Linux Container
# ```
# uname
# ```
# ````
# We will need to update/upgrade the OS, install pip and a few other applications we need, pip install geowombat, and a few more python dependancies for it. We will then exit the container and save a named copy of it. 
# 
# ````{tabbed} Linux Container
# ```
# # update Ubuntu
# apt update -y 
# apt upgrade -y
# 
# # install pip and a few other things 
# apt install python3-pip git gdal-bin libgdal-dev libspatialindex-dev   -y 
# 
# # install geowombat and with it geopandas, rasterio etc
# pip install git+https://github.com/jgrss/geowombat
# 
# # install a few more dependancies for geowombat, including jupyter notebooks
# pip install cython numpy retry requests opencv-python notebook
# 
# #test and exit - this should print the version of geowombat installed
# python -c "import geowombat as gw;print(gw.__version__)"
# exit
# ```
# ````
# Note that we are now in your boring old terminal/shell, we exited Ubuntu. 
# 
# We now need to create a named image that includes geowombat etc. Without doing this, the next time we start the osgeo/gdal image nothing will have been saved. 
# 
# ````{tabbed} Mac 
# ```
# # list all available containers
# docker ps -a
# 
# # find the "CONTAINER ID" of the container that was just exited seconds ago, 
# # and replace the example ID used below
# 
# # commit changes to new named image
# docker commit 9c3f33afcff9 geowombat
# 
# # list all available images, look for geowombat.
# docker images
# ```
# ````
# ````{tabbed} Windows
# ```
# # list all available containers
# docker ps -a
# 
# # find the "CONTAINER ID" of the container that was just exited seconds ago, 
# # and replace the example ID used below
# 
# # commit changes to new named image
# docker commit 9c3f33afcff9 geowombat
# 
# # list all available images, look for geowombat.
# docker images
# ```
# ````
# ````{tabbed} Linux 
# ```
# # list all available containers
# sudo docker ps -a
# 
# # find the "CONTAINER ID" of the container that was just exited seconds ago, 
# # and replace the example ID used below
# 
# # commit changes to new named image
# sudo docker commit 9c3f33afcff9 geowombat
# 
# # list all available images, look for geowombat.
# sudo docker images
# 
# # if you want to stop typing "sudo" before docker run the following, and log out of your computer
# sudo usermod -aG docker $USER
# ```
# ```` 
# 
# Ok, now we are getting somewhere. We have created a new image called "geowombat" that should have everything we need to get this done! Now the problem is how to access it?!
# 
# ```{note} 
# Keep in mind if you want to make changes to the Geowombat image you will need to first run it via the command line, make your changes, and then 'commit' or save another named version (ideally with a different name)
# ```
# 
# ### Access your geospatial python image 
# There are two ways to access this 1) through the command-line and 2) through Jupyter Notebooks. 
# 
# Let's start with command line only access. Note that this is almost exactly how we ran the osgeo/gdal image, except we replaced its name with geowombat. *Don't forget to replace `<user_name>` with your user name!*
# 
# ````{tabbed} Mac
# ```
# docker run -v /Users/<user_name>:/home  -it geowombat
# python
# ```
# ````
# ````{tabbed} Windows
# ```
# docker run -v C:/Users/<user_name>:/home  -it geowombat
# python
# ```
# ````
# ````{tabbed} Linux
# ```
# sudo docker run -v /home:/home  -it geowombat
# python
# ```
# ````
# Now you are at the python command prompt, start coding!
# 
# 
# Alternatively, we can access python through jupyter notebooks ([read about jupyter notebooks here](https://coderefinery.github.io/jupyter/motivation/)). Jupyter is probably the easiest way to start your coding. 
# 
# To do this we are going to 
# 
# ````{tabbed} Mac
# ```
# # Or if browser is  present
# sudo docker run -v /Users/<user_name>:/home  -it -p 8888:8888 geowombat
# jupyter notebook --ip 0.0.0.0  --allow-root
# 
# # or if the jupyter notebooks doesn't launch automatically
# sudo docker run -v C:/Users/<user_name>:/home  -it -p 8888:8888 geowombat
# jupyter notebook --ip 0.0.0.0 --no-browser --allow-root
# # THEN control click on URL printed to the bottom of terminal
# ```
# ````
# ````{tabbed} Windows
# ```
# # Or if browser is  present
# sudo docker run -v /home:/home  -it -p 8888:8888 geowombat
# jupyter notebook --ip 0.0.0.0  --allow-root
# 
# # or if the jupyter notebooks doesn't launch automatically
# sudo docker run -v /home:/home  -it -p 8888:8888 geowombat
# jupyter notebook --ip 0.0.0.0 --no-browser --allow-root
# # THEN control click on URL printed to the bottom of terminal
# ```
# ````
# 
# ````{tabbed} Linux
# ```
# # Iff browser is  present
# sudo docker run -v /home:/home  -it -p 8888:8888 geowombat
# jupyter notebook --ip 0.0.0.0  --allow-root
# 
# # or if the jupyter notebooks doesn't launch automatically
# sudo docker run -v /home:/home  -it -p 8888:8888 geowombat
# jupyter notebook --ip 0.0.0.0 --no-browser --allow-root
# # THEN control click on URL printed to the bottom of terminal
# ```
# ````
# Every time you want to run geowombat you are going to `run` the docker container called `geowombat`. 
# 
# ```{warning}
# **When working in your container make sure to store all your data outside of the container!** This is kind of like a school computer, where every time you log out, all the changes you made are deleted. You can save your data in your linked volume which in these examples can be found by typing `cd /home/` while inside your container.
# ```
# 
# To make this a little easier you can create an executable script on your desktop to run it when you want. 
# 
# ````{tabbed} Mac Bash
# ```
# # move to your desktop
# cd ~/Desktop/
# 
# # write a shell script called run_geowombat
# # between the ''s put whatever bash code you want
# echo '
# sudo docker run -v /home:/home  -it -p 8888:8888 geowombat
# jupyter notebook --ip 0.0.0.0  --allow-root
# ' > run_geowombat.sh
# 
# # allow it to be executable
# chmod 755 run_geowombat.sh  
# ```
# ````
# ````{tabbed} Windows
# ```
# # Not sure yet!
# ```
# ````
# 
# ````{tabbed} Linux
# ```
# # move to your desktop
# cd ~/Desktop/
# 
# # write a shell script called run_geowombat
# # between the ''s put whatever bash code you want
# echo '
# sudo docker run -v /home:/home  -it -p 8888:8888 geowombat
# jupyter notebook --ip 0.0.0.0  --allow-root
# ' > run_geowombat.sh
# 
# # allow it to be executable
# chmod +x run_geowombat.sh  
# ```
# ````
# 
# Now that we have an executable file we need to execute this, on linux at least, the only one I can test on, we need to execute it from the command line. But its pretty easy.
# 
# To execute our run_geowombat.sh script we need to navigate to the Desktop, then execute the file:
# 
# ````{tabbed} Mac Bash
# ```
# # move to your desktop
# cd ~/Desktop/
# 
# # execute it
# ./run_geowombat.sh
# ```
# ````
# ````{tabbed} Windows
# ```
# # Not sure yet!
# ```
# ````
# 
# ````{tabbed} Linux
# ```
# # move to your desktop
# cd ~/Desktop/
# 
# # execute it
# ./run_geowombat.sh
# ```
# ````
# 
# When you're done with your work inside the container, and double checked that your data is saved locally - not on the container - you can type `exit` in the terminal window to exit your geowombat container.
