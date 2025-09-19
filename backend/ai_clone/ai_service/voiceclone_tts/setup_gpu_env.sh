#!/bin/bash

echo "Setting up VoiceClone TTS with GPU support for RTX 5090..."

# Activate conda environment
echo "Activating conda environment 'tts'..."
source ~/.bashrc
eval "$(conda shell.bash hook)"
conda activate tts

# Install PyTorch with CUDA 12.8
echo "Installing PyTorch with CUDA 12.8..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 --force-reinstall

# Install other dependencies
echo "Installing project dependencies..."
pip install -r requirements.txt

# Install F5-TTS with latest version
echo "Installing F5-TTS..."
pip install f5-tts --upgrade

# Install additional audio processing libraries
echo "Installing additional audio libraries..."
pip install librosa soundfile scipy

# Test PyTorch CUDA compatibility
echo "Testing PyTorch CUDA compatibility..."
python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'Number of GPUs: {torch.cuda.device_count()}')
    for i in range(torch.cuda.device_count()):
        print(f'GPU {i}: {torch.cuda.get_device_name(i)}')
        print(f'GPU {i} memory: {torch.cuda.get_device_properties(i).total_memory / (1024**3):.1f}GB')
else:
    print('CUDA not available')
"

echo "Setup complete! Environment 'tts' is ready for GPU-accelerated inference."
