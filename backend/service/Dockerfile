FROM python:3.12-slim

WORKDIR /app

# Cài dependencies cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy code
COPY . .

# Cài Python packages
RUN pip install --no-cache-dir -r requirements.txt

CMD ["alembic", "upgrade", "head"]
