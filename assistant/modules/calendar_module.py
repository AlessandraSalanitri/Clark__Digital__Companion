import datetime

reminders = []

def handle_calendar_command(prompt):
    now = datetime.datetime.now()
    if "remind" in prompt:
        time_str = " ".join(prompt.split()[-2:])
        reminders.append((time_str, prompt))
        return f"Reminder set for {time_str}."

    elif "what do i have" in prompt:
        return "\n".join([f"At {t}, {msg}" for t, msg in reminders]) or "You have no reminders."

    return "Calendar command received."
