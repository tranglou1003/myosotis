"""
Quick start script for the refactored VietVoice TTS API
"""

def start_server():
    """Start the refactored VietVoice TTS API server"""
    try:
        # Import here to avoid dependency issues during setup
        import uvicorn
        from vietvoicetts.api.models import AppConfig
        
        # Create configuration from environment or defaults - FORCE reload=False for production
        config = AppConfig(reload=False)
        
        # Start server WITHOUT reload for production stability
        if config.reload:
            # Use import string for reload support
            uvicorn.run(
                "vietvoicetts.api.app:get_app",
                host=config.host,
                port=config.port,
                reload=False,  # Disable reload for production
                log_level=config.log_level,
                factory=True,
                reload_excludes=["results/*", "uploads/*", "*.wav", "*.mp3", "*.m4a"]  # Exclude audio files from reload
            )
        else:
            # Direct app instance for production
            from vietvoicetts.api.app import create_app
            app = create_app(config)
            uvicorn.run(
                app,
                host=config.host,
                port=config.port,
                log_level=config.log_level
            )
        
    except ImportError as e:
        print(f" Missing dependencies: {e}")
    except Exception as e:
        print(f"Error starting server: {e}")


if __name__ == "__main__":
    start_server()
