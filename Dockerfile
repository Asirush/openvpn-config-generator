# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN apt-get update && \
    apt-get install -y openvpn easy-rsa tar && \
    pip install --no-cache-dir -r requirements.txt

# Create a non-root user with specified UID and GID
RUN addgroup --gid 1001 user && \
    adduser --uid 1001 --gid 1001 --disabled-password --gecos "" user

# Switch to the non-root user
USER user

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]

##
# Command to run the application when the container starts
##CMD ["python", "main.py"]
