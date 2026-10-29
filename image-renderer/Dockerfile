FROM python:3.13-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir Pillow==11.3.0 \
    && useradd --uid 1000 --create-home renderer

WORKDIR /app
COPY server.py ./

USER renderer
CMD ["python", "server.py"]
