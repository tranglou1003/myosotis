# Voice Clone TTS - Technical Documentation for Coding Agents

## Project Overview

**Voice Clone TTS** is an advanced multilingual Text-to-Speech (TTS) system that supports both Vietnamese and English speech synthesis with voice cloning capabilities. The project provides:

- **Vietnamese TTS**: Using ONNX-optimized models for high-quality Vietnamese speech synthesis
- **English TTS**: Using F5-TTS library for state-of-the-art English speech synthesis  
- **Voice Cloning**: Support for custom voice replication using reference audio
- **Long Text Processing**: Advanced chunking algorithms for processing texts up to 10,000 characters
- **Multilingual Support**: Seamless switching between Vietnamese and English languages
- **Production-Ready API**: FastAPI-based REST API with async processing capabilities

## Architecture Overview

```
voiceclone_tts/
├── vietvoicetts/                    # Main Python package
│   ├── __init__.py                  # Package exports and version
│   ├── high_level_api.py           # High-level API for easy usage
│   ├── cli.py                      # Command-line interface
│   ├── main.py                     # Entry point
│   ├── api/                        # FastAPI application
│   │   ├── app.py                  # FastAPI application factory
│   │   ├── models.py               # Data models and configuration
│   │   ├── routers.py              # API endpoint routers
│   │   ├── services.py             # Business logic services
│   │   └── exceptions.py           # Custom exceptions
│   └── core/                       # Core TTS engine
│       ├── tts_engine.py           # Main TTS synthesis engine
│       ├── model_config.py         # Model configuration
│       ├── model.py                # Model management
│       ├── english_tts_engine.py   # F5-TTS English engine
│       ├── text_processor.py       # Text processing utilities
│       ├── audio_processor.py      # Audio processing utilities
│       ├── advanced_text_processor.py # Advanced chunking algorithms
│       ├── performance_optimizer.py # Performance optimization
│       └── voice_context_manager.py # Voice consistency management
├── f5_tts_repo/                    # F5-TTS submodule for English TTS
├── model_english/                  # English TTS models and samples
├── frontend/                       # React frontend application
├── examples/                       # Usage examples and samples
├── public/                         # Static files and results
├── results/                        # Generated audio outputs
├── uploads/                        # Uploaded reference audio files
├── requirements.txt                # Python dependencies
├── pyproject.toml                 # Python package configuration
└── start_server.py                # Production server startup script
```

## Core Components

### 1. TTS Engine (`vietvoicetts/core/tts_engine.py`)

The main synthesis engine with these key features:

#### **Multilingual Support**
- **Vietnamese**: ONNX-optimized models with gender/area/emotion selection
- **English**: F5-TTS integration for high-quality English synthesis
- **Automatic Language Detection**: Based on configuration and content

#### **Long Text Processing**
- **Smart Chunking**: Intelligent text segmentation with prosody awareness
- **Reference-Length Matching**: Advanced chunking strategy for voice cloning
- **Voice Consistency**: Maintains voice characteristics across chunks
- **Crossfade Synthesis**: Seamless audio concatenation

#### **Key Methods**
```python
def synthesize_long_text_optimized(self, text: str, gender=None, group=None, 
                                 area=None, emotion=None, reference_audio=None, 
                                 reference_text=None, progress_callback=None)
```

```python
def synthesize(self, text: str, gender=None, group=None, area=None, emotion=None,
              reference_audio=None, reference_text=None, output_path=None)
```

### 2. Model Configuration (`vietvoicetts/core/model_config.py`)

Comprehensive configuration system supporting:

#### **Vietnamese Voice Options**
- **Genders**: female, male
- **Groups**: story, news, audiobook, interview, review
- **Areas**: northern, southern, central
- **Emotions**: neutral, serious, monotone, sad, surprised, happy, angry

#### **English Voice Options**
- **Genders**: female, male
- **Groups**: story, news, audiobook, interview, review
- **Accents**: american, british, australian
- **Emotions**: neutral, serious, monotone, sad, surprised, happy, angry

#### **Performance Settings**
```python
class ModelConfig:
    # Processing limits for long text
    max_chunk_duration: float = 20.0
    min_target_duration: float = 1.0
    cross_fade_duration: float = 0.15
    speed: float = 1.0
    random_seed: int = 9527
    sample_rate: int = 24000
    language: str = "vietnamese"  # or "english"
```

