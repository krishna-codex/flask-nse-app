# Use official Python image as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files into the container
COPY . .

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Define the default command
CMD ["python", "main.py"]