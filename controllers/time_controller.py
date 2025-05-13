from assistant.modules import time_module

def fetch_time():
    try:
        return time_module.get_time()
    except Exception as e:
        print("[Time Controller Error]:", e)
        return "Unable to get the current time."
