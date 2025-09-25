"""
Simple script to run the FastAPI server
"""

import uvicorn
from config import Config

if __name__ == "__main__":
    uvicorn.run(
        "main_updated:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True,
        log_level=Config.LOG_LEVEL.lower()
    )
