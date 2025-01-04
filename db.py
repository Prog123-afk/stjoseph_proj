from mysql.connector import connect

TABLES = {}
TABLES["invoices"] = """
CREATE TABLE IF NOT EXISTS invoices (
    id INT NOT NULL AUTO_INCREMENT,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(255) NOT NULL,
    total DECIMAL(10, 2),
    PRIMARY KEY(id)
)
"""
TABLES["records"] = """
CREATE TABLE IF NOT EXISTS records (
    id INT NOT NULL AUTO_INCREMENT,
    invoice_id INT NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    qty INT NOT NULL,
    discount INT DEFAULT(0),
    PRIMARY KEY(id),
    FOREIGN KEY (invoice_id)
        REFERENCES invoices(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
"""

class DBConnection():
    def __init__(self):
        self.cnx = connect(
            user="avnadmin",
            password="AVNS_8U4N4u-MyxG8wVXrqjV",
            host="mysql-d5b1a0-anandashishdih-e230.b.aivencloud.com",
            database="defaultdb",
            port="10016"
        )
        print("Connected")

        with self.cnx.cursor() as cursor:
            cursor.execute(TABLES["invoices"])
            cursor.execute(TABLES["records"])

    def insert_record(self, data):
        query = (
            "INSERT INTO records(invoice_id, item_name, price, qty, discount)"
            f" VALUES({data['invoice_id']}, '{data['item_name']}', "
            f" {data['price']}, {data['qty']}, {data['discount']})"
        )

        with self.cnx.cursor() as cursor:
            cursor.execute(query)
            self.cnx.commit()
        
    def insert_invoice(self, inv):
        query = (
            f"INSERT INTO invoices(description) VALUES('{inv['description']}')"
        )

        with self.cnx.cursor() as cursor:
            cursor.execute(query)
            self.cnx.commit()
            i = cursor.lastrowid
            return i
    
    def get_invoices(self):
        with self.cnx.cursor() as cursor:
            cursor.execute("SELECT * FROM invoices ORDER BY created DESC")
            res = cursor.fetchall()
            return res
    
    def get_invoice_info(self, i):
        query = f'SELECT description, created, total FROM invoices WHERE id={i}'
        with self.cnx.cursor() as cursor:
            cursor.execute(query)
            res = cursor.fetchall()
            return res[0]
    
    def invoice_exists(self, i):
        with self.cnx.cursor() as cursor:
            cursor.execute(f'SELECT description FROM invoices WHERE id={i}')
            res = cursor.fetchall()
            return (len(res) > 0)

    def get_records(self, invoice_id):
        with self.cnx.cursor() as cursor:
            cursor.execute(f'SELECT * FROM records WHERE invoice_id={invoice_id}')
            res = cursor.fetchall()
            return res
    
    def set_amount(self, inv_id, total):
        with self.cnx.cursor() as cursor:
            cursor.execute(f'UPDATE invoices SET total = {total} WHERE id = {inv_id}')
            self.cnx.commit()
    
    def delete_records(self, invoice_id):
        with self.cnx.cursor() as cursor:
            cursor.execute(f'DELETE FROM records WHERE invoice_id={invoice_id}')
            self.cnx.commit()
    
    def delete_invoice(self, inv_id):
        with self.cnx.cursor() as cursor:
            cursor.execute(f'DELETE FROM invoices WHERE id = {inv_id}')
            self.cnx.commit()

    def close(self):
        self.cnx.close()
