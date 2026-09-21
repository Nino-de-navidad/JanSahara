# ==========================================================
# JANSAHARA - ELIGIBILITY ENGINE
# Stage 1.4 - Improved Eligibility Logic
# ==========================================================


# ==========================================================
# BASIC HELPERS
# ==========================================================

def normalize(value):
    if value is None:
        return ""

    return str(value).strip().lower()


def normalize_number(value):
    """
    Convert values such as:
    25
    25.5
    '25'
    '25.5'
    into float.
    """
    if value is None:
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def exact_match(value, allowed_values):
    """
    Exact normalized matching.
    Prevents errors such as:
    male matching female.
    """
    value = normalize(value)

    return value in [
        normalize(v)
        for v in allowed_values
    ]


def contains_any(text, keywords):

    text = normalize(text)

    return any(
        normalize(keyword) in text
        for keyword in keywords
    )


def parse_income(income):

    if income is None:
        return None

    text = normalize(income)

    if not text:
        return None

    text = text.replace(",", "")
    text = text.replace("₹", "")
    text = text.replace("rs.", "")
    text = text.replace("rs", "")

    # ------------------------------------------------------
    # Handle lakh
    # ------------------------------------------------------

    lakh_multiplier = 1

    if "lakh" in text or "lakhs" in text:
        lakh_multiplier = 100000

    # ------------------------------------------------------
    # Handle crore
    # ------------------------------------------------------

    crore_multiplier = 1

    if "crore" in text or "crores" in text:
        crore_multiplier = 10000000

    # ------------------------------------------------------
    # Extract numbers
    # ------------------------------------------------------

    numbers = []

    current = ""

    decimal_found = False

    for char in text:

        if char.isdigit():

            current += char

        elif char == "." and not decimal_found:

            current += char
            decimal_found = True

        else:

            if current:

                try:
                    numbers.append(float(current))
                except ValueError:
                    pass

                current = ""
                decimal_found = False

    if current:

        try:
            numbers.append(float(current))
        except ValueError:
            pass

    if not numbers:
        return None

    # ------------------------------------------------------
    # Apply multiplier
    # ------------------------------------------------------

    multiplier = max(
        lakh_multiplier,
        crore_multiplier
    )

    return max(numbers) * multiplier


def scheme_text(scheme):

    fields = [
        "scheme_name",
        "scheme_category",
        "scheme_type",
        "target_beneficiary",
        "education_level",
        "social_category",
        "gender_eligibility",
        "eligibility_summary",
        "scheme_description",
        "classification_keywords"
    ]

    return " ".join(
        normalize(scheme.get(field))
        for field in fields
    )


# ==========================================================
# RESULT HELPER
# ==========================================================

def result(status, reason):

    return {
        "status": status,
        "reason": reason
    }


# ==========================================================
# AGE
# ==========================================================

def check_age(user, scheme):

    age = normalize_number(
        user.get("age")
    )

    minimum = normalize_number(
        scheme.get("minimum_age")
    )

    maximum = normalize_number(
        scheme.get("maximum_age")
    )

    if minimum is None and maximum is None:

        return result(
            "not_applicable",
            "No age restriction recorded"
        )

    if age is None:

        return result(
            "unknown",
            "User age is not available"
        )

    if minimum is not None and age < minimum:

        return result(
            "fail",
            f"Age is below minimum requirement of {int(minimum)}"
        )

    if maximum is not None and age > maximum:

        return result(
            "fail",
            f"Age exceeds maximum requirement of {int(maximum)}"
        )

    return result(
        "pass",
        "Age requirement satisfied"
    )


# ==========================================================
# GENDER
# ==========================================================

