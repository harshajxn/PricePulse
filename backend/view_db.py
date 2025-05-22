import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("pricepulse.db")
cursor = conn.cursor()

# Print all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

# Print all rows from the 'products' table
print("\nEntries in 'products' table:")
cursor.execute("SELECT * FROM products")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
