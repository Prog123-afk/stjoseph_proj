from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt,QSize

from decimal import Decimal

from pdf import PdfFile
from utils import table_cell, icon_button, hbox

class InvoiceEditor(QMainWindow):
    def __init__(self, db, update=False, update_id=13, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.db = db
        self.update = update
        self.update_id = update_id

        self.setWindowTitle('Create Invoice')
        self.setFixedSize(950, 500)

        records = []
        if self.update:
            self.setWindowTitle("Edit Invoice")
            rows = self.db.get_records(self.update_id)

            for r in rows:
                print(r)
                records.append({
                    'Item Name': r[2],
                    'Price': r[3],
                    'Qty': r[4],
                    'Discount': r[5]
                })

        self.table = QTableWidget(self)
        self.table.setColumnCount(5)

        for (i, w) in enumerate([200, 100, 100, 100, 30]):
            self.table.setColumnWidth(i, w)

        headers = ['Item Name', 'Price (Rs)', 'Qty', "Disc (%)", ""]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(records))

        for (row, e) in enumerate(records):
            self.table.setItem(row, 0, QTableWidgetItem(e['Item Name']))
            self.table.setItem(row, 2, QTableWidgetItem(str(e['Qty'])))
            self.table.setItem(row, 1, QTableWidgetItem(str(e['Price'])))
            self.table.setItem(row, 3, QTableWidgetItem(str(e['Discount'])))
            self.table.setCellWidget(row, 4, icon_button('', 'delete', self.delete))  
      
        self.description = QLineEdit()
        if self.update:
            self.description.setText(self.db.get_invoice_info(self.update_id)[0])

        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Description: "))
        main_layout.addWidget(self.description)
        main_layout.addWidget(self.table)

        gen_invoice = None
        if self.update:
            gen_invoice = icon_button('Update Invoice', 'save', self.update_invoice)
        else:
            gen_invoice = icon_button('Generate Invoice', '', self.generate_invoice)

        main_layout.addWidget(gen_invoice)
        main_layout.addWidget(icon_button('Go Back', 'back', self.close))

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        dock = QDockWidget('New Record')
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

        form = QWidget()
        form_layout = QFormLayout(form)
        form.setLayout(form_layout)

        self.item_name = QLineEdit(form)
        self.price = QLineEdit(form)
        self.qty = QSpinBox(form, minimum=1, maximum=1000)
        self.qty.clear()
        self.discount = QSpinBox(form, minimum=0, maximum=100)
        self.discount.setValue(0)

        form_layout.addRow('Item Name:', self.item_name)
        form_layout.addRow('Price(Rs):', self.price)
        form_layout.addRow('Qty:', self.qty)
        form_layout.addRow('Discount(%) :', self.discount)
        form_layout.addRow(icon_button('Add', '', self.add_record))

        dock.setWidget(form)

    def delete(self):
        current_row = self.table.currentRow()

        button = QMessageBox.question(
            self,
            'Confirmation',
            'Are you sure that you want to delete the selected row?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        if button == QMessageBox.StandardButton.Yes:
            self.table.removeRow(current_row)

    def valid(self):
        item_name = self.item_name.text().strip()

        if not item_name:
            QMessageBox.critical(self, 'Error', 'Please enter the item name')
            self.first_name.setFocus()
            return False

        try:
            price = float(self.price.text().strip())
            qty = int(self.qty.text().strip())
            discount = int(self.discount.text().strip())

        except ValueError:
            QMessageBox.critical(self, 'Error', 'Please enter valid data')
            return False

        if qty <= 0 or discount >= 100 or discount < 0:
            QMessageBox.critical(
                self, 'Error', 'Please enter valid data')
            return False
        return True

    def reset_form(self):
        self.item_name.clear()
        self.price.clear()
        self.qty.clear()
        self.discount.setValue(0)

    def add_record(self):
        if not self.valid():
            return

        table = self.table
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(self.item_name.text().strip()))
        table.setItem(row, 1, QTableWidgetItem(self.price.text().strip()))
        table.setItem(row, 2, QTableWidgetItem(self.qty.text()))
        table.setItem(row, 3, QTableWidgetItem(self.discount.text()))
        table.setCellWidget(row, 4, icon_button('', 'delete', self.delete))
        self.reset_form()
  
    def generate_invoice(self):
        rows = self.table.rowCount()
        desc = self.description.text().strip()
        if desc == "":
            QMessageBox.critical(self, 'Error', 'Description cannot be empty')
            return
            
        records = []
        for i in range(rows):
            item_name = self.table.item(i, 0).text().strip()

            try:
                price = float(self.table.item(i, 1).text().strip())
                qty = int(self.table.item(i, 2).text().strip())
                discount = int(self.table.item(i, 3).text().strip())

                records.append({
                    'item_name': item_name, 'price': price,
                    'qty': qty, 'discount': discount
                })
            except ValueError:
                QMessageBox.critical(self, 'Error', 'Please enter valid data')
                return
        
        i = self.update_id
        if not self.update:
            i = self.db.insert_invoice({'description': desc})
        
        total_amt = 0
        for r in records:
            r['invoice_id'] = i
            self.db.insert_record(r)

            amt = price * qty
            amt = amt - (amt * (discount / 100))
            total_amt += amt
        self.db.set_amount(i, total_amt)

        self.receipt = InvoiceReceipt(self.db)
        self.receipt.prepare(i)
        self.receipt.show()
        self.close()
    
    def update_invoice(self):
        self.db.delete_records(self.update_id)
        self.generate_invoice()

    def close(self):
        self.hide()

