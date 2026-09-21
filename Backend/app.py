from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os

from eligibility_engine import check_eligibility
from recommendation_engine import generate_recommendations

from chatbot_engine import process_chat

load_dotenv()

app = Flask(__name__)
CORS(app)


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def empty_to_none(value):
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()

        if value == "":
            return None

    return value


# ==========================================================
# TEST DATABASE CONNECTION
# ==========================================================

@app.route("/test-db", methods=["GET"])
def test_db():

    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT DATABASE();")
        database = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "database": database,
            "message": "MySQL connection successful"
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================================
# USER REGISTRATION
# ==========================================================

@app.route("/api/register", methods=["POST"])
def register():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data received"
            }), 400

        email = data.get("email")
        password = data.get("password")

        # Validate email
        if not email:
            return jsonify({
                "status": "error",
                "message": "Email is required"
            }), 400

        # Validate password
        if not password:
            return jsonify({
                "status": "error",
                "message": "Password is required"
            }), 400

        if len(password) < 6:
            return jsonify({
                "status": "error",
                "message": "Password must contain at least 6 characters"
            }), 400

        email = email.strip().lower()

        conn = get_db_connection()
        cursor = conn.cursor()

        # --------------------------------------------------
        # Check whether email already exists
        # --------------------------------------------------

        cursor.execute(
            "SELECT user_id FROM user_accounts WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            cursor.close()
            conn.close()

            return jsonify({
                "status": "error",
                "message": "An account with this email already exists"
            }), 409

        # --------------------------------------------------
        # Generate new USER ID
        # --------------------------------------------------

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE user_id LIKE 'USR%'
            ORDER BY CAST(SUBSTRING(user_id, 4) AS UNSIGNED) DESC
            LIMIT 1
            """
        )

        last_user = cursor.fetchone()

        if last_user:

            last_number = int(last_user[0][3:])
            new_user_id = f"USR{last_number + 1:04d}"

        else:

            new_user_id = "USR0001"

        # --------------------------------------------------
        # Create empty profile
        # --------------------------------------------------

        cursor.execute(
            """
            INSERT INTO users (user_id)
            VALUES (%s)
            """,
            (new_user_id,)
        )

        # --------------------------------------------------
        # Hash password
        # --------------------------------------------------

        password_hash = generate_password_hash(password)

        # --------------------------------------------------
        # Create account
        # --------------------------------------------------

        cursor.execute(
            """
            INSERT INTO user_accounts (
                user_id,
                email,
                password_hash
            )
            VALUES (%s, %s, %s)
            """,
            (
                new_user_id,
                email,
                password_hash
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Account created successfully",
            "user_id": new_user_id
        }), 201

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================================
# USER LOGIN
# ==========================================================

@app.route("/api/login", methods=["POST"])
def login():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data received"
            }), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({
                "status": "error",
                "message": "Email and password are required"
            }), 400

        email = email.strip().lower()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Find account
        cursor.execute(
            """
            SELECT user_id, email, password_hash
            FROM user_accounts
            WHERE email = %s
            """,
            (email,)
        )

        account = cursor.fetchone()

        if not account:

            cursor.close()
            conn.close()

            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401

        # Verify password
        password_valid = check_password_hash(
            account["password_hash"],
            password
        )

        if not password_valid:

            cursor.close()
            conn.close()

            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401

        # Update last login
        cursor.execute(
            """
            UPDATE user_accounts
            SET last_login = CURRENT_TIMESTAMP
            WHERE user_id = %s
            """,
            (account["user_id"],)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Login successful",
            "user_id": account["user_id"],
            "email": account["email"]
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================================
# GET USER PROFILE
# ==========================================================

@app.route("/api/profile/<user_id>", methods=["GET"])
def get_user_profile(user_id):

    try:

        user_id = user_id.strip().upper()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:

            return jsonify({
                "status": "error",
                "message": "User profile not found"
            }), 404

        return jsonify({
            "status": "success",
            "profile": user
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==========================================================
# CHECK ELIGIBILITY FOR ALL SCHEMES
# ==========================================================

@app.route("/api/eligibility/<user_id>", methods=["GET"])
def check_user_eligibility(user_id):

    conn = None
    cursor = None

    try:

        # --------------------------------------------------
        # NORMALIZE USER ID
        # --------------------------------------------------

        user_id = user_id.strip().upper()

        # --------------------------------------------------
        # CONNECT TO DATABASE
        # --------------------------------------------------

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        # --------------------------------------------------
        # GET USER PROFILE
        # --------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:

            return jsonify({
                "status": "error",
                "message": "User profile not found"
            }), 404

        # --------------------------------------------------
        # GET ALL GOVERNMENT SCHEMES
        # --------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM government_schemes
            """
        )

        schemes = cursor.fetchall()

        if not schemes:

            return jsonify({
                "status": "error",
                "message": "No government schemes found"
            }), 404

        # --------------------------------------------------
        # RUN ELIGIBILITY ENGINE
        # --------------------------------------------------

        results = []

        for scheme in schemes:

            result = check_eligibility(
                user,
                scheme
            )

            results.append({

                "scheme_id":
                    scheme.get("scheme_id"),

                "scheme_name":
                    scheme.get("scheme_name"),

                "scheme_category":
                    scheme.get("scheme_category"),

                "eligibility":
                    result["eligibility"],

                "match_score":
                    result["match_score"],

                "passed_checks":
                    result["passed_checks"],

                "failed_checks":
                    result["failed_checks"],

                "unknown_checks":
                    result["unknown_checks"],

                "not_applicable_checks":
                    result["not_applicable_checks"]
            })

        # --------------------------------------------------
        # SORT BY MATCH SCORE
        # --------------------------------------------------

        results.sort(
            key=lambda x: x["match_score"],
            reverse=True
        )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        return jsonify({

            "status": "success",

            "user_id": user_id,

            "total_schemes_checked":
                len(results),

            "results":
                results

        }), 200

    except Exception as e:

        return jsonify({

            "status": "error",

            "message":
                str(e)

        }), 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ==========================================================
