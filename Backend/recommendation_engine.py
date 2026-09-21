# ==========================================================
# JanSahara Recommendation Engine
# Stage 2.1 - Recommendation Engine Skeleton
# ==========================================================

from typing import List, Dict, Any


# ==========================================================
# HELPER
# ==========================================================

def normalize(value):
    """
    Convert a value into a clean lowercase string.
    """
    if value is None:
        return ""

    return str(value).strip().lower()


# ==========================================================
# GET ELIGIBILITY RESULT
# ==========================================================

def get_eligibility_status(eligibility_result):
    """
    Extract eligibility status from an eligibility-engine result.
    """

    if not eligibility_result:
        return "unknown"

    return eligibility_result.get(
        "eligibility",
        "Unknown"
    )


# ==========================================================
# BASIC RECOMMENDATION CANDIDATE
# ==========================================================

def filter_candidates(candidates):
    filtered = []

    for candidate in candidates:

        eligibility_result = candidate.get(
            "eligibility_result",
            {}
        )

        status = eligibility_result.get(
            "eligibility",
            ""
        )

        # Remove only schemes where the user
        # is clearly not eligible
        if status != "Likely Not Eligible":
            filtered.append(candidate)

    return filtered

# ==========================================================
# BUILD RECOMMENDATION CANDIDATES
# ==========================================================

def build_candidates(schemes, eligibility_results):
    candidates = []

    for scheme, eligibility_result in zip(
        schemes,
        eligibility_results
    ):
        candidates.append({
            "scheme": scheme,
            "eligibility_result": eligibility_result
        })

    return candidates

# ==========================================================
# FILTER ELIGIBLE CANDIDATES
# ==========================================================

def filter_candidates(candidates):
    """
    Remove schemes that the eligibility engine has
    explicitly marked as not eligible.

    Potentially eligible schemes are retained because
    they may still be useful recommendations requiring
    verification.
    """

    filtered = []

    for candidate in candidates:

        eligibility = normalize(
            candidate.get("eligibility")
        )

        if eligibility == "likely not eligible":
            continue

        filtered.append(candidate)

    return filtered

# ==========================================================
# STAGE 2.2 - PROFILE MATCHING
# ==========================================================

def match_state(user, scheme):
    """
    Check whether the scheme's geographic coverage
    matches the user's state.
    """

    user_state = normalize(
        user.get("state")
    )

    scheme_state = normalize(
        scheme.get("state_scope")
    )

    if not user_state or not scheme_state:
        return 0.0

    if scheme_state in [
        "all india",
        "india",
        "national",
        "pan india",
        "all states",
        "all"
    ]:
        return 1.0

    if user_state in scheme_state:
        return 1.0

    return 0.0


# ==========================================================
# GENDER MATCH
# ==========================================================

def match_gender(user, scheme):
    user_gender = normalize(user.get("gender"))
    scheme_gender = normalize(scheme.get("gender_eligibility"))

    if not user_gender or not scheme_gender:
        return 0.5

    # Universal gender eligibility
    universal = [
        "all",
        "any",
        "both",
        "all genders",
        "all gender",
        "male / female",
        "male/female",
        "men and women",
        "men & women"
    ]

    if scheme_gender in universal:
        return 1.0

    # Female-only schemes
    female_terms = [
        "female",
        "women",
        "woman",
        "girl",
        "girls"
    ]

    # Male-only schemes
    male_terms = [
        "male",
        "men",
        "man",
        "boy",
        "boys"
    ]

    is_female_scheme = any(
        term == scheme_gender or scheme_gender.startswith(term)
        for term in female_terms
    )

    is_male_scheme = any(
        term == scheme_gender or scheme_gender.startswith(term)
        for term in male_terms
    )

    # User is female
    if user_gender in ["female", "woman", "women"]:
        if is_female_scheme:
            return 1.0
        if is_male_scheme:
            return 0.0

    # User is male
    if user_gender in ["male", "man", "men"]:
        if is_male_scheme:
            return 1.0
        if is_female_scheme:
            return 0.0

    # Unknown / unrestricted wording
    return 0.5


# ==========================================================
# SOCIAL CATEGORY MATCH
# ==========================================================

