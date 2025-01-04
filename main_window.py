from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from invoice_editor import InvoiceEditor
from list_invoice import ListInvoice
from utils import icon_button

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()

        self.db = db
        self.setWindowTitle("Invoice System")
        self.setFixedSize(900, 400)

        title = QLabel("Invoice Management System")
        font = title.font()
        font.setPointSize(40)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(icon_button('Create New Invoice', '', self.new_invoice))
        layout.addWidget(icon_button('Search By Id', '', self.modify_invoice))
        layout.addWidget(icon_button('List All Invoice', '', self.list_invoice))

        layout.setSpacing(15)

        widget = QWidget()
        widget.setLayout(layout)
        widget.setContentsMargins(50, 0, 50, 100)
        self.setCentralWidget(widget)
    
    def new_invoice(self):
        self.editor = InvoiceEditor(self.db)
        self.editor.show()
    
    def modify_invoice(self):
        inv_id, ok = QInputDialog.getInt(self, "Moidfy Invoice", "Enter the Invoice Id", min=1)
        if not ok:
            return
        
        if not self.db.invoice_exists(inv_id):
            QMessageBox.critical(self, 'Error', 'Invoice does not exist')
            return
        
        self.editor = InvoiceEditor(self.db, update=True, update_id=inv_id)
        self.editor.show()
    
    def list_invoice(self):
        self.viewer = ListInvoice(self.db)
        self.viewer.show()