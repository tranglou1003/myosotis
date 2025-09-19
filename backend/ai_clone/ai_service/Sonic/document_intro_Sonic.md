# SONIC PROJECT - CODING AGENT DOCUMENTATION

## Tổng quan dự án

**Sonic** là một AI model chuyên tạo video từ ảnh tĩnh và âm thanh (Audio-to-Video Generation). Dự án sử dụng các công nghệ tiên tiến như Stable Video Diffusion, CLIP, Whisper và RIFE để tạo ra những video chân thực với chuyển động môi và biểu cảm khuôn mặt đồng bộ với âm thanh đầu vào.

## Cấu trúc thư mục

```
Sonic/
├── sonic.py                    # Core class và logic chính
├── gradio_app.py              # Giao diện web Gradio
├── demo.py                    # Script demo command line
├── demo.sh                    # Shell script để chạy demo
├── requirements.txt           # Dependencies Python
├── README.md                  # Hướng dẫn cài đặt
├── config/
│   └── inference/
│       └── sonic.yaml         # Cấu hình inference
├── src/                       # Source code chính
│   ├── models/               # Định nghĩa models
│   ├── pipelines/            # Pipeline xử lý
│   ├── utils/                # Utilities và helpers
│   └── dataset/              # Data processing
├── checkpoints/              # Pre-trained models
│   ├── Sonic/               # Model weights chính
│   ├── stable-video-diffusion-img2vid-xt/
│   ├── whisper-tiny/        # Whisper ASR model
│   ├── RIFE/                # Frame interpolation
│   └── yoloface_v5m.pt      # Face detection
├── examples/                 # Ảnh và audio mẫu
│   ├── image/
│   └── wav/
├── tmp_path/                 # Temporary files
├── res_path/                 # Kết quả output
└── output/                   # Video outputs
```

## Core Components

### 1. Sonic Class (sonic.py)

**Chức năng chính**: Class trung tâm xử lý toàn bộ pipeline từ image + audio → video

**Key Methods**:
```python
__init__(device_id=0, enable_interpolate_frame=True)
```
- Khởi tạo tất cả models cần thiết
- Hỗ trợ CUDA và CPU fallback thông minh
- Load pre-trained weights từ checkpoints

```python
preprocess(image_path, expand_ratio=1.0)
```
- Phát hiện khuôn mặt trong ảnh
- Trả về bounding box để crop
- Sử dụng YOLOv5 face detection

```python
crop_image(input_image_path, output_image_path, crop_bbox)
```
- Crop ảnh theo bbox đã detect
- Chuẩn bị ảnh cho quá trình inference

```python
process(image_path, audio_path, output_path, ...)
```
- Pipeline chính: image + audio → video
- Xử lý audio qua Whisper
- Generate video frames
- Áp dụng frame interpolation (RIFE)
- Merge audio với video cuối cùng

### 2. Models Architecture

**Audio Processing**:
- **Whisper**: Extract audio features từ input audio
- **AudioProjModel**: Project audio features to token space
- **Audio2bucketModel**: Predict motion intensity từ audio

**Video Generation**:
- **UNetSpatioTemporalConditionModel**: Core diffusion model
- **CLIP Image Encoder**: Encode reference image
- **Stable Video Diffusion**: Base video generation pipeline

**Post-processing**:
- **RIFE**: Frame interpolation để tăng FPS
- **Face Detection**: YOLOv5 để crop khuôn mặt

### 3. Configuration (config/inference/sonic.yaml)

```yaml
# Model paths
pretrained_model_name_or_path: "checkpoints/stable-video-diffusion-img2vid-xt"
unet_checkpoint_path: "checkpoints/Sonic/unet.pth"
audio2token_checkpoint_path: "checkpoints/Sonic/audio2token.pth"
audio2bucket_checkpoint_path: "checkpoints/Sonic/audio2bucket.pth"

# Generation parameters
num_inference_steps: 25        # Số bước denoising
n_sample_frames: 25           # Số frames mỗi batch
fps: 12.5                     # Frame rate cơ bản
motion_bucket_scale: 1.0      # Scale chuyển động
audio_guidance_scale: 7.5     # Strength của audio conditioning

# Quality settings
weight_dtype: 'fp16'          # Precision (fp16/fp32)
image_size: 512              # Resolution đầu vào
use_interframe: True         # Bật frame interpolation
```

## APIs và Interfaces

### 1. Command Line Interface (demo.py)

