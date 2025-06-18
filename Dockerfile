# Gunakan base image Python 3.9 yang kompatibel
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    git \
    gcc \
    python3-dev \
    python3-distutils \
    && apt-get clean

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Jalankan Gunicorn di port Railway
CMD ["gunicorn", "loggingSystem.wsgi:application", "--bind", "0.0.0.0:${PORT}"]
