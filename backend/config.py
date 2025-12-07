# backend/config.py

import sys
from pathlib import Path

# PyInstaller (_MEIPASS при запуску .app)
def get_base_dir():
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent

# Основні шляхи
BASE_DIR = get_base_dir()
PROJECT_ROOT = BASE_DIR.parent

# Директорії
PROMPTS_DIR = PROJECT_ROOT / "prompts"
OUTPUT_DIR = PROJECT_ROOT / "output_summaries"
EXTRACTED_DIR = PROJECT_ROOT / "extracted_documents"

# Шляхи до фінального звіту
FINAL_REPORT_PATH = OUTPUT_DIR / "final_report.txt"
FINAL_REPORT_PDF_PATH = OUTPUT_DIR / "final_report.pdf"

# Шлях до моделі (GGUF)
MODEL_PATH = PROJECT_ROOT / "backend" / "llm_models" / "mistral-7b-instruct-v0.1.Q4_K_M.gguf"

# Шляхи до шаблонів
PROMPT_FILES = {
    "PJ": PROMPTS_DIR / "pj_old.txt",
    "VC": PROMPTS_DIR / "vc.txt",
    "PV": PROMPTS_DIR / "pv.txt",
    "RECLASS": PROMPTS_DIR / "reclass.txt",
    "UJD": PROMPTS_DIR / "ujd.txt",
    "TLL": PROMPTS_DIR / "tll.txt",
    "UNKNOWN": PROMPTS_DIR / "unknown.txt",
}

# Налаштування Ollama (не використовується якщо llama-cpp)
OLLAMA_MODEL = "mistral"
OLLAMA_HOST = "http://localhost:11434"

# Максимальна довжина тексту на chunk
MAX_CHARS_PER_CHUNK = 5000
