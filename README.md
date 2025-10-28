# 🚀 Sistema Automatizado de Trading ML con Kaggle

Sistema completo que descarga datos financieros, los procesa en Kaggle con Machine Learning, y envía resultados automáticamente a GitHub. Ejecución diaria automatizada.

## 📋 Índice

- [Descripción](#-descripción)
- [Arquitectura](#-arquitectura)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración](#️-configuración)
- [Uso](#-uso)
- [Automatización](#-automatización)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Troubleshooting](#-troubleshooting)

## 🎯 Descripción

Este sistema automatiza el siguiente flujo de trabajo:

1. **Descarga de datos** - Obtiene datos históricos de yfinance (forex/stocks)
2. **Almacenamiento** - Sube datos a Google Drive
3. **Procesamiento** - Crea y despliega script Python en Kaggle
4. **Machine Learning** - Kaggle ejecuta modelos de trading
5. **Resultados** - Kaggle envía resultados al repositorio de GitHub
6. **Automatización** - GitHub Actions ejecuta todo diariamente

## 🏗️ Arquitectura

```
┌─────────────────┐
│  GitHub Actions │ (Ejecuta diariamente)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ main_chunk.py   │ (Descarga datos de yfinance)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Google Drive   │ (Almacena CSV)
└────────┬────────┘
         │ file_id
         ▼
┌─────────────────┐
│  Forrest.py     │ (Se crea con file_id)
└────────┬────────┘
         │
         ├──────────────┐
         │              │
         ▼              ▼
┌─────────────┐  ┌─────────────┐
│   GitHub    │  │   Kaggle    │
│  (MT5 repo) │  │  (Ejecuta)  │
└─────────────┘  └──────┬──────┘
                        │ Resultados
                        ▼
                 ┌──────────────────┐
                 │     GitHub       │
                 │ (de-Kaggle-a-    │
                 │  github repo)    │
                 └──────────────────┘
```

## 📦 Requisitos

### Software
- Python 3.10+
- Git
- Cuenta de GitHub
- Cuenta de Kaggle
- Cuenta de Google (Google Drive API habilitada)

### Archivos de Credenciales
- `credentials.json` - Google Drive OAuth credentials
- `kaggle.json` - Kaggle API token
- GitHub Personal Access Token

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/jsgastondatamt5/MT5.git
cd MT5
```

### 2. Ejecutar script de setup

```bash
chmod +x setup.sh
./setup.sh
```

Este script:
- ✅ Verifica Python
- ✅ Instala dependencias
- ✅ Configura directorios
- ✅ Verifica importaciones

### 3. Instalación manual (alternativa)

```bash
pip install -r requirements.txt
mkdir -p ~/.kaggle
```

## ⚙️ Configuración

### 1. Google Drive API

1. Ve a [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Crea un proyecto o selecciona uno existente
3. Habilita "Google Drive API"
4. Crea "OAuth 2.0 Client ID" (tipo: Desktop app)
5. Descarga el JSON como `credentials.json`
6. Coloca `credentials.json` en la raíz del proyecto

### 2. Kaggle API

1. Ve a [Kaggle Account Settings](https://www.kaggle.com/settings/account)
2. En sección "API", haz clic en "Create New API Token"
3. Descarga el archivo `kaggle.json`
4. Coloca en `~/.kaggle/kaggle.json` o en la raíz del proyecto

```bash
mkdir -p ~/.kaggle
cp kaggle.json ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

### 3. GitHub Personal Access Token

1. Ve a [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Generate new token (classic)
3. Permisos necesarios: `repo` (todos), `workflow`
4. Copia el token generado

### 4. Archivo .env

Crea un archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
nano .env
```

Edita con tus valores:

```env
GITHUB_TOKEN=ghp_TU_TOKEN_AQUI
GITHUB_USERNAME=jsgastondatamt5
GITHUB_REPO=MT5
KAGGLE_USERNAME=jsgastonalgotrading
```

### 5. Forrest.ipynb

Asegúrate de tener `Forrest.ipynb` en la raíz del proyecto. Este notebook se convertirá automáticamente a `Forrest.py`.

## 🚀 Uso

### Ejecución Manual

```bash
# Ejecutar el pipeline completo
python main_chunk_kaggle.py
```

El script hará:
1. ✅ Descargar datos de yfinance
2. ✅ Subir CSV a Google Drive
3. ✅ Crear `Forrest.py` con el file_id
4. ✅ Pushear `Forrest.py` a GitHub
5. ✅ Desplegar `Forrest.py` en Kaggle
6. ✅ Kaggle procesará y enviará resultados a GitHub

### Ejecución desde Codespaces

1. Abre el repositorio en GitHub
2. Click en "Code" > "Codespaces" > "Create codespace"
3. Espera a que se cargue el entorno
4. Ejecuta setup:

```bash
./setup.sh
```

5. Configura tus credenciales
6. Ejecuta el script:

```bash
python main_chunk_kaggle.py
```

## ⏰ Automatización

### GitHub Actions (Recomendado)

El workflow está configurado en `.github/workflows/daily_data_pipeline.yml`

#### Configurar Secrets

1. Ve a tu repositorio en GitHub
2. Settings > Secrets and variables > Actions
3. Añade los siguientes secrets:

| Secret Name | Descripción | Cómo obtenerlo |
|------------|-------------|----------------|
| `GOOGLE_CREDENTIALS` | Contenido de `credentials.json` | Copia todo el JSON |
| `GOOGLE_TOKEN` | Contenido de `token.json` | Ejecuta una vez manual para generarlo |
| `KAGGLE_JSON` | Contenido de `kaggle.json` | Desde Kaggle settings |
| `GH_PAT` | Personal Access Token | GitHub settings > tokens |
| `GH_USERNAME` | Tu usuario de GitHub | `jsgastondatamt5` |
| `KAGGLE_USERNAME` | Tu usuario de Kaggle | `jsgastonalgotrading` |

#### Horario de Ejecución

Por defecto: **todos los días a las 02:00 UTC** (03:00 hora España en invierno)

Para cambiar el horario, edita `.github/workflows/daily_data_pipeline.yml`:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Cambiar aquí
```

Ejemplos de cron:
- `0 2 * * *` - 02:00 UTC diario
- `0 */6 * * *` - Cada 6 horas
- `0 9 * * 1-5` - 09:00 UTC, lunes a viernes

#### Ejecución Manual del Workflow

1. Ve a "Actions" en tu repositorio
2. Selecciona "Daily Data Download and Kaggle Processing"
3. Click en "Run workflow"

### Cron (Linux/Mac)

Alternativa para servidores locales:

```bash
crontab -e
```

Añade:

```bash
0 2 * * * cd /ruta/a/MT5 && /usr/bin/python3 main_chunk_kaggle.py >> /var/log/trading-pipeline.log 2>&1
```

## 📁 Estructura del Proyecto

```
MT5/
├── main_chunk_kaggle.py      # Script principal
├── Forrest.ipynb              # Template del notebook ML
├── Forrest.py                 # Script generado (auto-creado)
├── requirements.txt           # Dependencias Python
├── setup.sh                   # Script de configuración
├── .env.example               # Template de configuración
├── .env                       # Configuración (no commitear)
├── credentials.json           # Google Drive (no commitear)
├── token.json                 # Google token (no commitear)
├── kaggle.json                # Kaggle API (no commitear)
├── .github/
│   └── workflows/
│       └── daily_data_pipeline.yml  # GitHub Actions
└── README.md                  # Esta documentación
```

## 🔍 Troubleshooting

### Error: "No module named 'google'"

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

### Error: "kaggle: command not found"

```bash
pip install kaggle
```

### Error: Google Drive authentication

1. Elimina `token.json`
2. Vuelve a ejecutar el script
3. Sigue el flujo de OAuth en el navegador

### Error: "Permission denied" en Kaggle

1. Verifica que `kaggle.json` tiene permisos 600:
```bash
chmod 600 ~/.kaggle/kaggle.json
```

### Error: "Repository not found" en GitHub

1. Verifica que el Personal Access Token tiene permisos `repo`
2. Verifica que el nombre del repositorio es correcto
3. Verifica que tienes permisos de escritura en el repo

### El workflow de GitHub Actions falla

1. Verifica que todos los secrets están configurados
2. Revisa los logs en Actions > [nombre del workflow] > [ejecución]
3. Asegúrate de que `Forrest.ipynb` está en el repositorio

### Kaggle no ejecuta el script

1. Verifica en Kaggle que el kernel existe: `https://www.kaggle.com/[username]/forrest-trading-ml`
2. Revisa que "Internet" está habilitado en el kernel
3. Chequea los logs del kernel en Kaggle

## 📊 Verificación del Sistema

### Test Completo

```bash
# 1. Test de credenciales
python << EOF
from google.oauth2.credentials import Credentials
import os

# Test Google
if os.path.exists('credentials.json'):
    print("✅ Google credentials found")
else:
    print("❌ Google credentials missing")

# Test Kaggle
if os.path.exists(os.path.expanduser('~/.kaggle/kaggle.json')):
    print("✅ Kaggle credentials found")
else:
    print("❌ Kaggle credentials missing")
EOF

# 2. Test de imports
python << EOF
import pandas, numpy, yfinance, google.auth, kaggle
print("✅ All imports successful")
EOF

# 3. Test de ejecución
python main_chunk_kaggle.py
```

## 🎓 Recursos Adicionales

- [Google Drive API Documentation](https://developers.google.com/drive/api/guides/about-sdk)
- [Kaggle API Documentation](https://www.kaggle.com/docs/api)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [yfinance Documentation](https://github.com/ranaroussi/yfinance)

## 📝 Notas de Seguridad

- ⚠️ **NUNCA** commitees archivos de credenciales al repositorio
- ⚠️ **NUNCA** compartas tu Personal Access Token
- ✅ Añade a `.gitignore`:
  ```
  credentials.json
  token.json
  kaggle.json
  .env
  *.csv
  ```

## 🤝 Contribuciones

Para contribuir o reportar issues:
1. Crea un fork del repositorio
2. Crea una branch para tu feature
3. Haz commit de tus cambios
4. Push a tu branch
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de uso personal/educativo.

---

**Creado con ❤️ para automatizar trading con ML**

¿Preguntas? Abre un issue en GitHub.
