# 🔐 Guía de Configuración de GitHub Secrets

## ¿Qué son los Secrets?

Los Secrets son variables de entorno seguras que GitHub Actions puede usar durante la ejecución de workflows. Permiten almacenar información sensible como tokens y credenciales sin exponerlos en el código.

## 📋 Secrets Necesarios

Para que el workflow automático funcione, necesitas configurar estos 6 secrets:

| Secret | Descripción | Valor |
|--------|-------------|-------|
| `GOOGLE_CREDENTIALS` | Credenciales de Google Drive API | Contenido completo de `credentials.json` |
| `GOOGLE_TOKEN` | Token OAuth de Google | Contenido completo de `token.json` |
| `KAGGLE_JSON` | Credenciales de Kaggle API | Contenido completo de `kaggle.json` |
| `GH_PAT` | Personal Access Token de GitHub | Tu token de GitHub con permisos repo |
| `GH_USERNAME` | Usuario de GitHub | `jsgastondatamt5` |
| `KAGGLE_USERNAME` | Usuario de Kaggle | `jsgastonalgotrading` |

---

## 🛠️ Paso a Paso: Configurar Secrets

### 1. Acceder a la configuración de Secrets

1. Ve a tu repositorio: `https://github.com/jsgastondatamt5/MT5`
2. Click en **"Settings"** (⚙️ arriba a la derecha)
3. En el menú lateral izquierdo, click en **"Secrets and variables"**
4. Click en **"Actions"**
5. Verás la página "Actions secrets and variables"

### 2. Añadir cada Secret

Para cada secret, sigue estos pasos:

1. Click en el botón verde **"New repository secret"**
2. En **"Name"**, escribe el nombre del secret (ej: `GOOGLE_CREDENTIALS`)
3. En **"Secret"**, pega el valor correspondiente
4. Click en **"Add secret"**

---

## 📝 Cómo Obtener cada Valor

### Secret 1: `GOOGLE_CREDENTIALS`

**Qué es**: Credenciales OAuth de Google Drive API

**Cómo obtenerlo**:

1. Abre el archivo `credentials.json` en un editor de texto
2. **Copia TODO el contenido** del archivo (debe empezar con `{` y terminar con `}`)
3. Pega en el campo "Secret" de GitHub

**Ejemplo del formato** (tu archivo será diferente):
```json
{
  "web": {
    "client_id": "125681163751-61464mquea6ealit9vja2bg2f2pmf6i8.apps.googleusercontent.com",
    "project_id": "delta-essence-476417-m2",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    ...
  }
}
```

---

### Secret 2: `GOOGLE_TOKEN`

**Qué es**: Token de autenticación generado tras el primer login

**Cómo obtenerlo**:

⚠️ **IMPORTANTE**: Este archivo se genera DESPUÉS de ejecutar el script por primera vez y autorizar en el navegador.

1. Ejecuta una vez: `python3 main_chunk_kaggle.py`
2. Autoriza en el navegador cuando te lo pida
3. Se creará el archivo `token.json`
4. Abre `token.json` y **copia TODO el contenido**
5. Pega en el campo "Secret" de GitHub

**Si no tienes token.json aún**:
- Deja este secret en blanco por ahora
- Después de la primera ejecución manual, añádelo

---

### Secret 3: `KAGGLE_JSON`

**Qué es**: Credenciales API de Kaggle

**Cómo obtenerlo**:

1. Abre el archivo `kaggle.json`
2. **Copia TODO el contenido**
3. Pega en el campo "Secret" de GitHub

**El formato debe ser**:
```json
{
  "username": "jsgastonalgotrading",
  "key": "bdb31ba5d1dd3a955d1e856204126192"
}
```

---

### Secret 4: `GH_PAT` (Personal Access Token)

**Qué es**: Token de GitHub con permisos para modificar repositorios

**Cómo obtenerlo**:

Opción 1 - Usar el token que ya tienes:
```
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
```

Opción 2 - Crear uno nuevo (recomendado):

1. Ve a: https://github.com/settings/tokens
2. Click en **"Generate new token"** > **"Generate new token (classic)"**
3. Dale un nombre descriptivo: `MT5 Workflow`
4. **Selecciona estos permisos**:
   - ✅ `repo` (todos los sub-permisos)
   - ✅ `workflow`
5. Click en **"Generate token"**
6. **COPIA EL TOKEN** (solo se muestra una vez)
7. Pega en el campo "Secret" de GitHub

---

### Secret 5: `GH_USERNAME`

**Qué es**: Tu nombre de usuario de GitHub

**Valor**:
```
jsgastondatamt5
```

Simple, solo pega este texto en el secret.

---

### Secret 6: `KAGGLE_USERNAME`