### 3. Advanced Text Processing (`vietvoicetts/core/advanced_text_processor.py`)

#### **Smart Chunking Algorithm**
- **Prosody-Aware Segmentation**: Breaks text at natural speech boundaries
- **Context Preservation**: Maintains semantic coherence across chunks
- **Optimal Size Calculation**: Dynamic chunk sizing based on content complexity

#### **Reference-Length Matching Strategy**
- **Activation Threshold**: When target text is 2x+ longer than reference
- **Word Ratio Analysis**: Intelligent chunk size determination
- **Boundary Detection**: Sentence and prosody break point identification

### 4. English TTS Engine (`vietvoicetts/core/english_tts_engine.py`)

F5-TTS integration with these features:

#### **Model Management**
- **Cache System**: Thread-safe model caching for performance
- **Device Selection**: Smart GPU/CPU selection with compatibility testing
- **Local/Remote Models**: Support for local model files or HuggingFace models

#### **Voice Cloning**
- **Reference Audio Processing**: Automatic reference selection based on gender
- **Default References**: Built-in high-quality reference samples
- **Compatibility**: Same interface as Vietnamese TTS for seamless switching

### 5. FastAPI Application (`vietvoicetts/api/`)

Production-ready REST API with:

#### **Endpoints**
- `/api/tts/interactive-voice` - Interactive voice synthesis
- `/api/tts/voice-cloning` - Voice cloning synthesis
- `/api/tts/voice-cloning-file` - File-based voice cloning
- `/api/voices/samples` - Available voice samples
- `/api/health` - Health check and system status

#### **Request Models**
```python
@dataclass
class InteractiveVoiceRequest(SynthesisRequest):
    language: str = "vietnamese"
    gender: str = "female"
    group: str = "story"
    area_or_accent: str = "northern"
    emotion: str = "neutral"
    enable_chunking: bool = True
```

```python
@dataclass
class VoiceCloningRequest(SynthesisRequest):
    use_default_sample: bool = True
    reference_text: Optional[str] = None
    reference_audio_base64: Optional[str] = None
    enable_chunking: bool = True
    voice_consistency: float = 1.0
```

## Development Guidelines

### 1. Adding New Features

#### **New Language Support**
1. Add language to `MODEL_LANGUAGES` in `model_config.py`
2. Create new TTS engine in `core/` following `english_tts_engine.py` pattern
3. Update `tts_engine.py` to route language-specific requests
4. Add language options to API models in `api/models.py`

#### **New Voice Parameters**
1. Add constants to `model_config.py` (e.g., `MODEL_EMOTIONS`)
2. Update validation in API request models
3. Modify engine selection logic in core components
4. Update frontend UI components accordingly

### 2. Performance Optimization

#### **Memory Management**
- Models are cached globally with thread-safe access
- Automatic cleanup after synthesis sessions
- GPU memory monitoring and fallback to CPU
- Session pooling for ONNX models

#### **Processing Optimization**
- Text analysis before processing to choose optimal strategy
- Parallel chunk processing where possible
- Intelligent crossfade duration calculation
- Performance metrics collection and monitoring

### 3. Audio Quality Enhancement

#### **Chunking Quality**
- Prosody-aware boundary detection
- Voice consistency parameters across chunks
- Adaptive crossfade algorithms
- Energy and pitch continuity maintenance

#### **Reference Audio Handling**
- Support for multiple audio formats (WAV, MP3, M4A, FLAC)
- Automatic audio preprocessing and normalization
- Duration and quality validation
- Fallback reference selection

## Common Tasks for Coding Agents

### 1. Adding New Voice Samples

```python
# In model_config.py, add to appropriate language samples:
VIETNAMESE_SAMPLES = {
    "new_sample_id": {
        "audio_path": "path/to/sample.wav",
        "text": "Sample text in Vietnamese",
        "gender": "female",
        "area": "northern",
        "emotion": "neutral"
    }
}
```

### 2. Modifying Synthesis Parameters

