import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QCheckBox, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from UI.dossier_detail_window import DossierDetailWindow  # 🆕 імпорт наступного вікна

class DossierStartWindow(QWidget):
    def __init__(self, documents=None):
        super().__init__()
        self.setWindowTitle("Nieuw dossier aanmaken")
        self.setGeometry(200, 200, 800, 400)

        self.documents = documents or []  # Отримані документи з попереднього екрану

        layout = QVBoxLayout()

        title = QLabel("Nieuw dossier aanmaken")
        title.setFont(QFont("Arial", 24))
        layout.addWidget(title)

        credits = QLabel("Je hebt op dit moment nog 60 credit(s) over. Het aanmaken van een nieuw dossier kost 1 credit.")
        layout.addWidget(credits)

        uitleg = QLabel("Kies een van beide:\n\n"
                        "• Start met <b>LEEG</b> dossier, en upload hierbij je documenten stuk voor stuk\n"
                        "• Start met dossier op basis van een <b>ZIP</b>-bestand met je documenten")
        uitleg.setWordWrap(True)
        layout.addWidget(uitleg)

        voorwaarden = QLabel(
            "<b>Voorwaarden voor gebruik:</b><br><br>"
            "• Door gebruik te maken van deze service, ga ik akkoord met onze "
            "<a href='#'>algemene voorwaarden</a>, <a href='#'>hoofd overeenkomst</a> en "
            "<a href='#'>verwerkersovereenkomst</a>.<br>"
            "• Ik begrijp dat dit instrument slechts een hulpmiddel is en ikzelf verantwoordelijk ben voor de resultaten.<br>"
            "• Voor het aantal documenten en audio-bestanden per dossier geldt een fair-use policy."
        )
        voorwaarden.setWordWrap(True)
        voorwaarden.setOpenExternalLinks(True)
        layout.addWidget(voorwaarden)

        self.checkbox = QCheckBox("Ik accepteer bovenstaande voorwaarden voor gebruik")
        self.checkbox.stateChanged.connect(self.toggle_buttons)
        layout.addWidget(self.checkbox)

        button_layout = QHBoxLayout()

        self.btn_leeg = QPushButton("🗎 Leeg Dossier Aanmaken")
        self.btn_leeg.setEnabled(False)
        self.btn_leeg.clicked.connect(self.handle_leeg)

        self.btn_zip = QPushButton("📦 Dossier Aanmaken met Zip")
        self.btn_zip.setEnabled(False)
        self.btn_zip.clicked.connect(self.handle_zip)

        self.apply_button_style(self.btn_leeg)
        self.apply_button_style(self.btn_zip)

        button_layout.addWidget(self.btn_leeg)
        button_layout.addWidget(self.btn_zip)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def toggle_buttons(self):
        accepted = self.checkbox.isChecked()
        self.btn_leeg.setEnabled(accepted)
        self.btn_zip.setEnabled(accepted)

    def apply_button_style(self, button):
        button.setStyleSheet("""
            QPushButton {
                background-color: #4e6ef2;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #3b53c9;
            }
        """)

    def handle_leeg(self):
        QMessageBox.information(self, "Leeg Dossier", "Functie nog niet geïmplementeerd.")

    def handle_zip(self):
        # Переходимо до DossierDetailWindow з передачею документів
        self.detail_window = DossierDetailWindow(documents=self.documents)
        self.detail_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DossierStartWindow()
    window.show()
    sys.exit(app.exec_())