def check_gender(user, scheme):

    required = normalize(
        scheme.get("gender_eligibility")
    )

    user_gender = normalize(
        user.get("gender")
    )

    if not required:

        return result(
            "not_applicable",
            "No gender restriction recorded"
        )

    if required in [
        "all",
        "any",
        "both",
        "all genders",
        "not applicable"
    ]:

        return result(
            "not_applicable",
            "No gender restriction"
        )

    if not user_gender:

        return result(
            "unknown",
            "User gender is not available"
        )

    # ------------------------------------------------------
    # Exact gender handling
    # ------------------------------------------------------

    female_values = [
        "female",
        "woman",
        "women",
        "girl"
    ]

    male_values = [
        "male",
        "man",
        "men",
        "boy"
    ]

    if any(
        value in required.split(",")
        for value in female_values
    ):

        if user_gender in female_values:

            return result(
                "pass",
                "Female gender requirement satisfied"
            )

        return result(
            "fail",
            "Scheme requires female beneficiaries"
        )

    if any(
        value in required.split(",")
        for value in male_values
    ):

        if user_gender in male_values:

            return result(
                "pass",
                "Male gender requirement satisfied"
            )

        return result(
            "fail",
            "Scheme requires male beneficiaries"
        )

    # ------------------------------------------------------
    # Fallback
    # ------------------------------------------------------

    required_values = [
        normalize(x)
        for x in required.replace("/", ",").split(",")
        if normalize(x)
    ]

    if user_gender in required_values:

        return result(
            "pass",
            "Gender requirement satisfied"
        )

    return result(
        "fail",
        "Gender requirement not satisfied"
    )


# ==========================================================
# STATE
# ==========================================================

def check_state(user, scheme):

    required = normalize(
        scheme.get("state_scope")
    )

    user_state = normalize(
        user.get("state")
    )

    if not required:

        return result(
            "not_applicable",
            "No state restriction recorded"
        )

    national_values = [
        "all india",
        "all-india",
        "india",
        "central",
        "national",
        "pan india",
        "pan-india"
    ]

    if required in national_values:

        return result(
            "pass",
            "Scheme has national coverage"
        )

    if not user_state:

        return result(
            "unknown",
            "User state is not available"
        )

    required_values = [
        normalize(x)
        for x in required.replace("/", ",").split(",")
        if normalize(x)
    ]

    if user_state in required_values:

        return result(
            "pass",
            "State requirement satisfied"
        )

    return result(
        "fail",
        "Scheme is not available in user's state"
    )


# ==========================================================
# SOCIAL CATEGORY
# ==========================================================

def check_social_category(user, scheme):

    required = normalize(
        scheme.get("social_category")
    )

    user_category = normalize(
        user.get("social_category")
    )

    if not required:

        return result(
            "not_applicable",
            "No social-category restriction recorded"
        )

    if required in [
        "all",
        "any",
        "all categories",
        "general",
        "all social categories"
    ]:

        return result(
            "not_applicable",
            "No social-category restriction"
        )

    if not user_category:

        return result(
            "unknown",
            "User social category is not available"
        )

    required_values = [
        normalize(x)
        for x in required.replace("/", ",").split(",")
        if normalize(x)
    ]

    if user_category in required_values:

        return result(
            "pass",
            "Social-category requirement satisfied"
        )

    return result(
        "fail",
        "Social-category requirement not satisfied"
    )


# ==========================================================
# INCOME
# ==========================================================

def check_income(user, scheme):

    limit = normalize_number(
        scheme.get("income_limit")
    )

    if limit is None:

        return result(
            "not_applicable",
            "No income restriction recorded"
        )

    income = parse_income(
        user.get("annual_household_income")
    )

    if income is None:

        return result(
            "unknown",
            "Household income is not available"
        )

    if income <= limit:

        return result(
            "pass",
            f"Household income is within the scheme limit of ₹{limit:,.0f}"
        )

    return result(
        "fail",
        "Household income exceeds scheme limit"
    )


# ==========================================================
# STUDENT STATUS
# ==========================================================

def check_student_status(user, scheme):

    category = normalize(
        scheme.get("scheme_category")
    )

    beneficiary = normalize(
        scheme.get("target_beneficiary")
    )

    name = normalize(
        scheme.get("scheme_name")
    )

    # ------------------------------------------------------
    # Prefer structured scheme information
    # ------------------------------------------------------

    student_related = (
        category in [
            "education",
            "education/scholarship",
            "education - scholarship",
            "education/fellowship"
        ]
        or contains_any(
            beneficiary + " " + name,
            [
                "student",
                "scholarship",
                "fellowship"
            ]
        )
    )

    if not student_related:

        return result(
            "not_applicable",
            "No student-specific requirement detected"
        )

    studying = normalize(
        user.get("currently_studying")
    )

    if studying == "yes":

        return result(
            "pass",
            "User is currently studying"
        )

    if studying == "no":

        return result(
            "fail",
            "Scheme requires the applicant to be a student"
        )

    return result(
        "unknown",
        "Student status is not available"
    )


# ==========================================================
# EDUCATION - STAGE 1.6
# ==========================================================

