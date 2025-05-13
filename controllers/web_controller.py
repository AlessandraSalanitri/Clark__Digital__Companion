from assistant.modules import web

def handle_web_command(prompt: str):
    try:
        return web.perform_web_action(prompt)
    except Exception as e:
        print("[Web Controller Error]:", e)
        return {"error": "Web interaction failed."}

def confirm_checkout():
    try:
        return web.confirm_amazon_checkout()
    except Exception as e:
        print("[Checkout Error]:", e)
        return {"error": "Checkout simulation failed."}
