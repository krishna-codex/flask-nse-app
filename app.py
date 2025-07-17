import webbrowser
from flask import Flask, render_template_string
import pandas as pd
from threading import Timer

app = Flask(__name__)
file_path = "FII_DII_Trading_Activity_July_16_2025.xlsx"
df_nse = pd.read_excel(file_path, sheet_name="NSE Only")
df_all = pd.read_excel(file_path, sheet_name="NSE_BSE_MSEI")

HTML = """
<!doctype html><html><head><title>Dashboard</title></head><body>
<h2>NSE Only</h2>{{ nse | safe }}
<h2>NSE + BSE + MSEI</h2>{{ all | safe }}
</body></html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, nse=df_nse.to_html(index=False), all=df_all.to_html(index=False))

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=True, host="127.0.0.1", port=5000)
