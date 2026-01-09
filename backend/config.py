# backend/config.py

import os
import sys
from pathlib import Path


def get_base_dir() -> Path:
    """
    Folder where backend/ lives (works both from source and from PyInstaller .app on macOS).
    """
    return Path(__file__).resolve().parent


BASE_DIR = get_base_dir()
PROJECT_ROOT = BASE_DIR.parent

# --- Project directories ---
PROMPTS_DIR = BASE_DIR / "prompts"
OUTPUT_DIR = PROJECT_ROOT / "output_summaries"
EXTRACTED_DIR = PROJECT_ROOT / "extracted_documents"

# --- Final report outputs (if used) ---
FINAL_REPORT_PATH = OUTPUT_DIR / "final_report.txt"
FINAL_REPORT_PDF_PATH = OUTPUT_DIR / "final_report.pdf"

# --- LLM runtime params (keep your current values) ---
MAX_CHARS_PER_CHUNK = 1800
N_CTX = 2048
MAX_NEW_TOKENS = 180
AGGREGATE_GROUP_SIZE = 4
AGGREGATE_MAX_PARTIALS = 6

# --- Mapping: doc type -> prompt file ---
PROMPT_FILES = {
    "PV": PROMPTS_DIR / "pv.txt",
    "VC": PROMPTS_DIR / "vc.txt",
    "RECLASS": PROMPTS_DIR / "reclass.txt",
    "UJD": PROMPTS_DIR / "ujd.txt",
    "PJ": PROMPTS_DIR / "pj_old.txt",
    "TLL": PROMPTS_DIR / "tll.txt",
    "UNKNOWN": PROMPTS_DIR / "unknown.txt",
}

# --- Model download settings (first-run download) ---
# Use the v0.3 file you referenced in the workflow, but you can change it if needed.
MODEL_FILENAME = "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf"

MODEL_URL = (
    "https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/"
    "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf?download=true"
)

MODEL_SHA256 = "1270d22c0fbb3d092fb725d4d96c457b7b687a5f5a715abe1e818da303e562b6"



def get_user_data_dir(app_name: str = "ForensicSummarizer") -> Path:
    """
    Return a writable per-user data directory.

    macOS: ~/Library/Application Support/<app_name>
    Windows: %APPDATA%\\<app_name>
    Linux: ~/.local/share/<app_name>
    """
    home = Path.home()

    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / app_name

    if sys.platform.startswith("win"):
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / app_name
        return home / "AppData" / "Roaming" / app_name

    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / app_name

    return home / ".local" / "share" / app_name


def get_bundled_model_path() -> Path:
    """
    Path to a model bundled inside a PyInstaller macOS .app (legacy builds).
    IMPORTANT: we do NOT want to write into the .app after signing, only read if present.
    """
    if getattr(sys, "frozen", False) and sys.platform == "darwin":
        exe_path = Path(sys.executable).resolve()
        contents_dir = exe_path.parent.parent  # .../Contents
        resources_dir = contents_dir / "Resources"
        return resources_dir / "backend" / "llm_models" / MODEL_FILENAME

    # Source run fallback (if you still keep a local model next to the code)
    return PROJECT_ROOT / "backend" / "llm_models" / MODEL_FILENAME


def get_model_path() -> Path:
    """
    Prefer user-writable model location (for first-run download).
    If user model doesn't exist yet but a bundled model exists, use the bundled one.
    """
    user_models_dir = get_user_data_dir() / "llm_models"
    user_model_path = user_models_dir / MODEL_FILENAME

    if user_model_path.exists():
        return user_model_path

    bundled = get_bundled_model_path()
    if bundled.exists():
        return bundled

    # Default target location for download
    return user_model_path


MODEL_PATH = get_model_path()

# --- Not critical for offline mode; left for compatibility with ollama_client ---
OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_MODEL = "tinyllama"
