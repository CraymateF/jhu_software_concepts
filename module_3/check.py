import psycopg2
connection = psycopg2.connect(
    dbname = "gradcafe",
    user="fadetoblack")

cursor = connection.cursor()
cursor.execute("SELECT * FROM gradcafe_main;")
records = cursor.fetchall()
print(f"Total records in gradcafe_main: {len(records)}")
print("Sample record:")
if records:
    print(records[0])
else:    print("No records found.")
cursor.close()
connection.close()