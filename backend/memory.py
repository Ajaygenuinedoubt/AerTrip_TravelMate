memory_store = {
    "destination": None,
    "budget": None,
    "travel_dates": None,
    "language": "English"
}

def update_memory(key, value):
    memory_store[key] = value

def get_memory():
    return memory_store

def clear_memory():
    global memory_store

    memory_store = {
        "destination": None,
        "budget": None,
        "travel_dates": None,
        "language": "English"
    }
