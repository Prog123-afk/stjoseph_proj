from fpdf import FPDF

class PdfFile(FPDF):    
    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", style="I", size=8) 
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")
    
    def draw_banner(self, info):
        self.set_font("helvetica", size=40, style="B")
        self.ln(10)
        self.cell(80)
        self.cell(text="Invoice", align="C")
    
    def generate(self, file_name, data, info):
        self.add_page()
        self.image("icons/school.png", 10, 8, 33)

        self.draw_banner(info)
        self.ln(50)

        self.set_font("helvetica", size=12)
        self.cell(w=30, text="Date: ")
        self.cell(w=0, text=info[1].strftime('%d %B %Y'), align='L')
        self.ln(6)

        self.cell(w=30, text="Description: ")
        self.cell(w=0, text=info[0], align='L')
        self.ln(10)

        self.set_font("helvetica", size=14)
        self.set_y(90)
        with self.table(
            borders_layout="NO_HORIZONTAL_LINES",
            col_widths=(25, 80, 40, 20, 35, 50),
            text_align=("RIGHT", "LEFT", "RIGHT", "RIGHT", "RIGHT", "RIGHT"),
        ) as table:

            h_txt = [
                'S. No.', 'Item Name', 'Price (Rs)',
                'Qty', 'Disc (%)', 'Amount (Rs)'
            ]

            h_row = table.row()
            for s in h_txt:
                h_row.cell(s)

            for (i, r) in enumerate(data):
                row = table.row()
                row.cell(str(i+1))
                row.cell(r['Item Name'])
                row.cell(f'{ r['Price']:,.2f}')
                row.cell(str(r['Qty']))
                row.cell(f'{ r['Discount']}%')
                row.cell(f'{r['Amount']:,.2f}')    
        self.ln(10)
        
        amt = float(info[2])
        self.bottom_text(f"{"Subtotal":11}: Rs {amt:10,.2f}")
        self.bottom_text(f"{"Tax Rate":10}:   {"18%":10}")
        self.bottom_text(f"{"Tax":14}: Rs {amt*0.18:10,.2f}")
        
        self.ln(5)
        self.set_font("helvetica", size=20, style="B")
        self.bottom_text(f"Total: Rs {amt+amt*0.18:,.2f}", x=-95)
        
        self.output(file_name)
    
    def bottom_text(self, txt, x=-90):
        self.set_x(x)
        self.cell(text=txt)
        self.ln(7)