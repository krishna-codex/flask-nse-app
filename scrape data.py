import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import warnings
import sys
import logging

# Suppress all warnings and logs
warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.CRITICAL)

# Suppress undetected_chromedriver console error
class DevNull:
    def write(self, msg): pass
    def flush(self): pass

sys.stderr = DevNull()

def extract_table_data(table_element):
    rows = table_element.find_elements(By.TAG_NAME, "tr")
    data = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "th") + row.find_elements(By.TAG_NAME, "td")
        data.append([cell.text.strip() for cell in cells])
    if len(data) > 1:
        max_cols = max(len(row) for row in data)
        data = [row + [""] * (max_cols - len(row)) for row in data]
        return pd.DataFrame(data[1:], columns=data[0])
    return pd.DataFrame()

def connect_and_scrape():
    try:
        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')

        print("🌐 Launching browser...")
        driver = uc.Chrome(options=options)
        driver.get("https://www.nseindia.com/reports/fii-dii")
        time.sleep(8)  # Let the page load

        tables = driver.find_elements(By.TAG_NAME, "table")

        if len(tables) >= 3:
            print("✅ Found all required tables. Extracting...")

            # We're skipping the first table ("NSE Only")
            df_nse = extract_table_data(tables[1])              # Now saved as "NSE"
            df_combined = extract_table_data(tables[2])         # Now saved as "Combined NSE-BSE-MSEI"

            file_name = "fii_dii_data.xlsx"
            with pd.ExcelWriter(file_name, engine="openpyxl") as writer:
                df_nse.to_excel(writer, sheet_name="NSE", index=False)
                df_combined.to_excel(writer, sheet_name="Combined NSE-BSE-MSEI", index=False)

            print(f"✅ Data saved in '{file_name}' with sheets:")
            print("   - NSE")
            print("   - Combined NSE-BSE-MSEI")

        else:
            print(f"⚠️ Only {len(tables)} tables found. Expected at least 3.")

        driver.quit()

    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    connect_and_scrape()