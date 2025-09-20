# Dockerfile
FROM python:3.12-slim

# Install system deps
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /code

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Run server by default
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