def check_education(user, scheme):

    scheme_level = normalize(
        scheme.get("education_level")
    )

    scheme_text_value = scheme_text(scheme)

    # ------------------------------------------------------
    # No education requirement
    # ------------------------------------------------------

    if not scheme_level or scheme_level in [
        "n/a",
        "na",
        "not applicable",
        "all",
        "any"
    ]:
        return result(
            "not_applicable",
            "No specific education-level restriction"
        )

    # ------------------------------------------------------
    # User education
    # ------------------------------------------------------

    current_level = normalize(
        user.get("current_education_level")
    )

    highest_level = normalize(
        user.get("highest_qualification")
    )

    user_education = f"{current_level} {highest_level}"

    if not user_education.strip():
        return result(
            "unknown",
            "User education information is not available"
        )

    # ------------------------------------------------------
    # POSTGRADUATE
    # ------------------------------------------------------

    if (
        "postgraduate" in scheme_level
        or "post graduate" in scheme_level
        or "masters" in scheme_level
        or "master" in scheme_level
        or "pg" in scheme_level
    ):

        if (
            "postgraduate" in user_education
            or "post graduate" in user_education
            or "masters" in user_education
            or "master" in user_education
            or "pg" in user_education
        ):
            return result(
                "pass",
                "User has postgraduate-level education"
            )

        if (
            "undergraduate" in user_education
            or "bachelor" in user_education
            or "graduate" in user_education
            or "class 12" in user_education
            or "12th" in user_education
            or "higher secondary" in user_education
        ):
            return result(
                "fail",
                "Scheme requires postgraduate-level education"
            )

        return result(
            "unknown",
            "User education level could not be matched to postgraduate requirement"
        )

    # ------------------------------------------------------
    # UNDERGRADUATE
    # ------------------------------------------------------

    if (
        "undergraduate" in scheme_level
        or "under graduate" in scheme_level
        or "bachelor" in scheme_level
        or "ug" in scheme_level
    ):

        if (
            "undergraduate" in user_education
            or "under graduate" in user_education
            or "bachelor" in user_education
            or "bsc" in user_education
            or "b.tech" in user_education
            or "btech" in user_education
            or "ba " in user_education
            or "b.com" in user_education
        ):
            return result(
                "pass",
                "User has undergraduate-level education"
            )

        if (
            "postgraduate" in user_education
            or "post graduate" in user_education
            or "masters" in user_education
            or "master" in user_education
        ):
            return result(
                "pass",
                "User has education above the undergraduate level"
            )

        return result(
            "unknown",
            "User education level could not be matched to undergraduate requirement"
        )

    # ------------------------------------------------------
    # CLASS 12
    # ------------------------------------------------------

    if (
        "class 12" in scheme_level
        or "12th" in scheme_level
        or "higher secondary" in scheme_level
        or "senior secondary" in scheme_level
    ):

        if (
            "class 12" in user_education
            or "12th" in user_education
            or "higher secondary" in user_education
            or "senior secondary" in user_education
            or "undergraduate" in user_education
            or "postgraduate" in user_education
            or "bachelor" in user_education
            or "master" in user_education
        ):
            return result(
                "pass",
                "User has completed or is pursuing education at or above Class 12"
            )

        return result(
            "fail",
            "Scheme requires Class 12 or equivalent education"
        )

    # ------------------------------------------------------
    # CLASS 10
    # ------------------------------------------------------

    if (
        "class 10" in scheme_level
        or "10th" in scheme_level
        or "secondary" in scheme_level
        or "matric" in scheme_level
    ):

        if (
            "class 10" in user_education
            or "10th" in user_education
            or "class 12" in user_education
            or "12th" in user_education
            or "undergraduate" in user_education
            or "postgraduate" in user_education
            or "bachelor" in user_education
            or "master" in user_education
        ):
            return result(
                "pass",
                "User has completed or is pursuing education at or above Class 10"
            )

        return result(
            "fail",
            "Scheme requires Class 10 or equivalent education"
        )

    # ------------------------------------------------------
    # ITI
    # ------------------------------------------------------

    if "iti" in scheme_level:

        if "iti" in user_education:
            return result(
                "pass",
                "User has ITI qualification"
            )

        return result(
            "fail",
            "Scheme requires ITI qualification"
        )

    # ------------------------------------------------------
    # DIPLOMA
    # ------------------------------------------------------

    if "diploma" in scheme_level:

        if "diploma" in user_education:
            return result(
                "pass",
                "User has diploma qualification"
            )

        return result(
            "fail",
            "Scheme requires diploma qualification"
        )

    # ------------------------------------------------------
    # Mixed / flexible requirement
    # ------------------------------------------------------

    allowed_levels = [
        "class 10",
        "10th",
        "class 12",
        "12th",
        "iti",
        "diploma",
        "undergraduate",
        "graduate",
        "postgraduate",
        "bachelor",
        "master"
    ]

    if any(level in scheme_level for level in allowed_levels):

        if any(level in user_education for level in allowed_levels):
            return result(
                "pass",
                "User education matches one of the accepted education levels"
            )

        return result(
            "unknown",
            "User education could not be matched to the scheme requirement"
        )

    return result(
        "unknown",
        "Education requirement requires manual verification"
    )
    
