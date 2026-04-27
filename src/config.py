import os
from dotenv import load_dotenv

load_dotenv()

CSV_PATH = "data/General_Knowledge_Questions.csv"
OUTPUT_PATH = "outputs/results.csv"

WOLFRAM_APP_ID = os.getenv("WOLFRAM_APP_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
JUDGE_MODEL_NAME = os.getenv("JUDGE_MODEL_NAME", "gpt-4o-mini")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
WOLFRAM_CACHE_TTL_SECONDS = 4 * 60 * 60

DEMO_MODE = os.getenv("DEMO_MODE", "true").strip().lower() in {"1", "true", "yes", "on"}
