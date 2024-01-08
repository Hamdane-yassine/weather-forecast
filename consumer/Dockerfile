# Specify the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the consumer and database client files to the working directory
COPY consumer.py .
COPY database.py .
COPY __init__.py .

# Install the required dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the entrypoint command
CMD ["python", "consumer.py"]
