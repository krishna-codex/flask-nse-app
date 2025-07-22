# Use Alpine-based Python image
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies and Chrome headless
RUN apk update && apk add --no-cache \
    bash \
    curl \
    chromium \
    chromium-chromedriver \
    build-base \
    libffi-dev \
    postgresql-dev \
    musl-dev \
    gcc \
    python3-dev \
    freetype-dev \
    openblas-dev \
    jpeg-dev \
    zlib-dev \
    libjpeg \
    libxml2-dev \
    libxslt-dev \
    libressl \
    ttf-freefont \
    && pip install --upgrade pip setuptools wheel

# Set display port (for compatibility with headless Chrome)
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files
COPY . .

# Set ChromeDriver path for Selenium
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Run script
CMD ["python", "app.py"]