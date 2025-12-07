# backend/process_zip.py

import os
import json
import shutil
import zipfile
import tempfile
import re
from pathlib import Path

from backend.text_extraction import extract_text
from backend.classifiers import classify_document
from backend.summarizer import summarize_document

# Import absolute paths from config (cross‑platform + PyInstaller‑safe)
from backend.config import OUTPUT_DIR, EXTRACTED_DIR

# Ensure folders exist
OUTPUT_DIR.mkdir(exist_ok=True)
EXTRACTED_DIR.mkdir(exist_ok=True)


def process_zip(zip_path: Path, output_dir: Path = OUTPUT_DIR, output_format: str = "txt"):
    """
    Process a ZIP archive:
    - extract documents
    - classify each file
    - summarize content
    - save .txt and .json summaries
    - copy original docs to extracted_documents/
    """
    print(f"Start processing ZIP: {zip_path}")

    # Clear old output summaries
    for f in output_dir.glob("*_summary.*"):
        f.unlink()

    # Clear previously extracted documents
    for f in EXTRACTED_DIR.glob("*"):
        f.unlink()

    # Extract ZIP to a temporary folder
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
            print(f"Archive extracted to: {temp_dir}")

        # Process all files inside the temporary folder
        for root, _, files in os.walk(temp_dir):
            for filename in files:
                full_path = os.path.join(root, filename)
                print(f"\nProcessing: {filename}")

                try:
                    # Extract text from document
                    text = extract_text(Path(full_path))
                    if not text:
                        print("Warning: No text extracted.")
                        continue

                    # Classify document type
                    doc_type = classify_document(Path(full_path), text)
                    print(f"Document type: {doc_type}")

                    # Summarize based on type
                    summary = summarize_document(doc_type, text)

                    # Prepare output paths
                    stem = Path(filename).stem
                    txt_path = output_dir / f"{stem}_summary.txt"
                    json_path = output_dir / f"{stem}_summary.json"
                    extracted_copy_path = EXTRACTED_DIR / filename

                    # Save TXT summary
                    txt_path.write_text(summary, encoding="utf-8")

                    # Save JSON summary with metadata
                    json_data = {
                        "filename": filename,
                        "doc_type": doc_type,
                        "workflow": guess_workflow(doc_type),
                        "summary": summary,
                        "meta": extract_basic_meta(text)
                    }
                    json_path.write_text(
                        json.dumps(json_data, indent=2, ensure_ascii=False),
                        encoding="utf-8"
                    )

                    # Save a copy of the original file
                    shutil.copy(full_path, extracted_copy_path)

                    print(f"Saved: {txt_path.name} and {json_path.name}")

                except Exception as e:
                    print(f"Error processing {filename}: {e}")


def guess_workflow(doc_type: str) -> str:
    """Simple mapping from document type to workflow name."""
    mapping = {
        "PJ": "Oude Pro Justitia rapportage",
        "VC": "VC Samenvatter",
        "PV": "PV Samenvatter",
        "RECLASS": "Reclasseringsrapport",
        "TLL": "TLL Generator (obv vordering IBS)",
        "UJD": "Uittreksel Samenvatter",
        "UNKNOWN": "Standaard Samenvatting"
    }
    return mapping.get(doc_type, "Standaard Samenvatting")


def extract_basic_meta(text: str) -> dict:
    """
    Very simple rule-based metadata extraction.
    Can be replaced by an LLM later if needed.
    """
    meta = {}

    m = re.search(r"(?:Verdachte|Betrokkene|Persoon):?\s*(.+)", text, re.IGNORECASE)
    meta["verdachte"] = m.group(1).strip() if m else ""

    m = re.search(r"Geboortedatum:?\s*([\d\-\.]{8,12})", text, re.IGNORECASE)
    meta["geboortedatum"] = m.group(1).strip() if m else ""

    m = re.search(r"Delict:?\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
    meta["delict"] = m.group(1).strip() if m else ""

    m = re.search(r"Advies:?\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
    meta["advies"] = m.group(1).strip() if m else ""

    m = re.search(r"Risico(?:-inschatting)?:?\s*(Hoog|Midden|Laag)", text, re.IGNORECASE)
    meta["risico"] = m.group(1).capitalize() if m else ""

    return meta
