from llm_engine import generate_llm_response


context = """
Scheme Name: INSPIRE Scholarship for Higher Education (SHE)

Category: Education / Student

Eligibility:
Potentially Eligible - Verification Required

Eligibility Score:
75%

Important:
The user needs to verify the remaining eligibility requirement.

Benefit:
Scholarship support for eligible higher education students.
"""


response = generate_llm_response(
    "Am I eligible for the INSPIRE Scholarship?",
    context
)

print("\n======================================")
print("JANSAHARA LLM TEST")
print("======================================")
print(response)
print("======================================")
