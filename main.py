import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# 🔑 Alpaca API credentials
ALPACA_API_KEY = "PKGZOOB3FOFGJDYJQX6RK32H5D"
ALPACA_SECRET_KEY = "HPHRNsFzXeBAi1bGyfp7JDYkCqN65NZW24NBGVF4nt3M"

# 🕰️ Rango de fechas
start_date = datetime(2023, 10, 1)
end_date = datetime(2023, 10, 5)

# 🧲 Inicializar cliente Alpaca
client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)

# 📈 Solicitar datos
request_params = StockBarsRequest(
    symbol_or_symbols=["AAPL"],
    timeframe=TimeFrame.Day,
    start=start_date,
    end=end_date
)

bars = client.get_stock_bars(request_params)
df = bars.df
df.to_csv("aapl_data.csv", index=False)

# ☁️ Autenticación Google Drive
gauth = GoogleAuth()
gauth.LoadCredentialsFile("credentials.json")
if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()
gauth.SaveCredentialsFile("credentials.json")

drive = GoogleDrive(gauth)

# 📤 Subir archivo
file = drive.CreateFile({'title': 'aapl_data.csv'})
file.SetContentFile('aapl_data.csv')
file.Upload()

print("✅ Archivo subido a Google Drive.")
