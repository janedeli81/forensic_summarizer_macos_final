import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from UI.zip_upload_window import ZipUploadWindow  # 👉 імпорт нового вікна

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inloggen")
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("INLOGGEN")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Поле Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("E-mailadres*")
        layout.addWidget(self.email_input)

        # Поле Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Wachtwoord*")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Кнопка Login
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        if not email or not password:
            QMessageBox.warning(self, "Fout", "Voer zowel e-mailadres als wachtwoord in.")
            return

        # TODO: майбутнє оновлення — перевірка логіну (локально або через офлайн базу)

        # 👉 Закриваємо вікно логіну
        self.close()

        # 👉 Відкриваємо вікно завантаження ZIP-файлу
        self.zip_window = ZipUploadWindow()
        self.zip_window.show()


# ✅ Тестовий запуск
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
