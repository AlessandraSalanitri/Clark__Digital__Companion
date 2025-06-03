import datetime
import threading
import time
import dateparser
import re

reminders = []
reminder_condition = threading.Condition()
active_reminder = None

def extract_time_phrase(prompt: str) -> str:
    word_to_num = {
        "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
        "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"
    }
    
    prompt = prompt.lower()
    for word, num in word_to_num.items():
        prompt = re.sub(rf"\b{word}\b", num, prompt)

    patterns = [
        r"in \d+ (seconds?|minutes?|hours?|days?)",
        r"tomorrow(?: at \d{1,2}(?::\d{2})?\s?(am|pm)?)?",
        r"at \d{1,2}(?::\d{2})?\s?(am|pm)?",
        r"\d{1,2}(?::\d{2})?\s?(am|pm)?",
        r"in an? (hour|minute|day)",
        r"\d+ (seconds?|minutes?|hours?|days?) from now"
    ]
    for pattern in patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            return match.group()
    return prompt

def handle_calendar_command(prompt):
    global reminders
    now = datetime.datetime.now()
    normalized = prompt.lower()

    if "remind" in normalized or "set reminder" in normalized:
        time_phrase = extract_time_phrase(prompt)
        parsed_time = dateparser.parse(
            time_phrase,
            settings={
                "PREFER_DATES_FROM": "future",
                "RETURN_AS_TIMEZONE_AWARE": False,
                "RELATIVE_BASE": now
            }
        )

        if parsed_time:
            message = prompt.replace(time_phrase, "").strip()
            reminders.append((parsed_time, message))
            with reminder_condition:
                reminder_condition.notify()  # wake up checker
            return f"Reminder set for {parsed_time.strftime('%H:%M')}."
        else:
            return f"I couldn't understand the reminder time. (Got: '{time_phrase}')"

    elif "what do i have" in normalized:
        return "\n".join([f"At {t.strftime('%H:%M')}, {msg}" for t, msg in reminders]) or "You have no reminders."

    return "Calendar command received."

def reminder_checker():
    global reminders, active_reminder
    while True:
        with reminder_condition:
            if not reminders:
                reminder_condition.wait()
                
                
        now = datetime.datetime.now()
        for r in reminders[:]:
            t, msg = r
            if now >= t:
                print(f"[DEBUG] Reminder triggered: {msg}") 
                active_reminder = msg
                reminders.remove(r)
        time.sleep(1) 
        
        
def get_active_reminder():
    return active_reminder

def clear_active_reminder():
    global active_reminder
    active_reminder = None

threading.Thread(target=reminder_checker, daemon=True).start()
