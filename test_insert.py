import mysql.connector

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2232",
    database="govt_scheme_ai"
)

cursor = db.cursor()

# Test user data
sql = """
INSERT INTO users (
    user_id,
    age,
    gender,
    marital_status,
    citizenship,
    state,
    district,
    area_type
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

values = (
    "JAN00001",
    21,
    "Male",
    "Single",
    "Yes",
    "Maharashtra",
    "Mumbai",
    "Urban"
)

cursor.execute(sql, values)

db.commit()

print("Test user inserted successfully!")

cursor.close()
db.close()