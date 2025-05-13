
def detect_intent(prompt: str) -> str:
    prompt = prompt.lower()
    
    # recognizing intent of user divided by most important categories
    
    # help to view or describe a scene, object, surroundings
    if any(x in prompt for x in [
        "what am i holding", 
        "what is this", 
        "do you see", 
        "describe", 
        "what do you see", 
        "what color", 
        "can you see", 
        "what shape", 
        "person", 
        "object", 
        "who is this", 
        "what is in the room",
        "can you tell me what i’m holding",
        "what brand",
        "what’s the flavor",
        "can you see the label",
        "is this a bottle",
        "is it a can",
        "is this food",
        "what flavor",
        "is this a",
        "what is there",
        "what is in front of me",
    ]):
        return "vision"
    
    # help to read
    if any(x in prompt for x in [
        "read", 
        "read this notes", 
        "text", 
        "expiry", 
        "expiration", 
        "can you see the author", 
        "author of", 
        "what does it say", 
        "who wrote", 
        "label", 
        "name on", 
        "can you read",
        "expiring",               
        "expire",                        
        "expiration date",              
        "best before",                  
        "valid until" 
        "what's written",        
        "what is written",      
        "see what’s written",    
        "can you read this",     
        "read this",             
        "any ingredients", 
        "what's this box",
        "what does it say",        
        "ingredients"   
    ]):
        return "ocr"
    
    # help crossing the street
    if any(x in prompt for x in [
    "can i cross", 
    "is it safe to cross", 
    "traffic light", 
    "is the light green", 
    "is the light red", 
    "can i go", 
    "pedestrian light", 
    "crosswalk"
    ]):
        return "crossing"

    # help browsing
    if any(x in prompt for x in ["play", "search", "youtube", "open", "browse"]):
        return "web"
    
    # help know the weather
    if any(x in prompt for x in ["weather", "rain", "sun", "temperature", "forecast"]):
        return "weather"
    
    # help know the time
    if any(x in prompt for x in ["what time", "current time", "tell time", "time is it"]):
        return "time"
    
    # help for reminders, pills, appointment
    if any(x in prompt for x in ["remind", "calendar", "appointment", "medication"]):
        return "calendar"
    
    # help book train
    if any(x in prompt for x in ["train", "ticket", "search train tickets", "book", "book a train", "departure", "arrival", "travel to", "station"]):
        return "train"
    
    # help confirmation train booked
    if any(x in prompt for x in ["yes", "book it", "confirm train", "proceed with train", "go ahead", "i want this ticket"]):
        return "train-confirm"
   
   # help release anxiety, stress, loneliness- human-like companion.
    if any(x in prompt for x in ["sad", "lonely", "depressed", "anxious", "scared", "upset"]):
        return "chat"

    return "chat"
