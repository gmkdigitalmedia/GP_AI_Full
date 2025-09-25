# Multi-stage Docker build for MNIST MLOps Pipeline
# Stage 1: Base image with dependencies - Ubuntu 22.04
FROM ubuntu:22.04 as base

# Install Python 3.9 and required packages
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3.9-pip \
    python3.9-venv \
    python3.9-dev \
    git \
    curl \
    build-essential \
    && ln -sf /usr/bin/python3.9 /usr/bin/python3 \
    && ln -sf /usr/bin/python3.9 /usr/bin/python \
    && ln -sf /usr/bin/pip3 /usr/bin/pip \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Development image
FROM base as development

# Install development dependencies
RUN pip install jupyter ipykernel

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p logs artifacts/models artifacts/evaluation data

# Set default command for development
CMD ["python", "main.py", "--config", "config/default_config.yaml"]

# Stage 3: Production image
FROM base as production

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash mlops

# Copy only necessary files
COPY src/ src/
COPY config/ config/
COPY main.py .

# Create necessary directories and set permissions
RUN mkdir -p logs artifacts/models artifacts/evaluation data && \
    chown -R mlops:mlops /app

# Switch to non-root user
USER mlops

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import torch; print('Health check passed')" || exit 1

# Default command
CMD ["python", "main.py", "--config", "config/default_config.yaml"]

# Stage 4: Training image
FROM production as training

# Copy training-specific configurations
COPY config/training_config.yaml config/

# Set environment variables for training
ENV MLOPS_MODE=train
ENV MLOPS_TRAINING_EPOCHS=20
ENV MLOPS_TRAINING_DEVICE=auto

# Command for training
CMD ["python", "main.py", "--config", "config/training_config.yaml", "--mode", "train"]

# Stage 5: Evaluation image
FROM production as evaluation

# Copy evaluation-specific configurations
COPY config/evaluation_config.yaml config/

# Set environment variables for evaluation
ENV MLOPS_MODE=evaluate
ENV MLOPS_EVALUATION_DEVICE=auto

# Command for evaluation
CMD ["python", "main.py", "--config", "config/evaluation_config.yaml", "--mode", "evaluate"]