# ==========================================================
# COURSE / SUBJECT - STAGE 1.5
# ==========================================================

def check_course_subject(user, scheme):

    text = scheme_text(scheme)

    # ------------------------------------------------------
    # Detect whether scheme has a specific subject/course
    # requirement.
    # ------------------------------------------------------

    science_requirement = contains_any(
        text,
        [
            "basic science",
            "basic sciences",
            "natural science",
            "natural sciences",
            "basic and natural sciences"
        ]
    )

    if science_requirement:

        subject = normalize(
            user.get("course_subject")
        )

        if not subject:

            return result(
                "unknown",
                "User course/subject is not available to verify the required science discipline"
            )

        science_subjects = [
            "physics",
            "chemistry",
            "biology",
            "mathematics",
            "maths",
            "botany",
            "zoology",
            "statistics",
            "astronomy",
            "astrophysics",
            "biochemistry",
            "geology",
            "geophysics",
            "environmental science"
        ]

        if any(
            subject_name in subject
            for subject_name in science_subjects
        ):

            return result(
                "pass",
                "Course/subject appears to fall within eligible basic or natural sciences"
            )

        return result(
            "fail",
            "User's course/subject does not appear to match the required basic or natural science disciplines"
        )

    # ------------------------------------------------------
    # Generic course requirement
    # ------------------------------------------------------

    if contains_any(
        text,
        [
            "specific course",
            "specific subject",
            "eligible course",
            "eligible subject"
        ]
    ):

        subject = normalize(
            user.get("course_subject")
        )

        if not subject:

            return result(
                "unknown",
                "User course/subject is not available"
            )

        return result(
            "unknown",
            "Course/subject requires scheme-specific verification"
        )

    return result(
        "not_applicable",
        "No specific course or subject requirement detected"
    )

# ==========================================================
# EMPLOYMENT
# ==========================================================

def check_employment(user, scheme):

    category = normalize(
        scheme.get("scheme_category")
    )

    text = normalize(
        scheme.get("target_beneficiary")
    ) + " " + normalize(
        scheme.get("scheme_name")
    )

    employment_related = (
        category in [
            "employment",
            "employment/skill",
            "employment - skill"
        ]
        or contains_any(
            text,
            [
                "unemployed",
                "job seeker",
                "jobseeker",
                "employment"
            ]
        )
    )

    if not employment_related:

        return result(
            "not_applicable",
            "No employment requirement detected"
        )

    employment = normalize(
        user.get("employment_status")
    )

    if not employment:

        return result(
            "unknown",
            "Employment status is not available"
        )

    if "unemploy" in text:

        if "unemploy" in employment:

            return result(
                "pass",
                "User satisfies unemployment condition"
            )

        return result(
            "fail",
            "Scheme requires unemployed beneficiaries"
        )

    return result(
        "unknown",
        "Employment eligibility requires verification"
    )


# ==========================================================
# SKILL DEVELOPMENT
# ==========================================================

def check_skill_development(user, scheme):

    category = normalize(
        scheme.get("scheme_category")
    )

    text = (
        normalize(scheme.get("scheme_name"))
        + " "
        + normalize(scheme.get("target_beneficiary"))
        + " "
        + normalize(scheme.get("classification_keywords"))
    )

    if not (
        category in [
            "employment",
            "employment/skill",
            "employment - skill",
            "skill development"
        ]
        or contains_any(
            text,
            [
                "skill development",
                "skill training",
                "vocational training",
                "upskilling"
            ]
        )
    ):

        return result(
            "not_applicable",
            "No skill-development requirement detected"
        )

    interest = normalize(
        user.get("skill_development_interest")
    )

    if interest == "yes":

        return result(
            "pass",
            "User is interested in skill development"
        )

    if interest == "no":

        return result(
            "fail",
            "User is not interested in skill development"
        )

    return result(
        "unknown",
        "Skill-development interest is uncertain"
    )


