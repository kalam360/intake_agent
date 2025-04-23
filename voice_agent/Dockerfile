FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy requirements
COPY pyproject.toml ./

# Install Python dependencies
RUN uv pip install -e .

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 8000

# Start the application
CMD ["python", "main.py"]
