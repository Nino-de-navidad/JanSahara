import gspread
import mysql.connector
from google.oauth2.service_account import Credentials


# ============================================================
# GOOGLE SHEETS CONNECTION
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

credentials = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

client = gspread.authorize(credentials)

# PUT YOUR ACTUAL SPREADSHEET ID HERE
SPREADSHEET_ID = "1iW23X-_CEJImw8aI2x-6xKtiy4NjU_-6QwP4YypPymc"

spreadsheet = client.open_by_key(SPREADSHEET_ID)

# Use first worksheet
sheet = spreadsheet.get_worksheet(0)

print("Connected to Google Sheet:", spreadsheet.title)
print("Worksheet:", sheet.title)


# ============================================================
# READ GOOGLE SHEET
# ============================================================

headers = sheet.row_values(1)
rows = sheet.get_all_values()

print("Total columns:", len(headers))
print("Total rows:", len(rows))


if len(rows) <= 1:
    print("No form responses found.")
    exit()


# ============================================================
# MYSQL CONNECTION
# ============================================================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2232",
    database="govt_scheme_ai"
)

cursor = db.cursor()

print("Connected to MySQL database: govt_scheme_ai")


# ============================================================
# GOOGLE SHEET HEADER → MYSQL COLUMN MAPPING
# ============================================================

COLUMN_MAP = {

    "Age": "age",

    "Gender": "gender",

    "Marital Status": "marital_status",

    "Are you and Indian Citizen?": "citizenship",

    "State/Union Territory of Residence": "state",

    "  What type of area do you live in?  ": "area_type",

    "Which social category do you belong to?": "social_category",

    "Do you belong to a Below Poverty Line (BPL) household? ": "bpl_status",

    "  Do you have a ration card?  ": "ration_card",

    "  What type of ration card do you have?  ": "ration_card_type",

    "  Are you currently studying?  ": "currently_studying",

    "What is your highest completed educational qualification?  ": "highest_qualification",

    " What level of education are you currently pursuing?  ": "current_education_level",

    "What is your course/stream?  ": "course_stream",

    "What is your mode of study?": "study_mode",

    "Which Year of study are you currently in?": "year_of_study",

    "What was your percentage in your most recent completed examination?  ": "academic_percentage",

    "What is your current employment status?": "employment_status",

    "What is your primary occupation?": "occupation",

    "Are you currently looking for a job?": "job_seeking",

    "Are you interested in skill-development or vocational training?": "skill_development_interest",

    "Are you interested in starting or expanding a business?": "entrepreneurship_interest",

    "What is your approximate annual household income?  ": "annual_household_income",

    "What is your approximate annual personal income?": "annual_individual_income",

    "How many people live in your household?": "household_size",

    "How many children are there in your household?  ": "number_of_children",

    "How many dependents are there in your household?  ": "number_of_dependents",

    "Is your household primarily headed by a woman?": "women_headed_household",

    "Is your household a single-parent household?": "single_parent_household",

    "Are you one of the primary earning members of your household?  ": "primary_earner",

    "Do you have a disability or disability-related eligibility condition?  ": "disability_status",

    "What is your disability percentage?": "disability_percentage",

    "Do you have a government-issued disability certificate?": "disability_certificate",

    "Are you widow/widower?": "widow_status",

    "Are you an orphan?": "orphan_status",

    "Are you involved in agriculture or agricultural activities?  ": "involved_in_agriculture",

    "What is your role in agriculture?  ": "agriculture_role",

    "Wat is your land ownership status?": "land_ownership",

    "Approximately how much agricultural land do you own/use?  ": "land_holding_acres",

    "What type of agricultural activity do you primarily undertake?": "agriculture_type",

    "What is your ousing status?": "house_ownership",

    "What type of house  you live in?": "house_type",

    "Does your household have an electricity connection?": "electricity_connection",

    "What type of toilet facility does your household use?": "toilet_facility",

    "What is your primary source of drinking water?": "drinking_water_source",

    "How comfortable are you with using digital services?": "digital_literacy",

    "What type of smartphone access do you have?": "smartphone_access",

    "How frequently do you have access to the Internet?": "internet_access",

    "Which skills do you currently have?": "skills",

    "What type of government support are you looking for?": "scheme_interests",

    "What is your PRIMARY requirement?": "primary_requirement",

    "Are you currently recieving benefits from any government scheme?": "receiving_government_benefits",

    "Which government schemes are you currently recieving benefits from?": "current_schemes",

    "Have you previously applied for any government scheme?": "previous_scheme_application",

    "Was your previous application rejected?": "previous_application_rejected",

    "Which of the following documents do you currently have?": "available_documents",

    "Is the Information you provided accurate to the best of your knowledge?": "information_accuracy_confirmation"
}


