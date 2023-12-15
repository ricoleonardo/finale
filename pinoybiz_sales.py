import sqlite3
import pandas as pd
import time as time
from datetime import datetime, timedelta, date




# Connect to the database (creates the file if it doesn't exist)
conn = sqlite3.connect("pinoybiz_sales.db")

# Create cursor object
cursor = conn.cursor()

# 3. Dashboard Queries:

# 3.1 Total Order Amount for each Customer
print("\n3.1 Total Order Amount for each Customer")
cursor.execute("""
SELECT
  o.customer_id,
  c.name,
  o.product,
  CAST(o.amount AS DECIMAL(7,2)) AS amount,
  o.order_date,
  SUM(CAST(o.amount AS DECIMAL(7,2))) AS total_amount
FROM orders o
INNER JOIN customers c ON o.customer_id = c.id
GROUP BY o.customer_id, o.product, c.name, o.order_date;
""")

data = cursor.fetchall()
print ("\n\n Using INNER JOIN to include customer with orders!")
df = pd.DataFrame(data, columns=["customer_id", "name", "product", "amount", "order_date", "total_amount"])
# Apply lambda function to format total amount with currency symbol
df["total_amount"] = df["amount"].apply(lambda x: f"₱{x:.2f}")
print(df)

# 3.1 Write a query to fetch customer information along with their total amount, using a LEFT JOIN to include customers without orders.
print("\n3.1 Write a query to fetch customer information along with their total amount, using a LEFT JOIN to include customers without orders.")
cursor.execute("""
SELECT c.id, c.name, c.email, coalesce(SUM(o.amount), 0) AS total_amount
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name, c.email
ORDER BY c.id
""")

data = cursor.fetchall()

print ("\n\n Using LEFT JOIN to include customer without orders!")
df = pd.DataFrame(data, columns=["id", "name", "email", "total_amount"])
# Apply lambda function to format total amount with currency symbol
df["total_amount"] = df["total_amount"].apply(lambda x: f"₱{x:.2f}")
print(df)

# 3.2 Implement a subquery to identify customers who have made transactions of more than PHP 5,000 in total.
print("\n3.2 Implement a subquery to identify customers who have made transactions of more than PHP 5,000 in total.")
cursor.execute("""
SELECT *
FROM customers c
WHERE c.id IN (
	SELECT customer_id
	FROM orders o
	GROUP BY customer_id
	HAVING SUM(amount) > 5000
);
""")

data = cursor.fetchall()
print (" Customer with more than PHP 5,000.00")
df = pd.DataFrame(data, columns=["customer_id", "name", "email"])
print(df)

# 3.3 Create a query to display the product, discounted amount (using the calculate_discount stored procedure), and transactions date for all orders.
print("\n3.3 Create a query to display the product, discounted amount (using the calculate_discount stored procedure), and transactions date for all orders.")
# Stored Procedure Function for the SQL to perform the discounted amount with Transaction Date
def calculate_discount(amount):
  """
  Calculates a discount of 5% on the provided amount.
  """
  try:
    discount = amount * 0.05
    discounted = amount - discount
    return discounted
  except Exception as e:
    # Handle the exception
    print(f"Error calculating discount: {e}")
    return None
  finally:
    # Cleanup resources (if necessary)
    pass

conn.create_function("calculate_discount", 1, calculate_discount)

cursor.execute("""
SELECT o.product, calculate_discount(o.amount) AS discounted_amount, t.transaction_date
FROM orders o
INNER JOIN transactions t ON o.id = t.id;
""")

data = cursor.fetchall()
print("\n\n Products with 0.05 discount with transaction date")
df = pd.DataFrame(data, columns=["PRODUCTS", "discounted", "TRANSACTION_DATE"])
df["discounted"] = df["discounted"].apply(lambda x: f"₱{x:.2f}")
print(df)

# 4. Indexing and Optimization:
print("\n4. Indexing and Optimization:")
# 4.1 Add an index to the order_date column in the Orders table to optimize queries related to date-based filtering, considering the importance of timely transactions in the local market

# Add index to order_date
#cursor.execute("CREATE INDEX idx_order_date ON Orders (order_date);")


# Demonstrate improved performance
start_time = time.time()
cursor.execute("SELECT * FROM Orders WHERE order_date = '2023-12-06';")
results = cursor.fetchall()
end_time = time.time()

print(f"Query execution time with index: {end_time - start_time}")


# 5. Transactions:
# Begin a transaction to update the order amount for a specific order, ensuring the scenario aligns with a local business context.
# If the updated amount exceeds a predefined threshold (e.g., PHP 10,000), you are required to roll back the transaction. Otherwise, you should commit the transaction.
print("\n5. Transactions:")
order_id = 1
new_amount = 11000
cursor.execute(f"SELECT amount FROM Orders WHERE id = {order_id};")
current_amount = cursor.fetchone()[0]
print(current_amount)

