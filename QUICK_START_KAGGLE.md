# 🎯 Resumen: Script Modificado para Auto-Fechas y Kaggle

## ✅ Lo que pediste

1. ✅ **Descarga desde hoy hacia atrás (máximo posible)**
2. ✅ **Envía file ID a Kaggle**
3. ✅ **Archivo público automáticamente** (para que Kaggle pueda descargarlo)

---

## 📁 Archivos Principales

### **1. main_auto_kaggle.py** 
**Ejecutar en: Codespaces/Local**

**Qué hace:**
- 📅 Calcula automáticamente fechas desde HOY hacia atrás
- 📊 Descarga el máximo posible según tu API:
  - Stocks: 1 año (365 días)
  - Forex: 1 mes (30 días)
- ☁️ Sube a Google Drive
- 🌍 **HACE EL ARCHIVO PÚBLICO AUTOMÁTICAMENTE**
- 💾 Genera `drive_file_info.json` con file ID

**Ejecutar:**
```bash
python main_auto_kaggle.py
```

### **2. kaggle_notebook_processor.py**
**Ejecutar en: Kaggle**

**Qué hace:**
- 🔍 Lee el file ID (desde JSON o variable)
- 📥 Descarga desde Google Drive
- 📊 Carga datos en DataFrame
- 🤖 Analiza y procesa (incluye ejemplos)

**Usar:**
1. Crear nuevo notebook en Kaggle
2. Copiar este código
3. Configurar file ID (ver métodos abajo)
4. Run All

---

## 🚀 Cómo Usar (Guía Rápida)

### **Paso 1: En Codespaces**

```bash
# Ejecutar script
python main_auto_kaggle.py

# Seguir proceso OAuth si es primera vez
# El script hace automáticamente:
# ✅ Descarga desde hoy
# ✅ Sube a Drive
# ✅ Hace archivo público
# ✅ Genera drive_file_info.json
```

**Resultado:**
```
✅ SUCCESS! File uploaded to Google Drive
📄 File: eurusd_data_20251028.csv
📊 Records: 125,450
🆔 Drive ID: 1abc123xyz...
🔗 View: https://drive.google.com/file/d/1abc123xyz.../view
📥 Direct Download: https://drive.google.com/uc?id=1abc123xyz...

💾 File info saved: drive_file_info.json
```

### **Paso 2: Transferir a Kaggle**

**Opción A: Subir JSON (Más fácil)** ⭐

```bash
# 1. Descargar drive_file_info.json de Codespaces
# 2. En Kaggle: Add Data → Upload
# 3. Subir drive_file_info.json
# 4. Listo! El notebook lo leerá automáticamente
```

**Opción B: Variable de Entorno**

En Kaggle:
1. Add-ons → Secrets
2. Name: `DRIVE_FILE_ID`
3. Value: `1abc123xyz...` (copiar del terminal)

**Opción C: Hardcodear (testing)**

En el notebook de Kaggle, línea 30:
```python
DRIVE_FILE_ID = '1abc123xyz...'
```

### **Paso 3: En Kaggle**

```python
# Ejecutar notebook
# Automáticamente:
# ✅ Instala gdown
# ✅ Lee file ID
# ✅ Descarga desde Drive (sin autenticación!)
# ✅ Procesa datos
# ✅ Genera análisis
```

---

## 📊 Configuración de Fechas

El script calcula automáticamente el rango óptimo:

```python
# En main_auto_kaggle.py, líneas 31-34:
END_DATE = datetime.now()  # HOY
DAYS_TO_DOWNLOAD = 365  # 1 año (ajustable)
START_DATE = END_DATE - timedelta(days=DAYS_TO_DOWNLOAD)
```

**Modificar si quieres:**
- Más días: `DAYS_TO_DOWNLOAD = 730`  # 2 años
- Menos días: `DAYS_TO_DOWNLOAD = 90`  # 3 meses
- Rango específico:
  ```python
  START_DATE = datetime(2024, 1, 1)
  END_DATE = datetime(2024, 12, 31)
  ```

---

## 🔑 Características Clave

### **Auto-Fechas Inteligentes**

```python
def calculate_optimal_date_range(symbol_type='stock'):
    end = datetime.now()
    
    if symbol_type == 'forex':
        days = 30  # Forex limitado en free tier
    elif symbol_type == 'stock':
        days = 365  # Stocks más disponibilidad
    
    start = end - timedelta(days=days)
    return start, end
```

### **Archivo Público Automático**

```python
def make_file_public(file_id, credentials):
    """Hace el archivo accesible sin autenticación"""
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    service.permissions().create(
        fileId=file_id,
        body=permission
    ).execute()
```

**¿Por qué?** Para que Kaggle pueda descargar con `gdown` sin OAuth.

### **Info JSON Completa**

