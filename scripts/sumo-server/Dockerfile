# Use Ubuntu as the base image
FROM ubuntu:20.04

# Set environment variables
ENV SUMO_HOME /usr/share/sumo
ENV DEBIAN_FRONTEND=noninteractive
ENV FLASK_APP sumo-server.py
ENV FLASK_RUN_HOST 0.0.0.0

# Update and install SUMO and Python
RUN apt-get update && apt-get install -y \
    sumo \
    sumo-tools \
    sumo-doc \
    python3 \
    python3-pip

# Copy requirements.txt and sumo-server.py, and install Python packages
COPY requirements.txt .
COPY sumo-server.py .
RUN pip3 install -r requirements.txt

# Set the SUMO_HOME environment variable in the container
ENV SUMO_HOME /usr/share/sumo

# Run Flask when the container is started
CMD ["flask", "run"]