# ==========================================================
# ENTREPRENEURSHIP
# ==========================================================

def check_entrepreneurship(user, scheme):

    category = normalize(
        scheme.get("scheme_category")
    )

    text = (
        normalize(scheme.get("scheme_name"))
        + " "
        + normalize(scheme.get("target_beneficiary"))
        + " "
        + normalize(scheme.get("classification_keywords"))
    )

    entrepreneurship_related = (
        category in [
            "finance",
            "financial",
            "employment",
            "entrepreneurship"
        ]
        and contains_any(
            text,
            [
                "entrepreneur",
                "entrepreneurship",
                "self employment",
                "self-employment",
                "startup",
                "business loan",
                "enterprise"
            ]
        )
    )

    if not entrepreneurship_related:

        return result(
            "not_applicable",
            "No entrepreneurship requirement detected"
        )

    interest = normalize(
        user.get("entrepreneurship_interest")
    )

    if interest in [
        "yes",
        "interested"
    ]:

        return result(
            "pass",
            "User has entrepreneurship interest"
        )

    if interest == "no":

        return result(
            "fail",
            "User is not interested in entrepreneurship"
        )

    return result(
        "unknown",
        "Entrepreneurship interest is uncertain"
    )


# ==========================================================
# BPL
# ==========================================================

def check_bpl(user, scheme):

    text = (
        normalize(scheme.get("scheme_name"))
        + " "
        + normalize(scheme.get("target_beneficiary"))
        + " "
        + normalize(scheme.get("eligibility_summary"))
    )

    if not contains_any(
        text,
        [
            "bpl",
            "below poverty line",
            "below poverty"
        ]
    ):

        return result(
            "not_applicable",
            "No BPL requirement detected"
        )

    bpl = normalize(
        user.get("bpl_status")
    )

    if bpl == "yes":

        return result(
            "pass",
            "BPL requirement satisfied"
        )

    if bpl == "no":

        return result(
            "fail",
            "Scheme requires BPL status"
        )

    return result(
        "unknown",
        "BPL status is not available"
    )


# ==========================================================
# DISABILITY
# ==========================================================

def check_disability(user, scheme):

    text = (
        normalize(scheme.get("scheme_name"))
        + " "
        + normalize(scheme.get("target_beneficiary"))
        + " "
        + normalize(scheme.get("eligibility_summary"))
    )

    if not contains_any(
        text,
        [
            "disability",
            "disabled",
            "divyang",
            "persons with disabilities"
        ]
    ):

        return result(
            "not_applicable",
            "No disability requirement detected"
        )

    disability = normalize(
        user.get("disability_status")
    )

    if disability == "yes":

        return result(
            "pass",
            "Disability requirement satisfied"
        )

    if disability == "no":

        return result(
            "fail",
            "Scheme requires a person with disability"
        )

    return result(
        "unknown",
        "Disability status is not available"
    )


# ==========================================================
# WIDOW
# ==========================================================

def check_widow(user, scheme):

    text = scheme_text(scheme)

    if "widow" not in text:

        return result(
            "not_applicable",
            "No widow requirement detected"
        )

    status = normalize(
        user.get("widow_status")
    )

    if status == "yes":

        return result(
            "pass",
            "Widow-status requirement satisfied"
        )

    if status == "no":

        return result(
            "fail",
            "Scheme requires widow beneficiaries"
        )

    return result(
        "unknown",
        "Widow status is not available"
    )


# ==========================================================
# ORPHAN
# ==========================================================

def check_orphan(user, scheme):

    text = scheme_text(scheme)

    if "orphan" not in text:

        return result(
            "not_applicable",
            "No orphan requirement detected"
        )

    status = normalize(
        user.get("orphan_status")
    )

    if status == "yes":

        return result(
            "pass",
            "Orphan-status requirement satisfied"
        )

    if status == "no":

        return result(
            "fail",
            "Scheme requires orphan beneficiaries"
        )

    return result(
        "unknown",
        "Orphan status is not available"
    )