if new_amount > 10000:
  # Rollback transaction if exceeding threshold
  conn.rollback()
  print(f"Order amount update failed: exceeded threshold of PHP 10,000")
else:
  # Proceed with update
  cursor.execute(f"UPDATE Orders SET amount = {new_amount} WHERE id = {order_id};")
  conn.commit()
  print(f"Order amount updated successfully to PHP {new_amount}")


# 6. Stored Procedure Enhancement:
# 6.1 Modify the calculate_discount stored procedure to include an additional discount of 5% for transactions made within the last 30 days, reflecting local promotions
print("\n6.1 Stored Procedure Enhancement:") # This function will be called by the cursor execute below to get the value from the table orders and transaction
def calculate_discount1(amount, transaction_date):
    try:
        date_format = '%Y-%m-%d'        
        s_date = date.today() - timedelta(days=6)
        start_date = s_date.strftime(date_format)

        e_date = date.today()
        end_date = e_date.strftime(date_format)
             
        base_discount = amount * 0.05
        discounted1 = amount - base_discount

        if transaction_date >= start_date and transaction_date <= end_date:
            add_discount = amount * 0.05
            discounted = amount - (base_discount + add_discount)
            print(transaction_date) # to show which date are being calculate but based on the if functions
            return discounted
        else:
            print(transaction_date) # to show which date are being calculate but based on the if functions
            return discounted1
    
    except Exception as e:
        # Handle the exception
        print(f"Error calculating discount: {e}")
        return None
    finally:
        # Cleanup resources (if necessary)
        pass
    #cursor.close()
    #conn.close

conn.create_function("calculate_discount1", 2, calculate_discount1) # This will create the function. Also need to make it 2 based on the number of arguments also need to modify the select statement below

cursor.execute("""
SELECT o.product, calculate_discount1(o.amount, t.transaction_date) AS discounted_amount, t.transaction_date
FROM orders o
INNER JOIN transactions t ON o.id = t.id;
""")
data = cursor.fetchall()
#print(data)
print("\n\n 6.1 Products with 0.05 discount and additional discount based on the time specified with transaction date")
df = pd.DataFrame(data, columns=["PRODUCTS", "discounted", "TRANSACTION_DATE"])
df["discounted"] = df["discounted"].apply(lambda x: f"₱{x:.2f}")
print(df)


# 6.2 Update existing records and insert new records to reflect the changes
print("\n6.2.1 Update existing records:")

cursor.execute("""
UPDATE orders AS o
SET discounted_amount = calculate_discount1(o.amount, o.order_date)
""")
conn.commit()
print("Discount amounts updated successfully")


# we need to remark this because it will add more records - working
def addrecord():
  print("\n6.2.2 Insert new records to reflect the changes:")
  transaction_date = date.today() - timedelta(days=15)
  formatted_date = transaction_date.strftime('%Y-%m-%d')

  # Insert into Orders table
  cursor.execute("""
  INSERT INTO orders (product, amount, order_date, customer_id, transaction_id)
  VALUES ('Product Name', 100.00, ?, 1, 2)
  """, (formatted_date,))
  #
  # Get the last inserted order ID
  last_order_id = cursor.lastrowid
  #
  # Insert into Transactions table with the retrieved order ID
  cursor.execute("""
  INSERT INTO transactions (transaction_date, order_id)
  VALUES (?, ?)
  """, (formatted_date, last_order_id))
  #
  conn.commit()
  cursor.close()

# Add new records in orders
#addrecord()


# 7. Triggers:
'''
Create a trigger that updates the transaction_date in the Transactions table whenever a new order is inserted into the Orders table, aligning with local business practices.
Insert a new order and observe the automatic update of the transaction_date in the Transactions table.

'''
print("\n7 Create Triggers - one time run only:")
def create_triggers():
    cursor.execute("""
    CREATE TRIGGER update_transaction_date
    AFTER INSERT ON orders
    FOR EACH ROW
    BEGIN
    INSERT INTO transactions (transaction_date)
    VALUES (DATE('now'));
    END;
    """)
    conn.commit()
create_triggers()

# Add Orders entry and trigger to create date on Transaction Table
def addorders():
    cursor.execute("""
    INSERT INTO orders (customer_id, product, amount, order_date)
    VALUES (3, 'Puto', 190.00, (DATE('now')));
    """)
    order_id = cursor.lastrowid
    conn.commit()
    print("Triggers Complete")
#addorders()

