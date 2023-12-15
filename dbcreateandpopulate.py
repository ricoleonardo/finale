import sqlite3

# 1. Database Setup:
# Connect to the database (creates the file if it doesn't exist)
conn = sqlite3.connect("pinoybiz_sales.db")

# Create cursor object
cursor = conn.cursor()

# Define SQL statements to create tables
create_customers_table = """
CREATE TABLE IF NOT EXISTS customers (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE
);
"""

create_orders_table = """
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product varchar,
  amount DECIMAL(7,2) NOT NULL,
  order_date DATE NOT NULL,
  customer_id INTEGER NOT NULL,
  transaction_id,
  discounted_amount INTEGER,
  FOREIGN KEY (customer_id) REFERENCES customers(id),
  FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);
"""

create_transactions_table = """
CREATE TABLE IF NOT EXISTS transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  transaction_date DATE NOT NULL,
  order_id INTEGER,
  FOREIGN KEY (order_id) REFERENCES orders(transaction_id)
);
"""

# Execute the SQL statements to create the tables
cursor.execute(create_customers_table)
cursor.execute(create_orders_table)
cursor.execute(create_transactions_table)

# 2. Data Population:

# Define SQL statements to insert initial data
insert_customers = [
    ("Kalvin Jan Leonardo", "kalvin.leonardo@domain.com"),
    ("Isko Escolar", "isko.escolar@kitlatngcavite.com"),
    ("Duvall Danganan", "duvall.danganan@danganan.com"),
    ("Arvin Bongal", "arvin.bongal@bongal.com"),
    ("Mark Loma", "mark.loma@loma.com")
]

insert_orders = [
    ("Sapatos", "5550.00", "2023-12-06", 1, 1),
    ("Pantalon", "1000.00", "2023-12-07", 2, 1),
    ("Damit", "600.00", "2023-12-05", 3, 1),
    ("Mahabang damit", "800.00", "2023-11-30", 4, 1),
    ("Mahabang pantalon", "900.00", "2023-10-01", 1, 1)
]

insert_transactions = [
    ("2023-12-06", 1),
    ("2023-12-07", 1),
    ("2023-12-05", 1),
    ("2023-11-30", 1),
    ("2023-10-01", 1)
]

# Execute the SQL statements to insert the data

#cursor.execute('INSERT INTO customers (name, email, phone_number) VALUES (?, ?, ?)', ('rico', 'email', 'phone_number'))
for customer in insert_customers:
    cursor.execute("INSERT INTO customers (name, email) VALUES (?, ?)", customer)

for order in insert_orders:
    cursor.execute("INSERT INTO orders (product, amount, order_date, customer_id, transaction_id) VALUES (?, ?, ?, ?, ?)", order)

for transaction in insert_transactions:
    cursor.execute("INSERT INTO transactions (transaction_date, order_id) VALUES (?, ?)", (transaction))



# Commit changes and close the connection
conn.commit()
conn.close()

print("Database created successfully!")

