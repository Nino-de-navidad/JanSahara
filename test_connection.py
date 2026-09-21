import gspread
import mysql.connector
from google.oauth2.service_account import Credentials


# =========================
# GOOGLE SHEETS CONNECTION
# =========================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

credentials = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

client = gspread.authorize(credentials)

# Replace this with your actual Google Spreadsheet ID
SPREADSHEET_ID = "1iW23X-_CEJImw8aI2x-6xKtiy4NjU_-6QwP4YypPymc"

sheet = client.open_by_key(SPREADSHEET_ID).sheet1

data = sheet.get_all_records()

print("Google Sheets connected successfully!")
print("Number of responses:", len(data))


# =========================
# MYSQL CONNECTION
# =========================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2232",
    database="govt_scheme_ai"
)

print("MySQL connected successfully!")


# =========================
# FINAL TEST
# =========================

if len(data) > 0:
    print("Google Sheet contains responses.")
else:
    print("Google Sheet has no responses yet.")

print("Both connections are working!")

db.close()