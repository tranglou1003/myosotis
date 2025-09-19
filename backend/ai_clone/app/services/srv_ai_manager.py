"""
AI Manager Service - Manages conda environment execution and AI services
"""

import asyncio
import subprocess
import tempfile
import os
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class AIManager:
    """Manages AI operations within the Sonic_2 conda environment"""
    
    def __init__(self):
        self.conda_env = "Sonic_2"
        # Use relative paths from the project root
        base_path = Path(__file__).parent.parent.parent.absolute()
        self.voice_clone_path = base_path / "ai_service" / "voiceclone_tts"
        self.sonic_path = base_path / "ai_service" / "Sonic"
        self.temp_dir = base_path / "temp_clone"
        self.public_dir = base_path / "public" / "human_clone"
        
        # Ensure directories exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.public_dir.mkdir(parents=True, exist_ok=True)
    
    async def check_environment(self) -> Dict[str, Any]:
        """Check if the AI environment is properly configured"""
        try:
            logger.info("Checking AI environment...")
            
            # First check if we're in a conda environment
            conda_available = await self._check_conda_available()
            if not conda_available:
                return {
                    "status": "warning",
                    "message": "Conda environment not available - AI features disabled",
                    "conda_environment": "Not available",
                    "cuda_status": "Not checked (conda not available)",
                    "voice_clone_status": "Not available",
                    "sonic_status": "Not available",
                    "ai_features_enabled": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Check conda environment
            conda_check = await self._run_conda_command("python --version")
            if not conda_check["success"]:
                return {
                    "status": "error",
                    "message": "Conda environment not available",
                    "details": conda_check
                }
            
            # Check CUDA availability
            cuda_check = await self._run_conda_command(
                "python -c \"import torch; print('CUDA Available:', torch.cuda.is_available()); print('CUDA Devices:', torch.cuda.device_count())\""
            )
            
            # Check Voice Clone TTS
            voice_clone_check = await self._run_conda_command(
                f"python -c \"import sys; sys.path.append('{self.voice_clone_path}'); from vietvoicetts.high_level_api import synthesize; print('Voice Clone TTS: Available')\""
            )
            
            # Check Sonic
            sonic_check = await self._run_conda_command(
                f"python -c \"import sys; sys.path.append('{self.sonic_path}'); from sonic import Sonic; print('Sonic: Available')\""
            )
            
            return {
                "status": "success",
                "conda_environment": conda_check["stdout"].strip() if conda_check["success"] else "Not available",
                "cuda_status": cuda_check["stdout"].strip() if cuda_check["success"] else "Not available",
                "voice_clone_status": "Available" if voice_clone_check["success"] else f"Error: {voice_clone_check['stderr']}",
                "sonic_status": "Available" if sonic_check["success"] else f"Error: {sonic_check['stderr']}",
                "ai_features_enabled": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Environment check failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Environment check failed: {str(e)}",
                "ai_features_enabled": False,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_conda_available(self) -> bool:
        """Check if conda is available on the system"""
        try:
            process = await asyncio.create_subprocess_shell(
                "which conda",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return process.returncode == 0
        except Exception:
            return False
    
    async def _run_conda_command(self, command: str, timeout: int = 300) -> Dict[str, Any]:
        """Execute a command in the conda environment"""
        try:
            full_command = f"conda run -n {self.conda_env} {command}"
            
            logger.info(f"Executing: {full_command}")
            
            process = await asyncio.create_subprocess_shell(
                full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/app"
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
                
                return {
                    "success": process.returncode == 0,
                    "return_code": process.returncode,
                    "stdout": stdout.decode('utf-8') if stdout else "",
                    "stderr": stderr.decode('utf-8') if stderr else "",
                    "command": full_command
                }
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "success": False,
                    "return_code": -1,
                    "stdout": "",
                    "stderr": f"Command timed out after {timeout} seconds",
                    "command": full_command
                }
                
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            return {
                "success": False,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "command": command
            }
    
    async def run_ai_script(self, script_content: str, script_name: str, timeout: int = 600) -> Dict[str, Any]:
        """Execute a Python script in the conda environment"""
        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=self.temp_dir) as f:
                f.write(script_content)
                script_path = f.name
            
            try:
                # Make script executable
                os.chmod(script_path, 0o755)
                
                # Execute script
                result = await self._run_conda_command(f"python {script_path}", timeout=timeout)
                
                # Add script info to result
                result["script_name"] = script_name
                result["script_path"] = script_path
                
                return result
                
            finally:
                # Clean up script file
                try:
                    os.unlink(script_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary script {script_path}: {e}")
                    
        except Exception as e:
            logger.error(f"Script execution failed: {str(e)}")
            return {
                "success": False,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "script_name": script_name
            }
    
    def create_session_directory(self, session_id: str) -> Path:
        """Create a temporary directory for a processing session"""
        session_dir = self.temp_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir
    
    def cleanup_session(self, session_id: str) -> bool:
        """Clean up temporary files for a session"""
        try:
            session_dir = self.temp_dir / session_id
            if session_dir.exists():
                import shutil
                shutil.rmtree(session_dir)
                logger.info(f"Cleaned up session directory: {session_dir}")
                return True
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup session {session_id}: {e}")
            return False
    
    def get_public_file_url(self, filename: str) -> str:
        """Get the public URL for a generated file"""
        # Remove .mp4 extension if present
        if filename.endswith('.mp4'):
            session_id = filename[:-4]
        else:
            session_id = filename
        return f"/api/v1/videos/download/{session_id}"
    
    async def check_gpu_memory(self) -> Dict[str, Any]:
        """Check available GPU memory"""
        try:
            gpu_check = await self._run_conda_command(
                "python -c \"import torch; print('GPU Memory Free:', torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated()) if torch.cuda.is_available() else print('CUDA not available')\""
            )
            return {
                "success": gpu_check["success"],
                "memory_info": gpu_check["stdout"].strip() if gpu_check["success"] else "Not available"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
