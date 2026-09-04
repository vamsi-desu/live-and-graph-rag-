import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_answer(question, context):
    """
    Generate an answer using only the supplied graph context.
    """

    prompt = f"""
You are an employee knowledge assistant.

Answer the user's question using ONLY the information
provided in the graph context.

If the context does not contain enough information,
say:

"Not enough information in the employee graph."

Do not invent or assume information.

USER QUESTION:
{question}

GRAPH CONTEXT:
{context}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You answer questions using grounded "
                    "employee graph evidence."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
    )

    return response.choices[0].message.content