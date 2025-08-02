
import sqlite3

# Connect globally
conn = sqlite3.connect("db/inventory.db")
cursor = conn.cursor()


# create a new product
def create(name, category, color, quantity, price):
    cursor.execute("""
        INSERT INTO products (name, category, color, quantity, price)
        VALUES (?, ?, ?, ?, ?)
    """, (name, category, color, quantity, price))
    conn.commit()

# Fetch a single product by ID
def read(product_ids=None):
    if product_ids is None:
        # Read all products
        cursor.execute("SELECT * FROM products")
        return cursor.fetchall()
    
    elif isinstance(product_ids, int):
        # Read one product by ID
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_ids,))
        return cursor.fetchone()
    
    elif isinstance(product_ids, list):
        # Read multiple specific IDs
        placeholders = ','.join('?' for _ in product_ids)
        query = f"SELECT * FROM products WHERE id IN ({placeholders})"
        cursor.execute(query, product_ids)
        return cursor.fetchall()

#update any field of a product
def update(product_id, field, value):
    cursor.execute(f"UPDATE products SET {field} = ? WHERE id = ?", (value, product_id))
    conn.commit()

# Remove a product by ID
def delete(product_id):
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()

# find products by specific criteria
def filters(field, operator, value):
    query = f"SELECT * FROM products WHERE {field} {operator} ?"
    cursor.execute(query, (value,))
    return cursor.fetchall()

# sort by any field
def sort(field, descending=False):
    order = "DESC" if descending else "ASC"
    cursor.execute(f"SELECT * FROM products ORDER BY {field} {order}")
    return cursor.fetchall()

# copy an existing product
def replicate(product_id):
    product = read(product_id)
    if product:
        _, name, category, color, quantity, price = product
        create(name, category, color, quantity, price)


if __name__ == "__main__":
	print("Read item 3.")
	print(read(3))
	
	print("\nRead the times 3, 19, 20.")
	print(read([3, 19, 20]))
	
	print("\nFind products that cost less than 50.")
	print(filter("category", "<", ""))
	