def match_social_category(user, scheme):

    user_category = normalize(
        user.get("social_category")
    )

    scheme_category = normalize(
        scheme.get("social_category")
    )

    if not scheme_category:
        return 0.0

    if scheme_category in [
        "all",
        "any",
        "all categories",
        "general / obc / sc / st",
        "general, obc, sc, st"
    ]:
        return 1.0

    if not user_category:
        return 0.0

    if user_category in scheme_category:
        return 1.0

    return 0.0


# ==========================================================
# EDUCATION MATCH
# ==========================================================

def match_education(user, scheme):

    user_education = normalize(
        user.get("current_education_level")
    )

    highest_qualification = normalize(
        user.get("highest_qualification")
    )

    scheme_education = normalize(
        scheme.get("education_level")
    )

    if not scheme_education:
        return 0.0

    if scheme_education in [
        "n/a",
        "na",
        "not applicable",
        "all",
        "any"
    ]:
        return 0.0

    user_text = (
        user_education + " " +
        highest_qualification
    )

    # ------------------------------------------------------
    # Postgraduate
    # ------------------------------------------------------

    if (
        "postgraduate" in scheme_education
        or "post graduate" in scheme_education
        or "master" in scheme_education
        or "pg" in scheme_education
    ):

        if (
            "postgraduate" in user_text
            or "post graduate" in user_text
            or "master" in user_text
            or "pg" in user_text
        ):
            return 1.0

        return 0.0

    # ------------------------------------------------------
    # Undergraduate
    # ------------------------------------------------------

    if (
        "undergraduate" in scheme_education
        or "under graduate" in scheme_education
        or "bachelor" in scheme_education
        or "ug" in scheme_education
    ):

        if (
            "undergraduate" in user_text
            or "under graduate" in user_text
            or "bachelor" in user_text
            or "bsc" in user_text
            or "btech" in user_text
        ):
            return 1.0

        return 0.0

    # ------------------------------------------------------
    # ITI
    # ------------------------------------------------------

    if "iti" in scheme_education:

        if "iti" in user_text:
            return 1.0

        return 0.0

    # ------------------------------------------------------
    # Diploma
    # ------------------------------------------------------

    if "diploma" in scheme_education:

        if "diploma" in user_text:
            return 1.0

        return 0.0

    # ------------------------------------------------------
    # Class 12
    # ------------------------------------------------------

    if (
        "class 12" in scheme_education
        or "12th" in scheme_education
        or "higher secondary" in scheme_education
    ):

        if any(value in user_text for value in [
            "class 12",
            "12th",
            "higher secondary",
            "undergraduate",
            "postgraduate",
            "bachelor",
            "master"
        ]):
            return 1.0

        return 0.0

    # ------------------------------------------------------
    # Class 10
    # ------------------------------------------------------

    if (
        "class 10" in scheme_education
        or "10th" in scheme_education
        or "matric" in scheme_education
    ):

        if any(value in user_text for value in [
            "class 10",
            "10th",
            "class 12",
            "12th",
            "undergraduate",
            "postgraduate",
            "bachelor",
            "master"
        ]):
            return 1.0

        return 0.0

    return 0.0


# ==========================================================
# STUDENT STATUS MATCH
# ==========================================================

def match_student_status(user, scheme):

    studying = normalize(
        user.get("currently_studying")
    )

    scheme_text_value = (
        normalize(scheme.get("target_beneficiary")) +
        " " +
        normalize(scheme.get("eligibility_summary")) +
        " " +
        normalize(scheme.get("scheme_description"))
    )

    student_keywords = [
        "student",
        "students",
        "currently studying",
        "pursuing studies",
        "pursuing education"
    ]

    requires_student = any(
        keyword in scheme_text_value
        for keyword in student_keywords
    )

    if not requires_student:
        return 0.0

    if studying in ["yes", "true", "1"]:
        return 1.0

    return 0.0


# ==========================================================
# EMPLOYMENT MATCH
# ==========================================================

def match_employment(user, scheme):

    employment = normalize(
        user.get("employment_status")
    )

    scheme_text_value = (
        normalize(scheme.get("target_beneficiary")) +
        " " +
        normalize(scheme.get("eligibility_summary")) +
        " " +
        normalize(scheme.get("scheme_description"))
    )

    if not employment:
        return 0.0

    employment_keywords = [
        "unemployed",
        "job seeker",
        "job seekers",
        "worker",
        "workers",
        "employee",
        "employees",
        "employed"
    ]

    if not any(
        keyword in scheme_text_value
        for keyword in employment_keywords
    ):
        return 0.0

    if employment in scheme_text_value:
        return 1.0

    return 0.0


