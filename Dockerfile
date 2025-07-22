FROM python:3.9-alpine

# 🧱 Install system dependencies
RUN apk update && apk add --no-cache \
    bash \
    gcc \
    g++ \
    musl-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev \
    chromium \
    chromium-chromedriver \
    make \
    curl \
    jpeg-dev \
    zlib-dev \
    libstdc++ \
    py3-pip

# 🛠 Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 🐍 Set working directory
WORKDIR /app

# 📦 Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🧾 Copy source code
COPY . .

# 🔁 Run the scraper
CMD ["python", "app.py"]
