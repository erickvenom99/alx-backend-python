# Dockerfile
FROM python:3.10

WORKDIR /usr/src/app

# NEW STEP: Install system dependencies for packages like PyGObject
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    gir1.2-glib-2.0 \
    libgirepository1.0-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --upgrade pip --timeout 600 --retries 10

# The main installation step
RUN pip install --no-cache-dir --timeout 600 --retries 10 -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]