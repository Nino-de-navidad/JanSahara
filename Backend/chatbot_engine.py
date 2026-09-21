import re

from llm_engine import generate_llm_response

# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    if not text:
        return ""

    text = text.lower().strip()

    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(query):

    query = normalize_text(query)

    # --------------------------------------------------------
    # APPLICATION
    # --------------------------------------------------------

    application_keywords = [
        "how can i apply",
        "how do i apply",
        "how to apply",
        "where can i apply",
        "where to apply",
        "application process",
        "application procedure",
        "apply online",
        "apply offline",
        "documents required",
        "documents needed",
        "what documents",
        "application"
    ]

    for keyword in application_keywords:
        if keyword in query:
            return "application"

    # --------------------------------------------------------
    # ELIGIBILITY
    # --------------------------------------------------------

    eligibility_keywords = [
        "am i eligible",
        "am i eligible for",
        "is this scheme eligible for me",
        "do i qualify",
        "qualify for",
        "eligibility",
        "eligibility criteria",
        "eligibility requirements",
        "what are the eligibility",
        "who is eligible"
    ]

    for keyword in eligibility_keywords:
        if keyword in query:
            return "eligibility"

    # --------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------

    recommendation_keywords = [
        "recommend",
        "recommendation",
        "suggest",
        "suggestion",
        "scheme for me",
        "schemes for me",
        "eligible schemes",
        "what schemes",
        "which schemes",
        "schemes can i get",
        "schemes can i apply",
        "benefits can i get",
        "what benefits",
        "help me find",
        "suitable scheme"
    ]

    for keyword in recommendation_keywords:
        if keyword in query:
            return "recommendation"

    # --------------------------------------------------------
    # SCHEME INFORMATION
    # --------------------------------------------------------

    information_keywords = [
        "what is",
        "tell me about",
        "details",
        "information about",
        "information",
        "about this scheme",
        "benefits",
        "amount",
        "how much",
        "who can get"
    ]

    for keyword in information_keywords:
        if keyword in query:
            return "scheme_information"

    return "general"

# ============================================================
# EXTRACT SCHEME FROM QUERY
# ============================================================

def find_scheme(query, schemes):

    query = normalize_text(query)

    # --------------------------------------------------------
    # Exact scheme name / scheme ID matching
    # --------------------------------------------------------

    for scheme in schemes:

        scheme_name = normalize_text(
            scheme.get("scheme_name", "")
        )

        scheme_id = normalize_text(
            scheme.get("scheme_id", "")
        )

        if scheme_id and scheme_id in query:
            return scheme

        if scheme_name and scheme_name in query:
            return scheme

    # --------------------------------------------------------
    # Common abbreviations
    # --------------------------------------------------------

    abbreviations = {

        "pmjdy": "Pradhan Mantri Jan Dhan Yojana",

        "pmy": "Pradhan Mantri Yuva Yojana",

        "pmmy": "Pradhan Mantri Mudra Yojana",

        "pm svanidhi": "PM Street Vendor",

        "svanidhi": "PM Street Vendor",

        "cgtmse": "Credit Guarantee Fund Trust",

        "clcss": "Credit Linked Capital Subsidy",

        "inspire": "INSPIRE Scholarship",

        "she": "INSPIRE Scholarship"
    }

    for abbreviation, scheme_match in abbreviations.items():

        if abbreviation in query:

            scheme_match = normalize_text(
                scheme_match
            )

            for scheme in schemes:

                scheme_name = normalize_text(
                    scheme.get("scheme_name", "")
                )

                if scheme_match in scheme_name:
                    return scheme

    # --------------------------------------------------------
    # Word-based matching
    # --------------------------------------------------------

    query_words = set(query.split())

    best_scheme = None
    best_score = 0

    for scheme in schemes:

        scheme_name = normalize_text(
            scheme.get("scheme_name", "")
        )

        scheme_words = set(
            scheme_name.split()
        )

        if not scheme_words:
            continue

        common_words = query_words.intersection(
            scheme_words
        )

        score = len(common_words)

        if score > best_score:
            best_score = score
            best_scheme = scheme

    if best_score >= 2:
        return best_scheme

    return None


# ============================================================
# FORMAT RECOMMENDATIONS
# ============================================================

def format_recommendations(recommendations):

    if not recommendations:
        return (
            "I could not find any matching government schemes "
            "for your profile."
        )

    response = "Based on your profile, here are some relevant schemes:\n\n"

    for index, recommendation in enumerate(
        recommendations[:5],
        start=1
    ):

        name = recommendation.get(
            "scheme_name",
            "Unknown Scheme"
        )

        category = recommendation.get(
            "scheme_category",
            "General"
        )

        eligibility = recommendation.get(
            "eligibility",
            "Unknown"
        )

        score = recommendation.get(
            "recommendation_score",
            0
        )

        response += (
            f"{index}. {name}\n"
            f"   Category: {category}\n"
            f"   Eligibility: {eligibility}\n"
            f"   Recommendation Score: {score}\n\n"
        )

    return response


