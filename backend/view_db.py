import sqlite3

DATABASE_NAME = 'pricepulse.db'

def view_data():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("--- Tables ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(table['name'])

    print("\n--- Tracked Products ---")
    cursor.execute("SELECT id, url, title, image_url, last_checked_at, created_at FROM tracked_products")
    rows = cursor.fetchall()
    if not rows:
        print("No products being tracked.")
    for row in rows:
        print(f"ID: {row['id']}, URL: {row['url'][:50]}..., Title: {row['title'][:30]}..., Img: {row['image_url'] is not None}, LastChecked: {row['last_checked_at']}")

    print("\n--- Price History (latest 5 per product) ---")
    cursor.execute("SELECT DISTINCT product_url FROM price_history")
    product_urls = [row['product_url'] for row in cursor.fetchall()]

    if not product_urls:
        print("No price history available.")

    for p_url in product_urls:
        print(f"\nHistory for: {p_url[:60]}...")
        cursor.execute("""
            SELECT timestamp, price FROM price_history
            WHERE product_url = ?
            ORDER BY timestamp DESC
            LIMIT 5
        """, (p_url,))
        history_rows = cursor.fetchall()
        if not history_rows:
            print("  No history entries for this product yet.")
        for h_row in history_rows:
            print(f"  Timestamp: {h_row['timestamp']}, Price: {h_row['price']}")

    conn.close()

if __name__ == "__main__":
    view_data()