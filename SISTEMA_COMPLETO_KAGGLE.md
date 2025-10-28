# 🤖 Sistema Completo: Descarga Automática → Drive → Kaggle

## 🎯 ¿Qué hace este sistema?

```
┌──────────────┐     ┌───────────────┐     ┌─────────────┐
│   Codespaces │────▶│ Google Drive  │────▶│   Kaggle    │
│              │     │               │     │             │
│ Descarga     │     │ Almacena      │     │ Procesa     │
│ datos        │     │ archivo       │     │ y analiza   │
└──────────────┘     └───────────────┘     └─────────────┘
```

### **Flujo completo:**
1. 📥 **Codespaces:** Descarga datos desde hoy hacia atrás (máximo posible)
2. ☁️ **Google Drive:** Sube el archivo CSV y guarda el file ID
3. 📤 **Notificación:** Envía el file ID a Kaggle (webhook, JSON, o manualmente)
4. 🔬 **Kaggle:** Descarga desde Drive y procesa los datos

---

## 📁 Archivos Creados

| Archivo | Propósito | Dónde ejecutar |
|---------|-----------|----------------|
| `main_auto_kaggle.py` | Descarga datos y sube a Drive | Codespaces/local |
| `kaggle_notebook_processor.py` | Procesa datos desde Drive | Kaggle |
| `drive_file_info.json` | Guarda file ID para transferir | Generado automáticamente |

---

## 🚀 Configuración Paso a Paso

### **Parte 1: Codespaces - Descargar y Subir**

#### Paso 1: Preparar el script

El script `main_auto_kaggle.py` ya está configurado para:
- ✅ Descargar desde **hoy** hacia atrás
- ✅ Calcular automáticamente el máximo de datos disponible
- ✅ Subir a Google Drive
- ✅ Generar `drive_file_info.json` con el file ID

#### Paso 2: Ejecutar

```bash
python main_auto_kaggle.py
```

**Qué pasará:**
1. Detecta si tienes acceso a forex o stocks
2. Calcula el rango óptimo de fechas:
   - Forex: último mes (30 días)
   - Stocks: último año (365 días)
3. Descarga los datos con rate limiting
4. Sube a Google Drive
5. **Genera** `drive_file_info.json` con toda la información

#### Paso 3: Hacer el archivo público (IMPORTANTE)

Para que Kaggle pueda descargar sin autenticación:

**Opción A: Modificar el script para hacerlo automático**

Agrega esta función al final de `main_auto_kaggle.py`:

```python
def make_file_public(file_id, credentials):
    """Hace el archivo público para que Kaggle pueda descargarlo"""
    service = build('drive', 'v3', credentials=credentials)
    
    try:
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        service.permissions().create(
            fileId=file_id,
            body=permission
        ).execute()
        
        print("✅ File is now publicly accessible")
        return True
    except Exception as e:
        print(f"⚠️  Error making file public: {e}")
        return False

# Y luego llámala después de subir:
make_file_public(file_id, creds)
```

**Opción B: Hacerlo manualmente**

1. Ve a Google Drive
2. Encuentra tu archivo
3. Click derecho → Compartir
4. Cambiar a "Cualquier persona con el enlace"
5. Permisos: "Lector"
6. Copiar enlace

---

### **Parte 2: Transferir File ID a Kaggle**

Tienes **3 opciones** para pasar el file ID a Kaggle:

#### **Opción 1: Archivo JSON (Más Fácil)** ⭐ RECOMENDADO

Después de ejecutar el script, tendrás `drive_file_info.json`:

```json
{
  "drive_file_id": "1abc123...",
  "drive_file_url": "https://drive.google.com/...",
  "timestamp": "2025-10-28T...",
  "metadata": {
    "symbol": "AAPL",
    "rows": 125000,
    ...
  }
}
```

**En Kaggle:**
1. Ve a "Add Data" → "Upload"
2. Sube `drive_file_info.json`
3. Crea un dataset (ej: "drive-file-info")
4. En tu notebook, el script lo leerá automáticamente

**Ventaja:** Incluye metadata completa

#### **Opción 2: Variable de Entorno**

