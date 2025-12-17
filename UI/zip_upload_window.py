# UI/zip_upload_window.py

import sys
import os
import shutil
import zipfile
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QMessageBox, QTextEdit, QProgressBar
)
from PyQt5.QtGui import QFont

from backend.config import OUTPUT_DIR, EXTRACTED_DIR
from backend.summarizer_worker import ClassificationWorker, SummarizationWorker
from UI.document_overview_window import DocumentOverviewWindow


class ZipUploadWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dossier op basis van ZIP-bestand aanmaken")
        self.setGeometry(200, 200, 750, 450)

        self.selected_file = None
        self.all_files = []
        self.classified = {}  # path(str) -> {filename, doc_type, text}
        self.current_index = 0
        self.output_dir = OUTPUT_DIR
        self.extracted_dir = EXTRACTED_DIR

        layout = QVBoxLayout()

        title = QLabel("📦 Dossier op basis van ZIP-bestand aanmaken")
        title.setFont(QFont("Arial", 20))
        layout.addWidget(title)

        uitleg = QLabel("Zip bestand met dossierbestanden (gedownload van bestandenpostbus):")
        uitleg.setStyleSheet("color: gray;")
        layout.addWidget(uitleg)

        file_layout = QHBoxLayout()
        self.choose_btn = QPushButton("Choose File")
        self.choose_btn.clicked.connect(self.select_zip)
        self.file_label = QLabel("No file chosen")
        file_layout.addWidget(self.choose_btn)
        file_layout.addWidget(self.file_label)
        layout.addLayout(file_layout)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setFormat("%p% gereed")
        layout.addWidget(self.progress_bar)

        self.create_btn = QPushButton("✅ Aanmaken")
        self.create_btn.clicked.connect(self.confirm_creation)
        layout.addWidget(self.create_btn)

        self.setLayout(layout)

    def log(self, text: str):
        self.log_area.append(text)

    def select_zip(self):
        zip_path, _ = QFileDialog.getOpenFileName(
            self, "Selecteer ZIP-bestand", "", "ZIP bestanden (*.zip)"
        )
        if zip_path:
            self.selected_file = zip_path
            self.file_label.setText(Path(zip_path).name)

    def confirm_creation(self):
        if not self.selected_file:
            QMessageBox.warning(self, "Geen bestand", "Selecteer eerst een ZIP-bestand.")
            return

        for folder in [self.output_dir, self.extracted_dir]:
            if folder.exists():
                shutil.rmtree(folder)
            folder.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(self.selected_file, 'r') as zip_ref:
                zip_ref.extractall(self.extracted_dir)
                self.log(f"✅ ZIP uitgepakt naar")

            self.all_files = []
            for root, _, files in os.walk(self.extracted_dir):
                for filename in files:
                    full_path = Path(root) / filename
                    self.all_files.append(full_path)

            if not self.all_files:
                QMessageBox.warning(self, "Leeg", "ZIP-bestand bevat geen documenten.")
                return

            # Stage 1: classify all documents first (in background)
            self.start_classification()

        except Exception as e:
            QMessageBox.critical(self, "Fout", f"Fout bij uitpakken van ZIP:\n{e}")

    # ------------------------
    # Stage 1: classification
    # ------------------------
    def start_classification(self):
        self.log("🔎Detecting document types for all files...")

        # Show indeterminate progress while we classify
        self.progress_bar.setMaximum(0)
        self.progress_bar.setValue(0)

        self.classified = {}
        self.classifier = ClassificationWorker(self.all_files)
        self.classifier.progress.connect(self.log)
        self.classifier.error.connect(self.log)
        self.classifier.finished.connect(self.on_classification_finished)
        self.classifier.start()

    def on_classification_finished(self, results: list):
        # Build cache and also filter out skipped docs (no text)
        self.classified = {item["path"]: item for item in results}
        self.all_files = [Path(item["path"]) for item in results]

        if not self.all_files:
            QMessageBox.warning(self, "Leeg", "Geen documenten met tekst gevonden na classificatie.")
            return

        self.log("\n📌 Detected document types:")
        for item in results:
            self.log(f" • {item['filename']}  →  {item['doc_type']}")
        self.log("\n▶️ Starting summarization...\n")

        # Switch progress bar back to determinate for summarization stage
        self.progress_bar.setMaximum(len(self.all_files))
        self.progress_bar.setValue(0)

        self.current_index = 0
        self.process_next_file()

    # ------------------------
    # Stage 2: summarization
    # ------------------------
    def process_next_file(self):
        if self.current_index >= len(self.all_files):
            self.log("✅ Alle documenten verwerkt.")
            QMessageBox.information(self, "Klaar", f"{len(self.all_files)} documenten verwerkt.")
            self.open_next_window()
            return

        current_file = self.all_files[self.current_index]

        cached = self.classified.get(str(current_file))
        pre_doc_type = cached.get("doc_type") if cached else None
        pre_text = cached.get("text") if cached else None

        total = len(self.all_files)
        current = self.current_index + 1
        percent = int((current / total) * 100)
        self.log(f"📄 ({current}/{total}) {current_file.name} — {percent}%")

        self.worker = SummarizationWorker(
            current_file,
            self.output_dir,
            self.extracted_dir,
            doc_type=pre_doc_type,
            text=pre_text,
        )
        self.worker.progress.connect(self.log)
        self.worker.error.connect(self.log)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def on_worker_finished(self, result: dict):
        self.log(f"💾 Opgeslagen: {result['filename']}")
        self.current_index += 1
        self.progress_bar.setValue(self.current_index)
        self.process_next_file()

    def open_next_window(self):
        self.next_window = DocumentOverviewWindow()
        self.next_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ZipUploadWindow()
    window.show()
    sys.exit(app.exec_())
