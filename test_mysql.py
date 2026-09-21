import mysql.connector

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2232",
    database="govt_scheme_ai"
)

print("MySQL connected successfully!")

db.close()