# ============================================================
# MYSQL COLUMN LIST
# ============================================================

mysql_columns = [
    "age",
    "gender",
    "marital_status",
    "citizenship",
    "state",
    "district",
    "area_type",
    "social_category",
    "bpl_status",
    "ration_card",
    "ration_card_type",
    "currently_studying",
    "highest_qualification",
    "current_education_level",
    "course_stream",
    "institution_type",
    "study_mode",
    "year_of_study",
    "academic_percentage",
    "employment_status",
    "occupation",
    "job_seeking",
    "skill_development_interest",
    "entrepreneurship_interest",
    "annual_household_income",
    "annual_individual_income",
    "household_size",
    "number_of_children",
    "number_of_dependents",
    "women_headed_household",
    "single_parent_household",
    "primary_earner",
    "disability_status",
    "disability_percentage",
    "disability_certificate",
    "widow_status",
    "orphan_status",
    "involved_in_agriculture",
    "agriculture_role",
    "land_ownership",
    "land_holding_acres",
    "agriculture_type",
    "house_ownership",
    "house_type",
    "electricity_connection",
    "toilet_facility",
    "drinking_water_source",
    "digital_literacy",
    "smartphone_access",
    "internet_access",
    "skills",
    "scheme_interests",
    "primary_requirement",
    "receiving_government_benefits",
    "current_schemes",
    "previous_scheme_application",
    "previous_application_rejected",
    "available_documents",
    "information_accuracy_confirmation"
]


# ============================================================
# HELPER FUNCTION
# ============================================================

def clean_value(value):

    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value


# ============================================================
# GENERATE NEXT USER ID
# ============================================================

cursor.execute("""
    SELECT user_id
    FROM users
    WHERE user_id LIKE 'JAN%'
    ORDER BY CAST(SUBSTRING(user_id, 4) AS UNSIGNED) DESC
    LIMIT 1
""")

result = cursor.fetchone()

if result:
    last_id = result[0]
    last_number = int(last_id[3:])
    next_number = last_number + 1
else:
    next_number = 1


# ============================================================
# PROCESS EACH GOOGLE SHEET RESPONSE
# ============================================================

for sheet_row_number, row in enumerate(rows[1:], start=2):

    print("\nProcessing Google Sheet row:", sheet_row_number)

    # --------------------------------------------------------
    # DUPLICATE CHECK
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT user_id
        FROM users
        WHERE google_sheet_row = %s
        """,
        (sheet_row_number,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        print(
            "Already imported:",
            existing_user[0],
            "- skipping row"
        )
        continue


    # --------------------------------------------------------
    # CREATE USER ID
    # --------------------------------------------------------

    user_id = f"JAN{next_number:05d}"
    next_number += 1


    # --------------------------------------------------------
    # CREATE DATA DICTIONARY
    # --------------------------------------------------------

    data = {}

    for column_number, header in enumerate(headers):

        if column_number >= len(row):
            value = None
        else:
            value = clean_value(row[column_number])

        if header in COLUMN_MAP:

            mysql_column = COLUMN_MAP[header]

            data[mysql_column] = value


    # --------------------------------------------------------
    # IMPORTANT:
    # district and institution_type are not currently present
    # in the Google Sheet headers you provided.
    # --------------------------------------------------------

    data["district"] = None
    data["institution_type"] = None


    # --------------------------------------------------------
    # BUILD INSERT
    # --------------------------------------------------------

    columns = ["user_id", "google_sheet_row"]

    values = [user_id, sheet_row_number]

    for column in mysql_columns:

        columns.append(column)

        values.append(
            data.get(column)
        )


    placeholders = ", ".join(["%s"] * len(columns))

    column_names = ", ".join(
        f"`{column}`"
        for column in columns
    )


    sql = f"""
        INSERT INTO users
        ({column_names})
        VALUES
        ({placeholders})
    """


    # --------------------------------------------------------
    # INSERT INTO MYSQL
    # --------------------------------------------------------

    try:

        cursor.execute(sql, values)

        db.commit()

        print(
            "SUCCESS:",
            user_id,
            "inserted successfully."
        )

    except mysql.connector.Error as error:

        db.rollback()

        print(
            "ERROR inserting",
            user_id,
            ":",
            error
        )


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()
db.close()

print("\n========================================")
print("Google Sheets → MySQL import completed")
print("========================================")