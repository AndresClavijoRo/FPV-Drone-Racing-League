FROM python:3.10
# Set the working directory in the container to /backend
WORKDIR /backend
# Copy the current directory contents into the container at /backend
COPY . .
# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
# Make port 8000 available to the world outside this container
EXPOSE 8000
# run app
CMD ["gunicorn", "--workers=4" ,"app:app", "--bind", "0.0.0.0:8000"]