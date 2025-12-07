import sys
import json
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QDateTime, Qt

from UI.final_report_window import FinalReportWindow
from backend.config import OUTPUT_DIR  # ✅ use from config


class DossierDocumentsWindow(QWidget):
    def __init__(self, documents=None):
        super().__init__()
        self.setWindowTitle("Documenten in Dossier")
        self.setGeometry(200, 200, 950, 500)

        self.layout = QVBoxLayout()

        title = QLabel("📂 Documenten in huidig dossier")
        title.setFont(QFont("Arial", 18))
        self.layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Bestandsnaam", "Document Type", "Workflow",
            "Status", "Datum", "Actie"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.table)

        self.load_documents()

        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("➕ Nieuw document toevoegen")
        self.add_btn.clicked.connect(self.add_document)

        self.gen_btn = QPushButton("🧠 Genereer (concept)rapport (BETA)")
        self.gen_btn.clicked.connect(self.generate_report)

        for btn in (self.add_btn, self.gen_btn):
            btn.setStyleSheet("""
                QPushButton {
                    padding: 10px;
                    font-weight: bold;
                    border-radius: 6px;
                    background-color: #4e6ef2;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #3b53c9;
                }
            """)
            button_layout.addWidget(btn)

        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

    def load_documents(self):
        if not OUTPUT_DIR.exists():
            OUTPUT_DIR.mkdir(exist_ok=True)

        json_files = sorted(OUTPUT_DIR.glob("*_summary.json"))
        self.table.setRowCount(len(json_files))

        for row, json_path in enumerate(json_files):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                filename = data.get("filename", json_path.stem)
                doc_type = data.get("doc_type", "Onbekend")
                workflow = data.get("workflow", "Samenvatting (default)")
                status = "Samenvatting aanwezig"

                self.table.setItem(row, 0, QTableWidgetItem(filename))
                self.table.setItem(row, 1, QTableWidgetItem(doc_type))
                self.table.setItem(row, 2, QTableWidgetItem(workflow))

                status_item = QTableWidgetItem(status)
                status_item.setForeground(Qt.darkGray)
                self.table.setItem(row, 3, status_item)

                dt = QDateTime.fromSecsSinceEpoch(int(json_path.stat().st_mtime))
                self.table.setItem(row, 4, QTableWidgetItem(dt.toString("dd MMMM yyyy HH:mm")))

                delete_btn = QPushButton("Verwijderen")
                delete_btn.setStyleSheet("color: red; font-weight: bold;")
                delete_btn.clicked.connect(
                    lambda _, r=row, f=json_path: self.remove_row(r, f)
                )
                self.table.setCellWidget(row, 5, delete_btn)

            except Exception as e:
                QMessageBox.warning(self, "Fout", f"Kan JSON niet laden:\n{json_path.name}\n{e}")

    def remove_row(self, row, filepath: Path):
        reply = QMessageBox.question(
            self, "Bevestiging", f"Weet je zeker dat je '{filepath.name}' wilt verwijderen?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                txt_version = filepath.with_suffix(".txt")
                if filepath.exists():
                    filepath.unlink()
                if txt_version.exists():
                    txt_version.unlink()
                self.table.removeRow(row)
                QMessageBox.information(self, "Verwijderd", f"{filepath.name} is verwijderd.")
            except Exception as e:
                QMessageBox.critical(self, "Fout", f"Kon bestand niet verwijderen:\n{e}")

    def add_document(self):
        QMessageBox.information(
            self, "Nieuw document",
            "Functie om documenten toe te voegen komt later."
        )

    def generate_report(self):
        self.report_window = FinalReportWindow()
        self.report_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DossierDocumentsWindow()
    window.show()
    sys.exit(app.exec_())
