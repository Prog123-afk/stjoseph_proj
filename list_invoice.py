from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from decimal import Decimal

from pdf import PdfFile
from utils import table_cell, icon_button, hbox
from invoice_editor import InvoiceReceipt, InvoiceEditor

class ListInvoice(QMainWindow):
    def __init__(self, db):
        super().__init__()

        self.setWindowTitle("All Invoices")
        self.setFixedSize(800, 500)
        self.db = db

        self.table = QTableWidget(self)
        self.table.setColumnCount(7)
        for (i, w) in enumerate([50, 320, 130, 120, 40, 40, 40]):
            self.table.setColumnWidth(i, w)

        records = self.db.get_invoices()
        rows = []

        for r in records:
            rows.append({
                'Id': r[0],
                'Description': r[2],
                'Date': r[1],
                'Amount': r[3]
            })
        
        self.table.setHorizontalHeaderLabels([
            'Id', 'Description', 'Date', 'Amount(Rs)', '', '', ''
        ])

        self.table.setRowCount(len(rows))

        for (row, e) in enumerate(rows):
            self.table.setItem(row, 0, table_cell(str(e['Id'])))
            self.table.setItem(row, 1, table_cell(str(e['Description'])))
            self.table.setItem(row, 2, table_cell(e['Date'].strftime('%d/%m/%y')))
            self.table.setItem(row, 3, table_cell(f'{e['Amount']:,.2f}'))

            self.table.setCellWidget(row, 4, icon_button('', 'delete', self.delete))
            self.table.setCellWidget(row, 5, icon_button('', 'edit', self.edit))
            self.table.setCellWidget(row, 6, icon_button('', 'view', self.view))
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table)
        main_layout.addWidget(icon_button('Go Back', 'back', self.close))

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
    
    def view(self):
        self.receipt = InvoiceReceipt(self.db)
        current_row = self.table.currentRow()
        i = int(self.table.item(current_row, 0).text().strip())
        self.receipt.prepare(i)
        self.receipt.show()
    
    def delete(self):
        current_row = self.table.currentRow()
        i = int(self.table.item(current_row, 0).text().strip())

        button = QMessageBox.question(
            self,
            'Confirmation',
            'Are you sure that you want to delete the selected invoice?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        if button == QMessageBox.StandardButton.Yes:
            self.table.removeRow(current_row)
            self.db.delete_invoice(i)
    
    def edit(self):
        current_row = self.table.currentRow()
        i = int(self.table.item(current_row, 0).text().strip())

        self.editor = InvoiceEditor(self.db, update=True, update_id=i)
        self.editor.show()
        self.hide()
    
    def close(self):
        self.hide()