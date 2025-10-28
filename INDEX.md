# 📚 Sistema de Trading ML Automatizado - Índice de Documentación

> Sistema completo para descargar datos financieros, procesarlos con ML en Kaggle y automatizar todo con GitHub Actions

---

## 🎯 ¿Por dónde empiezo?

### Si quieres empezar AHORA MISMO (5 minutos):
→ Lee **[QUICKSTART.md](QUICKSTART.md)**

### Si quieres entender el sistema completo:
→ Lee **[README.md](README.md)**

### Si necesitas configurar GitHub Secrets:
→ Lee **[GITHUB_SECRETS.md](GITHUB_SECRETS.md)**

---

## 📖 Documentación Disponible

| Documento | Descripción | Cuándo usarlo |
|-----------|-------------|---------------|
| **[QUICKSTART.md](QUICKSTART.md)** | Guía rápida de inicio (5 min) | Primera vez que usas el sistema |
| **[README.md](README.md)** | Documentación completa del sistema | Para entender arquitectura y troubleshooting |
| **[GITHUB_SECRETS.md](GITHUB_SECRETS.md)** | Guía de configuración de secrets | Para automatizar con GitHub Actions |
| Este archivo (INDEX.md) | Índice de navegación | Punto de entrada a la docs |

---

## 🗂️ Estructura de Archivos

```
proyecto/
│
├── 📚 DOCUMENTACIÓN
│   ├── INDEX.md              ← Estás aquí
│   ├── QUICKSTART.md         ← Inicio rápido
│   ├── README.md             ← Documentación completa
│   └── GITHUB_SECRETS.md     ← Configurar secrets
│
├── 🚀 SCRIPTS PRINCIPALES
│   ├── main_chunk_kaggle.py  ← Script principal del pipeline
│   ├── Forrest.ipynb         ← Template del notebook ML
│   └── Forrest_template.py   ← Versión Python del notebook
│
├── 🔧 SCRIPTS DE SETUP
│   ├── setup.sh              ← Setup automático del entorno
│   ├── setup_credentials.py  ← Configurar credenciales interactivamente
│   ├── test_setup.py         ← Test del sistema
│   └── deploy.sh             ← Deployment rápido a GitHub
│
├── ⚙️  CONFIGURACIÓN
│   ├── .env.example          ← Template de variables de entorno
│   ├── requirements.txt      ← Dependencias Python
│   ├── .gitignore            ← Archivos a ignorar en git
│   └── .devcontainer/        ← Config para Codespaces
│
├── 🔐 CREDENCIALES (no commitear)
│   ├── credentials.json      ← Google Drive API
│   ├── token.json            ← Token OAuth (auto-generado)
│   ├── kaggle.json           ← Kaggle API
│   └── .env                  ← Variables de entorno
│
└── 🤖 AUTOMATIZACIÓN
    └── .github/workflows/
        └── daily_data_pipeline.yml  ← GitHub Actions workflow
```

---

## 🎬 Flujo de Trabajo

### 1️⃣ Setup Inicial (Primera vez)

```bash
# Opción A: Setup automático
chmod +x setup.sh
./setup.sh

# Opción B: Setup interactivo
python3 setup_credentials.py
```

**Resultado**: Sistema configurado y listo para usar

---

### 2️⃣ Ejecución Manual

```bash
# Verificar configuración
python3 test_setup.py

# Ejecutar pipeline completo
python3 main_chunk_kaggle.py
```

**Qué hace**:
1. ✅ Descarga datos de yfinance
2. ✅ Sube CSV a Google Drive
3. ✅ Crea `Forrest.py` con file_id
4. ✅ Pushea a GitHub
5. ✅ Despliega en Kaggle
6. ✅ Kaggle procesa y envía resultados

---

### 3️⃣ Deployment a GitHub

```bash
# Hacer ejecutable
chmod +x deploy.sh

# Ejecutar deployment
./deploy.sh
```

**Resultado**: Todo el sistema desplegado en tu repo de GitHub

---

### 4️⃣ Automatización (GitHub Actions)

1. Configura secrets siguiendo **[GITHUB_SECRETS.md](GITHUB_SECRETS.md)**
2. El workflow se ejecutará automáticamente cada día a las 02:00 UTC
3. Monitorea en: `https://github.com/jsgastondatamt5/MT5/actions`

---

## 🔑 Credenciales Necesarias

