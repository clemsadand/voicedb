import sqlite3
from faker import Faker
import random

#Initializz Faker
faker = Faker()

#reconnect or reuse DB
conn = sqlite3.connect("db/inventory.db")
cursor = conn.cursor()

#drop and recreate table to avoid duplicate entries
cursor.execute("DROP TABLE IF EXISTS products")
cursor.execute("""
CREATE TABLE products (
	id INTEGER PRIMARY KEY,
	name TEXT,
	category TEXT,
	color TEXT, 
	quantity INTEGER,
	price REAL
)
"""
)

#predefuned categories and colors
categories = ["Furniture", "Electronics", "Clothing", "Books", "Toys", "Kitchen"]
colors = ["red", "blue", "green", "black", "white", "orange", "purple"]

#let's generate 1000 fake products
products = []

for i in range(1, 21):
	category = random.choice(categories)
	name = faker.word().capitalize() + " " + faker.word().capitalize()
	color = random.choice(colors)
	quantity = random.randint(1, 100)
	price = round(random.uniform(5.0, 500.0), 2)
	products.append((i, name, category, color, quantity, price))
	
# Insert into DB
cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)", products)
conn.commit()

cursor.execute("SELECT * FROM products LIMIT 5")
for row in cursor.fetchall():
    print(row)


