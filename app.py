
import os
import time
import pandas as pd
import psycopg2
import warnings
import logging
import sys
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait

# 🔇 Suppress warnings and logs
warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.CRITICAL)

# ✅ Force Python to flush output immediately
sys.stdout.reconfigure(line_buffering=True)

# ✅ Load environment variables from .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "host.docker.internal")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def extract_table_data(table):
    rows = table.find_elements(By.TAG_NAME, "tr")
    data = [
        [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, "th") + row.find_elements(By.TAG_NAME, "td")]
        for row in rows
    ]
    if len(data) > 1:
        max_cols = max(len(r) for r in data)
        return pd.DataFrame([r + [""] * (max_cols - len(r)) for r in data[1:]], columns=data[0])
    return pd.DataFrame()

def save_to_postgres(df, table):
    try:
        with psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        ) as conn:
            with conn.cursor() as cursor:
                columns = df.columns.tolist()
                col_defs = ', '.join([f'"{col}" TEXT' for col in columns])
                cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({col_defs});')
                placeholders = ', '.join(['%s'] * len(columns))
                col_names = ', '.join([f'"{col}"' for col in columns])
                insert_query = f'INSERT INTO "{table}" ({col_names}) VALUES ({placeholders});'
                cursor.executemany(insert_query, df.itertuples(index=False, name=None))
        print(f"✅ Data saved to PostgreSQL table: {table}")
    except Exception as e:
        print(f"❌ DB Error: {e}")

def webdriver_config():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.90 Safari/537.36")
    chrome_options.binary_location = "/usr/bin/chromium"  # ✅ REQUIRED LINE

    prefs = {
        "download.prompt_for_download": False,        
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def connect_and_scrape():
    try:
        # options = Options()
        # options.add_argument("--headless=new")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--disable-gpu")
        # options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_argument("--window-size=1920,1080")
        # options.add_argument("--remote-debugging-port=9222")
        # options.add_argument("--disable-extensions")
        # options.add_argument("--disable-infobars")
        # options.add_argument("--start-maximized")
        # options.add_argument("--disable-accelerated-2d-canvas")
        # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.224 Safari/537.36")
        # options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # print("🌐 Launching headless browser...")
        # driver = webdriver.Chrome(service=Service(), options=options)
        driver = webdriver_config()
        driver.implicitly_wait(10)

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
        with psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        ) as conn:
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

    except Exception as e:
        print(f"❌ Verification Error: {e}")

if __name__ == "__main__":
    connect_and_scrape()
    verify_data_from_db()
