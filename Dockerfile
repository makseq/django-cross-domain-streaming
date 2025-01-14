# Use the official Python 3.12 image from the Docker Hub
FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements-freeze.txt /app/

# Install the dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements-freeze.txt

# Copy the entire project into the container
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Set the CELERY_ENABLED environment variable
ENV CELERY_ENABLED=false

# Command to run the application
CMD ["uvicorn", "core.asgi:application", "--host", "0.0.0.0", "--port", "8000"]