```python
# In model_config.py, adjust processing limits:
class ModelConfig:
    max_chunk_duration: float = 25.0  # Increase for longer chunks
    chunking_threshold: int = 1200     # Characters before chunking
    cross_fade_duration: float = 0.2   # Longer crossfade for smoother transitions
```

### 3. API Endpoint Extension

```python
# In api/routers.py, add new endpoint:
@synthesis_router.post("/new-endpoint")
async def new_synthesis_endpoint(
    request: NewRequestModel,
    service: TTSService = Depends(get_tts_service)
):
    try:
        result = service.new_synthesis_method(
            text=request.text,
            # ... other parameters
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 4. Error Handling Enhancement

```python
# In core/tts_engine.py, add robust error handling:
def synthesize_chunk_with_retry(self, chunk, max_retries=3):
    for attempt in range(max_retries):
        try:
            return self.synthesize_chunk(chunk)
        except MemoryError:
            # Reduce chunk size and retry
            chunk = self.reduce_chunk_size(chunk)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff
```

## Testing and Validation

### 1. Model Testing
- Validate model loading for both Vietnamese and English
- Test voice parameter combinations
- Verify audio quality and format consistency
- Performance benchmarking across different text lengths

### 2. API Testing
- Unit tests for all endpoints
- Integration tests for complete synthesis workflows
- Load testing for concurrent requests
- Error scenario testing

### 3. Audio Quality Testing
- Subjective quality evaluation
- Objective metrics (MOS, similarity scores)
- Cross-fade quality assessment
- Voice consistency across chunks

## Deployment Considerations

### 1. Server Configuration
```python
# In start_server.py:
config = AppConfig(
    host="0.0.0.0",
    port=8888,
    reload=False,  # Production stability
    workers=1,     # Single worker for model sharing
    enable_gpu=True,
    max_concurrent_requests=10
)
```

### 2. Model Optimization
- Pre-load models during server startup
- Use model caching for performance
- Monitor GPU memory usage
- Implement graceful degradation to CPU

### 3. Production Monitoring
- Request logging and performance metrics
- Error tracking and alerting
- Audio quality monitoring
- Resource usage monitoring

## Integration Examples

### 1. High-Level API Usage
```python
from vietvoicetts import TTSApi, synthesize

# Simple synthesis
audio, duration = synthesize(
    text="Hello, this is a test in English",
    language="english",
    gender="female"
)

# Voice cloning
audio, duration = synthesize(
    text="Text to synthesize",
    language="vietnamese", 
    reference_audio="reference.wav",
    reference_text="Reference text"
)
```

### 2. Direct Engine Usage
```python
from vietvoicetts.core.tts_engine import TTSEngine
from vietvoicetts.core.model_config import ModelConfig

# Create configuration
config = ModelConfig(language="english")

# Use engine with context management
with TTSEngine(config) as engine:
    audio, time = engine.synthesize_long_text_optimized(
        text="Very long text for processing...",
        reference_audio="ref.wav",
        reference_text="Reference audio text"
    )
```

### 3. API Service Integration
```python
from vietvoicetts.api.services import TTSService
from vietvoicetts.api.models import VoiceCloningRequest

# Create service
service = TTSService()

# Create request
request = VoiceCloningRequest(
    text="Text to synthesize",
    language="vietnamese",
    use_default_sample=False,
    reference_text="Custom reference text",
    reference_audio_base64="base64_encoded_audio"
)

# Process request
result = service.synthesize_voice_cloning(**request.__dict__)
```

## Troubleshooting Guide

### 1. Common Issues

#### **Model Loading Failures**
- Check ONNX runtime installation
- Verify model file paths and permissions
- Ensure sufficient GPU memory
- Check CUDA compatibility

#### **Audio Quality Issues**
- Verify reference audio quality and format
- Check chunking parameters for long text
- Validate crossfade duration settings
- Ensure proper text preprocessing

#### **Performance Issues**
- Monitor GPU memory usage
- Check concurrent request limits
- Optimize chunking strategy
- Consider model caching

### 2. Debug Mode
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debug configuration
config = ModelConfig(debug=True, verbose=True)
```

This documentation provides comprehensive guidance for understanding and modifying the Voice Clone TTS system. The modular architecture allows for easy extension and customization while maintaining high audio quality and performance.
