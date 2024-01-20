# Use an official Python runtime as the base image
# Specify the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the producer.py file to the container
COPY producer.py .
COPY database.py .
COPY __init__.py .
# For test purposes
COPY current.json .
COPY forecast.json .

# Install the required dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run when the container starts
CMD ["python", "producer.py"]
