FROM python:3.10
#Make upload directory
RUN mkdir -p /srv/upload
# Set the working directory in the container to /backend
WORKDIR /backend

ADD ./requirements.txt /backend/requirements.txt
# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
#Install ffmpeg
RUN apt-get update -y 
RUN apt-get install ffmpeg  -y
# Copy the current directory contents into the container at /backend
ADD . /backend
# Make port 8000 available to the world outside this container
EXPOSE 8000

