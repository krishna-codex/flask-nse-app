import os
import time
import pandas as pd
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv
import warnings
import sys
import logging

# 🔇 Suppress warnings and logs
warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.CRITICAL)

class DevNull:
    def write(self, msg): pass
    def flush(self): pass
sys.stderr = DevNull()

# ✅ Load environment variables from .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

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

def save_to_postgres(df, table_name):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        columns = df.columns.tolist()
        col_defs = ', '.join([f'"{col}" TEXT' for col in columns])
        create_query = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({col_defs});'
        cursor.execute(create_query)

        placeholders = ', '.join(['%s'] * len(columns))
        col_names = ', '.join([f'"{col}"' for col in columns])
        insert_query = f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders});'

        for row in df.itertuples(index=False, name=None):
            cursor.execute(insert_query, row)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Data saved to PostgreSQL table: {table_name}")

    except Exception as e:
        print(f"❌ DB Error: {e}")

def connect_and_scrape():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.7204.157 Safari/537.36"
        )
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        print("🌐 Launching headless browser...")

        # ✅ Auto-detect ChromeDriver in Windows/macOS/Docker
        driver = webdriver.Chrome(options=chrome_options)

        driver.get("https://www.nseindia.com")
        time.sleep(2)
        driver.get("https://www.nseindia.com/reports/fii-dii")

        print("⏳ Waiting for tables to load...")
        WebDriverWait(driver, 15).until(lambda d: len(d.find_elements(By.TAG_NAME, "table")) >= 3)

        tables = driver.find_elements(By.TAG_NAME, "table")
        if len(tables) >= 3:
            print("✅ Tables found. Extracting...")

            df_nse = extract_table_data(tables[1])
            df_combined = extract_table_data(tables[2])

            scraped_date = df_nse["DATE"].iloc[0].strip().replace("/", "-").replace(" ", "_")
            print(f"📆 Scraped Data Date: {scraped_date}")

            save_to_postgres(df_nse, "nse")
            save_to_postgres(df_combined, "combined_nse_bse_msei")

        else:
            print(f"⚠️ Only {len(tables)} tables found. Expected at least 3.")

        driver.quit()

    except Exception as e:
        print(f"❌ Scraping Error:\n{str(e)}")

def verify_data_from_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

        df_nse_all = pd.read_sql("SELECT * FROM nse", conn)
        df_combined_all = pd.read_sql("SELECT * FROM combined_nse_bse_msei", conn)

        latest_date_nse = df_nse_all["DATE"].max()
        latest_date_combined = df_combined_all["DATE"].max()

        df_nse_latest = df_nse_all[df_nse_all["DATE"] == latest_date_nse].drop_duplicates()
        df_combined_latest = df_combined_all[df_combined_all["DATE"] == latest_date_combined].drop_duplicates()

        print(f"\n📊 NSE Table Preview (Date: {latest_date_nse}):")
        print(df_nse_latest.to_string(index=False))

        print(f"\n📊 Combined Table Preview (Date: {latest_date_combined}):")
        print(df_combined_latest.to_string(index=False))

        conn.close()

    except Exception as e:
        print(f"❌ Verification Error: {e}")

if __name__ == "__main__":
    connect_and_scrape()
    verify_data_from_db()