# ==========================================================
# SINGLE GIRL CHILD - STAGE 1.5
# ==========================================================

def check_single_girl_child(user, scheme):

    text = scheme_text(scheme)

    if "single girl child" not in text:
        return result(
            "not_applicable",
            "No single-girl-child requirement detected"
        )

    # ------------------------------------------------------
    # Gender
    # ------------------------------------------------------

    gender = normalize(
        user.get("gender")
    )

    if gender == "male":
        return result(
            "fail",
            "Scheme requires a female/single girl child applicant"
        )

    if not gender:
        return result(
            "unknown",
            "User gender is not available"
        )

    # ------------------------------------------------------
    # Dedicated profile field
    # ------------------------------------------------------

    status = normalize(
        user.get("single_girl_child")
    )

    if status in ["yes", "true", "1"]:
        return result(
            "pass",
            "Single-girl-child requirement satisfied"
        )

    if status in ["no", "false", "0"]:
        return result(
            "fail",
            "Applicant does not satisfy the single-girl-child condition"
        )

    return result(
        "unknown",
        "Single-girl-child status is not available in the user profile"
    )

# ==========================================================
# CHILDREN
# ==========================================================

def check_children(user, scheme):

    text = scheme_text(scheme)

    if "single girl child" in text:
        return result(
            "not_applicable",
            "Single-girl-child requirement is handled by check_single_girl_child"
        )

    # ------------------------------------------------------
    # SPECIAL CASE
    # ------------------------------------------------------

    if "single girl child" in text:

        return result(
            "unknown",
            "Single-girl-child condition is not captured by the current questionnaire"
        )

    if not contains_any(
        text,
        [
            "child welfare",
            "mother and child",
            "children welfare"
        ]
    ):

        return result(
            "not_applicable",
            "No children-related requirement detected"
        )

    children = normalize_number(
        user.get("number_of_children")
    )

    if children is None:

        return result(
            "unknown",
            "Number of children is not available"
        )

    if children > 0:

        return result(
            "pass",
            "User has children"
        )

    return result(
        "fail",
        "Scheme requires beneficiaries with children"
    )


# ==========================================================
# SINGLE PARENT
# ==========================================================

def check_single_parent(user, scheme):

    text = scheme_text(scheme)

    if not contains_any(
        text,
        [
            "single parent",
            "single-parent"
        ]
    ):

        return result(
            "not_applicable",
            "No single-parent requirement detected"
        )

    status = normalize(
        user.get("single_parent_household")
    )

    if status == "yes":

        return result(
            "pass",
            "Single-parent condition satisfied"
        )

    if status == "no":

        return result(
            "fail",
            "Scheme requires a single-parent household"
        )

    return result(
        "unknown",
        "Single-parent status is not available"
    )


# ==========================================================
# WOMEN
# ==========================================================

def check_women(user, scheme):

    text = scheme_text(scheme)

    if "single girl child" in text:

        return result(
            "not_applicable",
            "Specific single-girl-child rule handled separately"
        )

    if not contains_any(
        text,
        [
            "women",
            "woman",
            "female beneficiaries",
            "girls"
        ]
    ):

        return result(
            "not_applicable",
            "No women-specific requirement detected"
        )

    gender = normalize(
        user.get("gender")
    )

    if gender == "female":

        return result(
            "pass",
            "Women-specific gender requirement satisfied"
        )

    if gender:

        return result(
            "fail",
            "Scheme is intended for women/girls"
        )

    return result(
        "unknown",
        "User gender is not available"
    )


# ==========================================================
# AGRICULTURE
# ==========================================================

def check_agriculture(user, scheme):

    text = (
        normalize(scheme.get("scheme_name"))
        + " "
        + normalize(scheme.get("target_beneficiary"))
        + " "
        + normalize(scheme.get("classification_keywords"))
    )

    if not contains_any(
        text,
        [
            "farmer",
            "farmers",
            "agriculture",
            "agricultural",
            "cultivator",
            "cultivation"
        ]
    ):

        return result(
            "not_applicable",
            "No agriculture requirement detected"
        )

    status = normalize(
        user.get("involved_in_agriculture")
    )

    if status == "yes":

        return result(
            "pass",
            "User is involved in agriculture"
        )

    if status == "no":

        return result(
            "fail",
            "Scheme is intended for agricultural beneficiaries"
        )

    return result(
        "unknown",
        "Agriculture status is not available"
    )