# ==========================================================
# BPL MATCH
# ==========================================================

def match_bpl(user, scheme):

    bpl = normalize(
        user.get("bpl_status")
    )

    scheme_text_value = (
        normalize(scheme.get("target_beneficiary")) +
        " " +
        normalize(scheme.get("eligibility_summary")) +
        " " +
        normalize(scheme.get("scheme_description"))
    )

    if "bpl" not in scheme_text_value:
        return 0.0

    if bpl in ["yes", "true", "1"]:
        return 1.0

    return 0.0


# ==========================================================
# CATEGORY MATCH
# ==========================================================

def match_category(user, scheme):

    scheme_category = normalize(
        scheme.get("scheme_category")
    )

    if not scheme_category:
        return 0.0

    education = normalize(
        user.get("current_education_level")
    )

    studying = normalize(
        user.get("currently_studying")
    )

    employment = normalize(
        user.get("employment_status")
    )

    # Education / Student
    if "education" in scheme_category:

        if (
            studying in ["yes", "true", "1"]
            or "student" in education
        ):
            return 1.0

    # Employment / Skill
    if (
        "employment" in scheme_category
        or "skill" in scheme_category
    ):

        if employment:
            return 1.0

    return 1.0



def get_eligibility_score(eligibility_result):
    """
    Convert eligibility status into a recommendation score.
    """

    status = eligibility_result.get("eligibility", "")

    if status == "Likely Eligible":
        return 1.0

    elif status == "Potentially Eligible - Verification Required":
        return 0.75

    elif status == "Insufficient Eligibility Data":
        return 0.50

    return 0.0


