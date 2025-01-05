from db import DBConnection
from main_window import MainWindow
from PyQt6.QtWidgets import QApplication

try:
    db = DBConnection()
    app = QApplication([])

    font = app.font()
    font.setPointSize(14)
    app.setFont(font)

    window = MainWindow(db)
    window.show()

    app.exec()
except Exception as e:
    print("Unexpected Error Occurred")
    print(str(e))
