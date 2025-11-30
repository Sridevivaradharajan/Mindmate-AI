"""Configuration and logging setup for MindMate AI."""

import logging
import os
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mindmate.log') if os.path.exists('.') else logging.NullHandler()
    ]
)

logger = logging.getLogger("mindmate")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
TEMP_DIR = PROJECT_ROOT / "temp"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

try:
    if GOOGLE_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        logger.info("✅ Google AI configured")
    else:
        logger.warning("⚠️ GOOGLE_API_KEY not set - some features may be limited")
except ImportError:
    logger.warning("⚠️ google-generativeai not installed. Install with: pip install google-generativeai")
except Exception as e:
    logger.error(f"❌ Failed to configure Google AI: {e}")

# Model settings
DEFAULT_MODEL = "gemini-2.0-flash-exp"
TEMPERATURE = 0.7
MAX_OUTPUT_TOKENS = 2048

# Feature flags
ENABLE_AUDIO_ANALYSIS = True
ENABLE_IMAGE_ANALYSIS = True
ENABLE_PDF_PROCESSING = True
ENABLE_WEB_SCRAPING = True

# Limits
MAX_FILE_SIZE_MB = 50
MAX_AUDIO_DURATION_SEC = 300
MAX_PDF_PAGES = 50

logger.info("✅ MindMate AI configuration loaded")
