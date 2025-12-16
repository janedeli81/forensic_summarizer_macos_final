# backend/config.py

import sys
from pathlib import Path


def get_base_dir() -> Path:
    """
    Return the directory of the backend package (where config.py lives).
    This works both in normal runs and inside a PyInstaller bundle,
    because PyInstaller sets __file__ to the correct location.
    """
    return Path(__file__).resolve().parent


BASE_DIR = get_base_dir()
PROJECT_ROOT = BASE_DIR.parent

# Project directories
PROMPTS_DIR = BASE_DIR / "prompts"  # backend/prompts
OUTPUT_DIR = PROJECT_ROOT / "output_summaries"
EXTRACTED_DIR = PROJECT_ROOT / "extracted_documents"

# Final report paths
FINAL_REPORT_PATH = OUTPUT_DIR / "final_report.txt"
FINAL_REPORT_PDF_PATH = OUTPUT_DIR / "final_report.pdf"

# Prompt templates
PROMPT_FILES = {
    "PJ": PROMPTS_DIR / "pj_old.txt",
    "VC": PROMPTS_DIR / "vc.txt",
    "PV": PROMPTS_DIR / "pv.txt",
    "RECLASS": PROMPTS_DIR / "reclass.txt",
    "UJD": PROMPTS_DIR / "ujd.txt",
    "TLL": PROMPTS_DIR / "tll.txt",
    "UNKNOWN": PROMPTS_DIR / "unknown.txt",
}

# Max characters per chunk
MAX_CHARS_PER_CHUNK = 5000


def get_model_path() -> Path:
    """
    Return the path to the GGUF model.

    - In normal/dev runs: <project_root>/backend/llm_models/<model_name>
    - In macOS .app (PyInstaller bundle): <Contents>/Resources/backend/llm_models/<model_name>
    """
    model_name = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

    # Running from macOS .app bundle
    if getattr(sys, "frozen", False) and sys.platform == "darwin":
        # .../forensic_summarizer.app/Contents/MacOS/forensic_summarizer
        exe_path = Path(sys.executable).resolve()
        contents_dir = exe_path.parent.parent  # -> .../Contents
        resources_dir = contents_dir / "Resources"
        return resources_dir / "backend" / "llm_models" / model_name

    # Normal (dev / Windows / macOS from source)
    return PROJECT_ROOT / "backend" / "llm_models" / model_name


MODEL_PATH = get_model_path()
