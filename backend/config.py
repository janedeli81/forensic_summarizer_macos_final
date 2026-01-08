# backend/config.py

import sys
from pathlib import Path


def get_base_dir() -> Path:
    """
    Папка, де лежить backend/ (працює і з PyInstaller .app на macOS).
    """
    return Path(__file__).resolve().parent


BASE_DIR = get_base_dir()
PROJECT_ROOT = BASE_DIR.parent

# --- Директорії проєкту ---
PROMPTS_DIR = BASE_DIR / "prompts"
OUTPUT_DIR = PROJECT_ROOT / "output_summaries"
EXTRACTED_DIR = PROJECT_ROOT / "extracted_documents"

# --- Фінальний звіт (якщо ви ним користуєтесь) ---
FINAL_REPORT_PATH = OUTPUT_DIR / "final_report.txt"
FINAL_REPORT_PDF_PATH = OUTPUT_DIR / "final_report.pdf"

# --- Параметри для TinyLlama офлайн ---
MAX_CHARS_PER_CHUNK = 1800        # було 5000 — робимо менші шматки
N_CTX = 2048                      # безпечно для TinyLlama-1.1B-Chat
MAX_NEW_TOKENS = 180              # короткі виходи
AGGREGATE_GROUP_SIZE = 4          # зводимо групами по 3–4
AGGREGATE_MAX_PARTIALS = 6        # у фіналі враховуємо не більше 6 часткових

# --- Відповідність тип → файл промпта ---
PROMPT_FILES = {
    "PV": PROMPTS_DIR / "pv.txt",
    "VC": PROMPTS_DIR / "vc.txt",
    "RECLASS": PROMPTS_DIR / "reclass.txt",
    "UJD": PROMPTS_DIR / "ujd.txt",
    "PJ": PROMPTS_DIR / "pj_old.txt",
    "TLL": PROMPTS_DIR / "tll.txt",
    "UNKNOWN": PROMPTS_DIR / "unknown.txt",
}

def get_model_path() -> Path:
    """
    Де лежить gguf-модель TinyLlama. Для macOS .app беремо Resources/backend/llm_models/.
    """
    # model_name = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    model_name = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"

    # macOS .app (PyInstaller)
    if getattr(sys, "frozen", False) and sys.platform == "darwin":
        exe_path = Path(sys.executable).resolve()
        contents_dir = exe_path.parent.parent  # .../Contents
        resources_dir = contents_dir / "Resources"
        return resources_dir / "backend" / "llm_models" / model_name

    # Звичайний режим (Windows/macOS із джерельного коду)
    return PROJECT_ROOT / "backend" / "llm_models" / model_name


MODEL_PATH = get_model_path()

# --- Не критично для офлайн-режиму; залишено для сумісності з ollama_client ---
OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_MODEL = "tinyllama"