```json
{
  "drive_file_id": "1abc123...",
  "drive_file_url": "https://drive.google.com/...",
  "download_url": "https://drive.google.com/uc?id=...",
  "timestamp": "2025-10-28T12:00:00",
  "metadata": {
    "symbol": "AAPL",
    "start_date": "2024-10-28",
    "end_date": "2025-10-28",
    "total_rows": 125450,
    "file_size_mb": 8.5
  }
}
```

---

## 📈 Ejemplo Completo End-to-End

### **Día 1: Setup**

```bash
# Terminal en Codespaces
python main_auto_kaggle.py

# Output:
# 📅 Date range: Último año completo
#    From: 2024-10-28
#    To: 2025-10-28
# 📥 Downloading AAPL data...
# ⏰ Estimated time: 73.0 minutes for 365 days
# [progreso...]
# ✅ Download complete: 125,450 records
# ☁️ Uploading to Google Drive...
# 🌍 Making file public...
# ✅ File is now publicly accessible
# 💾 Saving file info to drive_file_info.json...
```

### **Transferir a Kaggle**

```bash
# Descargar drive_file_info.json
# En Kaggle: Upload como dataset
```

### **En Kaggle**

```python
# Ejecutar notebook
# Output:
# ✅ File ID found in JSON file
# 📥 Downloading from Google Drive...
# ✅ Download complete: trading_data.csv (8.50 MB)
# 📊 DATA ANALYSIS
# ✅ Analysis complete!
```

---

## ⏰ Tiempos Estimados

| Datos | Días | Requests | Tiempo (5 req/min) |
|-------|------|----------|-------------------|
| 1 semana | 7 | 7 | ~2 min |
| 1 mes | 30 | 30 | ~6 min |
| 3 meses | 90 | 90 | ~18 min |
| 1 año | 365 | 365 | ~73 min |

**Tip:** Para testing inicial, usa 30 días. Luego aumenta.

---

## 🔄 Automatización

### **Opción 1: Cron Job**

```bash
# Ejecutar diario a las 9 AM
0 9 * * * cd /workspaces/MT5 && python main_auto_kaggle.py
```

### **Opción 2: GitHub Actions**

Ver archivo completo en `SISTEMA_COMPLETO_KAGGLE.md`

### **Opción 3: Kaggle Scheduled Run**

En Kaggle:
- Settings → Schedule
- Frequency: Daily
- Time: 10 AM (después del data update)

---

## 🆘 Troubleshooting Rápido

### **"Failed to download in Kaggle"**
✅ **Solución:** Ya está resuelto. El script hace el archivo público automáticamente.

### **"No file ID found"**
✅ **Solución:** 
- Verifica que subiste `drive_file_info.json` a Kaggle
- O configuraste variable de entorno `DRIVE_FILE_ID`

### **"Takes too long"**
✅ **Solución:**
- Reduce `DAYS_TO_DOWNLOAD` a 30 o 90 días
- O ejecuta overnight para rangos grandes

### **"Rate limit"**
✅ **Solución:**
- El script ya tiene delays automáticos (12s)
- Si aún falla, aumenta `DELAY_BETWEEN_REQUESTS = 15`

---

## 📚 Documentación Completa

- **[SISTEMA_COMPLETO_KAGGLE.md](computer:///mnt/user-data/outputs/SISTEMA_COMPLETO_KAGGLE.md)** - Guía detallada completa
- **[main_auto_kaggle.py](computer:///mnt/user-data/outputs/main_auto_kaggle.py)** - Script principal modificado
- **[kaggle_notebook_processor.py](computer:///mnt/user-data/outputs/kaggle_notebook_processor.py)** - Notebook para Kaggle

---

## ✅ Lo que Cambia vs Original

| Característica | Original | Nuevo |
|----------------|----------|-------|
| **Fechas** | Hardcoded 2023-2024 | Automático desde hoy |
| **Rango** | Fijo 9 meses | Inteligente según datos |
| **Público** | Manual | Automático |
| **Kaggle** | No integrado | Completamente integrado |
| **File ID** | No se guarda | JSON automático |
| **Download URL** | No disponible | Generado automáticamente |

---

## 🎯 TL;DR (Too Long; Didn't Read)

```bash
# 1. Ejecuta en Codespaces
python main_auto_kaggle.py
# → Descarga desde HOY hacia atrás (máximo)
# → Sube a Drive (público automáticamente)
# → Genera drive_file_info.json

# 2. Transfiere a Kaggle
# → Sube drive_file_info.json como dataset

# 3. En Kaggle
# → Ejecuta kaggle_notebook_processor.py
# → ¡Listo! Datos procesados automáticamente
```

**¿Necesitas más detalles?** Lee [SISTEMA_COMPLETO_KAGGLE.md](computer:///mnt/user-data/outputs/SISTEMA_COMPLETO_KAGGLE.md)

**¿Listo para empezar?** Ejecuta `python main_auto_kaggle.py` ahora! 🚀