| Credencial | Archivo | Cómo obtener |
|------------|---------|--------------|
| Google Drive | `credentials.json` | [Console](https://console.cloud.google.com/apis/credentials) |
| Google Token | `token.json` | Auto-generado al autorizar |
| Kaggle | `kaggle.json` | [Settings](https://www.kaggle.com/settings/account) |
| GitHub | Token PAT | [Tokens](https://github.com/settings/tokens) |

**Detalles completos en**: [GITHUB_SECRETS.md](GITHUB_SECRETS.md)

---

## 🛠️ Scripts Disponibles

### Setup y Configuración

| Script | Descripción | Uso |
|--------|-------------|-----|
| `setup.sh` | Setup automático del entorno | `./setup.sh` |
| `setup_credentials.py` | Configurar credenciales interactivamente | `python3 setup_credentials.py` |
| `test_setup.py` | Verificar que todo está configurado | `python3 test_setup.py` |

### Ejecución

| Script | Descripción | Uso |
|--------|-------------|-----|
| `main_chunk_kaggle.py` | Pipeline completo | `python3 main_chunk_kaggle.py` |
| `deploy.sh` | Deployment a GitHub | `./deploy.sh` |

---

## 🔍 Verificación del Sistema

### ✅ Checklist de Funcionamiento

Verifica que todo funciona correctamente:

```bash
# 1. Test de configuración
python3 test_setup.py

# 2. Test de credenciales
ls -la credentials.json kaggle.json  # Deben existir

# 3. Test de imports
python3 -c "import pandas, yfinance, google.auth, kaggle; print('✅ OK')"

# 4. Test de Git
git remote -v  # Debe mostrar tu repo

# 5. Test de Kaggle CLI
kaggle datasets list --max-size 1
```

### 📊 Verificar Ejecución Completa

Después de ejecutar `main_chunk_kaggle.py`:

1. **Google Drive**: Verifica que hay un CSV nuevo
2. **GitHub**: Verifica que `Forrest.py` se actualizó
3. **Kaggle**: Ve a tu kernel y verifica que se ejecutó
4. **Resultados**: Verifica el repo `de-Kaggle-a-github`

---

## 🆘 Solución Rápida de Problemas

### Errores Comunes

| Error | Solución Rápida |
|-------|----------------|
| "No module named..." | `pip install -r requirements.txt` |
| "credentials.json not found" | Descarga desde Google Cloud Console |
| "kaggle: command not found" | `pip install kaggle` |
| "Permission denied" | `chmod 600 ~/.kaggle/kaggle.json` |
| Git authentication fails | Verifica tu Personal Access Token |

**Más detalles**: [README.md#troubleshooting](README.md#troubleshooting)

---

## 🎯 Objetivos del Sistema

Este sistema automatiza:

1. **Descarga diaria** de datos financieros (EURUSD, etc.)
2. **Almacenamiento** en Google Drive
3. **Procesamiento ML** en Kaggle con modelos avanzados
4. **Entrega de resultados** a GitHub para análisis
5. **Todo de forma automática** cada día

---

## 📈 Arquitectura del Sistema

```
GitHub Actions (cron diario)
          ↓
main_chunk_kaggle.py
          ↓
     yfinance API
          ↓
   Google Drive (CSV)
          ↓
    file_id obtenido
          ↓
   Forrest.py creado
          ↓
    ├─→ GitHub (MT5)
    └─→ Kaggle (ejecuta ML)
              ↓
         Resultados
              ↓
    GitHub (de-Kaggle-a-github)
```

---

## 🚀 Próximos Pasos

### Si es tu primera vez:
1. Lee [QUICKSTART.md](QUICKSTART.md)
2. Ejecuta `setup_credentials.py`
3. Ejecuta `python3 main_chunk_kaggle.py`

### Si quieres automatizar:
1. Lee [GITHUB_SECRETS.md](GITHUB_SECRETS.md)
2. Configura los 6 secrets en GitHub
3. Ejecuta el workflow manualmente para probar
4. Deja que se ejecute automáticamente cada día

### Si algo falla:
1. Ejecuta `python3 test_setup.py`
2. Revisa logs en GitHub Actions
3. Consulta [README.md](README.md) sección Troubleshooting

---

## 📞 Soporte

- **Test del sistema**: `python3 test_setup.py`
- **Logs de GitHub Actions**: `https://github.com/jsgastondatamt5/MT5/actions`
- **Documentación completa**: [README.md](README.md)

---

## 📄 Licencia y Notas

- Sistema de uso personal/educativo
- **NUNCA** commitees archivos de credenciales
- Usa `.gitignore` para proteger archivos sensibles
- Mantén tus tokens seguros

---

**Sistema creado con ❤️ para automatizar trading con Machine Learning**

🎉 **¡Listo para empezar!** → [QUICKSTART.md](QUICKSTART.md)
