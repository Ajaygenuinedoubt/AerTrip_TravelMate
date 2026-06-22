from groq import Groq
from backend.config import GROQ_API_KEY

client = Groq(
    api_key=GROQ_API_KEY
)

def classify_intent(query):

    prompt = f"""
    Classify the query.

    Categories:

    TRAVEL
    OFF_TOPIC
    JAILBREAK

    Query:
    {query}

    Return only one word.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()