def match_beneficiary(user, scheme):
    """
    Determine how strongly the user's profile matches
    the specific beneficiary requirements of a scheme.

    1.0 = direct match
    0.5 = insufficient information / neutral
    0.0 = clear mismatch
    """

    text = normalize(
        " ".join([
            str(scheme.get("target_beneficiary", "")),
            str(scheme.get("eligibility_summary", "")),
            str(scheme.get("scheme_description", ""))
        ])
    )

    gender = normalize(user.get("gender"))
    studying = normalize(user.get("currently_studying"))
    bpl = normalize(user.get("bpl_status"))
    disability = normalize(user.get("disability_status"))
    agriculture = normalize(user.get("involved_in_agriculture"))
    employment = normalize(user.get("employment_status"))
    job_seeking = normalize(user.get("job_seeking"))
    widow = normalize(user.get("widow_status"))
    orphan = normalize(user.get("orphan_status"))
    single_parent = normalize(user.get("single_parent_household"))
    entrepreneurship = normalize(
        user.get("entrepreneurship_interest")
    )
    skill_interest = normalize(
        user.get("skill_development_interest")
    )

    scores = []

    # ==================================================
    # WOMEN / GIRLS
    # ==================================================

    if any(word in text for word in [
        "women",
        "woman",
        "female",
        "girl",
        "girls"
    ]):

        if gender == "female":
            scores.append(1.0)

        elif gender == "male":
            return 0.0

        else:
            scores.append(0.5)

    # ==================================================
    # WIDOW
    # ==================================================

    if "widow" in text:

        if widow in ["yes", "true", "1"]:
            scores.append(1.0)

        elif widow in ["no", "false", "0"]:
            return 0.0

        else:
            scores.append(0.5)

    # ==================================================
    # ORPHAN
    # ==================================================

    if "orphan" in text:

        if orphan in ["yes", "true", "1"]:
            scores.append(1.0)

        elif orphan in ["no", "false", "0"]:
            return 0.0

        else:
            scores.append(0.5)

    # ==================================================
    # SINGLE PARENT
    # ==================================================

    if any(word in text for word in [
        "single parent",
        "single-parent",
        "single mother",
        "single father"
    ]):

        if single_parent in ["yes", "true", "1"]:
            scores.append(1.0)

        elif single_parent in ["no", "false", "0"]:
            return 0.0

        else:
            scores.append(0.5)

    # ==================================================
    # DISABILITY
    # ==================================================

    if any(word in text for word in [
        "disability",
        "disabled",
        "divyang",
        "persons with disabilities",
        "persons with disability"
    ]):

        if disability in ["yes", "true", "1"]:
            scores.append(1.0)

        elif disability in ["no", "false", "0"]:
            return 0.0

        else:
            scores.append(0.5)

    # ==================================================
    # AGRICULTURE
    # ==================================================

    if any(word in text for word in [
        "farmer",
        "farmers",
        "agriculture",
        "agricultural",
        "cultivator"
    ]):

        if agriculture in [
            "yes",
            "true",
            "1",
            "farmer",
            "engaged in agriculture"
        ]:
            scores.append(1.0)

        elif agriculture in ["no", "false", "0"]:
            return 0.0

        else:
            scores.append(0.5)

    # ==================================================
    # STUDENT
    # ==================================================

    if any(word in text for word in [
        "student",
        "students",
        "undergraduate",
        "postgraduate",
        "college student",
        "university student"
    ]):

        if studying in ["yes", "true", "1"]:
            scores.append(1.0)

        elif studying in ["no", "false", "0"]:
            return 0.0

        else:
            scores.append(0.5)

    # ==================================================
    # UNEMPLOYED / JOB SEEKER
    # ==================================================

    if any(word in text for word in [
        "unemployed",
        "job seeker",
        "jobseeker"
    ]):

        if (
            employment in [
                "unemployed",
                "job seeker",
                "jobseeker"
            ]
            or job_seeking in ["yes", "true", "1"]
        ):
            scores.append(1.0)

        elif (
            employment == "employed"
            and job_seeking in ["no", "false", "0"]
        ):
            return 0.0

        else:
            scores.append(0.5)

    # ==================================================
    # ENTREPRENEUR / BUSINESS
    # ==================================================

    if any(word in text for word in [
        "entrepreneur",
        "entrepreneurs",
        "enterprise",
        "self employed",
        "self-employed"
    ]):

        if entrepreneurship in [
            "yes",
            "true",
            "1",
            "interested"
        ]:
            scores.append(1.0)

        elif entrepreneurship in [
            "no",
            "false",
            "0",
            "not interested"
        ]:
            return 0.0

        else:
            scores.append(0.5)

    # ==================================================
    # SKILL DEVELOPMENT
    # ==================================================

    if any(word in text for word in [
        "skill development",
        "vocational training",
        "skilling",
        "skill training"
    ]):

        if skill_interest in [
            "yes",
            "true",
            "1",
            "interested"
        ]:
            scores.append(1.0)

        elif skill_interest in [
            "no",
            "false",
            "0",
            "not interested"
        ]:
            return 0.0

        else:
            scores.append(0.5)

    # ==================================================
    # BPL
    # ==================================================

    if any(word in text for word in [
        "bpl",
        "below poverty line"
    ]):

        if bpl in ["yes", "true", "1"]:
            scores.append(1.0)

        elif bpl in ["no", "false", "0"]:
            return 0.0

        else:
            scores.append(0.5)

    # ==================================================
    # SPECIFIC CIRCUMSTANCES
    # ==================================================
    #
    # These are NOT directly available in the current
    # user profile. Therefore, do NOT assume a match.
    #

    specific_conditions = [
        "violence",
        "domestic violence",
        "abuse",
        "shelter",
        "homeless",
        "trafficking",
        "victim of crime",
        "crime victim",
        "distress",
        "rehabilitation"
    ]

    if any(condition in text for condition in specific_conditions):

        # No corresponding profile field currently exists.
        scores.append(0.5)

    # ==================================================
    # FINAL SCORE
    # ==================================================

    if not scores:
        return 0.5

    return sum(scores) / len(scores)

    
def calculate_profile_match(user, scheme):
    """
    Calculate overall profile matching score.
    """

    scores = []

    # State
    scores.append(match_state(user, scheme))

    # Gender
    scores.append(match_gender(user, scheme))

    # Social category
    scores.append(match_social_category(user, scheme))

    # Education
    education_value = normalize(scheme.get("education_level"))

    if education_value not in [
        "",
        "n/a",
        "na",
        "not applicable",
        "none"
    ]:
        scores.append(match_education(user, scheme))

    # Student status
    scheme_text_value = normalize(
        " ".join([
            str(scheme.get("target_beneficiary", "")),
            str(scheme.get("eligibility_summary", "")),
            str(scheme.get("scheme_description", ""))
        ])
    )

    if any(word in scheme_text_value for word in [
        "student",
        "students",
        "currently studying",
        "undergraduate",
        "postgraduate"
    ]):
        scores.append(match_student_status(user, scheme))

    # Employment
    if any(word in scheme_text_value for word in [
        "employment",
        "employed",
        "unemployed",
        "job seeker",
        "worker"
    ]):
        scores.append(match_employment(user, scheme))

    # BPL
    if "bpl" in scheme_text_value:
        scores.append(match_bpl(user, scheme))

    if not scores:
        return 1.0

    return sum(scores) / len(scores)