**En Kaggle Notebook:**
1. Click en "Add-ons" → "Secrets"
2. Agregar nuevo secreto:
   - Name: `DRIVE_FILE_ID`
   - Value: Tu file ID (ej: `1abc123xyz...`)
3. El script lo leerá automáticamente

**Ventaja:** Más seguro, no expones el ID públicamente

#### **Opción 3: Webhook (Avanzado)**

Para automatización completa, configura un webhook:

```python
# En tu backend/servidor:
@app.route('/kaggle-webhook', methods=['POST'])
def handle_data_upload():
    data = request.json
    file_id = data['drive_file_id']
    
    # Trigger Kaggle kernel
    # ...
    
    return {'status': 'success'}
```

**Luego en `.env` de Codespaces:**
```bash
KAGGLE_WEBHOOK_URL=https://tu-servidor.com/kaggle-webhook
```

---

### **Parte 3: Kaggle - Procesar Datos**

#### Paso 1: Crear Notebook en Kaggle

1. New Notebook
2. Copiar el código de `kaggle_notebook_processor.py`
3. (O subir directamente el archivo)

#### Paso 2: Configurar Datos

Según la opción que elegiste:

**Si usaste Opción 1 (JSON):**
- Add Data → Tu dataset "drive-file-info"
- El script encontrará automáticamente el file ID

**Si usaste Opción 2 (Variable):**
- Add-ons → Secrets → Agregar DRIVE_FILE_ID
- El script lo leerá de `os.getenv()`

**Si hardcodeaste:**
- Modificar línea 30 del notebook:
  ```python
  DRIVE_FILE_ID = 'tu_file_id_aqui'
  ```

#### Paso 3: Ejecutar

Click "Run All" o ejecutar celda por celda:

1. Instala `gdown` (automático)
2. Lee el file ID
3. Descarga desde Drive
4. Carga los datos en DataFrame
5. Analiza y procesa

#### Paso 4: Personalizar Análisis

El notebook incluye ejemplos básicos:
- Medias móviles (SMA)
- Señales de compra/venta
- Estadísticas básicas

**Agrega tu propio análisis:**
```python
# Tus modelos de ML
from sklearn.ensemble import RandomForestClassifier

# Tus estrategias de trading
def mi_estrategia(df):
    # ...
    pass

# Tus visualizaciones
import plotly.express as px
fig = px.line(df, x='timestamp', y='close')
fig.show()
```

---

## 🔄 Automatización Completa

### **Opción A: Cron Job en Codespaces**

Para ejecutar diariamente:

```bash
# Agregar a crontab
0 9 * * * cd /workspaces/MT5 && python main_auto_kaggle.py
```

### **Opción B: GitHub Actions**

Crear `.github/workflows/daily_update.yml`:

```yaml
name: Daily Data Update

on:
  schedule:
    - cron: '0 9 * * *'  # 9 AM daily
  workflow_dispatch:  # Manual trigger

jobs:
  update-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run data update
        env:
          POLYGON_API_KEY: ${{ secrets.POLYGON_API_KEY }}
          GOOGLE_CREDENTIALS_PATH: ${{ secrets.GOOGLE_CREDENTIALS }}
        run: python main_auto_kaggle.py
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: drive-file-info
          path: drive_file_info.json
```

### **Opción C: Kaggle Scheduled Run**

En Kaggle:
1. Settings → Schedule
2. Frequency: Daily
3. Time: Después de tu data update
4. El notebook se ejecutará automáticamente

---

## 📊 Ejemplo Completo de Uso

### **Día 1: Configuración Inicial**

```bash
# 1. En Codespaces
git clone tu-repo
cd MT5
pip install -r requirements.txt

# 2. Autorizar Google Drive (una vez)
python main_auto_kaggle.py
# Seguir proceso OAuth

# 3. Hacer archivo público (añadir al script)
# Ver código arriba en "Opción A"

# 4. En Kaggle
# Subir drive_file_info.json como dataset
# Crear notebook con kaggle_notebook_processor.py
# Run All
```

### **Día 2+: Automático**

```bash
# En Codespaces (o automático con cron/GitHub Actions)
python main_auto_kaggle.py

# En Kaggle (o scheduled run)
# Ejecutar notebook manualmente o esperar scheduled run
```

