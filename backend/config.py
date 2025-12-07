# backend/config.py

import sys
from pathlib import Path


def get_base_dir() -> Path:
    """
    Base dir for resources that йдуть разом із кодом (prompts, тощо).
    Працює і для звичайного запуску, і для PyInstaller (_MEIPASS).
    """
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


BASE_DIR = get_base_dir()
PROJECT_ROOT = BASE_DIR.parent

# Директорії в проекті
PROMPTS_DIR = PROJECT_ROOT / "prompts"
OUTPUT_DIR = PROJECT_ROOT / "output_summaries"
EXTRACTED_DIR = PROJECT_ROOT / "extracted_documents"

# Фінальний звіт
FINAL_REPORT_PATH = OUTPUT_DIR / "final_report.txt"
FINAL_REPORT_PDF_PATH = OUTPUT_DIR / "final_report.pdf"

# Шаблони промптів
PROMPT_FILES = {
    "PJ": PROMPTS_DIR / "pj_old.txt",
    "VC": PROMPTS_DIR / "vc.txt",
    "PV": PROMPTS_DIR / "pv.txt",
    "RECLASS": PROMPTS_DIR / "reclass.txt",
    "UJD": PROMPTS_DIR / "ujd.txt",
    "TLL": PROMPTS_DIR / "tll.txt",
    "UNKNOWN": PROMPTS_DIR / "unknown.txt",
}

# MAX символів на chunk
MAX_CHARS_PER_CHUNK = 5000


def get_model_path() -> Path:
    """
    Повертає шлях до GGUF-моделі.

    - При звичайному запуску (з коду) -> backend/llm_models/...
    - При запуску з .app (PyInstaller) -> inside .app/Contents/Resources/backend/llm_models/...
    """
    model_name = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"

    # Якщо запущено з .app (PyInstaller bundle)
    if getattr(sys, "frozen", False) and sys.platform == "darwin":
        # /.../forensic_summarizer.app/Contents/MacOS/forensic_summarizer
        exe_path = Path(sys.executable).resolve()
        contents_dir = exe_path.parent.parent  # .. / Contents
        resources_dir = contents_dir / "Resources"
        return resources_dir / "backend" / "llm_models" / model_name

    # Звичайний запуск (dev / Windows / macOS з коду)
    return PROJECT_ROOT / "backend" / "llm_models" / model_name


MODEL_PATH = get_model_path()
