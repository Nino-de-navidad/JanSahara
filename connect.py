import gspread
from google.oauth2.service_account import Credentials

# Google Sheets permission
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

# Load credentials
credentials = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

# Connect to Google
client = gspread.authorize(credentials)

# Your Google Spreadsheet ID
SPREADSHEET_ID = "1iW23X-_CEJImw8aI2x-6xKtiy4NjU_-6QwP4YypPymc"

# Open spreadsheet directly using its ID
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# Read all responses
data = sheet.get_all_records()

print("Google Sheet connected successfully!")
print("Number of responses:", len(data))

if len(data) > 0:
    print("\nFirst response:")
    print(data[0])
else:
    print("\nNo responses found yet.")