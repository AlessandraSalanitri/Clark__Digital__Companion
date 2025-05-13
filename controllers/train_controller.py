from assistant.modules import trainline

def book_train(prompt: str) -> str:
    try:
        return trainline.book_train_ticket(prompt)
    except Exception as e:
        print("[Train Controller Error]:", e)
        return "Sorry, I couldn't book a train."

def confirm_booking() -> str:
    try:
        return trainline.confirm_train_booking()
    except Exception as e:
        print("[Train Confirm Error]:", e)
        return "Sorry, confirmation failed."
