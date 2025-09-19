"""
Human Clone Service - Main pipeline for Voice Clone TTS + Sonic talking face integration
"""

import asyncio
import base64
import uuid
import logging
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from services.srv_ai_manager import AIManager
from schemas.sche_human_clone import HumanCloneRequest, HumanCloneResult, HumanCloneStatus
from utils.exception_handler import CustomException, ExceptionType

logger = logging.getLogger(__name__)


class HumanCloneService:
    """Service for human cloning AI pipeline (Voice Clone TTS + Sonic talking face)"""
    
    def __init__(self):
        self.ai_manager = AIManager()
        # Use relative paths from the project root
        base_path = Path(__file__).parent.parent.parent.absolute()
        self.temp_dir = base_path / "temp_clone"
        self.public_dir = base_path / "public" / "human_clone"
        
        # Ensure directories exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.public_dir.mkdir(parents=True, exist_ok=True)
    
    async def clone_human(self, request: HumanCloneRequest) -> HumanCloneResult:
        """Main pipeline: reference_audio + image + target_text → talking face video"""
        session_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting human clone process for session: {session_id}")
            
            # Check if AI environment is available
            logger.info("Checking AI environment...")
            env_status = await self.ai_manager.check_environment()
            if not env_status.get("ai_features_enabled", False):
                logger.error(f"AI features not available: {env_status}")
                return HumanCloneResult(
                    session_id=session_id,
                    status=HumanCloneStatus.FAILED,
                    message=f"AI features not available: {env_status.get('message', 'Unknown error')}",
                    metadata={
                        "error": "ai_environment_unavailable",
                        "env_status": env_status
                    }
                )
            
            logger.info("AI environment check passed")
            
            # Step 1: Setup session directory
            logger.info(f"Creating session directory for: {session_id}")
            session_dir = self.ai_manager.create_session_directory(session_id)
            logger.info(f"Session directory created: {session_dir}")
            
            # Step 2: Save input files from base64
            logger.info("Saving input files from base64 data...")
            file_paths = await self._save_input_files(session_dir, request)
            logger.info(f"Input files saved: {list(file_paths.keys())}")
            
            # Step 3: Generate voice clone
            logger.info("Starting voice clone generation...")
            voice_result = await self._generate_voice_clone(session_dir, file_paths, request)
            if not voice_result["success"]:
                logger.error(f"Voice clone failed: {voice_result['stderr']}")
                raise CustomException(f"Voice clone failed: {voice_result['stderr']}")
            logger.info("Voice clone generation completed")
            
            # Step 4: Generate talking face with Sonic
            logger.info("Starting talking face generation...")
            video_result = await self._generate_talking_face(session_dir, file_paths, voice_result, request)
            if not video_result["success"]:
                logger.error(f"Talking face generation failed: {video_result['stderr']}")
                raise CustomException(f"Talking face generation failed: {video_result['stderr']}")
            logger.info("Talking face generation completed")
            
            # Step 5: Move final video to public directory
            logger.info("Finalizing video output...")
            final_video_path = await self._finalize_video(session_id, video_result)
            logger.info(f"Video finalized at: {final_video_path}")
            
            # Step 6: Cleanup temporary files
            logger.info("Cleaning up temporary files...")
            await asyncio.create_task(self._cleanup_session_async(session_id))
            logger.info("Cleanup completed")
            
            logger.info(f"Human clone process completed successfully for session: {session_id}")
            return HumanCloneResult(
                session_id=session_id,
                status=HumanCloneStatus.COMPLETED,
                video_url=self.ai_manager.get_public_file_url(f"{session_id}.mp4"),
                video_filename=f"{session_id}.mp4",
                duration_seconds=self._extract_duration_from_result(video_result),
                processing_time_seconds=self._calculate_processing_time(session_id),
                message="Human clone generated successfully",
                metadata={
                    "language": request.language,
                    "dynamic_scale": request.dynamic_scale,
                    "voice_clone_info": voice_result.get("voice_info", {}),
                    "sonic_info": video_result.get("sonic_info", {})
                }
            )
            
        except Exception as e:
            logger.error(f"Human clone process failed for session {session_id}: {str(e)}")
            # Cleanup on error
            await asyncio.create_task(self._cleanup_session_async(session_id))
            
            if isinstance(e, CustomException):
                raise e
            else:
                raise CustomException(f"Human clone processing failed: {str(e)}")
    
    async def _save_input_files(self, session_dir: Path, request: HumanCloneRequest) -> Dict[str, Path]:
        """Save base64 encoded files to session directory"""
        try:
            file_paths = {}
            
            # Save reference audio
            audio_data = base64.b64decode(request.reference_audio_base64)
            audio_path = session_dir / "reference_audio.wav"
            with open(audio_path, 'wb') as f:
                f.write(audio_data)
            file_paths["reference_audio"] = audio_path
            
            # Save reference image  
            image_data = base64.b64decode(request.image_base64)
            image_path = session_dir / "reference_image.jpg"
            with open(image_path, 'wb') as f:
                f.write(image_data)
            file_paths["reference_image"] = image_path
            
            logger.info(f"Saved input files: {list(file_paths.keys())}")
            return file_paths
            
        except Exception as e:
            logger.error(f"Failed to save input files: {str(e)}")
            raise CustomException(f"Invalid input file data: {str(e)}")
    
    async def _generate_voice_clone(self, session_dir: Path, file_paths: Dict[str, Path], request: HumanCloneRequest) -> Dict[str, Any]:
        """Generate voice clone using vietvoicetts"""
        try:
            output_audio_path = session_dir / "generated_audio.wav"
            
            # Create voice clone script with proper escaping
            reference_text_escaped = request.reference_text.replace('"', '\\"').replace('\n', '\\n')
            target_text_escaped = request.target_text.replace('"', '\\"').replace('\n', '\\n')
            
            # Choose the appropriate synthesis method based on language
            if request.language.lower() == "vietnamese":
                # Use Vietnamese ONNX model
                script_content = f'''
import sys
import os
sys.path.append("/app/ai_service/voiceclone_tts")

try:
    from vietvoicetts.high_level_api import synthesize
    from vietvoicetts.core.model_config import ModelConfig
    
    # Voice synthesis with Vietnamese ONNX model
    print("Starting Vietnamese voice clone synthesis...")
    print("Reference text: {reference_text_escaped}")
    print("Target text: {target_text_escaped}")
    print("Reference audio: {file_paths['reference_audio']}")
    print("Output path: {output_audio_path}")
    print("Language: vietnamese")
    
    # Create Vietnamese config
    tts_config = ModelConfig(language="vietnamese")
    print(f"Using Vietnamese ONNX model")
    print(f"Model path resolved to: {{tts_config.model_path}}")
    
    # Call synthesize with Vietnamese config
    duration = synthesize(
        text="{target_text_escaped}",
        output_path="{output_audio_path}",
        reference_audio="{file_paths['reference_audio']}",
        reference_text="{reference_text_escaped}",
        config=tts_config
    )
    
    print("Vietnamese voice clone completed successfully")
    print(f"Duration: {{duration}} seconds")
    print("Output file: {output_audio_path}")
    
    # Verify output file exists
    if os.path.exists("{output_audio_path}"):
        file_size = os.path.getsize("{output_audio_path}")
        print(f"Output file size: {{file_size}} bytes")
        if file_size > 1000:  # At least 1KB
            print("Vietnamese voice generation successful!")
        else:
            print("Warning: Output file too small, may be corrupted")
    else:
        print("ERROR: Output file not created")
        
except Exception as e:
    print(f"ERROR: {{str(e)}}")
    import traceback
    traceback.print_exc()
'''
            else:
                # Use English F5-TTS model  
                script_content = f'''
import sys
import os
sys.path.append("/app/ai_service/voiceclone_tts")

try:
    from vietvoicetts.high_level_api import synthesize
    from vietvoicetts.core.model_config import ModelConfig
    
    # Voice synthesis with English F5-TTS model
    print("Starting English voice clone synthesis...")
    print("Reference text: {reference_text_escaped}")
    print("Target text: {target_text_escaped}")
    print("Reference audio: {file_paths['reference_audio']}")
    print("Output path: {output_audio_path}")
    print("Language: english")
    
    # Create English config
    tts_config = ModelConfig(language="english")
    print(f"Using English F5-TTS model")
    print(f"Model path resolved to: {{tts_config.model_path}}")
    
    # Call synthesize with English config
    duration = synthesize(
        text="{target_text_escaped}",
        output_path="{output_audio_path}",
        reference_audio="{file_paths['reference_audio']}",
        reference_text="{reference_text_escaped}",
        config=tts_config
    )
    
    print("English voice clone completed successfully")
    print(f"Duration: {{duration}} seconds")
    print("Output file: {output_audio_path}")
    
    # Verify output file exists
    if os.path.exists("{output_audio_path}"):
        file_size = os.path.getsize("{output_audio_path}")
        print(f"Output file size: {{file_size}} bytes")
        if file_size > 1000:  # At least 1KB
            print("English voice generation successful!")
        else:
            print("Warning: Output file too small, may be corrupted")
    else:
        print("ERROR: Output file not created")
        
except Exception as e:
    print(f"ERROR: {{str(e)}}")
    import traceback
    traceback.print_exc()
'''
                
            logger.info("Starting voice clone generation...")
            result = await self.ai_manager.run_ai_script(script_content, "voice_clone", timeout=300)
            
            # Check result and set audio_path
            if result["success"]:
                if output_audio_path.exists():
                    result["audio_path"] = output_audio_path
                    result["voice_info"] = self._parse_voice_output(result["stdout"])
                    logger.info(f"Voice generation successful: {output_audio_path}")
                else:
                    logger.error(f"Voice generation script succeeded but output file not found: {output_audio_path}")
                    result["success"] = False
                    result["stderr"] = f"Output audio file not created: {output_audio_path}. Script stdout: {result.get('stdout', 'No output')}. Script stderr: {result.get('stderr', 'No errors')}"
            else:
                logger.error(f"Voice generation script failed: {result.get('stderr', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Voice clone generation failed: {str(e)}")
            return {
                "success": False,
                "stderr": str(e),
                "stdout": ""
            }
    
    async def _generate_talking_face(self, session_dir: Path, file_paths: Dict[str, Path], voice_result: Dict[str, Any], request: HumanCloneRequest) -> Dict[str, Any]:
        """Generate talking face using Sonic"""
        try:
            crop_path = session_dir / "cropped_face.jpg"
            output_video_path = session_dir / "output_video.mp4"
            
            # Check audio_path from voice_result
            if not voice_result.get("success", False):
                return {
                    "success": False,
                    "stderr": f"Voice generation failed: {voice_result.get('stderr', 'Unknown error')}",
                    "stdout": ""
                }
            
            if "audio_path" not in voice_result:
                return {
                    "success": False,
                    "stderr": "No audio_path in voice generation result",
                    "stdout": ""
                }
            
            audio_path = voice_result["audio_path"]
            
            # Check if audio file exists
            if not os.path.exists(str(audio_path)):
                return {
                    "success": False,
                    "stderr": f"Generated audio file not found: {audio_path}",
                    "stdout": ""
                }
            
            # Create Sonic script
            script_content = f'''
import sys
import os
sys.path.append("/app/ai_service/Sonic")

try:
    from sonic import Sonic
    
    # Initialize Sonic with GPU
    sonic = Sonic(device_id=0, enable_interpolate_frame=True)
    print("Sonic initialized successfully")
    
    # Preprocess image to detect face
    face_info = sonic.preprocess("{file_paths['reference_image']}", expand_ratio=1.0)
    print(f"Face detection completed. Faces found: {{face_info['face_num']}}")
    
    if face_info['face_num'] > 0:
        # Crop face from image
        sonic.crop_image("{file_paths['reference_image']}", "{crop_path}", face_info['crop_bbox'])
        print("Face cropping completed")
        
        # Generate talking face video
        sonic.process(
            "{crop_path}", 
            "{audio_path}", 
            "{output_video_path}", 
            dynamic_scale={request.dynamic_scale}
        )
        print(f"Talking face generation completed")
        print(f"Output video: {output_video_path}")
        
        # Verify output
        if os.path.exists("{output_video_path}"):
            file_size = os.path.getsize("{output_video_path}")
            print(f"Video file size: {{file_size}} bytes")
        else:
            print("ERROR: Output video not created")
    else:
        print("ERROR: No face detected in the reference image")
        
except Exception as e:
    print(f"ERROR: {{str(e)}}")
    import traceback
    traceback.print_exc()
'''
            
            logger.info("Starting talking face generation...")
            result = await self.ai_manager.run_ai_script(script_content, "sonic_talking_face", timeout=600)
            
            # Check result and set video_path
            if result["success"]:
                if output_video_path.exists():
                    result["video_path"] = output_video_path
                    result["sonic_info"] = self._parse_sonic_output(result["stdout"])
                    logger.info(f"Talking face generation successful: {output_video_path}")
                else:
                    logger.error(f"Sonic script succeeded but output file not found: {output_video_path}")
                    result["success"] = False
                    result["stderr"] = f"Output video file not created: {output_video_path}"
            else:
                logger.error(f"Sonic generation script failed: {result.get('stderr', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Talking face generation failed: {str(e)}")
            return {
                "success": False,
                "stderr": str(e),
                "stdout": ""
            }
    
    async def _finalize_video(self, session_id: str, video_result: Dict[str, Any]) -> Path:
        """Move generated video to public directory"""
        try:
            # Check if video_result has success and video_path
            if not video_result.get("success", False):
                raise CustomException(f"Video generation failed: {video_result.get('stderr', 'Unknown error')}")
            
            if "video_path" not in video_result:
                raise CustomException("No video_path in video generation result")
            
            source_path = video_result["video_path"]
            
            # Check if video file exists
            if not os.path.exists(str(source_path)):
                raise CustomException(f"Generated video file not found: {source_path}")
            
            final_filename = f"{session_id}.mp4"
            final_path = self.public_dir / final_filename
            
            # Move video to public directory
            import shutil
            shutil.move(str(source_path), str(final_path))
            
            logger.info(f"Video finalized: {final_path}")
            return final_path
            
        except Exception as e:
            logger.error(f"Failed to finalize video: {str(e)}")
            raise CustomException(f"Failed to save final video: {str(e)}")
    
    async def _cleanup_session_async(self, session_id: str):
        """Async cleanup of session directory"""
        try:
            await asyncio.sleep(1)  # Brief delay to ensure files are released
            self.ai_manager.cleanup_session(session_id)
        except Exception as e:
            logger.warning(f"Session cleanup failed for {session_id}: {e}")
    
    def _parse_voice_output(self, stdout: str) -> Dict[str, Any]:
        """Parse voice generation output for metadata"""
        info = {}
        for line in stdout.split('\n'):
            if "Duration:" in line:
                try:
                    duration_str = line.split("Duration:")[1].strip().split()[0]
                    info["duration_seconds"] = float(duration_str)
                except:
                    pass
            elif "Output file size:" in line:
                try:
                    size_str = line.split("size:")[1].strip().split()[0]
                    info["file_size_bytes"] = int(size_str)
                except:
                    pass
        return info
    
    def _parse_sonic_output(self, stdout: str) -> Dict[str, Any]:
        """Parse Sonic output for metadata"""
        info = {}
        for line in stdout.split('\n'):
            if "Faces found:" in line:
                try:
                    faces_str = line.split("found:")[1].strip()
                    info["faces_detected"] = int(faces_str)
                except:
                    pass
            elif "Video file size:" in line:
                try:
                    size_str = line.split("size:")[1].strip().split()[0]
                    info["video_size_bytes"] = int(size_str)
                except:
                    pass
        return info
    
    def _extract_duration_from_result(self, video_result: Dict[str, Any]) -> Optional[float]:
        """Extract video duration from result"""
        sonic_info = video_result.get("sonic_info", {})
        return sonic_info.get("duration_seconds")
    
    def _calculate_processing_time(self, session_id: str) -> Optional[float]:
        """Calculate total processing time (placeholder for future implementation)"""
        # TODO: Track start/end times for accurate processing time calculation
        return None
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the human clone service"""
        try:
            env_status = await self.ai_manager.check_environment()
            gpu_status = await self.ai_manager.check_gpu_memory()
            
            return {
                "service": "human_clone",
                "status": "healthy" if env_status["status"] == "success" else "unhealthy",
                "environment": env_status,
                "gpu": gpu_status,
                "directories": {
                    "temp_dir": str(self.temp_dir),
                    "public_dir": str(self.public_dir),
                    "temp_exists": self.temp_dir.exists(),
                    "public_exists": self.public_dir.exists()
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "service": "human_clone",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