# ==========================================================
# HOUSING
# ==========================================================

def check_housing(user, scheme):

    text = (
        normalize(scheme.get("scheme_name"))
        + " "
        + normalize(scheme.get("target_beneficiary"))
        + " "
        + normalize(scheme.get("classification_keywords"))
    )

    if not contains_any(
        text,
        [
            "housing",
            "rural housing",
            "housing assistance",
            "house construction"
        ]
    ):

        return result(
            "not_applicable",
            "No housing requirement detected"
        )

    house_type = normalize(
        user.get("house_type")
    )

    ownership = normalize(
        user.get("house_ownership")
    )

    if not house_type and not ownership:

        return result(
            "unknown",
            "Housing information is not available"
        )

    return result(
        "unknown",
        "Housing condition requires scheme-specific verification"
    )


# ==========================================================
# RATION CARD
# ==========================================================

def check_ration_card(user, scheme):

    text = (
        normalize(scheme.get("scheme_name"))
        + " "
        + normalize(scheme.get("target_beneficiary"))
        + " "
        + normalize(scheme.get("eligibility_summary"))
    )

    if not contains_any(
        text,
        [
            "ration card",
            "food security",
            "food subsidy",
            "aay",
            "phh"
        ]
    ):

        return result(
            "not_applicable",
            "No ration-card requirement detected"
        )

    ration = normalize(
        user.get("ration_card")
    )

    if ration == "yes":

        return result(
            "pass",
            "Ration-card requirement satisfied"
        )

    if ration == "no":

        return result(
            "fail",
            "Scheme requires a ration card"
        )

    return result(
        "unknown",
        "Ration-card status is not available"
    )


# ==========================================================
# MAIN ELIGIBILITY ENGINE
# ==========================================================

def check_eligibility(user, scheme):

    checks = []

    check_functions = [

    check_age,
    check_gender,
    check_state,
    check_social_category,
    check_income,
    check_education,

    # Stage 1.5
    check_course_subject,
    check_single_girl_child,

    check_student_status,
    check_employment,
    check_skill_development,
    check_entrepreneurship,
    check_bpl,
    check_disability,
    check_widow,
    check_orphan,
    check_children,
    check_single_parent,
    check_women,
    check_agriculture,
    check_housing,
    check_ration_card

    ]

    # ------------------------------------------------------
    # RUN ALL CHECKS
    # ------------------------------------------------------

    for function in check_functions:

        check = function(
            user,
            scheme
        )

        checks.append({

            "check":
                function.__name__,

            "status":
                check["status"],

            "reason":
                check["reason"]

        })

    # ------------------------------------------------------
    # GROUP RESULTS
    # ------------------------------------------------------

    passed = [
        c for c in checks
        if c["status"] == "pass"
    ]

    failed = [
        c for c in checks
        if c["status"] == "fail"
    ]

    unknown = [
        c for c in checks
        if c["status"] == "unknown"
    ]

    not_applicable = [
        c for c in checks
        if c["status"] == "not_applicable"
    ]

    # ------------------------------------------------------
    # SCORE
    #
    # IMPORTANT:
    # UNKNOWN conditions are included.
    #
    # PASS = satisfied
    # FAIL = not satisfied
    # UNKNOWN = needs verification
    # N/A = ignored
    # ------------------------------------------------------

    applicable = (
        passed
        + failed
        + unknown
    )

    if len(applicable) > 0:

        match_score = round(
            len(passed)
            /
            len(applicable)
            *
            100,
            2
        )

    else:

        match_score = 0

    # ------------------------------------------------------
    # FINAL ELIGIBILITY
    # ------------------------------------------------------

    if len(failed) > 0:

        eligibility = "Likely Not Eligible"

    elif len(unknown) > 0:

        eligibility = (
            "Potentially Eligible - "
            "Verification Required"
        )

    elif len(passed) > 0:

        eligibility = "Likely Eligible"

    else:

        eligibility = "Insufficient Eligibility Data"

    # ------------------------------------------------------
    # RETURN
    # ------------------------------------------------------

    return {

        "eligibility":
            eligibility,

        "match_score":
            match_score,

        "passed_checks":
            passed,

        "failed_checks":
            failed,

        "unknown_checks":
            unknown,

        "not_applicable_checks":
            not_applicable,

        "all_checks":
            checks
    }