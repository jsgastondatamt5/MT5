import pandas as pd
from datetime import datetime
from MetaTrader5 import initialize, shutdown, copy_rates_range
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Inicializar MT5
initialize()

# Descargar datos
rates = copy_rates_range("EURUSD", timeframe=1,  # 1 = M1
                         from_date=datetime(2023, 1, 1),
                         to_date=datetime(2023, 1, 2))

# Guardar como CSV
df = pd.DataFrame(rates)
df.to_csv("eurusd.csv", index=False)

# Autenticación con Google Drive
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

# Subir archivo
file = drive.CreateFile({'title': 'eurusd.csv'})
file.SetContentFile('eurusd.csv')
file.Upload()

shutdown()
print("Archivo subido a Google Drive.")