# RECOMMENDATIONS
# ==========================================================
# Stage 2.7
#
# Flow:
#
# User Profile
#      ↓
# MySQL
#      ↓
# Eligibility Engine
#      ↓
# Recommendation Engine
#      ↓
# Top 10 Schemes
# ==========================================================

@app.route("/api/recommendations/<user_id>", methods=["GET"])
def get_user_recommendations(user_id):

    conn = None
    cursor = None

    try:

        # --------------------------------------------------
        # NORMALIZE USER ID
        # --------------------------------------------------

        user_id = user_id.strip().upper()

        # --------------------------------------------------
        # CONNECT TO DATABASE
        # --------------------------------------------------

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        # --------------------------------------------------
        # GET USER PROFILE
        # --------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:

            return jsonify({
                "status": "error",
                "message": "User profile not found"
            }), 404

        # --------------------------------------------------
        # GET ALL GOVERNMENT SCHEMES
        # --------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM government_schemes
            """
        )

        schemes = cursor.fetchall()

        if not schemes:

            return jsonify({
                "status": "error",
                "message": "No government schemes found"
            }), 404

        # --------------------------------------------------
        # RUN ELIGIBILITY ENGINE
        # --------------------------------------------------

        eligibility_results = []

        for scheme in schemes:

            result = check_eligibility(
                user,
                scheme
            )

            eligibility_results.append(result)

        # --------------------------------------------------
        # RUN RECOMMENDATION ENGINE
        # --------------------------------------------------

        recommendation_output = generate_recommendations(
            user,
            schemes,
            eligibility_results,
            top_n=10
        )

        # --------------------------------------------------
        # GET RECOMMENDATIONS
        # --------------------------------------------------

        recommendations = recommendation_output.get(
            "recommendations",
            []
        )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        return jsonify({

            "status": "success",

            "user_id":
                user_id,

            "total_schemes":
                len(schemes),

            "total_candidates":
                recommendation_output.get(
                    "total_candidates",
                    0
                ),

            "recommendations":
                recommendations

        }), 200

    except Exception as e:

        return jsonify({

            "status": "error",

            "message":
                str(e)

        }), 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ==========================================================
# GOOGLE FORMS → MYSQL
# ==========================================================

@app.route("/api/users", methods=["POST"])
def add_user():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data received"
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # ======================================================
        # GET DATA
        # ======================================================

        user_id = data.get("user_id")
        google_sheet_row = data.get("google_sheet_row")

        # ======================================================
        # NEW SYSTEM:
        # UPDATE EXISTING USER PROFILE
        # ======================================================

        if user_id:

            user_id = user_id.strip().upper()

            # --------------------------------------------------
            # Check whether the user exists
            # --------------------------------------------------

            cursor.execute(
                """
                SELECT user_id
                FROM users
                WHERE user_id = %s
                """,
                (user_id,)
            )

            existing_user = cursor.fetchone()

            if not existing_user:

                cursor.close()
                conn.close()

                return jsonify({
                    "status": "error",
                    "message": "Invalid JanSahara User ID"
                }), 404

            # --------------------------------------------------
            # Update existing profile
            # --------------------------------------------------

            update_query = """
            UPDATE users
            SET
                age = %s,
                gender = %s,
                marital_status = %s,
                citizenship = %s,
                state = %s,
                district = %s,
                area_type = %s,
                social_category = %s,
                bpl_status = %s,
                ration_card = %s,
                ration_card_type = %s,
                currently_studying = %s,
                highest_qualification = %s,
                current_education_level = %s,
                course_stream = %s,
                institution_type = %s,
                study_mode = %s,
                year_of_study = %s,
                academic_percentage = %s,
                employment_status = %s,
                occupation = %s,
                job_seeking = %s,
                skill_development_interest = %s,
                entrepreneurship_interest = %s,
                annual_household_income = %s,
                annual_individual_income = %s,
                household_size = %s,
                number_of_children = %s,
                number_of_dependents = %s,
                women_headed_household = %s,
                single_parent_household = %s,
                primary_earner = %s,
                disability_status = %s,
                disability_percentage = %s,
                disability_certificate = %s,
                widow_status = %s,
                orphan_status = %s,
                involved_in_agriculture = %s,
                agriculture_role = %s,
                land_ownership = %s,
                land_holding_acres = %s,
                agriculture_type = %s,
                house_ownership = %s,
                house_type = %s,
                electricity_connection = %s,
                toilet_facility = %s,
                drinking_water_source = %s,
                digital_literacy = %s,
                smartphone_access = %s,
                internet_access = %s,
                skills = %s,
                scheme_interests = %s,
                primary_requirement = %s,
                receiving_government_benefits = %s,
                current_schemes = %s,
                previous_scheme_application = %s,
                previous_application_rejected = %s,
                available_documents = %s,
                information_accuracy_confirmation = %s,
                google_sheet_row = %s
            WHERE user_id = %s
            """

            update_values = (
                data.get("age"),
                data.get("gender"),
                data.get("marital_status"),
                data.get("citizenship"),
                data.get("state"),
                data.get("district"),
                data.get("area_type"),
                data.get("social_category"),
                data.get("bpl_status"),
                data.get("ration_card"),
                data.get("ration_card_type"),
                data.get("currently_studying"),
                data.get("highest_qualification"),
                data.get("current_education_level"),
                data.get("course_stream"),
                data.get("institution_type"),
                data.get("study_mode"),
                data.get("year_of_study"),
                empty_to_none(
                    data.get("academic_percentage")
                ),
                data.get("employment_status"),
                data.get("occupation"),
                data.get("job_seeking"),
                data.get("skill_development_interest"),
                data.get("entrepreneurship_interest"),
                data.get("annual_household_income"),
                data.get("annual_individual_income"),
                data.get("household_size"),
                data.get("number_of_children"),
                data.get("number_of_dependents"),
                data.get("women_headed_household"),
                data.get("single_parent_household"),
                data.get("primary_earner"),
                data.get("disability_status"),
                empty_to_none(
                    data.get("disability_percentage")
                ),
                data.get("disability_certificate"),
                data.get("widow_status"),
                data.get("orphan_status"),
                data.get("involved_in_agriculture"),
                data.get("agriculture_role"),
                data.get("land_ownership"),
                empty_to_none(
                    data.get("land_holding_acres")
                ),
                data.get("agriculture_type"),
                data.get("house_ownership"),
                data.get("house_type"),
                data.get("electricity_connection"),
                data.get("toilet_facility"),
                data.get("drinking_water_source"),
                data.get("digital_literacy"),
                data.get("smartphone_access"),
                data.get("internet_access"),
                data.get("skills"),
                data.get("scheme_interests"),
                data.get("primary_requirement"),
                data.get("receiving_government_benefits"),
                data.get("current_schemes"),
                data.get("previous_scheme_application"),
                data.get("previous_application_rejected"),
                data.get("available_documents"),
                data.get("information_accuracy_confirmation"),
                google_sheet_row,
                user_id
            )

            cursor.execute(
                update_query,
                update_values
            )

            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({
                "status": "success",
                "message": "User profile updated successfully",
                "user_id": user_id
            }), 200

        # ======================================================
        # OLD SYSTEM:
        # CREATE NEW USER
        #
        # This is kept for compatibility with old submissions
        # that don't contain a JanSahara User ID.
        # ======================================================

        if google_sheet_row:

            cursor.execute(
                """
                SELECT user_id
                FROM users
                WHERE google_sheet_row = %s
                """,
                (google_sheet_row,)
            )

            existing_user = cursor.fetchone()

            if existing_user:

                cursor.close()
                conn.close()

                return jsonify({
                    "status": "success",
                    "message": "This Google Sheet row already exists",
                    "user_id": existing_user[0]
                }), 200

        # --------------------------------------------------
        # Generate new User ID
        # --------------------------------------------------

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE user_id LIKE 'USR%'
            ORDER BY CAST(SUBSTRING(user_id, 4) AS UNSIGNED) DESC
            LIMIT 1
            """
        )

        last_user = cursor.fetchone()

        if last_user:

            last_number = int(last_user[0][3:])
            new_user_id = f"USR{last_number + 1:04d}"

        else:

            new_user_id = "USR0001"

        # --------------------------------------------------
        # Insert new user
        # --------------------------------------------------

        query = """
        INSERT INTO users (
            user_id,
            age,
            gender,
            marital_status,
            citizenship,
            state,
            district,
            area_type,
            social_category,
            bpl_status,
            ration_card,
            ration_card_type,
            currently_studying,
            highest_qualification,
            current_education_level,
            course_stream,
            institution_type,
            study_mode,
            year_of_study,
            academic_percentage,
            employment_status,
            occupation,
            job_seeking,
            skill_development_interest,
            entrepreneurship_interest,
            annual_household_income,
            annual_individual_income,
            household_size,
            number_of_children,
            number_of_dependents,
            women_headed_household,
            single_parent_household,
            primary_earner,
            disability_status,
            disability_percentage,
            disability_certificate,
            widow_status,
            orphan_status,
            involved_in_agriculture,
            agriculture_role,
            land_ownership,
            land_holding_acres,
            agriculture_type,
            house_ownership,
            house_type,
            electricity_connection,
            toilet_facility,
            drinking_water_source,
            digital_literacy,
            smartphone_access,
            internet_access,
            skills,
            scheme_interests,
            primary_requirement,
            receiving_government_benefits,
            current_schemes,
            previous_scheme_application,
            previous_application_rejected,
            available_documents,
            information_accuracy_confirmation,
            google_sheet_row
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s
        )
        """

        values = (
            new_user_id,
            data.get("age"),
            data.get("gender"),
            data.get("marital_status"),
            data.get("citizenship"),
            data.get("state"),
            data.get("district"),
            data.get("area_type"),
            data.get("social_category"),
            data.get("bpl_status"),
            data.get("ration_card"),
            data.get("ration_card_type"),
            data.get("currently_studying"),
            data.get("highest_qualification"),
            data.get("current_education_level"),
            data.get("course_stream"),
            data.get("institution_type"),
            data.get("study_mode"),
            data.get("year_of_study"),
            empty_to_none(
                data.get("academic_percentage")
            ),
            data.get("employment_status"),
            data.get("occupation"),
            data.get("job_seeking"),
            data.get("skill_development_interest"),
            data.get("entrepreneurship_interest"),
            data.get("annual_household_income"),
            data.get("annual_individual_income"),
            data.get("household_size"),
            data.get("number_of_children"),
            data.get("number_of_dependents"),
            data.get("women_headed_household"),
            data.get("single_parent_household"),
            data.get("primary_earner"),
            data.get("disability_status"),
            empty_to_none(
                data.get("disability_percentage")
            ),
            data.get("disability_certificate"),
            data.get("widow_status"),
            data.get("orphan_status"),
            data.get("involved_in_agriculture"),
            data.get("agriculture_role"),
            data.get("land_ownership"),
            empty_to_none(
                data.get("land_holding_acres")
            ),
            data.get("agriculture_type"),
            data.get("house_ownership"),
            data.get("house_type"),
            data.get("electricity_connection"),
            data.get("toilet_facility"),
            data.get("drinking_water_source"),
            data.get("digital_literacy"),
            data.get("smartphone_access"),
            data.get("internet_access"),
            data.get("skills"),
            data.get("scheme_interests"),
            data.get("primary_requirement"),
            data.get("receiving_government_benefits"),
            data.get("current_schemes"),
            data.get("previous_scheme_application"),
            data.get("previous_application_rejected"),
            data.get("available_documents"),
            data.get("information_accuracy_confirmation"),
            google_sheet_row
        )

        cursor.execute(
            query,
            values
        )

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "User successfully added",
            "user_id": new_user_id
        }), 201

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



