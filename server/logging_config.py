import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / "server.log", mode='a')
    ]
)

# Main application logger
logger = logging.getLogger("va_server")
logger.setLevel(logging.DEBUG)

# Uvicorn access logger (to catch all HTTP requests/responses)
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_access.setLevel(logging.INFO)

# Uvicorn error logger
uvicorn_error = logging.getLogger("uvicorn.error")
uvicorn_error.setLevel(logging.INFO)
