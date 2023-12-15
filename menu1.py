from tkinter import *
from tkinter import ttk
import sqlite3
import pandas as pd
import time as time
from datetime import timedelta, date


root = Tk()
root.title(" Pinoy Business Sales Menu ")
root.geometry("900x500")
df = None

# Databases
conn = sqlite3.connect('pinoybiz_sales.db')

# Create Cursor
cursor = conn.cursor()


# Output frame and text widget (defined outside functions)
output_frame = ttk.Frame(root, borderwidth=5, relief="groove")
output_frame.grid(row=15, column=0, columnspan=2)
output_text = Text(output_frame, font=("Courier New", 10), width=90, height=10)
output_text.pack(padx=10, pady=5)


# Common Task
def fetch_data_and_format(query, columns):
    # Databases
    #conn = sqlite3.connect('add.db')
    conn = sqlite3.connect('pinoybiz_sales.db')
    conn.create_function("calculate_discount1", 2, calculate_discount1)
    # Create Cursor
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)
    for col in df.columns:
        if col == "amount":
            df[col] = df[col].apply(lambda x: f"₱{x:.2f}")
    return df


def display_results(df): # to Clear Result
    output_text.delete(0.0, END)
    output_text.insert(END, df.to_string(index=False))

# Create Query 3.1
def query3_1():
    query = ""
    # Databases
    #conn = sqlite3.connect('add.db')
    conn = sqlite3.connect('pinoybiz_sales.db')

    # Create Cursor
    cursor = conn.cursor()

    query = """
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
        """

    columns = ["customer_id", "name", "product", "amount", "order_date", "total_amount"]
    df = fetch_data_and_format(query, columns)
    display_results(df)


# Create Query 3.2
def query3_2():
    query = """
        SELECT *
        FROM customers c
        WHERE c.id IN (
            SELECT customer_id
            FROM orders o
            GROUP BY customer_id
            HAVING SUM(amount) > 5000
        );
    """
    columns = ["customer_id", "name", "email"]
    df = fetch_data_and_format(query, columns)
    display_results(df)


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


def enchancement():
    query = """
    SELECT o.product, calculate_discount1(o.amount, t.transaction_date) AS discounted_amount, t.transaction_date
    FROM orders o
    INNER JOIN transactions t ON o.id = t.id;
    """
    columns = ["PRODUCTS", "discounted", "TRANSACTION_DATE"]
    df = fetch_data_and_format(query, columns)
    display_results(df)

def submit():
    conn = sqlite3.connect('pinoybiz_sales.db')
    cursor = conn.cursor()

    # Insert into Table
    cursor.execute("INSERT INTO orders (customer_id, product, amount, order_date) VALUES (?, ?, ?, ?)", 
                (customer_id_txt.get(), product_txt.get(), float(amount_txt.get()), order_date_txt.get()))

    # Commit Changes
    conn.commit()

    # Close connection
    conn.close()

    # Clear the text boxes
    customer_id_txt.delete(0, END)
    product_txt.delete(0, END)
    amount_txt.delete(0, END)
    order_date_txt.delete(0, END)


# Create Query Button
query_button3_1 = Button(root, text="3.1 Total Order Amount for each Customer", command=query3_1)
query_button3_1.grid(row=4, column=0, columnspan=2, pady=10, padx=10, ipadx=100)

query_button = Button(root, text="3.2 Implement a subquery to identify customers who have made transactions of more than PHP 5,000 in total.", command=query3_2)
query_button.grid(row=5, column=0, columnspan=2, pady=10, padx=10, ipadx=100)

query_button = Button(root, text="6 Functions", command=enchancement)
query_button.grid(row=6, column=0, columnspan=2, pady=10, padx=10, ipadx=100)


# Create Text Boxes
customer_id_txt = Entry(root, width=30)
customer_id_txt.grid(row=8, column=1, padx=20, pady=(30, 0))

product_txt = Entry(root, width=30)
product_txt.grid(row=9, column=1, padx=20)

amount_txt = Entry(root, width=30)
amount_txt.grid(row=10, column=1, padx=30 )

order_date_txt = Entry(root, width=30)
order_date_txt.grid(row=11, column=1, padx=30, pady=(0, 30))

# Create Text Box Labels

customer_id_label = Label(root, text="Customer ID")
customer_id_label.grid(row=8, column=0, padx=20, pady=(30, 0))

product_label = Label(root, text="Product")
product_label.grid(row=9, column=0, padx=20)

amount_label = Label(root, text="Amount")
amount_label.grid(row=10, column=0, padx=20)

order_date_label = Label(root, text="Order Date")
order_date_label.grid(row=11, column=0, padx=20, pady=(0, 10))

#Submit button
submit_button = Button(root, text="Add Record", command=submit)
submit_button.grid(row=12, column=0, columnspan=2, pady=10, padx=10, ipadx=10)

my_menu = Menu(root)
root.config(menu=my_menu)
root.mainloop()
conn.close()