from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QTableWidgetItem, QPushButton, QHBoxLayout, QLabel

def icon_button(txt, icon_name, handler):
    btn = QPushButton(txt)
    btn.clicked.connect(handler)
    if icon_name == "":
        return btn 

    icon = QIcon(f"icons/{icon_name}.png")
    btn.setIconSize(QSize(28, 28))
    btn.setIcon(icon)
    return btn

def table_cell(txt):
    item = QTableWidgetItem(txt)
    item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
    return item

def hbox(items):
    box = QHBoxLayout()
    for i in items:
        box.addWidget(QLabel(i))
    return box