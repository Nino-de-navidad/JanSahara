from transformers import pipeline


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading JanSahara LLM...")

llm = pipeline(
    "text-generation",
    model=MODEL_NAME,
    device_map="auto",
    dtype="auto"
)

print("JanSahara LLM loaded successfully.")


# ============================================================
# GENERATE RESPONSE
# ============================================================

def generate_llm_response(
    user_query,
    context
):

    system_prompt = """
You are JanSahara, a government scheme assistance chatbot.

Your role is ONLY to explain information supplied by the
JanSahara system.

STRICT RULES:

1. Use ONLY facts explicitly present in the provided context.

2. NEVER add facts from your own knowledge.

3. NEVER invent or assume:
   - eligibility criteria
   - benefits
   - financial amounts
   - documents
   - application procedures
   - application portals
   - deadlines
   - age limits
   - income limits
   - government rules

4. Do NOT independently calculate or decide eligibility.

5. If an eligibility result is provided by JanSahara,
   report that result exactly.

6. If the eligibility result says:
   "Potentially Eligible - Verification Required",
   clearly state that verification is required.

7. If information needed to answer the question is missing,
   say:
   "This information is not available in the JanSahara database."

8. Do not create URLs. Only mention a URL if it is explicitly
   provided in the context.

9. Keep responses concise, clear and easy to understand.

10. When discussing eligibility, remind the user to verify
    the final requirements using the official scheme source.
"""


    user_prompt = f"""
User question:
{user_query}

JanSahara verified information:
{context}

Using only the verified information above, answer the user's question.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    output = llm(
        messages,
        max_new_tokens=250,
        do_sample=True,
        temperature=0.3,
        top_p=0.9
    )

    generated = output[0]["generated_text"]

    # The pipeline returns the conversation.
    # Extract the final assistant response.
    if isinstance(generated, list):

        response = generated[-1].get(
            "content",
            ""
        )

    else:

        response = str(generated)

    return response.strip()