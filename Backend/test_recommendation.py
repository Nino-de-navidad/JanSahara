from recommendation_engine import generate_recommendations


# Test user profile
user = {
    "age": 27,
    "gender": "Male",
    "state": "Maharashtra",
    "social_category": "General",
    "currently_studying": "Yes",
    "current_education_level": "Undergraduate",
    "highest_qualification": "Undergraduate",
    "employment_status": "Student",
    "bpl_status": "Yes",
    "disability_status": "No",
    "agriculture_status": "No"
}


# Temporary test schemes
schemes = [
    {
        "scheme_id": "EDU001",
        "scheme_name": "Test Education Scholarship",
        "scheme_category": "Education / Student",
        "state_scope": "All India",
        "gender_eligibility": "All",
        "social_category": "All",
        "education_level": "Undergraduate",
        "target_beneficiary": "Students",
        "eligibility_summary": "For undergraduate students",
        "scheme_description": "Scholarship for students pursuing higher education"
    },
    {
        "scheme_id": "FIN001",
        "scheme_name": "Pradhan Mantri Mudra Yojana",
        "scheme_category": "Financial / Banking",
        "state_scope": "All India",
        "gender_eligibility": "All",
        "social_category": "All",
        "education_level": "N/A",
        "target_beneficiary": "Entrepreneurs and small businesses",
        "eligibility_summary": "For eligible entrepreneurs",
        "scheme_description": "Financial support for micro enterprises"
    }
]


# Eligibility results corresponding to the schemes
eligibility_results = [
    {
        "scheme_id": "EDU001",
        "eligibility": "Likely Eligible",
        "match_score": 100.0
    },
    {
        "scheme_id": "FIN001",
        "eligibility": "Likely Eligible",
        "match_score": 100.0
    }
]


# Generate recommendations
result = generate_recommendations(
    user,
    schemes,
    eligibility_results,
    top_n=10
)


# Print result
print("\n===== RECOMMENDATION RESULTS =====\n")

print("Total Candidates:",
      result["total_candidates"])

print("\nTop Recommendations:\n")

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

    print()