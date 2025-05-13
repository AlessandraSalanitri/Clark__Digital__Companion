import os
import urllib.parse
import shutil
import time
from audio.voice import tts

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from config.config import DEMO_AMAZON_EMAIL, DEMO_AMAZON_PASSWORD

last_context = {
    "intent": None,
    "query": None,
    "results": [], 
}

def get_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    chrome_path = shutil.which("chrome") or r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        print("Chrome not found.")
        tts("I need Google Chrome to open websites. Please install it.")
        return None

    options.binary_location = chrome_path
    try:
        driver = uc.Chrome(options=options)
        return driver
    except Exception as e:
        print("Chrome launch failed:", e)
        tts("I tried to launch the browser, but something went wrong.")
        return None


# Store last item selected globally for ordering
last_driver = None  # to keep browser session live



################## PERFORM SEARCH SCRAPING AND COMPLETING PURCHASE ON AMAZON ##################
def perform_web_action(prompt):
    global last_driver, last_context

    prompt = prompt.lower()

    if "amazon" in prompt or ("search" in prompt and "top" not in prompt):
        return search_amazon(prompt)

    elif "top 5" in prompt or "cheapest" in prompt:
        if last_context["intent"] == "amazon_search" and last_context["query"]:
            return search_amazon(last_context["query"], raw=True)
        else:
            return "Can you clarify what you'd like me to list?"

    elif "buy it" in prompt or "order it" in prompt:
        return confirm_amazon_checkout()

    return general_google_search(prompt)




def search_amazon(prompt, raw=False):
    global last_driver, last_context

    search_query = prompt if raw else extract_keywords(prompt)    
    last_context["intent"] = "amazon_search"
    last_context["query"] = search_query
    query = urllib.parse.quote(search_query)
    
    
    driver = get_driver()
    if not driver:
        return "Unable to open browser."

    url = f"https://www.amazon.com/s?k={query}"
    driver.get(url)
    last_driver = driver  # save driver for next step

    tts(f"Searching Amazon for {search_query}")

    try:
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
    
        items = soup.select("div.s-result-item[data-component-type='s-search-result']")
        results = []
                
        for item in items[:5]:  
            title_elem = item.select_one("h2 span.a-text-normal")
            price_elem = item.select_one("span.a-price > span.a-offscreen")
            rating_elem = item.select_one("span.a-icon-alt")

            title = title_elem.text.strip() if title_elem else "No title"
            price = price_elem.text.strip() if price_elem else "Unknown"
            rating = rating_elem.text.strip() if rating_elem else "No rating"

            results.append({
                "title": title,
                "price": price,
                "rating": rating
            })
            
        last_context["results"] = results


        if results:
            print(f"[Clark] Parsed {len(results)} Amazon results.")
            return {"amazon_results": results}
        else:
            return {"amazon_results": []}

    except Exception as e:
        print("Amazon parse error:", e)
        return "I opened Amazon but couldn't fetch results."


def extract_keywords(prompt):
    ignore = ["can you", "please", "could you", "would you", "i want", "search", "look for", "find", "on amazon", "in amazon", "browse", "buy", "order", "for me", "a product", "the product", "check", "see"]
    prompt = prompt.lower()
    for phrase in ignore:
        prompt = prompt.replace(phrase, "")
    return prompt.strip()


def login_amazon(driver):
    try:
        sign_in_btn = driver.find_element(By.ID, "nav-link-accountList")
        sign_in_btn.click()
        time.sleep(2)

        email_input = driver.find_element(By.ID, "ap_email")
        email_input.send_keys(DEMO_AMAZON_EMAIL)
        driver.find_element(By.ID, "continue").click()
        time.sleep(2)

        password_input = driver.find_element(By.ID, "ap_password")
        password_input.send_keys(DEMO_AMAZON_PASSWORD)
        driver.find_element(By.ID, "signInSubmit").click()
        time.sleep(3)

        print("Logged into demo Amazon.")
        tts("Logged into your Amazon account.")
        return True

    except Exception as e:
        print("Amazon login failed:", e)
        tts("I couldn't log into Amazon. Please check demo credentials.")
        return False



def confirm_amazon_checkout():
    global last_driver

    try:
        if not last_driver:
            return "No previous product to act on."

        tts("Attempting to add the item to cart and simulate checkout.")

        # Click first product
        product = last_driver.find_elements(By.CSS_SELECTOR, "h2 a")[0]
        product.click()
        time.sleep(2)

        # Switch to new tab
        last_driver.switch_to.window(last_driver.window_handles[-1])

        # OPTIONAL: Login if needed
        if "signin" in last_driver.current_url:
            login_amazon(last_driver)

        # Click 'Add to cart'
        add_btn = last_driver.find_element(By.ID, "add-to-cart-button")
        add_btn.click()
        time.sleep(2)

        # Proceed to cart
        last_driver.get("https://www.amazon.com/gp/cart/view.html")
        time.sleep(2)

        # Simulate final step
        tts("Item is now in cart. For demo, I’m stopping before payment.")

        # Optionally go to cart (don't buy!)
        tts("Item added to cart. I’m stopping here for safety.")

        return "Added to cart. Ready for checkout, but we’re stopping for demo."

    except Exception as e:
        print("Checkout simulation failed:", e)
        return "I couldn't complete the cart step. Please try again."


def general_google_search(prompt):
    driver = get_driver()
    if not driver:
        return "Unable to open browser."

    lower_prompt = prompt.lower()

    if "youtube" in lower_prompt or "play" in lower_prompt:
        try:
            driver.get("https://www.youtube.com")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "search_query"))
            )
            keywords = extract_keywords(prompt)
            search_input = driver.find_element(By.NAME, "search_query")
            search_input.send_keys(keywords)
            search_input.send_keys(Keys.RETURN)

            tts(f"Looking on YouTube for {keywords}")
            return f"Searching YouTube for '{keywords}'."
        except Exception as e:
            print("YouTube search failed:", e)
            return "Opened YouTube, but couldn't search properly."

    # Fallback to Google
    keywords = extract_keywords(prompt)
    query = urllib.parse.quote(keywords)
    url = f"https://www.google.com/search?q={query}"
    driver.get(url)
    tts(f"Searching Google for {keywords}")
    return f"Searching Google for '{keywords}'."