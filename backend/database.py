import sqlite3

def init_db():
    conn = sqlite3.connect('pricepulse.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price TEXT,
            url TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_product_to_db(product_data, url):
    conn = sqlite3.connect('pricepulse.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO products (title, price, url, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (product_data['title'], product_data['price'], url, product_data['timestamp']))

    conn.commit()
    conn.close()
