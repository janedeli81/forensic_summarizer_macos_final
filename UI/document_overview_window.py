import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QHBoxLayout, QScrollArea, QLineEdit,
    QFormLayout, QMessageBox, QApplication
)
from PyQt5.QtGui import QFont
from pathlib import Path

from backend.config import OUTPUT_DIR  # ✅ use from config


class DocumentOverviewWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Documentoverzicht")
        self.resize(800, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        title = QLabel("📄 Documentoverzicht en workflow selectie")
        title.setFont(QFont("Arial", 20))
        self.layout.addWidget(title)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.document_widgets = []
        self.load_documents()

        button_layout = QHBoxLayout()
        self.create_btn = QPushButton("Dossier aanmaken")
        self.create_btn.setStyleSheet("background-color: green; color: white; padding: 10px;")
        self.create_btn.clicked.connect(self.go_next)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)

        button_layout.addWidget(self.create_btn)
        button_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(button_layout)

    def load_documents(self):
        files = sorted(OUTPUT_DIR.glob("*_summary.txt"))

        for file_path in files:
            filename = file_path.name

            form = QFormLayout()
            container = QWidget()
            container.setLayout(form)

            name_field = QLineEdit(filename)
            name_field.setReadOnly(True)

            type_box = QComboBox()
            type_box.addItems([
                "Oude PJ rapportage",
                "Reclasseringsrapport",
                "TLL rapport",
                "Observatieverslag",
                "Onbekend"
            ])

            workflow_box = QComboBox()
            workflow_box.addItems([
                "Oude Pro Justitia (Oude PJ) rapportage Samenvatter 1.0 - Maart 2024",
                "Reclasseringsrapport Samenvatter 1.0 - Maart 2024",
                "TLL Generator (obv vordering IBS)",
                "Standaard Samenvatting"
            ])

            form.addRow("Naam:", name_field)
            form.addRow("Document Type:", type_box)
            form.addRow("Workflow:", workflow_box)

            self.scroll_layout.addWidget(container)

            self.document_widgets.append({
                "filename": filename,
                "type_box": type_box,
                "workflow_box": workflow_box
            })

    def go_next(self):
        from UI.dossier_start_window import DossierStartWindow

        selected_docs = []
        for doc in self.document_widgets:
            selected_docs.append({
                "filename": doc["filename"],
                "doc_type": doc["type_box"].currentText(),
                "workflow": doc["workflow_box"].currentText()
            })

        self.next_window = DossierStartWindow(documents=selected_docs)
        self.next_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DocumentOverviewWindow()
    window.show()
    sys.exit(app.exec_())