def calculate_category_relevance(user, scheme):
    """
    Calculate category relevance for recommendation.

    Priority:
    1. Primary requirement
    2. Scheme interests
    3. Current profile situation
    4. General relevance
    """

    category = normalize(
        scheme.get("scheme_category", "")
    )

    requirement = normalize(
        user.get("primary_requirement")
    )

    interests = normalize(
        user.get("scheme_interests")
    )

    studying = normalize(
        user.get("currently_studying")
    )

    job_seeking = normalize(
        user.get("job_seeking")
    )

    skill_interest = normalize(
        user.get("skill_development_interest")
    )

    entrepreneurship = normalize(
        user.get("entrepreneurship_interest")
    )

    agriculture = normalize(
        user.get("involved_in_agriculture")
    )

    bpl = normalize(
        user.get("bpl_status")
    )

    gender = normalize(
        user.get("gender")
    )

    # ==================================================
    # 1. PRIMARY REQUIREMENT = STRONGEST SIGNAL
    # ==================================================

    if requirement:

        if any(word in requirement for word in [
            "child", "children", "child welfare"
        ]):
            if "women" in category or "child" in category:
                return 1.0

        if any(word in requirement for word in [
            "education", "scholarship", "student", "study"
        ]):
            if "education" in category or "student" in category:
                return 1.0

        if any(word in requirement for word in [
            "financial", "finance", "loan", "banking", "credit"
        ]):
            if "financial" in category or "banking" in category:
                return 1.0

        if any(word in requirement for word in [
            "skill", "training", "employment", "job", "career"
        ]):
            if "employment" in category or "skill" in category:
                return 1.0

        if any(word in requirement for word in [
            "business", "entrepreneur", "startup"
        ]):
            if "financial" in category or "banking" in category:
                return 1.0

        if any(word in requirement for word in [
            "agriculture", "farmer", "farming"
        ]):
            if "agriculture" in category:
                return 1.0

        if any(word in requirement for word in [
            "welfare", "social welfare", "social support"
        ]):
            if (
                "social" in category
                or "welfare" in category
                or "citizen" in category
            ):
                return 1.0

    # ==================================================
    # 2. SCHEME INTEREST = SECONDARY SIGNAL
    # ==================================================

    if interests:

        if (
            any(word in interests for word in [
                "education", "scholarship"
            ])
            and ("education" in category or "student" in category)
        ):
            return 0.75

        if (
            "skill development" in interests
            and ("skill" in category or "employment" in category)
        ):
            return 0.75

        if (
            any(word in interests for word in [
                "financial assistance", "financial", "banking"
            ])
            and ("financial" in category or "banking" in category)
        ):
            return 0.75

        if (
            any(word in interests for word in [
                "child welfare", "children"
            ])
            and ("women" in category or "child" in category)
        ):
            return 0.75

        if (
            any(word in interests for word in [
                "agriculture", "farmer"
            ])
            and "agriculture" in category
        ):
            return 0.75

        if (
            any(word in interests for word in [
                "health", "healthcare"
            ])
            and (
                "health" in category
                or "social" in category
                or "welfare" in category
            )
        ):
            return 0.75

        if (
            any(word in interests for word in [
                "electricity", "utilities"
            ])
            and (
                "welfare" in category
                or "social" in category
                or "citizen" in category
            )
        ):
            return 0.75

    # ==================================================
    # 3. PROFILE-BASED RELEVANCE
    # ==================================================

    if "education" in category or "student" in category:
        if studying in ["yes", "true", "1"]:
            return 0.55
        return 0.30

    if "employment" in category or "skill" in category:
        if job_seeking in ["yes", "true", "1"]:
            return 0.55

        if skill_interest in [
            "yes", "true", "1", "interested"
        ]:
            return 0.55

        return 0.30

    if "financial" in category or "banking" in category:
        if entrepreneurship in [
            "yes", "true", "1", "interested"
        ]:
            return 0.55

        return 0.30

    if "agriculture" in category:
        if agriculture in [
            "yes", "true", "1", "farmer"
        ]:
            return 0.55

        return 0.10

    if "women" in category or "child" in category:
        if gender == "female":
            return 0.40

        return 0.10

    if (
        "citizen" in category
        or "social" in category
        or "welfare" in category
    ):
        if bpl in ["yes", "true", "1"]:
            return 0.55

        return 0.30

    return 0.10


