import os
from dotenv import load_dotenv
import mysql.connector

from recommendation_engine import generate_recommendations
from eligibility_engine import check_eligibility

load_dotenv()

TEST_USER_ID = "USR0002"


def main():

    # -------------------------------------------------
    # 1. Connect to database
    # -------------------------------------------------
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "govt_scheme_ai")
    )

    cursor = conn.cursor(dictionary=True)

    # -------------------------------------------------
    # 2. Get test user
    # -------------------------------------------------
    cursor.execute(
        "SELECT * FROM users WHERE user_id = %s",
        (TEST_USER_ID,)
    )

    user = cursor.fetchone()

    if not user:
        print(f"ERROR: User {TEST_USER_ID} not found.")
        cursor.close()
        conn.close()
        return

    # -------------------------------------------------
    # 3. Get all schemes
    # -------------------------------------------------
    cursor.execute(
        "SELECT * FROM government_schemes ORDER BY scheme_id"
    )

    schemes = cursor.fetchall()

    print("=" * 70)
    print("JANSAHARA - STAGE 2.6 VALIDATION")
    print("=" * 70)

    print(f"Test User     : {TEST_USER_ID}")
    print(f"Total Schemes : {len(schemes)}")
    print()

    # -------------------------------------------------
    # 4. Run eligibility for all 100 schemes
    # -------------------------------------------------
    eligibility_results = []

    for scheme in schemes:

        result = check_eligibility(
            user,
            scheme
        )

        eligibility_results.append(result)

    # -------------------------------------------------
    # 5. Eligibility statistics
    # -------------------------------------------------
    eligible = 0
    verification_required = 0
    not_eligible = 0
    unknown = 0

    for result in eligibility_results:

        status = result.get(
            "eligibility",
            "Unknown"
        )

        if status == "Likely Eligible":
            eligible += 1

        elif status == "Potentially Eligible - Verification Required":
            verification_required += 1

        elif status == "Likely Not Eligible":
            not_eligible += 1

        else:
            unknown += 1

    # -------------------------------------------------
    # 6. Generate recommendations
    # -------------------------------------------------
    recommendation_output = generate_recommendations(
        user,
        schemes,
        eligibility_results,
        top_n=10
    )

    recommendations = recommendation_output.get(
        "recommendations",
        []
    )

    total_candidates = recommendation_output.get(
        "total_candidates",
        0
    )

    # -------------------------------------------------
    # 7. Recommendation statistics
    # -------------------------------------------------
    scored = 0
    missing_scores = []

    for recommendation in recommendations:

        score = recommendation.get(
            "recommendation_score"
        )

        if score is not None:
            scored += 1
        else:
            missing_scores.append(
                recommendation.get("scheme_id")
            )

    # -------------------------------------------------
    # 8. Check duplicate IDs
    # -------------------------------------------------
    recommendation_ids = [
        r.get("scheme_id")
        for r in recommendations
    ]

    duplicates = [
        scheme_id
        for scheme_id in set(recommendation_ids)
        if recommendation_ids.count(scheme_id) > 1
    ]

    # -------------------------------------------------
    # 9. Print validation summary
    # -------------------------------------------------
    print("ELIGIBILITY SUMMARY")
    print("-" * 70)

    print(f"Likely Eligible                       : {eligible}")
    print(
        f"Potentially Eligible - Verification : "
        f"{verification_required}"
    )
    print(f"Likely Not Eligible                   : {not_eligible}")
    print(f"Unknown / Other                       : {unknown}")

    print()
    print("RECOMMENDATION SUMMARY")
    print("-" * 70)

    print(f"Total schemes loaded                 : {len(schemes)}")
    print(f"Candidates after eligibility filter  : {total_candidates}")
    print(f"Top recommendations generated        : {len(recommendations)}")
    print(f"Recommendations with scores          : {scored}")

    print()
    print("DATA INTEGRITY")
    print("-" * 70)

    print(f"Duplicate recommendation IDs         : {len(duplicates)}")
    print(f"Missing recommendation scores        : {len(missing_scores)}")

    # -------------------------------------------------
    # 10. Top 10 recommendations
    # -------------------------------------------------
    print()
    print("=" * 70)
    print("TOP 10 RECOMMENDATIONS")
    print("=" * 70)

    for i, recommendation in enumerate(
        recommendations,
        start=1
    ):

        print(
            f"{i}. {recommendation.get('scheme_name')}"
        )

        print(
            f"   Scheme ID    : "
            f"{recommendation.get('scheme_id')}"
        )

        print(
            f"   Category     : "
            f"{recommendation.get('scheme_category')}"
        )

        print(
            f"   Eligibility  : "
            f"{recommendation.get('eligibility')}"
        )

        print(
            f"   Eligibility Score : "
            f"{recommendation.get('eligibility_score')}"
        )

        print(
            f"   Recommendation Score : "
            f"{recommendation.get('recommendation_score')}"
        )

        print()

    # -------------------------------------------------
    # 11. Final Stage 2.6 check
    # -------------------------------------------------
    print("=" * 70)

    if (
        len(schemes) == 100
        and len(eligibility_results) == 100
        and len(recommendations) <= 10
        and scored == len(recommendations)
        and len(duplicates) == 0
        and len(missing_scores) == 0
    ):
        print("STAGE 2.6 STATUS: PASSED")
    else:
        print("STAGE 2.6 STATUS: REVIEW REQUIRED")

    print("=" * 70)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()