@app.route("/api/chat/<user_id>", methods=["POST"])
def chat_with_user(user_id):

    conn = None
    cursor = None

    try:

        user_id = user_id.strip().upper()

        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "Request body is required"
            }), 400

        query = data.get("query", "").strip()

        if not query:
            return jsonify({
                "status": "error",
                "message": "Query is required"
            }), 400

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        # ----------------------------------------------------
        # GET USER
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:

            return jsonify({
                "status": "error",
                "message": "User profile not found"
            }), 404

        # ----------------------------------------------------
        # GET SCHEMES
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM government_schemes
            """
        )

        schemes = cursor.fetchall()

        if not schemes:

            return jsonify({
                "status": "error",
                "message": "No government schemes found"
            }), 404

        # ----------------------------------------------------
        # RUN ELIGIBILITY
        # ----------------------------------------------------

        eligibility_results = []

        for scheme in schemes:

            result = check_eligibility(
                user,
                scheme
            )

            # Keep scheme ID with result
            result["scheme_id"] = scheme.get(
                "scheme_id"
            )

            eligibility_results.append(result)

        # ----------------------------------------------------
        # RUN RECOMMENDATION
        # ----------------------------------------------------

        recommendation_output = generate_recommendations(
            user,
            schemes,
            eligibility_results,
            top_n=10
        )

        # ----------------------------------------------------
        # PROCESS CHAT QUERY
        # ----------------------------------------------------

        chat_result = process_chat(
            user,
            schemes,
            eligibility_results,
            recommendation_output,
            query
        )

        return jsonify({
            "status": "success",
            "user_id": user_id,
            "query": query,
            "intent": chat_result.get(
                "intent",
                "general"
            ),
            "response": chat_result.get(
                "response",
                ""
            ),
            "scheme_id": chat_result.get(
                "scheme_id"
            ),
            "scheme_name": chat_result.get(
                "scheme_name"
            ),
            "eligibility": chat_result.get(
                "eligibility"
            ),
            "eligibility_score": chat_result.get(
                "eligibility_score"
            )
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# Add these routes to app.py (before the START FLASK SERVER section)

@app.route("/api/schemes", methods=["GET"])
def get_schemes():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT scheme_id, scheme_name, government_level, state_scope,
                   ministry_department, scheme_category, scheme_type,
                   target_beneficiary, eligibility_summary, benefit_description,
                   application_mode, application_portal, scheme_description,
                   official_source_url, classification_keywords
            FROM government_schemes
            ORDER BY scheme_category, scheme_name
        """)
        schemes = cursor.fetchall()
        return jsonify({"status": "success", "total_schemes": len(schemes), "schemes": schemes}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route("/api/schemes/<scheme_id>", methods=["GET"])
def get_scheme(scheme_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM government_schemes WHERE scheme_id = %s", (scheme_id.strip().upper(),))
        scheme = cursor.fetchone()
        if not scheme:
            return jsonify({"status": "error", "message": "Scheme not found"}), 404
        return jsonify({"status": "success", "scheme": scheme}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()



# ==========================================================
# START FLASK SERVER
# ==========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

