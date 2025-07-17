import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def connect_to_fii_dii_page():
    # Set up Chrome options
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--start-maximized')
    # Don't use headless mode if you want the browser to stay open
    # options.add_argument('--headless')  # Only if you want headless

    # Start browser session
    print("🌐 Launching browser and connecting to NSE FII/DII page...")
    driver = uc.Chrome(options=options)

    try:
        # Open FII/DII Reports page
        driver.get("https://www.nseindia.com/reports/fii-dii")
        time.sleep(6)  # Allow time for JavaScript-heavy content to load

        print(f"✅ Connected. Page title: {driver.title}")
        print("🚦 Browser will remain open. Press Ctrl+C to exit in terminal.")
        
        # Keep browser open without quitting
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("🧹 Exit requested. Closing browser.")
        driver.quit()
    except Exception as e:
        print(f"❌ Error: {e}")
        driver.quit()

# ✅ Fixed line below
if __name__ == "__main__":
    connect_to_fii_dii_page()