def calculate_keyword_relevance(user, scheme):
    """
    Calculate scheme-specific keyword relevance.

    Returns:
        1.0 = strong direct relevance
        0.75 = good relevance
        0.50 = moderate relevance
        0.25 = weak relevance
        0.10 = little/no relevance
    """

    scheme_text = normalize(
        " ".join([
            str(scheme.get("scheme_name", "")),
            str(scheme.get("classification_keywords", "")),
            str(scheme.get("target_beneficiary", "")),
            str(scheme.get("eligibility_summary", "")),
            str(scheme.get("scheme_description", ""))
        ])
    )

    requirement = normalize(
        user.get("primary_requirement")
    )

    interests = normalize(
        user.get("scheme_interests")
    )

    matches = 0
    total = 0

    # ==================================================
    # PRIMARY REQUIREMENT
    # ==================================================

    if requirement:
        total += 2

        requirement_keywords = []

        if any(word in requirement for word in [
            "child", "children", "child welfare"
        ]):
            requirement_keywords = [
                "child",
                "children",
                "girl",
                "women",
                "welfare",
                "protection"
            ]

        elif any(word in requirement for word in [
            "education", "scholarship", "student", "study"
        ]):
            requirement_keywords = [
                "education",
                "student",
                "scholarship",
                "college",
                "university",
                "fellowship"
            ]

        elif any(word in requirement for word in [
            "financial", "finance", "loan", "banking", "credit"
        ]):
            requirement_keywords = [
                "loan",
                "credit",
                "finance",
                "financial",
                "banking",
                "enterprise",
                "business"
            ]

        elif any(word in requirement for word in [
            "skill", "training", "employment", "job"
        ]):
            requirement_keywords = [
                "skill",
                "training",
                "employment",
                "job",
                "apprenticeship",
                "vocational"
            ]

        elif any(word in requirement for word in [
            "agriculture", "farmer", "farming"
        ]):
            requirement_keywords = [
                "farmer",
                "agriculture",
                "agricultural",
                "cultivator"
            ]

        if requirement_keywords:
            keyword_matches = sum(
                1 for keyword in requirement_keywords
                if keyword in scheme_text
            )

            if keyword_matches >= 3:
                matches += 2
            elif keyword_matches >= 1:
                matches += 1

    # ==================================================
    # SCHEME INTERESTS
    # ==================================================

    if interests:
        total += 1

        interest_groups = {
            "education": [
                "education",
                "scholarship",
                "student"
            ],
            "skill development": [
                "skill",
                "training",
                "employment",
                "apprenticeship"
            ],
            "financial assistance": [
                "financial",
                "loan",
                "credit",
                "banking",
                "business"
            ],
            "child welfare": [
                "child",
                "children",
                "girl",
                "women",
                "welfare"
            ],
            "healthcare": [
                "health",
                "medical",
                "healthcare"
            ],
            "food security": [
                "food",
                "ration",
                "nutrition"
            ],
            "electricity": [
                "electricity",
                "power",
                "energy"
            ]
        }

        interest_match = False

        for interest, keywords in interest_groups.items():

            if interest in interests:

                if any(
                    keyword in scheme_text
                    for keyword in keywords
                ):
                    interest_match = True
                    break

        if interest_match:
            matches += 1

    # ==================================================
    # SPECIFIC PROFILE SIGNALS
    # ==================================================

    if normalize(user.get("currently_studying")) in [
        "yes", "true", "1"
    ]:

        total += 1

        if any(word in scheme_text for word in [
            "student",
            "scholarship",
            "education",
            "college",
            "university"
        ]):
            matches += 1

    if normalize(user.get("bpl_status")) in [
        "yes", "true", "1"
    ]:

        total += 1

        if any(word in scheme_text for word in [
            "bpl",
            "below poverty",
            "poor",
            "low income"
        ]):
            matches += 1

    # ==================================================
    # FINAL SCORE
    # ==================================================

    if total == 0:
        return 0.10

    raw_score = matches / total

    if raw_score >= 0.75:
        return 1.0

    if raw_score >= 0.50:
        return 0.75

    if raw_score >= 0.25:
        return 0.50

    if raw_score > 0:
        return 0.25

    return 0.10