class InvoiceReceipt(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.setWindowTitle("Invoice Receipt")
        self.setFixedSize(890, 600)
        self.db = db
    
    def prepare(self, i):
        self.i = i
        rows = self.db.get_records(i)
    
        grid = QTableWidget()
        grid.setColumnCount(6)
        headers = ['S.No', 'Item Name', 'Price(Rs)', 'Qty', "Disc(%)", "Amount(Rs)"]
        grid.setHorizontalHeaderLabels(headers)
        grid.setRowCount(len(rows))

        col_widths = [50, 300, 150, 60, 100, 150]
        for (i, w) in enumerate(col_widths):
            grid.setColumnWidth(i, w)
        
        self.data = []
        for (i, r) in enumerate(rows):
            self.data.append({
                'Item Name': r[2],
                'Price': r[3],
                'Qty': r[4],
                'Discount': r[5],
                'Amount': r[3] * Decimal(r[4])
            })

            grid.setItem(i, 0, table_cell(str(i+1)))
            grid.setItem(i, 1, table_cell(r[2]))
            grid.setItem(i, 2, table_cell(f'{r[3]:,.2f}'))
            grid.setItem(i, 3, table_cell(str(r[4])))
            grid.setItem(i, 4, table_cell(str(r[5])))

            r_amt = float(r[3]) * r[4]
            r_amt -= r_amt * (r[5]/100)
            grid.setItem(i, 5, table_cell(f'{r_amt:,.2f}'))
        
        self.info = self.db.get_invoice_info(self.i)

        main_layout = QVBoxLayout()
        main_layout.addLayout(hbox(['Invoice Id:', str(self.i)]))
        main_layout.addLayout(hbox(['Date:', self.info[1].strftime('%d %B %Y')]))
        #main_layout.addLayout(hbox(['Time:', self.info[1].strftime('%I:%M %p')]))
        main_layout.addLayout(hbox(['Description:', self.info[0]]))

        amt = float(self.info[2])
        total_amt = amt + (amt * 0.18)

        main_layout.addWidget(grid)
        main_layout.addLayout(hbox(['Subtotal:', f'{amt:,.2f}']))
        main_layout.addLayout(hbox(['Tax rate:', '18%']))
        main_layout.addLayout(hbox(['Tax:', 'Rs ' + f'{total_amt*0.18:,.2f}']))
        main_layout.addLayout(hbox(['Total:', 'Rs ' + f'{total_amt:,.2f}']))
        main_layout.addWidget(icon_button('Save as PDF', 'pdf', self.save_pdf))
        main_layout.addWidget(icon_button('Go Back', 'back', self.close))

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
    
    def close(self):
        self.hide()
    
    def save_pdf(self):
        fileName, _ = QFileDialog.getSaveFileName(self, 
            "Save File", f"invoice-{self.i}", "PDF Files(*.pdf)")
        if fileName == "":
            return

        try:
            print("Saving", fileName)
            f = PdfFile()
            f.generate(fileName, self.data, self.info)
            self.hide()
        except Exception:
            QMessageBox.critical(self, 'Error', 'Failed to save pdf')