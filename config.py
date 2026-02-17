"""
Configuration management for Multi-Agent Bug Hunter System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration for the bug hunter system"""
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Model Configuration
    PRIMARY_MODEL = "gemini-2.0-flash-exp"
    FALLBACK_MODEL = "gemini-1.5-pro"
    MODEL_TEMPERATURE = 0.1
    MAX_TOKENS = 8192
    
    # MCP Server Configuration
    MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8003")
    MCP_TIMEOUT = 30
    
    # ChromaDB Configuration
    CHROMA_PERSIST_DIR = os.path.join(os.getcwd(), "chroma_db")
    CHROMA_COLLECTION_NAME = "bug_patterns"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # Workflow Configuration
    MAX_ITERATIONS = 10
    SIMILARITY_THRESHOLD = 0.75
    TOP_K_SIMILAR_BUGS = 3
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent
    EXAMPLES_DIR = PROJECT_ROOT / "examples"
    OUTPUT_DIR = PROJECT_ROOT / "output"
    LOGS_DIR = PROJECT_ROOT / "logs"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Create necessary directories
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.EXAMPLES_DIR.mkdir(exist_ok=True)
        
        return True

# Validate configuration on import
Config.validate()
