# ============================================================
# JANSAHARA LLM ENGINE
# ============================================================
#
# The LLM is optional.
# This allows JanSahara to run on low-memory hosting services.
#
# Set ENABLE_LLM=true in the environment when a sufficiently
# powerful server is available.
# ============================================================

import os

ENABLE_LLM = os.getenv("ENABLE_LLM", "false").lower() == "true"

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

llm = None


# ============================================================
# LOAD MODEL ONLY WHEN ENABLED
# ============================================================

def load_llm():

    global llm

    if not ENABLE_LLM:
        return None

    if llm is not None:
        return llm

    try:

        from transformers import pipeline

        print("Loading JanSahara LLM...")

        llm = pipeline(
            "text-generation",
            model=MODEL_NAME,
            device_map="auto",
            dtype="auto"
        )

        print("JanSahara LLM loaded successfully.")

        return llm

    except Exception as e:

        print("JanSahara LLM could not be loaded:", e)

        llm = None

        return None


# ============================================================
# GENERATE RESPONSE
# ============================================================

def generate_llm_response(
    user_query,
    context
):

    model = load_llm()

    # --------------------------------------------------------
    # LLM DISABLED / UNAVAILABLE
    # --------------------------------------------------------

    if model is None:

        return (
            "I can provide information from the JanSahara "
            "database, but the AI explanation service is "
            "currently unavailable. Please use the scheme "
            "details, eligibility result, recommendation "
            "and official source provided by JanSahara."
        )

    # --------------------------------------------------------
    # SYSTEM PROMPT
    # --------------------------------------------------------

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

    try:

        output = model(
            messages,
            max_new_tokens=250,
            do_sample=True,
            temperature=0.3,
            top_p=0.9
        )

        generated = output[0]["generated_text"]

        if isinstance(generated, list):

            response = generated[-1].get(
                "content",
                ""
            )

        else:

            response = str(generated)

        return response.strip()

    except Exception as e:

        print("LLM response error:", e)

        return (
            "The AI explanation service is currently "
            "unavailable. Please refer to the JanSahara "
            "scheme information and official source."
        )