def build_llm_context(
    user,
    scheme=None,
    eligibility=None,
    recommendations=None
):

    context = ""

    # --------------------------------------------------------
    # USER PROFILE
    # --------------------------------------------------------

    if user:

        context += "USER PROFILE:\n"

        context += (
            f"Age: {user.get('age', 'N/A')}\n"
        )

        context += (
            f"Gender: {user.get('gender', 'N/A')}\n"
        )

        context += (
            f"State: {user.get('state', 'N/A')}\n"
        )

        context += (
            f"Education: {user.get('education', 'N/A')}\n"
        )

        context += "\n"

    # --------------------------------------------------------
    # SPECIFIC SCHEME
    # --------------------------------------------------------

    if scheme:

        context += (
            f"Official Source URL: "
            f"{scheme.get('official_source_url', 'N/A')}\n"
        )            

        context += "SCHEME INFORMATION:\n"

        context += (
            f"Scheme Name: "
            f"{scheme.get('scheme_name', 'N/A')}\n"
        )

        context += (
            f"Category: "
            f"{scheme.get('scheme_category', 'N/A')}\n"
        )

        context += (
            f"Target Beneficiary: "
            f"{scheme.get('target_beneficiary', 'N/A')}\n"
        )

        context += (
            f"Benefits: "
            f"{scheme.get('benefit_description', 'N/A')}\n"
        )

        context += (
            f"Eligibility Summary: "
            f"{scheme.get('eligibility_summary', 'N/A')}\n"
        )

        context += (
            f"Application Mode: "
            f"{scheme.get('application_mode', 'N/A')}\n"
        )

        context += (
            f"Application Portal: "
            f"{scheme.get('application_portal', 'N/A')}\n"
        )

        context += (
            f"Documents Required: "
            f"{scheme.get('documents_required', 'N/A')}\n"
        )

        context += "\n"

    # --------------------------------------------------------
    # ELIGIBILITY
    # --------------------------------------------------------

    if eligibility:

        context += "ELIGIBILITY RESULT:\n"

        context += (
            f"Eligibility: "
            f"{eligibility.get('eligibility', 'N/A')}\n"
        )

        context += (
            f"Match Score: "
            f"{eligibility.get('match_score', 0)}%\n"
        )

        context += "\n"

    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    if recommendations:

        context += "RECOMMENDED SCHEMES:\n"

        for recommendation in recommendations[:5]:

            context += (
                f"- {recommendation.get('scheme_name', 'N/A')}\n"
            )

            context += (
                f"  Category: "
                f"{recommendation.get('scheme_category', 'N/A')}\n"
            )

            context += (
                f"  Eligibility: "
                f"{recommendation.get('eligibility', 'N/A')}\n"
            )

            context += (
                f"  Recommendation Score: "
                f"{recommendation.get('recommendation_score', 0)}\n"
            )

    return context


# ============================================================
# MAIN CHAT PROCESSOR
# ============================================================

def process_chat(
    user,
    schemes,
    eligibility_results,
    recommendation_output,
    query
):

    intent = detect_intent(query)

    # --------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------

    if intent == "recommendation":

        recommendations = recommendation_output.get(
            "recommendations",
            []
        )

        context = build_llm_context(
            user=user,
            recommendations=recommendations
        )

        response = generate_llm_response(
            query,
            context
        )

        return {
            "intent": intent,
            "response": response,
            "recommendations": recommendations
        }

    # --------------------------------------------------------
    # SPECIFIC SCHEME QUERY
    # --------------------------------------------------------

    scheme = find_scheme(
        query,
        schemes
    )

    # --------------------------------------------------------
    # ELIGIBILITY
    # --------------------------------------------------------

    if intent == "eligibility":

        if not scheme:

            return {
                "intent": intent,
                "response": (
                    "Please mention the name of the "
                    "government scheme you want to check."
                )
            }

        scheme_id = scheme.get("scheme_id")

        eligibility = None

        for result in eligibility_results:

            if result.get("scheme_id") == scheme_id:
                eligibility = result
                break

        if not eligibility:

            return {
                "intent": intent,
                "response": (
                    "I could not find eligibility information "
                    "for this scheme."
                )
            }

        status = eligibility.get(
            "eligibility",
            "Unknown"
        )

        score = eligibility.get(
            "match_score",
            0
        )

        context = build_llm_context(
            user=user,
            scheme=scheme,
            eligibility=eligibility
        )

        response = generate_llm_response(
            query,
            context
        )

        return {
            "intent": intent,
            "scheme_id": scheme_id,
            "scheme_name": scheme.get("scheme_name"),
            "eligibility": status,
            "eligibility_score": score,
            "response": response
        }

    # --------------------------------------------------------
    # APPLICATION INFORMATION
    # --------------------------------------------------------

    if intent == "application":

        if not scheme:

            return {
                "intent": intent,
                "response": (
                    "Please mention the name of the scheme "
                    "you want application information for."
                )
            }

        application_mode = scheme.get(
            "application_mode",
            "Not available"
        )

        portal = scheme.get(
            "application_portal",
            "Not available"
        )

        documents = scheme.get(
            "documents_required",
            "Not available"
        )

        context = build_llm_context(
            user=user,
            scheme=scheme
        )

        response = generate_llm_response(
            query,
            context
        )

        return {
            "intent": intent,
            "scheme_id": scheme.get("scheme_id"),
            "scheme_name": scheme.get("scheme_name"),
            "response": response
        }

    # --------------------------------------------------------
    # SCHEME INFORMATION
    # --------------------------------------------------------

    if intent == "scheme_information":

        if not scheme:

            return {
                "intent": intent,
                "response": (
                    "Please mention the name of the scheme "
                    "you want information about."
                )
            }

        context = build_llm_context(
            user=user,
            scheme=scheme
        )

        response = generate_llm_response(
            query,
            context
        )

        return {
            "intent": intent,
            "scheme_id": scheme.get("scheme_id"),
            "scheme_name": scheme.get("scheme_name"),
            "response": response
        }

    # --------------------------------------------------------
    # GENERAL
    # --------------------------------------------------------

    return {
        "intent": "general",
        "response": (
            "I can help you with government schemes. "
            "You can ask me things like:\n\n"
            "• What schemes are available for me?\n"
            "• Am I eligible for INSPIRE Scholarship?\n"
            "• How can I apply for PMMY?\n"
            "• Tell me about PMJDY."
        )
    }