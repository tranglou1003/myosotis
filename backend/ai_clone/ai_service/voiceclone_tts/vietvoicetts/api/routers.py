"""
FastAPI routers for TTS endpoints with multilingual and async support
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Depends
from typing import Optional
import base64

from .schemas import (
    HealthResponse, VoiceOptionsResponse, InteractiveVoiceRequest,
    VoiceCloningRequest, SynthesisResponse, ReferenceSamplesResponse,
    ErrorResponse, AsyncJobRequest, AsyncJobResponse, JobStatusResponse
)
from .services import TTSService
from .exceptions import TTSError, ValidationError


def get_tts_service() -> TTSService:
    """Dependency to get TTS service instance"""
    return TTSService()


# Health router
health_router = APIRouter(prefix="", tags=["Health"])


@health_router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="VietVoice TTS API is running"
    )


# Voice options router
voice_router = APIRouter(prefix="/api", tags=["Voice Options"])


@voice_router.get("/voice-options", response_model=VoiceOptionsResponse)
async def get_voice_options(service: TTSService = Depends(get_tts_service)):
    """Get available voice options for interactive voice customization"""
    try:
        options = service.get_voice_options()
        return VoiceOptionsResponse(**options)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@voice_router.get("/reference-samples", response_model=ReferenceSamplesResponse)
async def get_reference_samples(service: TTSService = Depends(get_tts_service)):
    """Get available default reference samples for voice cloning"""
    try:
        samples = service.get_reference_samples()
        return ReferenceSamplesResponse(**samples)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Synthesis router
synthesis_router = APIRouter(prefix="/api", tags=["Speech Synthesis"])


@synthesis_router.post("/interactive-voice", response_model=SynthesisResponse)
async def interactive_voice_synthesis(
    request: InteractiveVoiceRequest,
    service: TTSService = Depends(get_tts_service)
):
    """Interactive Voice Customization - Synthesize speech with customizable voice parameters"""
    try:
        response = service.synthesize_interactive_voice(
            text=request.text,
            language=request.language.value,
            gender=request.gender.value,
            group=request.group.value,
            area_or_accent=request.area_or_accent,
            emotion=request.emotion.value,
            speed=request.speed,
            random_seed=request.random_seed
        )
        return response
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TTSError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@synthesis_router.post("/voice-cloning", response_model=SynthesisResponse)
async def voice_cloning_synthesis(
    request: VoiceCloningRequest,
    service: TTSService = Depends(get_tts_service)
):
    """Voice Cloning - Synthesize speech using reference audio (JSON mode)"""
    try:
        response = service.synthesize_voice_cloning(
            text=request.text,
            language=request.language.value,
            use_default_sample=request.use_default_sample,
            default_sample_id=request.default_sample_id,
            reference_text=request.reference_text,
            reference_audio_base64=request.reference_audio_base64,
            speed=request.speed,
            random_seed=request.random_seed
        )
        return response
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TTSError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@synthesis_router.post("/voice-cloning-upload", response_model=SynthesisResponse)
async def voice_cloning_with_upload(
    text: str = Form(..., description="Text to synthesize"),
    language: str = Form("vietnamese", description="Language selection (vietnamese or english)"),
    reference_text: str = Form(..., description="Reference text for uploaded audio"),
    speed: float = Form(1.0, ge=0.5, le=2.0, description="Speech speed multiplier"),
    random_seed: int = Form(9527, ge=1, le=99999, description="Random seed"),
    reference_audio: UploadFile = File(..., description="Reference audio file"),
    service: TTSService = Depends(get_tts_service)
):
    """Voice Cloning - Synthesize speech using uploaded reference audio file"""
    try:
        # Enhanced validation with detailed error messages
        text = text.strip()
        reference_text = reference_text.strip()
        
        # Text validation with enhanced limits
        if len(text) == 0:
            raise ValidationError("Text không được để trống")
        if len(text) > 10000:  # Increased limit for long text support
            raise ValidationError("Text quá dài! Tối đa 10.000 ký tự cho voice cloning")
        
        # Reference text validation with increased limit
        if not reference_text:
            raise ValidationError("Reference text không được để trống")
        if len(reference_text) > 2000:  # Increased from 1000
            raise ValidationError("Reference text quá dài! Tối đa 2.000 ký tự")
        
        # Text length compatibility check - make it optional warning only
        text_words = len(text.split())
        ref_words = len(reference_text.split())
        
        # Only show warning for very large differences (more than 10x)
        if text_words > 0 and ref_words > 0:
            ratio = max(text_words, ref_words) / min(text_words, ref_words)
            if ratio > 10:
                print(f"Warning: Large text length difference detected. "
                      f"Target: {text_words} words, Reference: {ref_words} words. "
                      f"This may affect voice cloning quality but processing will continue.")
        
        # File validation
        if not reference_audio.filename:
            raise ValidationError("Không có file audio được upload")
        
        # Validate file extension
        allowed_extensions = {'wav', 'mp3', 'm4a', 'flac', 'ogg'}
        file_ext = reference_audio.filename.split('.')[-1].lower()
        if file_ext not in allowed_extensions:
            raise ValidationError(
                f"Định dạng file không được hỗ trợ: .{file_ext}. "
                f"Các định dạng được hỗ trợ: {', '.join(allowed_extensions)}"
            )
        
        # Read and validate file size
        try:
            audio_content = await reference_audio.read()
        except Exception as e:
            raise ValidationError(f"Không thể đọc file audio: {str(e)}")
        
        max_size = 16 * 1024 * 1024  # 16MB
        if len(audio_content) > max_size:
            raise ValidationError(
                f"File audio quá lớn! Kích thước tối đa: 16MB. "
                f"Kích thước hiện tại: {len(audio_content) / (1024*1024):.1f}MB"
            )
        
        # Validate minimum file size
        if len(audio_content) < 1024:  # Less than 1KB
            raise ValidationError("File audio quá nhỏ! Vui lòng upload file audio hợp lệ")
        
        # Validate audio content type
        if not reference_audio.content_type or not reference_audio.content_type.startswith('audio/'):
            # Try to detect by file extension if content type is missing
            valid_audio_types = {
                'wav': 'audio/wav',
                'mp3': 'audio/mpeg', 
                'm4a': 'audio/mp4',
                'flac': 'audio/flac',
                'ogg': 'audio/ogg'
            }
            
            if file_ext not in valid_audio_types:
                raise ValidationError("File không phải là file audio hợp lệ")
        
        # Encode to base64 and validate audio duration
        try:
            import base64
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            
            # Quick audio duration check using simple heuristics
            # This is a rough estimation - more precise duration checking would require audio processing libraries
            estimated_duration_seconds = len(audio_content) / (44100 * 2)  # Rough estimate for 16-bit 44kHz
            
            # Validate audio duration
            from .models import Constants
            if estimated_duration_seconds > Constants.MAX_REFERENCE_AUDIO_DURATION:
                print(f"⚠️  Warning: Reference audio might be too long ({estimated_duration_seconds:.1f}s > {Constants.MAX_REFERENCE_AUDIO_DURATION}s). "
                      f"This may cause slower processing and smaller chunk sizes. Consider using shorter reference audio.")
            elif estimated_duration_seconds < Constants.MIN_REFERENCE_AUDIO_DURATION:
                raise ValidationError(
                    f"Reference audio quá ngắn ({estimated_duration_seconds:.1f}s). "
                    f"Tối thiểu {Constants.MIN_REFERENCE_AUDIO_DURATION}s để đảm bảo chất lượng voice cloning."
                )
        except Exception as e:
            raise ValidationError(f"Không thể xử lý file audio: {str(e)}")
        
        # Call service with enhanced error handling
        try:
            response = service.synthesize_voice_cloning(
                text=text,
                language=language,
                use_default_sample=False,
                reference_text=reference_text,
                reference_audio_base64=audio_base64,
                speed=speed,
                random_seed=random_seed
            )
            
            return response
            
        except Exception as service_error:
            # Enhanced error message for common issues
            error_msg = str(service_error)
            if "ONNXRuntimeError" in error_msg or "cannot broadcast" in error_msg:
                raise TTSError(
                    "Lỗi xử lý voice cloning. Có thể do text và audio reference không tương thích về độ dài hoặc nội dung. "
                    "Vui lòng thử với text ngắn hơn hoặc audio reference phù hợp hơn."
                )
            elif "memory" in error_msg.lower():
                raise TTSError(
                    "Lỗi bộ nhớ trong quá trình xử lý. Vui lòng thử với file audio nhỏ hơn hoặc text ngắn hơn."
                )
            else:
                raise TTSError(f"Lỗi voice cloning: {error_msg}")
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TTSError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Log the full error for debugging
        import traceback
        error_trace = traceback.format_exc()
        print(f"Unexpected error in voice cloning upload: {error_trace}")
        
        raise HTTPException(
            status_code=500, 
            detail=f"Lỗi không mong muốn: {str(e)}"
        )


# Async processing router
async_router = APIRouter(prefix="/api/async", tags=["Async Processing"])


@async_router.post("/interactive-voice", response_model=AsyncJobResponse)
async def async_interactive_voice_synthesis(
    request: InteractiveVoiceRequest,
    service: TTSService = Depends(get_tts_service)
):
    """Submit interactive voice synthesis job for async processing"""
    try:
        if not request.async_processing:
            raise ValidationError("async_processing must be True for async endpoints")
        
        job_response = await service.submit_async_job(
            job_type="interactive_voice",
            request_data=request.dict(),
            priority=request.priority
        )
        return job_response
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TTSError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@async_router.post("/voice-cloning", response_model=AsyncJobResponse)
async def async_voice_cloning_synthesis(
    request: VoiceCloningRequest,
    service: TTSService = Depends(get_tts_service)
):
    """Submit voice cloning job for async processing"""
    try:
        if not request.async_processing:
            raise ValidationError("async_processing must be True for async endpoints")
        
        job_response = await service.submit_async_job(
            job_type="voice_cloning",
            request_data=request.dict(),
            priority=request.priority
        )
        return job_response
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TTSError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@async_router.get("/job-status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    service: TTSService = Depends(get_tts_service)
):
    """Get status of an async processing job"""
    try:
        status_response = await service.get_job_status(job_id)
        return status_response
    except ValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@async_router.delete("/job/{job_id}")
async def cancel_job(
    job_id: str,
    service: TTSService = Depends(get_tts_service)
):
    """Cancel a pending or running job"""
    try:
        result = await service.cancel_job(job_id)
        return {"message": f"Job {job_id} cancelled successfully", "result": result}
    except ValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
