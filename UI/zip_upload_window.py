# UI/zip_upload_window.py

import sys
import os
import shutil
import zipfile
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QTextEdit,
    QProgressBar,
    QFrame,
    QSizePolicy,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from backend.config import OUTPUT_DIR, EXTRACTED_DIR
from backend.summarizer_worker import ClassificationWorker, SummarizationWorker
from UI.document_overview_window import DocumentOverviewWindow
from UI.ui_theme import apply_window_theme


class ZipUploadWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dossier op basis van ZIP-bestand aanmaken")
        self.setMinimumSize(1100, 720)
        self._center_on_screen()

        self.selected_file = None
        self.all_files = []
        self.classified = {}  # path(str) -> {filename, doc_type, text}
        self.current_index = 0
        self.output_dir = OUTPUT_DIR
        self.extracted_dir = EXTRACTED_DIR

        self.classifier = None
        self.worker = None

        self._build_ui()
        apply_window_theme(self)

    def _build_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.page = QFrame()
        self.page.setObjectName("page")

        page_layout = QVBoxLayout(self.page)
        page_layout.setContentsMargins(70, 54, 70, 54)
        page_layout.setSpacing(14)

        # Title (smaller + wrap to avoid cropping)
        title = QLabel("Dossier op basis van ZIP-bestand aanmaken")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignLeft)
        title.setWordWrap(True)
        page_layout.addWidget(title)

        uitleg = QLabel("Zip bestand met dossierbestanden (gedownload van bestandenpostbus):")
        uitleg.setObjectName("fieldLabel")
        uitleg.setFont(QFont("Segoe UI", 12))
        uitleg.setWordWrap(True)
        page_layout.addWidget(uitleg)

        # File row
        file_row = QHBoxLayout()
        file_row.setSpacing(12)

        self.choose_btn = QPushButton("Bestand kiezen")
        self.choose_btn.setObjectName("secondaryButton")
        self.choose_btn.setCursor(Qt.PointingHandCursor)
        self.choose_btn.clicked.connect(self.select_zip)
        self.choose_btn.setFixedHeight(40)

        self.file_label = QLabel("Geen bestand gekozen")
        self.file_label.setObjectName("fieldLabel")
        self.file_label.setFont(QFont("Segoe UI", 12))
        self.file_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        file_row.addWidget(self.choose_btn, 0, Qt.AlignLeft)
        file_row.addWidget(self.file_label, 1, Qt.AlignVCenter)
        page_layout.addLayout(file_row)

        # Log area
        self.log_area = QTextEdit()
        self.log_area.setObjectName("input")
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Segoe UI", 11))
        self.log_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.log_area.setMinimumHeight(360)
        page_layout.addWidget(self.log_area, 1)

        # Bottom row: progress (left) + button (right)
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(14)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setFormat("%p% gereed")
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(28)
        self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid rgba(0, 0, 0, 18);
                border-radius: 10px;
                background: rgb(255, 255, 255);
                padding: 2px;
                text-align: center;
                color: rgb(50, 50, 50);
            }
            QProgressBar::chunk {
                border-radius: 8px;
                background: #ffd700;
            }
        """)

        self.create_btn = QPushButton("Aanmaken")
        self.create_btn.setObjectName("primaryButton")
        self.create_btn.setCursor(Qt.PointingHandCursor)
        self.create_btn.clicked.connect(self.confirm_creation)
        self.create_btn.setFixedHeight(44)
        self.create_btn.setFixedWidth(160)

        bottom_row.addWidget(self.progress_bar, 1)
        bottom_row.addWidget(self.create_btn, 0, Qt.AlignRight)

        page_layout.addLayout(bottom_row)

        # Wrap page
        wrapper = QVBoxLayout()
        wrapper.setContentsMargins(26, 22, 26, 26)
        wrapper.addWidget(self.page)

        container = QWidget()
        container.setLayout(wrapper)

        root.addWidget(container)
        self.setLayout(root)

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

        self._set_ui_busy(True)

        for folder in [self.output_dir, self.extracted_dir]:
            if folder.exists():
                shutil.rmtree(folder)
            folder.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(self.selected_file, "r") as zip_ref:
                zip_ref.extractall(self.extracted_dir)
                self.log(f"ZIP uitgepakt naar: {self.extracted_dir}")

            self.all_files = []
            for root, _, files in os.walk(self.extracted_dir):
                for filename in files:
                    full_path = Path(root) / filename
                    self.all_files.append(full_path)

            if not self.all_files:
                self._set_ui_busy(False)
                QMessageBox.warning(self, "Leeg", "ZIP-bestand bevat geen documenten.")
                return

            self.start_classification()

        except Exception as e:
            self._set_ui_busy(False)
            QMessageBox.critical(self, "Fout", f"Fout bij uitpakken van ZIP:\n{e}")

    # ------------------------
    # Stage 1: classification
    # ------------------------
    def start_classification(self):
        self.log("Detecting document types for all files...")

        self.progress_bar.setMaximum(0)  # indeterminate
        self.progress_bar.setValue(0)

        self.classified = {}
        self.classifier = ClassificationWorker(self.all_files)
        self.classifier.progress.connect(self.log)
        self.classifier.error.connect(self.log)
        self.classifier.finished.connect(self.on_classification_finished)
        self.classifier.start()

    def on_classification_finished(self, results: list):
        self.classified = {item["path"]: item for item in results}
        self.all_files = [Path(item["path"]) for item in results]

        if not self.all_files:
            self._set_ui_busy(False)
            QMessageBox.warning(self, "Leeg", "Geen documenten met tekst gevonden na classificatie.")
            return

        self.log("\nDetected document types:")
        for item in results:
            self.log(f" • {item['filename']}  →  {item['doc_type']}")
        self.log("\nStarting summarization...\n")

        self.progress_bar.setMaximum(len(self.all_files))
        self.progress_bar.setValue(0)

        self.current_index = 0
        self.process_next_file()

    # ------------------------
    # Stage 2: summarization
    # ------------------------
    def process_next_file(self):
        if self.current_index >= len(self.all_files):
            self.log("Alle documenten verwerkt.")
            QMessageBox.information(self, "Klaar", f"{len(self.all_files)} documenten verwerkt.")
            self._set_ui_busy(False)
            self.open_next_window()
            return

        current_file = self.all_files[self.current_index]

        cached = self.classified.get(str(current_file))
        pre_doc_type = cached.get("doc_type") if cached else None
        pre_text = cached.get("text") if cached else None

        total = len(self.all_files)
        current = self.current_index + 1
        percent = int((current / total) * 100)
        self.log(f"({current}/{total}) {current_file.name} — {percent}%")

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
        self.log(f"Opgeslagen: {result['filename']}")
        self.current_index += 1
        self.progress_bar.setValue(self.current_index)
        self.process_next_file()

    def open_next_window(self):
        self.next_window = DocumentOverviewWindow()
        self.next_window.show()
        self.close()

    def _set_ui_busy(self, busy: bool):
        self.choose_btn.setEnabled(not busy)
        self.create_btn.setEnabled(not busy)

    def closeEvent(self, event):
        self._stop_threads()
        event.accept()

    def _stop_threads(self):
        for t in [self.worker, self.classifier]:
            if t is None:
                continue
            try:
                if hasattr(t, "isRunning") and t.isRunning():
                    if hasattr(t, "requestInterruption"):
                        t.requestInterruption()
                    if hasattr(t, "quit"):
                        t.quit()
                    if hasattr(t, "wait"):
                        t.wait(3000)
            except Exception:
                pass

    def _center_on_screen(self):
        screen = QApplication.primaryScreen()
        if not screen:
            return
        rect = screen.availableGeometry()
        x = rect.x() + (rect.width() - self.width()) // 2
        y = rect.y() + (rect.height() - self.height()) // 2
        self.move(x, y)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ZipUploadWindow()
    window.show()
    sys.exit(app.exec_())
