# Dockerfile for AI Human Clone Service 
FROM nvidia/cuda:12.8.0-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    curl \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install cuDNN 8 for CUDA 12.8 from existing NVIDIA CUDA repository
RUN apt-get update \
    && apt-get install -y --no-install-recommends libcudnn8 libcudnn8-dev libcudnn8-samples \
    && apt-mark hold libcudnn8 libcudnn8-dev libcudnn8-samples \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
ENV CONDA_DIR=/opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -b -p $CONDA_DIR \
    && rm /tmp/miniconda.sh
ENV PATH=$CONDA_DIR/bin:$PATH

# Initialize conda
RUN conda init bash

# Copy the packed environment 
COPY sonic2_env.tar.gz /tmp/sonic2_env.tar.gz

# Create environment directory and extract the packed environment
RUN mkdir -p $CONDA_DIR/envs/Sonic_2 \
    && cd $CONDA_DIR/envs/Sonic_2 \
    && tar -xzf /tmp/sonic2_env.tar.gz \
    && rm /tmp/sonic2_env.tar.gz

# Set environment variables
ENV CONDA_DEFAULT_ENV=Sonic_2
ENV PATH=$CONDA_DIR/envs/Sonic_2/bin:$PATH
ENV PYTHONHTTPSVERIFY=0

# Set working directory
WORKDIR /app
# Copy source code
COPY . /app


RUN pip install f5-tts

RUN pip install git+https://github.com/SWivid/F5-TTS.git

RUN python -c "import f5_tts; print('successfully')"

WORKDIR /app

# Expose port
EXPOSE 8779

# Default command
CMD ["conda", "run", "-n", "Sonic_2", "python", "-u", "app/ai_worker.py"]