---

## 🎯 Mejoras Opcionales

### **1. Webhook Real con Flask**

```python
# webhook_server.py
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/data-ready', methods=['POST'])
def handle_upload():
    data = request.json
    file_id = data['drive_file_id']
    
    # Actualizar dataset de Kaggle
    with open('drive_file_info.json', 'w') as f:
        json.dump(data, f)
    
    # Commit a dataset de Kaggle via API
    subprocess.run([
        'kaggle', 'datasets', 'version',
        '-p', '.', '-m', f"New data: {file_id}"
    ])
    
    return {'status': 'success'}

if __name__ == '__main__':
    app.run(port=5000)
```

Deployar en:
- Heroku (gratis)
- Railway
- Render
- Google Cloud Run

### **2. Notificaciones por Email/Slack**

Agregar al script principal:

```python
import smtplib
from email.mime.text import MIMEText

def notify_completion(file_id, file_url):
    msg = MIMEText(f"New data available!\nFile ID: {file_id}\nURL: {file_url}")
    msg['Subject'] = '📊 New Trading Data Ready'
    msg['From'] = 'tu@email.com'
    msg['To'] = 'destino@email.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('tu@email.com', 'password')
        server.send_message(msg)
```

### **3. Dashboard de Monitoring**

Crear `status.json` con:
```json
{
  "last_update": "2025-10-28T09:00:00",
  "status": "success",
  "records": 125000,
  "file_id": "1abc...",
  "next_update": "2025-10-29T09:00:00"
}
```

Y mostrar en web simple o Streamlit dashboard.

---

## 🔧 Troubleshooting

### **Error: "Failed to download from Drive in Kaggle"**

**Solución:**
1. Verifica que el archivo sea público
2. Prueba el link manualmente: `https://drive.google.com/uc?id=TU_FILE_ID`
3. Si no funciona, el archivo no es público

**Hacer público:**
```python
# Agregar al script de upload
make_file_public(file_id, creds)
```

### **Error: "No file ID found in Kaggle"**

**Solución:**
1. Verifica que subiste `drive_file_info.json`
2. O configuraste la variable de entorno
3. Revisa el path en Kaggle: `/kaggle/input/[nombre-dataset]/drive_file_info.json`

### **Error: "Rate limit" en Polygon**

**Solución:**
- Reducir el rango de fechas (menos días)
- Aumentar delay entre requests
- Upgrade a plan pagado de Polygon

---

## 📈 Casos de Uso

### **Caso 1: Backtesting Diario**
- Codespaces descarga datos cada día
- Kaggle ejecuta backtesting automático
- Resultados en dashboard/email

### **Caso 2: ML Model Training**
- Acumular datos históricos en Drive
- Kaggle re-entrena modelo semanalmente
- Deploy modelo actualizado

### **Caso 3: Trading Signals**
- Descarga datos en tiempo "casi real"
- Kaggle genera señales de trading
- Webhook envía señales a bot de trading

---

## ✅ Checklist Final

**Setup inicial:**
- [ ] Script modificado para auto-fechas
- [ ] Google Drive autorizado
- [ ] Archivo se hace público automáticamente
- [ ] `drive_file_info.json` se genera correctamente
- [ ] Kaggle notebook configurado
- [ ] Primera ejecución exitosa end-to-end

**Automatización:**
- [ ] Cron job o GitHub Actions configurado
- [ ] Kaggle scheduled run configurado
- [ ] Notificaciones funcionando (opcional)
- [ ] Monitoring dashboard (opcional)

**Producción:**
- [ ] Manejo de errores robusto
- [ ] Logs guardados
- [ ] Backup de datos
- [ ] Alertas si falla

---

## 🎓 Conclusión

Ahora tienes un sistema completo:
1. ✅ Descarga automática desde hoy
2. ✅ Máximo de datos posible
3. ✅ Upload a Google Drive
4. ✅ File ID transferido a Kaggle
5. ✅ Procesamiento automático en Kaggle

**Todo configurado para correr automáticamente cada día!** 🚀

¿Necesitas ayuda con alguna parte específica?
