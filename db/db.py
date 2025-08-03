import sqlite3
import threading
from contextlib import contextmanager

# Thread-local storage for database connections
_local = threading.local()

def get_connection():
    """Get a thread-local database connection"""
    if not hasattr(_local, 'conn'):
        _local.conn = sqlite3.connect("db/inventory.db", check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row  # Enable column access by name
    return _local.conn

@contextmanager
def get_cursor():
    """Context manager for database operations"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()

# Create a new product
def create(name, category, color, quantity, price):
    """Create a new product in the database"""
    with get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO products (name, category, color, quantity, price)
            VALUES (?, ?, ?, ?, ?)
        """, (name, category, color, quantity, price))
        return cursor.lastrowid

# Fetch products by ID(s) or all products
def read(product_ids=None):
    """
    Read products from database
    - product_ids=None: Read all products
    - product_ids=int: Read single product by ID
    - product_ids=list: Read multiple products by IDs
    """
    with get_cursor() as cursor:
        if product_ids is None:
            # Read all products
            cursor.execute("SELECT * FROM products ORDER BY id")
            return cursor.fetchall()
        
        elif isinstance(product_ids, int):
            # Read one product by ID
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_ids,))
            return cursor.fetchone()
        
        elif isinstance(product_ids, list):
            # Read multiple specific IDs
            if not product_ids:  # Empty list
                return []
            placeholders = ','.join('?' for _ in product_ids)
            query = f"SELECT * FROM products WHERE id IN ({placeholders}) ORDER BY id"
            cursor.execute(query, product_ids)
            return cursor.fetchall()
        
        else:
            raise ValueError("product_ids must be None, int, or list")

# Update any field of a product
def update(product_id, field, value):
    """Update a specific field of a product"""
    # Validate field name to prevent SQL injection
    allowed_fields = ['name', 'category', 'color', 'quantity', 'price']
    if field not in allowed_fields:
        raise ValueError(f"Invalid field '{field}'. Allowed fields: {allowed_fields}")
    
    with get_cursor() as cursor:
        # Check if product exists first
        cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
        if not cursor.fetchone():
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Update the field
        query = f"UPDATE products SET {field} = ? WHERE id = ?"
        cursor.execute(query, (value, product_id))
        
        if cursor.rowcount == 0:
            raise ValueError(f"No product updated with ID {product_id}")

# Remove a product by ID
def delete(product_id):
    """Delete a product by ID"""
    with get_cursor() as cursor:
        # Check if product exists first
        cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
        if not cursor.fetchone():
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Delete the product
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        
        if cursor.rowcount == 0:
            raise ValueError(f"No product deleted with ID {product_id}")

# Find products by specific criteria
def filters(field, operator, value):
    """Filter products by field, operator, and value"""
    # Validate field name to prevent SQL injection
    allowed_fields = ['id', 'name', 'category', 'color', 'quantity', 'price']
    if field not in allowed_fields:
        raise ValueError(f"Invalid field '{field}'. Allowed fields: {allowed_fields}")
    
    # Validate operator to prevent SQL injection
    allowed_operators = ['=', '!=', '<', '<=', '>', '>=', 'LIKE']
    if operator not in allowed_operators:
        raise ValueError(f"Invalid operator '{operator}'. Allowed operators: {allowed_operators}")
    
    with get_cursor() as cursor:
        query = f"SELECT * FROM products WHERE {field} {operator} ? ORDER BY id"
        
        # Handle LIKE operator for case-insensitive string matching
        if operator == 'LIKE':
            value = f"%{value}%"
        
        cursor.execute(query, (value,))
        return cursor.fetchall()

# Sort by any field
def sort(field, descending=False):
    """Sort products by a specific field"""
    # Validate field name to prevent SQL injection
    allowed_fields = ['id', 'name', 'category', 'color', 'quantity', 'price']
    if field not in allowed_fields:
        raise ValueError(f"Invalid field '{field}'. Allowed fields: {allowed_fields}")
    
    order = "DESC" if descending else "ASC"
    
    with get_cursor() as cursor:
        query = f"SELECT * FROM products ORDER BY {field} {order}"
        cursor.execute(query)
        return cursor.fetchall()

# Copy an existing product
def replicate(product_id):
    """Create a copy of an existing product"""
    with get_cursor() as cursor:
        # Get the original product
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Create a copy (excluding the ID)
        cursor.execute("""
            INSERT INTO products (name, category, color, quantity, price)
            VALUES (?, ?, ?, ?, ?)
        """, (product['name'], product['category'], product['color'], 
              product['quantity'], product['price']))
        
        return cursor.lastrowid

# Get database statistics
def get_stats():
    """Get database statistics"""
    with get_cursor() as cursor:
        stats = {}
        
        # Total products
        cursor.execute("SELECT COUNT(*) as total FROM products")
        stats['total_products'] = cursor.fetchone()['total']
        
        # Products by category
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM products 
            GROUP BY category 
            ORDER BY count DESC
        """)
        stats['by_category'] = cursor.fetchall()
        
        # Products by color
        cursor.execute("""
            SELECT color, COUNT(*) as count 
            FROM products 
            GROUP BY color 
            ORDER BY count DESC
        """)
        stats['by_color'] = cursor.fetchall()
        
        # Price statistics
        cursor.execute("""
            SELECT 
                MIN(price) as min_price,
                MAX(price) as max_price,
                AVG(price) as avg_price,
                SUM(quantity * price) as total_value
            FROM products
        """)
        stats['price_stats'] = cursor.fetchone()
        
        return stats

# Close all connections (useful for cleanup)
def close_connections():
    """Close all thread-local connections"""
    if hasattr(_local, 'conn'):
        _local.conn.close()
        delattr(_local, 'conn')

# Test the database functions
if __name__ == "__main__":
    print("🧪 Testing database functions...")
    
    try:
        # Test read all
        print("\n📊 All products:")
        products = read()
        print(f"Found {len(products)} products")
        
        if products:
            # Test read single
            print(f"\n🔍 Reading product {products[0]['id']}:")
            single_product = read(products[0]['id'])
            print(f"Product: {single_product['name']}")
            
            # Test filters
            print(f"\n🎨 Products with color '{products[0]['color']}':")
            filtered = filters('color', '=', products[0]['color'])
            print(f"Found {len(filtered)} products")
            
            # Test sort
            print(f"\n💰 Products sorted by price:")
            sorted_products = sort('price')
            for p in sorted_products[:3]:  # Show first 3
                print(f"  {p['name']}: ${p['price']}")
        
        # Test stats
        print(f"\n📈 Database statistics:")
        stats = get_stats()
        print(f"Total products: {stats['total_products']}")
        print(f"Categories: {len(stats['by_category'])}")
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        close_connections()