```bash
python demo.py <image_path> <audio_path> <output_path> [options]

Options:
--dynamic_scale: Điều chỉnh cường độ chuyển động (0.5-2.0)
--crop: Tự động crop khuôn mặt
--seed: Random seed cho reproducibility
```

### 2. Gradio Web Interface (gradio_app.py)

**Features**:
- Upload image và audio file
- Slider điều chỉnh dynamic scale
- Preview video output
- Examples gallery
- Real-time processing

**URL**: http://localhost:8081 khi chạy

### 3. Python API

```python
from sonic import Sonic

# Khởi tạo
pipe = Sonic(device_id=0, enable_interpolate_frame=True)

# Xử lý
face_info = pipe.preprocess(image_path, expand_ratio=0.5)
if face_info['face_num'] > 0:
    pipe.crop_image(image_path, crop_path, face_info['crop_bbox'])
    pipe.process(crop_path, audio_path, output_path)
```

## Technical Details

### Audio Processing Pipeline

1. **Audio Loading**: Librosa load audio với sample rate 16kHz
2. **Feature Extraction**: Whisper encoder → hidden states
3. **Temporal Windowing**: Chia audio thành windows 3000 frames
4. **Motion Prediction**: Audio2bucket predicts motion intensity
5. **Token Generation**: AudioProjModel tạo conditioning tokens

### Video Generation Pipeline

1. **Image Preprocessing**: Face detection → crop → resize
2. **CLIP Encoding**: Extract image embeddings
3. **Temporal Conditioning**: Combine image + audio features
4. **Diffusion Process**: UNet generates video frames
5. **Post-processing**: Frame interpolation + audio sync

### Device Compatibility

**CUDA Support**:
- Automatic fallback từ CUDA sang CPU
- Test CUDA availability trước khi sử dụng
- Mixed precision support (fp16/fp32)

**Memory Optimization**:
- Chunked processing cho video dài
- Gradient checkpointing
- Dynamic batch sizing

## Installation & Setup

### Requirements

```bash
# Core dependencies
pip install -r requirements.txt

# Additional modelscope for model download
pip install modelscope
```

### Model Downloads

```bash
# Tạo environment
conda create -n Sonic python=3.10
conda activate Sonic

# Download models qua ModelScope
modelscope download --model zeabur/comfyui-sonic --local_dir checkpoints/comfyui-sonic
modelscope download --model stabilityai/stable-video-diffusion-img2vid-xt --local_dir checkpoints/stable-video-diffusion-img2vid-xt  
modelscope download --model openai-mirror/whisper-tiny --local_dir checkpoints/whisper-tiny
```

### Folder Structure After Setup

```
checkpoints/
├── Sonic/
│   ├── audio2bucket.pth      # Audio to motion model
│   ├── audio2token.pth       # Audio encoder
│   ├── unet.pth             # Main diffusion model
│   └── configuration.json
├── stable-video-diffusion-img2vid-xt/
│   ├── unet/                # SVD UNet weights
│   ├── vae/                 # Video VAE
│   ├── image_encoder/       # CLIP encoder
│   └── scheduler/           # Noise scheduler
├── whisper-tiny/            # Whisper ASR model
├── RIFE/                    # Frame interpolation
│   └── flownet.pkl
└── yoloface_v5m.pt          # Face detection
```

## Usage Examples

### Basic Usage

```python
from sonic import Sonic

# Initialize
sonic = Sonic(device_id=0)

# Process single video
result = sonic.process(
    image_path="examples/image/face.jpg",
    audio_path="examples/wav/speech.wav", 
    output_path="output/result.mp4",
    min_resolution=512,
    inference_steps=25,
    dynamic_scale=1.0
)
```

### Advanced Usage với Custom Parameters

```python
# High quality với nhiều inference steps
sonic.process(
    image_path="portrait.jpg",
    audio_path="audio.wav",
    output_path="high_quality.mp4",
    min_resolution=768,
    inference_steps=50,
    dynamic_scale=1.2,
    keep_resolution=True,
    seed=42
)
```

### Batch Processing

```python
import os
from pathlib import Path

sonic = Sonic(device_id=0)

images_dir = "input_images/"
audio_dir = "input_audio/"
output_dir = "results/"

for img_file in Path(images_dir).glob("*.jpg"):
    for aud_file in Path(audio_dir).glob("*.wav"):
        output_path = f"{output_dir}/{img_file.stem}_{aud_file.stem}.mp4"
        sonic.process(str(img_file), str(aud_file), output_path)
```

## Performance Tuning

