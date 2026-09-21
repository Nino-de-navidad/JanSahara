from eligibility_engine import check_eligibility


# ==========================================================
# SAMPLE USER
# ==========================================================

user = {
    "age": 27,
    "gender": "Female",
    "state": "Madhya Pradesh",
    "social_category": "General",

    "annual_household_income":
        "2,50,001 - 5,00,000",

    "currently_studying": "Yes",

    "current_education_level":
        "Undergraduate",

    "highest_qualification":
        "Class 12",

    "employment_status":
        "Business Owner",

    "job_seeking": "No",

    "skill_development_interest":
        "Not Sure",

    "entrepreneurship_interest":
        "Not Sure",

    "bpl_status": "Yes",

    "disability_status": "No",

    "widow_status": "No",

    "orphan_status": "No",

    "number_of_children": 2,

    "involved_in_agriculture": "No",

    "house_type": "Kutcha",

    "house_ownership": "Own House",

    "ration_card": "No"
}


# ==========================================================
# SAMPLE SCHEME
# ==========================================================

scheme = {

    "scheme_id": "TEST001",

    "scheme_name":
        "Test Child Welfare Scheme",

    "scheme_category":
        "Women / Child",

    "scheme_type":
        "Financial Assistance",

    "target_beneficiary":
        "Women with children",

    "education_level":
        "All",

    "social_category":
        "All",

    "minimum_age": 18,

    "maximum_age": 60,

    "income_limit": 500000,

    "gender_eligibility":
        "Female",

    "state_scope":
        "Madhya Pradesh",

    "eligibility_summary":
        "Financial assistance for women with children",

    "scheme_description":
        "Financial assistance for women and child welfare",

    "classification_keywords":
        "women child welfare financial assistance"
}


# ==========================================================
# RUN ENGINE
# ==========================================================

result = check_eligibility(user, scheme)


# ==========================================================
# DISPLAY RESULT
# ==========================================================

print("\n===================================")
print("JANSAHARA ELIGIBILITY RESULT")
print("===================================")

print(
    "Eligibility:",
    result["eligibility"]
)

print(
    "Match Score:",
    result["match_score"],
    "%"
)


print("\nPASSED CHECKS:")

for check in result["passed_checks"]:

    print(
        "✓",
        check["reason"]
    )


print("\nFAILED CHECKS:")

for check in result["failed_checks"]:

    print(
        "✗",
        check["reason"]
    )


print("\nUNKNOWN CHECKS:")

for check in result["unknown_checks"]:

    print(
        "?",
        check["reason"]
    )