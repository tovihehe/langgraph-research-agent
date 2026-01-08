# Base Python image (slim version for minimal footprint)
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app/api

# Add the root directory to PYTHONPATH for module resolution
ENV PYTHONPATH="/app"

# Copy dependency file 
COPY ./api/requirements.txt /app/api/requirements.txt
COPY ./requirements.txt /app/requirements.txt

# Install required packages
RUN pip install --no-cache-dir -r /app/api/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the API code into the container
COPY ./api /app/api

# Copy the agents directory into the container
COPY ./agents /app/api/agents

# Copy the config directory into the container
COPY ./config /app/api/config

# Expose the port used by FastAPI
EXPOSE 8000

# Command to start FastAPI using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
