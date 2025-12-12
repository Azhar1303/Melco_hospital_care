import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Primary text model (lightweight, fast)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

# Vision-Language Model for image processing (multimodal)
OLLAMA_VLM_MODEL = os.getenv("OLLAMA_VLM_MODEL", "qwen3-vl:4b")

# LLaVA placeholder for high-memory GPU systems (optional)
OLLAMA_LLAVA_MODEL = os.getenv("OLLAMA_LLAVA_MODEL", "llava:13b")

FIREBASE_CREDENTIAL_PATH = os.getenv("FIREBASE_CREDENTIAL_PATH", "serviceAccount.json")
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")  # set in .env
