# backend/model_manager.py

from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path
from typing import Callable, Optional
from urllib.request import Request, urlopen

from backend.config import MODEL_PATH, MODEL_URL, MODEL_SHA256

ProgressCb = Optional[Callable[[str], None]]


def _fmt_bytes(n: int) -> str:
    # Human readable, simple
    gb = 1024 ** 3
    mb = 1024 ** 2
    if n >= gb:
        return f"{n / gb:.2f} GB"
    return f"{n / mb:.1f} MB"


def ensure_model_ready(progress_cb: ProgressCb = None) -> Path:
    """
    Ensure the GGUF model exists at MODEL_PATH (user-writable dir).
    Downloads it on first run into a safe location (NOT inside .app bundle).

    Set FS_OFFLINE=1 to prevent auto-download and raise an error instead.
    """
    model_path = Path(MODEL_PATH)
    model_path.parent.mkdir(parents=True, exist_ok=True)

    # If already present and non-trivial size, return
    if model_path.exists() and model_path.stat().st_size > 10 * 1024 * 1024:
        return model_path

    if os.environ.get("FS_OFFLINE", "").strip() == "1":
        raise RuntimeError(
            f"Model not found at {model_path}. Auto-download disabled (FS_OFFLINE=1)."
        )

    tmp_path = model_path.with_suffix(model_path.suffix + ".part")

    if progress_cb:
        progress_cb(f"LLM model not found. Downloading to: {model_path}")

    req = Request(
        MODEL_URL,
        headers={
            "User-Agent": "ForensicSummarizer/1.0 (model-downloader)",
        },
    )

    hasher = hashlib.sha256() if MODEL_SHA256 else None

    downloaded = 0
    last_update = 0.0
    started = time.time()

    with urlopen(req) as resp:
        total_str = resp.headers.get("Content-Length")
        total = int(total_str) if total_str and total_str.isdigit() else None

        with open(tmp_path, "wb") as f:
            while True:
                chunk = resp.read(4 * 1024 * 1024)  # 4MB
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)

                if hasher:
                    hasher.update(chunk)

                # Progress update (rate-limited)
                now = time.time()
                if progress_cb and (now - last_update) > 0.5:
                    last_update = now
                    if total:
                        pct = int(downloaded * 100 / total)
                        progress_cb(
                            f"Downloading model... {pct}% ({_fmt_bytes(downloaded)} / {_fmt_bytes(total)})"
                        )
                    else:
                        progress_cb(f"Downloading model... {_fmt_bytes(downloaded)}")

    # Verify checksum if provided
    if hasher and MODEL_SHA256:
        digest = hasher.hexdigest().lower()
        expected = MODEL_SHA256.strip().lower()
        if digest != expected:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass
            raise RuntimeError(
                "Downloaded model checksum mismatch. "
                f"Expected {expected}, got {digest}."
            )

    # Atomic replace
    tmp_path.replace(model_path)

    if progress_cb:
        elapsed = time.time() - started
        progress_cb(f"Model download complete. Size: {_fmt_bytes(downloaded)}. Time: {elapsed:.1f}s")

    return model_path
