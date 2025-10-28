# 🚀 Guía Rápida de Inicio

## Para empezar AHORA MISMO (5 minutos)

### 1️⃣ Setup Inicial (Primera vez)

```bash
# Clonar tu repositorio
git clone https://github.com/jsgastondatamt5/MT5.git
cd MT5

# Ejecutar setup
chmod +x setup.sh
./setup.sh

# Configurar credenciales interactivamente
python3 setup_credentials.py
```

### 2️⃣ Primera Ejecución

```bash
# Verificar que todo está bien
python3 test_setup.py

# Ejecutar el pipeline completo
python3 main_chunk_kaggle.py
```

Esto hará:
- ✅ Descargar datos de yfinance
- ✅ Subir a Google Drive
- ✅ Crear Forrest.py
- ✅ Pushear a GitHub
- ✅ Desplegar en Kaggle
- ✅ Kaggle procesará y enviará resultados

### 3️⃣ Desde Codespaces

1. Ve a tu repo en GitHub
2. Click en "Code" > "Codespaces" > "Create codespace"
3. Espera a que cargue (instalará dependencias automáticamente)
4. Ejecuta:

```bash
python3 setup_credentials.py  # Primera vez
python3 main_chunk_kaggle.py  # Ejecutar pipeline
```

### 4️⃣ Automatización Diaria

#### Opción A: GitHub Actions (Recomendado)

1. Ve a Settings > Secrets and variables > Actions
2. Añade estos secrets:

```
GOOGLE_CREDENTIALS  → Contenido de credentials.json
GOOGLE_TOKEN        → Contenido de token.json (ejecuta una vez manual primero)
KAGGLE_JSON         → Contenido de kaggle.json
GH_PAT              → Tu GitHub Personal Access Token
GH_USERNAME         → jsgastondatamt5
KAGGLE_USERNAME     → jsgastonalgotrading
```

3. El workflow se ejecutará automáticamente cada día a las 02:00 UTC

#### Opción B: Ejecución Manual

Para ejecutar manualmente:
1. Ve a "Actions" en tu repo
2. Selecciona "Daily Data Download and Kaggle Processing"
3. Click en "Run workflow"

---

## 📁 Archivos Importantes

### Archivos que DEBES tener:

| Archivo | Descripción | Cómo obtener |
|---------|-------------|--------------|
| `credentials.json` | Google Drive API | [Google Cloud Console](https://console.cloud.google.com/apis/credentials) |
| `kaggle.json` | Kaggle API | [Kaggle Settings](https://www.kaggle.com/settings/account) |
| `.env` | Variables de entorno | Crear con `setup_credentials.py` |
| `Forrest.ipynb` | Template ML | Ya incluido ✅ |

### Archivos que NO commitear:

```gitignore
credentials.json
token.json
kaggle.json
.env
*.csv
```

---

## ⚡ Comandos Rápidos

```bash
# Test completo del sistema
python3 test_setup.py

# Ejecutar pipeline completo
python3 main_chunk_kaggle.py

# Configurar credenciales
python3 setup_credentials.py

# Ver logs de GitHub Actions
# Settings > Actions > Daily Data Download

# Ver ejecución en Kaggle
# https://www.kaggle.com/jsgastonalgotrading/forrest-trading-ml
```

---

## 🆘 Solución Rápida de Problemas

### Error: "No module named 'google'"
```bash
pip install -r requirements.txt
```

### Error: Google Drive authentication
```bash
rm token.json
python3 main_chunk_kaggle.py  # Volverá a pedir autenticación
```

### Error: Kaggle "Permission denied"
```bash
chmod 600 ~/.kaggle/kaggle.json
```

### GitHub Actions falla
1. Verifica que TODOS los secrets están configurados
2. Revisa los logs en Actions > [workflow] > [ejecución]
3. Asegúrate de que `Forrest.ipynb` está en el repo

---

## 📊 Verificar que Funciona

### 1. Verificar datos en Drive:
- Ve a [Google Drive](https://drive.google.com)
- Busca `eurusd_1m_data_*.csv`

### 2. Verificar script en GitHub:
- Ve a tu repo: `https://github.com/jsgastondatamt5/MT5`
- Deberías ver `Forrest.py` actualizado

### 3. Verificar ejecución en Kaggle:
- Ve a `https://www.kaggle.com/jsgastonalgotrading/forrest-trading-ml`
- Verifica que el kernel se ejecutó

### 4. Verificar resultados:
- Ve a `https://github.com/jsgastondatamt5/de-Kaggle-a-github`
- Deberías ver carpetas con resultados timestamped

---

## 🎯 Flujo Completo Visual

```
┌──────────────┐
│ GitHub       │  Ejecuta diariamente 02:00 UTC
│ Actions      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ main_chunk   │  Descarga EURUSD de yfinance
│ _kaggle.py   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Google       │  Almacena CSV
│ Drive        │  Obtiene file_id
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Forrest.py   │  Se crea con file_id
│              │  ↓
│              │  Push a GitHub → Push a Kaggle
└──────┬───────┘
       │
       ├────────────┬─────────────┐
       ▼            ▼             ▼
   GitHub      Kaggle         Resultados
    (MT5)    (Ejecuta ML)   (de-Kaggle-a-github)
```

---

## 📞 Soporte

- **Logs de ejecución**: `Actions > [workflow name]`
- **Test del sistema**: `python3 test_setup.py`
- **Verificar credenciales**: Revisa que todos los archivos JSON son válidos

---

**¡Listo para empezar!** 🎉

Ejecuta: `python3 setup_credentials.py`
