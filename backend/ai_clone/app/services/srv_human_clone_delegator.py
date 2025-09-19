"""
Human Clone Service Delegator - Delegates AI processing to AI Worker service
"""

import httpx
import asyncio
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException

from app.schemas.sche_human_clone import HumanCloneRequest, HumanCloneResult
from app.utils.response_formatter import DataResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class HumanCloneDelegatorService:
    """Service that delegates AI processing to the AI Worker microservice"""
    
    def __init__(self):
        # AI Worker service URL from environment or default
        self.ai_service_url = settings.AI_SERVICE_URL
        self.timeout = 300.0  # 5 minutes timeout
        self.poll_interval = 2.0  # 2 seconds between status checks
    
    async def clone_human(self, request: HumanCloneRequest) -> DataResponse[HumanCloneResult]:
        """
        Delegate AI processing to AI Worker service with job queue
        """
        try:
            logger.info("Delegating human clone request to AI Worker service")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Create job in AI worker
                response = await client.post(
                    f"{self.ai_service_url}/ai/human-clone/generate",
                    json=request.dict()
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"AI Worker error: {response.text}"
                    )
                
                job_data = response.json()
                job_id = job_data["job_id"]
                logger.info(f"AI Worker job created: {job_id}")
                
                # Poll for completion
                result = await self._poll_job_completion(client, job_id)
                
                return DataResponse[HumanCloneResult].success(
                    data=HumanCloneResult(**result),
                    message="Human clone generated successfully"
                )
                
        except httpx.RequestError as e:
            logger.error(f"Network error calling AI Worker: {e}")
            # Fallback to local processing if AI Worker unavailable
            return await self._fallback_local_processing(request)
        except Exception as e:
            logger.error(f"Human clone processing failed: {e}")
            return DataResponse[HumanCloneResult].error(
                message=f"AI processing failed: {str(e)}"
            )
    
    async def _poll_job_completion(self, client: httpx.AsyncClient, job_id: str) -> Dict[str, Any]:
        """Poll AI Worker for job completion"""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > self.timeout:
                raise HTTPException(
                    status_code=408, 
                    detail=f"AI processing timeout after {self.timeout} seconds"
                )
            
            # Check job status
            response = await client.get(f"{self.ai_service_url}/ai/human-clone/status/{job_id}")
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to check job status"
                )
            
            status_data = response.json()
            logger.info(f"Job {job_id} status: {status_data['status']}")
            
            if status_data["status"] == "completed":
                return status_data["result"]
            elif status_data["status"] == "failed":
                error_msg = status_data.get("error", "AI processing failed")
                raise HTTPException(status_code=500, detail=error_msg)
            
            # Wait before next poll
            await asyncio.sleep(self.poll_interval)
    
    async def _fallback_local_processing(self, request: HumanCloneRequest) -> DataResponse[HumanCloneResult]:
        """Fallback to local processing if AI Worker is unavailable"""
        logger.warning("AI Worker unavailable, falling back to local processing")
        
        try:
            # Import local human clone service for fallback
            from app.services.srv_human_clone import HumanCloneService
            
            local_service = HumanCloneService()
            
            # Check if local AI environment is available
            health_status = await local_service.get_health_status()
            if health_status.get("status") != "healthy":
                return DataResponse[HumanCloneResult].error(
                    message="Both AI Worker and local processing are unavailable"
                )
            
            # Process locally
            result = await local_service.clone_human(request)
            
            # Add fallback metadata
            if hasattr(result, 'metadata'):
                result.metadata = result.metadata or {}
                result.metadata["fallback_mode"] = True
                result.message = f"{result.message} (processed locally)"
            
            return DataResponse[HumanCloneResult].success(
                data=result,
                message="Human clone generated successfully (local fallback)"
            )
            
        except Exception as e:
            logger.error(f"Local fallback processing failed: {e}")
            return DataResponse[HumanCloneResult].error(
                message=f"Both AI Worker and local processing failed: {str(e)}"
            )
    
    async def get_environment_status(self) -> Dict[str, Any]:
        """Get AI environment status from worker or local"""
        status = {
            "ai_worker": {"available": False},
            "local": {"available": False}
        }
        
        # Check AI Worker availability
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.ai_service_url}/health")
                if response.status_code == 200:
                    worker_status = response.json()
                    status["ai_worker"] = {
                        "available": True,
                        "status": worker_status
                    }
                    logger.info("AI Worker is available")
        except Exception as e:
            logger.warning(f"AI Worker not available: {e}")
            status["ai_worker"]["error"] = str(e)
        
        # Check local processing availability
        try:
            from app.services.srv_human_clone import HumanCloneService
            local_service = HumanCloneService()
            local_status = await local_service.get_health_status()
            status["local"] = {
                "available": local_status.get("status") == "healthy",
                "status": local_status
            }
            logger.info(f"Local processing status: {local_status.get('status')}")
        except Exception as e:
            logger.warning(f"Local processing not available: {e}")
            status["local"]["error"] = str(e)
        
        # Overall status
        status["overall"] = {
            "available": status["ai_worker"]["available"] or status["local"]["available"],
            "preferred_mode": "ai_worker" if status["ai_worker"]["available"] else "local"
        }
        
        return status
    
    async def get_ai_worker_jobs(self) -> Dict[str, Any]:
        """Get current jobs from AI Worker"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.ai_service_url}/ai/jobs")
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"Failed to get jobs: {response.status_code}"}
        except Exception as e:
            logger.error(f"Failed to get AI Worker jobs: {e}")
            return {"error": str(e)}


# Create singleton instance
human_clone_delegator = HumanCloneDelegatorService()
