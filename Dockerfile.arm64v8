# Use Alpine-based Python image
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PATH="/opt/venv/bin:$PATH"

# Install system dependencies including Chromium and ChromeDriver
RUN apk update && apk add --no-cache \
    chromium \
    chromium-chromedriver \
    bash \
    libstdc++ \
    libgcc \
    libx11 \
    libxcomposite \
    libxdamage \
    libxext \
    libxi \
    nss \
    libxcb \
    libxrandr \
    libxfixes \
    libxrender \
    libxtst \
    libc6-compat \
    libjpeg-turbo \
    libpng \
    freetype \
    ttf-freefont \
    mesa-gl \
    dbus \
    alsa-lib \
    build-base \
    && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the source code
COPY app.py .
COPY .env .

# Default command
CMD ["python", "app.py"]






