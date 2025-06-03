import time
import re
import logging
from audio.voice import tts
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from assistant.modules.web import get_driver
import platform
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

last_train_driver = None
last_train_options = []

def get_day_selector(date):
    if platform.system() == "Windows":
        return date.strftime("%#d")
    return date.strftime("%-d")


def parse_train_query(prompt):
    match = re.search(r'from\s+(.*?)\s+to\s+(.*?)(?:\s|$)', prompt.lower())
    if match:
        origin = match.group(1)
        destination = match.group(2)
    else:
        origin = "London"
        destination = "Manchester"

    date = "tomorrow" if "tomorrow" in prompt.lower() else "today"
    time_str = "10:00"

    # Detect trip type
    if "return" in prompt.lower() and "open" not in prompt.lower():
        trip_type = "return"
    elif "open return" in prompt.lower():
        trip_type = "open-return"
    elif "one-way" in prompt.lower() or "one way" in prompt.lower():
        trip_type = "one-way"
    else:
        trip_type = "unknown"

    return origin.title(), destination.title(), date, time_str, trip_type


def book_train_ticket(prompt):
    origin, destination, date, time_str, trip_type = parse_train_query(prompt)
    
    if trip_type == "unknown":
        return "awaiting_trip_type"

    tts(f"Looking for a {trip_type.replace('-', ' ')} train from {origin} to {destination} {date} at {time_str}")

    driver = get_driver()
    if not driver:
        return "Unable to open browser."

    try:
        driver.get("https://www.thetrainline.com/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "origin")))

        # Accept cookies
        try:
            accept_cookies = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            accept_cookies.click()
        except BaseException:
            pass

        # Fill 'From' field
        from_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "origin"))
        )
        from_input.clear()
        from_input.send_keys(origin)
        time.sleep(1)
        from_input.send_keys(Keys.ENTER)

        # Fill 'To' field
        to_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "destination"))
        )
        to_input.clear()
        to_input.send_keys(destination)
        time.sleep(1)
        to_input.send_keys(Keys.ENTER)

        # Select trip type tab
        try:
            trip_type_id_map = {
                "one-way": "single",
                "return": "return",
                "open-return": "openReturn"
            }

            if trip_type in trip_type_id_map:
                driver.find_element(By.ID, trip_type_id_map[trip_type]).click()
                time.sleep(1)
            else:
                logger.warning("Unknown trip type, defaulting to 'one-way'")
                driver.find_element(By.ID, "single").click()
        except Exception as e:
            logger.warning(f"Could not select trip type: {e}")

        # Fill date and time
        try:
            date_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "jsf-outbound-time-input-toggle"))
            )

            date_field.click()
            time.sleep(1)

            # Select date from calendar based on `date`
            if date == "tomorrow":
                day_selector = get_day_selector(datetime.today() + timedelta(days=1))
            else:
                day_selector = get_day_selector(datetime.today())


            target_date = datetime.today() + timedelta(days=1) if date == "tomorrow" else datetime.today()
            iso = target_date.strftime("%Y-%m-%d")

            calendar_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"button[data-date='{iso}']"))
            )

            calendar_button.click()
            time.sleep(1)

            # time entry
            time_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            for input_elem in time_inputs:
                if "time" in input_elem.get_attribute("name").lower():
                    input_elem.clear()
                    input_elem.send_keys(time_str)
                    break

        except Exception as e:
            logger.warning(f"Could not set date/time: {e}")

        # Disable "Open places to stay" checkbox if checked
        try:
            checkbox = driver.find_element(By.ID, "bookingPromo")
            if checkbox.is_selected():
                label = driver.find_element(By.CSS_SELECTOR, "label[for='bookingPromo']")
                label.click()
                logger.info("Unchecked 'Open places to stay'")
                time.sleep(0.5)
        except Exception as e:
            logger.warning(f"Could not uncheck 'Open places to stay': {e}")

        # Click the real search button
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test='submit-journey-search-button']"))
        )
        search_button.click()
        tts("Searching for available trains.")

        # wait for results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test='journey-result']"))
        )
        time.sleep(1)


        # Scrape results
        options = driver.find_elements(By.CSS_SELECTOR, "div[data-test='journey-result']")

        if not options:
            tts("No results found.")
            return "No train options available."

        results = []
        for option in options[:3]:
            try:
                time_elem = option.find_element(By.CSS_SELECTOR, "div[data-test='time'] span")
                price_elem = option.find_element(By.CSS_SELECTOR, "div[data-test='price'] strong")
                train_time = time_elem.text if time_elem else "Unknown time"
                train_price = price_elem.text if price_elem else "Unknown price"
                results.append(f"{train_time} for {train_price}")
            except Exception as e:
                logger.warning(f"Error parsing option: {e}")
                continue

        spoken = ". ".join(results)
        tts(f"I found a few options. {spoken}. Want me to continue to checkout?")

        global last_train_driver
        last_train_driver = driver
        last_train_options = results

        return "Train options retrieved. Say 'yes' to proceed."

    except Exception as e:
        logger.exception("An error occurred during train booking.")
        tts("I couldn't finish searching trains.")
        driver.quit()
        return "Error occurred during train booking."


def confirm_train_booking():
    global last_train_driver

    try:
        if not last_train_driver:
            return "No train selection to proceed with."

        # Simulate clicking the first "Buy" or "View" button
        btn = WebDriverWait(last_train_driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test='buy-button']"))
        )
        btn.click()
        tts("Taking you to checkout. You can complete the booking there.")
        return "Proceeding to checkout (simulated)."
    except Exception as e:
        logger.warning(f"Train checkout failed: {e}")
        return "Something went wrong trying to continue to checkout."

