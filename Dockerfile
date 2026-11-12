# Build stage
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production runtime stage
FROM python:3.11-slim
WORKDIR /app

# Create a non-privileged user and group with a proper home directory
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -m -s /bin/bash appuser

# Copy installed python dependencies from builder to appuser's home
COPY --from=builder /root/.local /home/appuser/.local
COPY . /app

# Fix ownership for both the app directory and the user's home directory
RUN chown -R appuser:appuser /app /home/appuser

# Switch to non-root user
USER appuser

# Update PATH for user binary installations
ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]