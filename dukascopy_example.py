from datetime import datetime, timedelta
import dukascopy_python
from dukascopy_python.instruments import INSTRUMENT_FX_MAJORS_GBP_USD

start = datetime(2022, 1, 1)
end = datetime(2022, 5, 1)
instrument = INSTRUMENT_FX_MAJORS_GBP_USD
interval = dukascopy_python.INTERVAL_MIN_1
offer_side = dukascopy_python.OFFER_SIDE_BID

df = dukascopy_python.fetch(
    instrument,
    interval,
    offer_side,
    start,
    end,
)

# Convertir el índice a columna (si el timestamp está en el índice)
df = df.reset_index()

# Verificar los nombres de columnas (por si necesitas renombrar 'index')
print("Columnas del DataFrame:", df.columns.tolist())

df = df.rename(columns={'index': 'timestamp'})
# Guardar como CSV incluyendo la columna del timestamp
df.to_csv("output.csv", index=False)