def calculate_recommendation_score(user, scheme, eligibility_result):
    """
    Final JanSahara recommendation score.

    Eligibility is the most important factor.
    User needs and scheme-specific relevance
    are used to differentiate schemes.
    """

    eligibility_score = get_eligibility_score(
        eligibility_result
    )

    profile_score = calculate_profile_match(
        user,
        scheme
    )

    category_score = calculate_category_relevance(
        user,
        scheme
    )

    beneficiary_score = match_beneficiary(
        user,
        scheme
    )

    keyword_score = calculate_keyword_relevance(
        user,
        scheme
    )

    # Final weighted score
    final_score = (
        eligibility_score * 45
        + category_score * 25
        + keyword_score * 15
        + beneficiary_score * 10
        + profile_score * 5
    )

    return round(final_score, 2)    

    
def debug_recommendation_score(user, scheme, eligibility_result):

    print("\n===== DETAILED SCORE DEBUG =====")
    print("Scheme:", scheme.get("scheme_name"))
    print("Gender User:", repr(user.get("gender")))
    print("Gender Scheme:", repr(scheme.get("gender_eligibility")))

    print("\n--- Individual Profile Matches ---")

    state_score = match_state(user, scheme)
    gender_score = match_gender(user, scheme)
    social_score = match_social_category(user, scheme)

    print("State:", state_score)
    print("Gender:", gender_score)
    print("Social Category:", social_score)

    education_value = normalize(
        scheme.get("education_level")
    )

    if education_value not in [
        "",
        "n/a",
        "na",
        "not applicable",
        "none"
    ]:
        education_score = match_education(user, scheme)
        print("Education:", education_score)
    else:
        education_score = None
        print("Education: NOT APPLICABLE")

    profile_score = calculate_profile_match(
        user,
        scheme
    )

    category_score = calculate_category_relevance(
        user,
        scheme
    )

    beneficiary_score = match_beneficiary(
        user,
        scheme
    )

    keyword_score = calculate_keyword_relevance(
        user,
        scheme
    )

    eligibility_score = get_eligibility_score(
        eligibility_result
    )

    print("\n--- Final Components ---")
    print("Eligibility:", eligibility_score)
    print("Profile:", profile_score)
    print("Category:", category_score)
    print("Beneficiary:", beneficiary_score)
    print("Keyword:", keyword_score)

    final_score = (
        eligibility_score * 40
        + profile_score * 20
        + category_score * 15
        + beneficiary_score * 15
        + keyword_score * 10
    )

    print("FINAL:", round(final_score, 2))
    
# ==========================================================
# RECOMMENDATION ENGINE
# ==========================================================

def generate_recommendations(
    user,
    schemes,
    eligibility_results,
    top_n=10
):
    """
    Generate ranked scheme recommendations.
    """

    candidates = build_candidates(
        schemes,
        eligibility_results
    )

    candidates = filter_candidates(candidates)

    recommendations = []

    for candidate in candidates:

        # Extract scheme and eligibility result
        scheme = candidate.get("scheme", {})
        eligibility_result = candidate.get(
            "eligibility_result",
            {}
        )

        # Calculate recommendation score
        score = calculate_recommendation_score(
            user,
            scheme,
            eligibility_result
        )

        recommendation = {
            "scheme_id": scheme.get("scheme_id"),
            "scheme_name": scheme.get("scheme_name"),
            "scheme_category": scheme.get("scheme_category"),
            "eligibility": eligibility_result.get(
                "eligibility",
                "Unknown"
            ),
            "eligibility_score": eligibility_result.get(
                "match_score",
                0
            ),
            "recommendation_score": score
        }

        recommendations.append(recommendation)

    # Highest score first
    recommendations.sort(
        key=lambda x: x["recommendation_score"],
        reverse=True
    )

    # Top N recommendations
    recommendations = recommendations[:top_n]

    return {
        "total_candidates": len(candidates),
        "recommendations": recommendations
    }    
