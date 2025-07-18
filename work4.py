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

# 🧪 Load environment variables from .env file
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

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

        # Dynamically build CREATE TABLE query
        columns = df.columns.tolist()
        col_defs = ', '.join([f'"{col}" TEXT' for col in columns])
        create_query = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({col_defs});'
        cursor.execute(create_query)

        # Insert data
        placeholders = ', '.join(['%s'] * len(columns))
        col_names = ', '.join([f'"{col}"' for col in columns])
        insert_query = f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders});'

        for row in df.itertuples(index=False, name=None):
            cursor.execute(insert_query, row)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Data saved to table: {table_name}")

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
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"
        )
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        print("🌐 Launching headless browser...")
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

            # 💾 Save to PostgreSQL
            save_to_postgres(df_nse, "nse")
            save_to_postgres(df_combined, "combined_nse_bse_msei")

        else:
            print(f"⚠️ Only {len(tables)} tables found. Expected at least 3.")

        driver.quit()

    except Exception as e:
        print(f"❌ Real Error occurred:\n{str(e)}")

if __name__ == "__main__":
    connect_and_scrape()

#for checking the data is stores in the data base 

import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

# Read from nse table
df = pd.read_sql("SELECT * FROM nse", conn)
print(df.head())



















