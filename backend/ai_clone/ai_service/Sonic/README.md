Hướng dẫn install:
```
conda create -n Sonic python=3.10
```
```
conda activate Sonic
```
```
pip3 install -r requirements.txt
```
```
pip install modelscope
```
```
modelscope download --model zeabur/comfyui-sonic --local_dir ~/ai_giasu/Sonic/checkpoints/comfyui-sonic
```
```
mkdir -p checkpoints
```
```
modelscope download --model stabilityai/stable-video-diffusion-img2vid-xt --local_dir ~/ai_giasu/Sonic/checkpoints/stable-video-diffusion-img2vid-xt
```
```
modelscope download --model openai-mirror/whisper-tiny --local_dir ~/ai_giasu/Sonic/checkpoints/whisper-tiny
```
Đây là cấu trúc chuẩn:
```
/opt/ai-platform/lldataset/240/modelscope/modelscope/hub/Sonic/
├── RIFE/
│   └── flownet.pkl
├── Sonic/
│   ├── audio2bucket.pth
│   ├── audio2token.pth
│   ├── configuration.json
│   ├── ...
│   └── unet.pth
├── stable-video-diffusion-img2vid-xt/
│   └── ...
├── whisper-tiny/
│   └── ...
└── yoloface_v5m.pt
```