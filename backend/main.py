# ```python
import json
import time
import google.generativeai as genai

from fastapi import FastAPI
from fastapi import WebSocket
from fastapi import WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import GEMINI_API_KEY
from backend.prompts import SYSTEM_PROMPT
from backend.guardrails import detect_jailbreak
from backend.intent_classifier import classify_intent
from backend.travel_search import travel_search
from backend.logger import log_turn
from backend.memory import get_memory, update_memory







# =====================================================
# Gemini Setup
# =====================================================

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash"
)

# =====================================================
# FastAPI
# =====================================================

app = FastAPI(title="TravelMate AI")

app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)

# =====================================================
# Homepage
# =====================================================

@app.get("/")
async def home():
    return FileResponse("frontend/index.html")


# =====================================================
# Greeting
# =====================================================

WELCOME_MESSAGE = """
Hello 

I'm TravelMate AI.

I can help with:

 Flights
 Hotels
 Destinations
 Travel Itineraries
 Trip Planning

Where would you like to travel today?
"""


# =====================================================
# Extract memory
# =====================================================

def update_user_memory(text):

    lower = text.lower()

    destinations = [
        "goa",
        "paris",
        "london",
        "dubai",
        "bali",
        "tokyo",
        "bangkok",
        "singapore"
    ]

    for city in destinations:

        if city in lower:
            update_memory("destination", city.title())


# =====================================================
# Generate Travel Response
# =====================================================

def generate_response(user_text):

    memory = get_memory()

    destination = memory.get("destination")

    context = ""

    if destination:
        context += f"User destination preference: {destination}\n"

    prompt = f"""
{SYSTEM_PROMPT}

Travel Context:
{context}

User:
{user_text}
"""

    response = model.generate_content(prompt)

    return response.text


# =====================================================
# WebSocket
# =====================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    try:

        await websocket.send_json(
            {
                "type": "greeting",
                "message": WELCOME_MESSAGE
            }
        )

        while True:

            data = await websocket.receive_text()

            payload = json.loads(data)

            user_text = payload.get("text", "").strip()

            if not user_text:
                continue

            start_time = time.time()

            # ======================================
            # Memory Update
            # ======================================

            update_user_memory(user_text)

            # ======================================
            # Jailbreak Check
            # ======================================

            if detect_jailbreak(user_text):

                response = (
                    "I'm TravelMate AI and can only assist with travel "
                    "planning, destinations, hotels, flights and itineraries. "
                    "How can I help with your travel plans?"
                )

                latency = round(time.time() - start_time, 2)

                log_turn(
                    user_text,
                    response,
                    latency
                )

                await websocket.send_json(
                    {
                        "type": "response",
                        "message": response,
                        "latency": latency,
                        "intent": "JAILBREAK"
                    }
                )

                continue

            # ======================================
            # Intent Classification
            # ======================================

            try:
                intent = classify_intent(user_text)

            except Exception:
                intent = "TRAVEL"

            # ======================================
            # Off Topic
            # ======================================

            if intent == "OFF_TOPIC":

                response = (
                    "I specialize in travel assistance only. "
                    "I can help with flights, hotels, destinations, "
                    "visa information and trip planning."
                )

                latency = round(time.time() - start_time, 2)

                log_turn(
                    user_text,
                    response,
                    latency
                )

                await websocket.send_json(
                    {
                        "type": "response",
                        "message": response,
                        "latency": latency,
                        "intent": "OFF_TOPIC"
                    }
                )

                continue

            # ======================================
            # Travel Search Trigger
            # ======================================

            search_keywords = [
                "hotel",
                "flight",
                "best places",
                "tourist",
                "destination",
                "trip",
                "travel"
            ]

            use_search = any(
                word in user_text.lower()
                for word in search_keywords
            )

            search_context = ""

            if use_search:

                try:

                    result = travel_search(user_text)

                    organic = result.get("organic", [])

                    top_results = []

                    for item in organic[:3]:

                        title = item.get("title", "")
                        snippet = item.get("snippet", "")

                        top_results.append(
                            f"{title}\n{snippet}"
                        )

                    search_context = "\n".join(top_results)

                except Exception:
                    search_context = ""

            # ======================================
            # Gemini Response
            # ======================================

            final_prompt = f"""
{SYSTEM_PROMPT}

IMPORTANT:
Detect the user's language automatically and respond in the same language.

Search Results:
{search_context}

User Question:
{user_text}
"""

            gemini_response = model.generate_content(
                final_prompt
            )

            response = gemini_response.text

            latency = round(
                time.time() - start_time,
                2
            )

            log_turn(
                user_text,
                response,
                latency
            )

            await websocket.send_json(
                {
                    "type": "response",
                    "message": response,
                    "latency": latency,
                    "intent": intent
                }
            )

    except WebSocketDisconnect:

        print("Client disconnected")

    except Exception as e:

        print("ERROR:", e)

        await websocket.close()