### GPU Memory Optimization

```python
# Giảm memory usage
sonic = Sonic(device_id=0, enable_interpolate_frame=False)

# Hoặc điều chỉnh config
config.decode_chunk_size = 4  # Giảm từ 8 xuống 4
config.n_sample_frames = 16   # Giảm batch size
```

### Speed vs Quality Trade-offs

```python
# Fast mode (low quality)
sonic.process(..., inference_steps=10, min_resolution=256)

# Balanced mode  
sonic.process(..., inference_steps=25, min_resolution=512)

# High quality mode
sonic.process(..., inference_steps=50, min_resolution=768)
```

## Error Handling & Debugging

### Common Issues

1. **CUDA Out of Memory**:
```python
# Fallback to CPU hoặc giảm resolution
sonic = Sonic(device_id=-1)  # Force CPU
# hoặc
sonic.process(..., min_resolution=256)
```

2. **No Face Detected**:
```python
face_info = sonic.preprocess(image_path, expand_ratio=0.8)
if face_info['face_num'] == 0:
    print("Không phát hiện được khuôn mặt, thử điều chỉnh expand_ratio")
```

3. **Audio Format Issues**:
```python
# Convert audio về format đúng
from pydub import AudioSegment
audio = AudioSegment.from_file("input.mp3")
audio = audio.set_frame_rate(16000).set_channels(1)
audio.export("converted.wav", format="wav")
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging trong process
sonic.process(..., verbose=True)
```

## Integration Guidelines

### Web Service Integration

```python
from flask import Flask, request, jsonify
import tempfile
import os

app = Flask(__name__)
sonic_model = Sonic(device_id=0)

@app.route('/generate_video', methods=['POST'])
def generate_video():
    image_file = request.files['image']
    audio_file = request.files['audio']
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        img_path = os.path.join(tmp_dir, 'input.jpg')
        aud_path = os.path.join(tmp_dir, 'input.wav')
        out_path = os.path.join(tmp_dir, 'output.mp4')
        
        image_file.save(img_path)
        audio_file.save(aud_path)
        
        result = sonic_model.process(img_path, aud_path, out_path)
        
        if result == 0:
            return send_file(out_path, as_attachment=True)
        else:
            return jsonify({'error': 'Processing failed'}), 500
```

### Docker Integration

```dockerfile
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app

CMD ["python", "gradio_app.py"]
```

## Best Practices

### 1. Input Preprocessing
- Sử dụng ảnh có khuôn mặt rõ ràng, không bị che khuất
- Audio nên có chất lượng tốt, 16kHz sample rate
- Crop ảnh để focus vào khuôn mặt

### 2. Parameter Tuning
- `dynamic_scale`: 0.8-1.2 cho chuyển động tự nhiên
- `inference_steps`: 25-50 cho balance speed/quality
- `min_resolution`: 512 cho most cases, 768 cho high quality

### 3. Production Deployment
- Monitor GPU memory usage
- Implement request queuing
- Cache model weights
- Use async processing cho multiple requests

### 4. Quality Control
- Validate face detection trước khi process
- Check audio length (không quá dài)
- Implement timeout cho long-running requests

## Troubleshooting Guide

### Model Loading Issues
```python
# Check model files exist
import os
checkpoint_dir = "checkpoints/Sonic/"
required_files = ["unet.pth", "audio2token.pth", "audio2bucket.pth"]
for file in required_files:
    if not os.path.exists(os.path.join(checkpoint_dir, file)):
        print(f"Missing: {file}")
```

### Memory Issues
```python
# Monitor GPU memory
import torch
if torch.cuda.is_available():
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    print(f"GPU Used: {torch.cuda.memory_allocated(0) / 1e9:.1f} GB")
```

### Performance Monitoring
```python
import time
start_time = time.time()
result = sonic.process(...)
end_time = time.time()
print(f"Processing time: {end_time - start_time:.2f} seconds")
```

## Future Enhancements

1. **Multi-GPU Support**: Parallel processing trên multiple GPUs
2. **Real-time Processing**: Streaming video generation
3. **Custom Model Training**: Fine-tune trên dataset riêng
4. **Mobile Optimization**: Quantization cho mobile deployment
5. **Cloud Integration**: AWS/GCP deployment scripts

---

**Note**: Document này cung cấp toàn bộ thông tin cần thiết để hiểu và làm việc với Sonic project. Mọi thay đổi code nên tuân theo architecture đã định nghĩa và maintain backward compatibility.
