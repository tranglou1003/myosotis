
import uvicorn
from vietvoicetts.api.app import create_app
from vietvoicetts.api.models import AppConfig


def main():
    """Main entry point"""
    config = AppConfig(reload=False)  # Explicitly disable reload for production
    app = create_app(config)
    
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        reload=config.reload,
        workers=config.workers if not config.reload else 1,
        log_level=config.log_level
    )


if __name__ == "__main__":
    main()