**Qué es**: Tu nombre de usuario de Kaggle

**Valor**:
```
jsgastonalgotrading
```

Simple, solo pega este texto en el secret.

---

## ✅ Verificar que está todo bien

Después de añadir todos los secrets, deberías ver 6 secrets en la lista:

```
GOOGLE_CREDENTIALS     Updated [fecha]
GOOGLE_TOKEN           Updated [fecha]
GH_PAT                 Updated [fecha]
GH_USERNAME            Updated [fecha]
KAGGLE_JSON            Updated [fecha]
KAGGLE_USERNAME        Updated [fecha]
```

---

## 🧪 Probar el Workflow

### Ejecución Manual (Primera vez)

1. Ve a tu repositorio: `https://github.com/jsgastondatamt5/MT5`
2. Click en **"Actions"** (arriba)
3. Selecciona el workflow: **"Daily Data Download and Kaggle Processing"**
4. Click en **"Run workflow"** (botón azul a la derecha)
5. Confirm con **"Run workflow"**

### Verificar Logs

1. Aparecerá una nueva ejecución en la lista
2. Click en ella para ver detalles
3. Click en el job para ver los logs en tiempo real
4. Busca ✅ o ❌ para ver si tuvo éxito

---

## 🐛 Solución de Problemas

### Error: "Secret GOOGLE_CREDENTIALS not found"

**Causa**: No has añadido el secret o el nombre está mal escrito

**Solución**:
1. Verifica que el nombre es exactamente `GOOGLE_CREDENTIALS` (mayúsculas)
2. Asegúrate de haberlo añadido en Actions secrets (no Environment secrets)

### Error: "Invalid JSON" en GOOGLE_CREDENTIALS

**Causa**: El JSON está incompleto o tiene formato incorrecto

**Solución**:
1. Abre `credentials.json` en un editor de texto
2. Verifica que está COMPLETO (empieza con `{` y termina con `}`)
3. Copia TODO el contenido sin modificar
4. Actualiza el secret

### Error: "Authentication failed" en Kaggle

**Causa**: Las credenciales de Kaggle son incorrectas

**Solución**:
1. Ve a https://www.kaggle.com/settings/account
2. En "API", click en "Create New API Token"
3. Descarga el nuevo `kaggle.json`
4. Actualiza el secret `KAGGLE_JSON` con el nuevo contenido

### Error: "Permission denied" al push a GitHub

**Causa**: El Personal Access Token no tiene permisos suficientes

**Solución**:
1. Verifica que el token tiene permisos `repo` y `workflow`
2. O genera un nuevo token con estos permisos
3. Actualiza el secret `GH_PAT`

---

## 🔄 Actualizar un Secret

Si necesitas cambiar un secret:

1. Ve a Settings > Secrets and variables > Actions
2. Click en el secret que quieres actualizar
3. Click en **"Update secret"**
4. Pega el nuevo valor
5. Click en **"Update secret"**

---

## 📊 Monitorear Ejecuciones

### Ver todas las ejecuciones:
`https://github.com/jsgastondatamt5/MT5/actions`

### Ver una ejecución específica:
Click en cualquier ejecución de la lista para ver:
- ✅ Pasos completados
- ⏳ Pasos en progreso
- ❌ Pasos fallidos
- 📋 Logs detallados de cada paso

---

## ⏰ Horario de Ejecución Automática

Por defecto, el workflow se ejecuta:
- **Todos los días a las 02:00 UTC**
- Equivale a **03:00 hora de España** (en invierno)
- Equivale a **04:00 hora de España** (en verano)

Para cambiar el horario:
1. Edita `.github/workflows/daily_data_pipeline.yml`
2. Busca la línea: `- cron: '0 2 * * *'`
3. Cambia los números según necesites
4. Commit y push

**Ejemplos de cron**:
- `0 6 * * *` → 06:00 UTC (07:00/08:00 España)
- `0 */6 * * *` → Cada 6 horas
- `0 9 * * 1-5` → 09:00 UTC, solo de lunes a viernes

---

## 🎯 Checklist Final

Antes de que todo funcione, verifica:

- ✅ Los 6 secrets están configurados en GitHub
- ✅ Los nombres de los secrets son exactamente como se especifica
- ✅ El workflow existe en `.github/workflows/daily_data_pipeline.yml`
- ✅ El archivo `Forrest.ipynb` está en el repositorio
- ✅ Has ejecutado el workflow manualmente al menos una vez
- ✅ No hay errores en los logs de la ejecución

---

**¿Todo listo?** 🚀

El sistema debería ejecutarse automáticamente cada día. Puedes monitorear las ejecuciones en la pestaña "Actions" de tu repositorio.

¿Preguntas? Revisa los logs en Actions o consulta el README.md principal.
