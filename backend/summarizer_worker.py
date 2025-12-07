# backend/summarizer_worker.py

from PyQt5.QtCore import QThread, pyqtSignal
from pathlib import Path
import json
import shutil

from backend.summarizer import summarize_document
from backend.classifiers import classify_document
from backend.text_extraction import extract_text
from backend.process_zip import guess_workflow, extract_basic_meta


class SummarizationWorker(QThread):
    progress = pyqtSignal(str)      # для логів
    finished = pyqtSignal(dict)     # результат: {"filename", "summary", "doc_type", ...}
    error = pyqtSignal(str)

    def __init__(self, file_path: Path, output_dir: Path, extracted_dir: Path):
        super().__init__()
        self.file_path = file_path
        self.output_dir = output_dir
        self.extracted_dir = extracted_dir

    def run(self):
        try:
            filename = self.file_path.name
            self.progress.emit(f"📄 Processing: {filename}")

            text = extract_text(self.file_path)
            if not text:
                self.error.emit(f"⚠️ No text extracted from {filename}")
                return

            doc_type = classify_document(self.file_path, text)
            self.progress.emit(f"🔍 Document type: {doc_type}")

            summary = summarize_document(doc_type, text)

            # File save
            stem = self.file_path.stem
            txt_path = self.output_dir / f"{stem}_summary.txt"
            json_path = self.output_dir / f"{stem}_summary.json"
            extracted_copy = self.extracted_dir / filename

            txt_path.write_text(summary, encoding="utf-8")

            json_data = {
                "filename": filename,
                "doc_type": doc_type,
                "workflow": guess_workflow(doc_type),
                "summary": summary,
                "meta": extract_basic_meta(text)
            }
            json_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")


            self.finished.emit({
                "filename": filename,
                "doc_type": doc_type,
                "summary": summary,
                "path": txt_path
            })

        except Exception as e:
            self.error.emit(f"❌ Error processing {self.file_path.name}: {e}")
