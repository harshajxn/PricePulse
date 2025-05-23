import sqlite3

DATABASE_NAME = 'pricepulse.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table to store products users want to track
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracked_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            title TEXT,
            image_url TEXT,
            last_checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table to store price history for each tracked product
    # 'product_id' will be a foreign key to 'tracked_products.id'
    # For simplicity now, we'll just store the URL directly, but a FK is better practice.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_url TEXT NOT NULL,
            price TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (product_url) REFERENCES tracked_products (url) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

# Function to add a product to be tracked (or update its title/image)
def add_or_update_tracked_product(url, title, image_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO tracked_products (url, title, image_url)
            VALUES (?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
            title=excluded.title,
            image_url=excluded.image_url,
            last_checked_at=CURRENT_TIMESTAMP
        ''', (url, title, image_url))
        product_id = cursor.lastrowid
        if not product_id: # if ON CONFLICT occurred, get the existing id
             cursor.execute("SELECT id FROM tracked_products WHERE url = ?", (url,))
             row = cursor.fetchone()
             if row:
                 product_id = row['id']
        conn.commit()
        return product_id
    except sqlite3.IntegrityError as e:
        print(f"Error adding/updating tracked product {url}: {e}")
        return None
    finally:
        conn.close()

# Function to save a new price point for a product
def save_price_history(product_url, price, timestamp):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO price_history (product_url, price, timestamp)
            VALUES (?, ?, ?)
        ''', (product_url, price, timestamp))
        conn.commit()
    except Exception as e:
        print(f"Error saving price history for {product_url}: {e}")
    finally:
        conn.close()

# Function to get all products that need to be tracked
def get_all_tracked_product_urls():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM tracked_products")
    urls = [row['url'] for row in cursor.fetchall()]
    conn.close()
    return urls

# Function to get price history for a specific product URL
def get_product_price_history(product_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, price FROM price_history
        WHERE product_url = ?
        ORDER BY timestamp ASC
    ''', (product_url,))
    history = [{'timestamp': row['timestamp'], 'price': row['price']} for row in cursor.fetchall()]
    conn.close()
    return history

# Function to get details of a tracked product by URL
def get_tracked_product_details(product_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, image_url FROM tracked_products WHERE url = ?", (product_url,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"title": row["title"], "image_url": row["image_url"]}
    return None