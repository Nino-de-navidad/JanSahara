import mysql.connector

from eligibility_engine import check_eligibility
from recommendation_engine import generate_recommendations


import inspect
import recommendation_engine

print("\n===== CATEGORY FUNCTION SOURCE =====")
print(
    inspect.getsource(
        recommendation_engine.calculate_category_relevance
    )
)
print("===== END CATEGORY FUNCTION =====")


import recommendation_engine

print(
    "CATEGORY FUNCTION:",
    recommendation_engine.calculate_category_relevance.__code__.co_firstlineno
)

# ==========================================
# 1. CONNECT TO MYSQL
# ==========================================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2232",
    database="govt_scheme_ai"
)

cursor = db.cursor(dictionary=True)

print("\n===== DATABASE CONNECTED =====")


# ==========================================
# 2. GET LATEST USER
# ==========================================

cursor.execute("""
    SELECT *
    FROM users
    ORDER BY created_at DESC
    LIMIT 1
""")

user = cursor.fetchone()

if not user:
    print("No user found in users table.")
    cursor.close()
    db.close()
    exit()

print("\n===== USER LOADED =====")
print("User ID:", user.get("user_id"))


print("\n===== USER RECOMMENDATION FIELDS =====")

for field in [
    "gender",
    "currently_studying",
    "current_education_level",
    "employment_status",
    "job_seeking",
    "skill_development_interest",
    "entrepreneurship_interest",
    "involved_in_agriculture",
    "bpl_status",
    "scheme_interests",
    "primary_requirement"
]:
    print(
        field,
        "=>",
        repr(user.get(field))
    )

# ==========================================
# 3. GET ALL SCHEMES
# ==========================================

cursor.execute("""
    SELECT *
    FROM government_schemes
""")

schemes = cursor.fetchall()

print("\n===== SCHEMES LOADED =====")
print("Total schemes:", len(schemes))

print("\n===== CATEGORY FUNCTION DIRECT TEST =====")

for scheme_id in ["EDU003", "FIN001", "WOC003"]:
    scheme = next(
        s for s in schemes
        if s["scheme_id"] == scheme_id
    )

    score = recommendation_engine.calculate_category_relevance(
        user,
        scheme
    )

    print(
        scheme["scheme_name"],
        "=>",
        score
    )

# ==========================================
# 4. RUN ELIGIBILITY ENGINE
# ==========================================

eligibility_results = []

for scheme in schemes:

    result = check_eligibility(
        user,
        scheme
    )

    eligibility_results.append(result)


print("\n===== ELIGIBILITY COMPLETE =====")


# ==========================================
# 5. RUN RECOMMENDATION ENGINE
# ==========================================

result = generate_recommendations(
    user,
    schemes,
    eligibility_results,
    top_n=10
)

from recommendation_engine import debug_recommendation_score

for scheme, eligibility_result in zip(
    schemes,
    eligibility_results
):
    if scheme.get("scheme_id") in [
        "WOC003",
        "EDU003",
        "FIN001"
    ]:
        debug_recommendation_score(
            user,
            scheme,
            eligibility_result
        )

# ==========================================
# 6. DISPLAY RESULTS
# ==========================================

print("\n==========================================")
print("       JANSAHARA TOP 10 RECOMMENDATIONS")
print("==========================================")

print(
    "\nTotal Candidates:",
    result["total_candidates"]
)

print("\n")


for i, recommendation in enumerate(
    result["recommendations"],
    start=1
):

    print(
        f"{i}. {recommendation['scheme_name']}"
    )

    print(
        f"   Scheme ID: "
        f"{recommendation['scheme_id']}"
    )

    print(
        f"   Category: "
        f"{recommendation['scheme_category']}"
    )

    print(
        f"   Eligibility: "
        f"{recommendation['eligibility']}"
    )

    print(
        f"   Eligibility Score: "
        f"{recommendation['eligibility_score']}"
    )

    print(
        f"   Recommendation Score: "
        f"{recommendation['recommendation_score']}"
    )

    print("------------------------------------------")


# ==========================================
# 7. CLOSE DATABASE
# ==========================================

cursor.close()
db.close()

print("\n===== TEST COMPLETE =====")