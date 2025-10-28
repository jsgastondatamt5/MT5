# 🔐 Guía de Autorización Google Drive - Paso a Paso

## 📸 Lo que veo en tu pantalla

✅ **Datos descargados:** 30,569 filas guardadas en `eurusd_1min.csv`  
⏳ **Problema:** Atascado en la autorización de Google Drive

---

## 🚀 Solución Completa (5 minutos)

### **PASO 1: Copia la URL completa**

En tu terminal (parte inferior), verás algo como:
```
🔗 STEP 1: Open this link in your browser:
================================================================================
https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=125681163751-...
================================================================================
```

**Acción:**
1. Selecciona **toda** la URL (desde `https://` hasta el final)
2. Haz clic derecho → Copiar
3. O usa Ctrl+C (Windows) / Cmd+C (Mac)

---

### **PASO 2: Abre la URL en tu navegador**

**Acción:**
1. Abre una **nueva pestaña** en tu navegador
2. Pega la URL (Ctrl+V / Cmd+V)
3. Presiona Enter

---

### **PASO 3: Autoriza el acceso a Google Drive**

Verás una pantalla de Google pidiendo permisos:

```
┌─────────────────────────────────────────┐
│   🔵 Iniciar sesión con Google          │
│                                          │
│   [Tu email]                             │
│   ********                               │
│                                          │
│   [Siguiente]                            │
└─────────────────────────────────────────┘
```

**Acción:**
1. Inicia sesión con tu cuenta de Google
2. Luego verás:
   ```
   "MT5" quiere acceder a tu cuenta de Google Drive
   
   Esto permitirá que MT5:
   • Crear archivos en Google Drive
   
   [Cancelar]  [Permitir]
   ```
3. Haz clic en **"Permitir"** o **"Allow"**

---

### **PASO 4: Extrae el código de autorización**

Después de hacer clic en "Permitir", serás redirigido a:

```
http://localhost:8080/?code=4/0AXXXxxxxxxxxxxxxxxxxx&scope=https://www.googleapis.com/auth/drive.file
```

**⚠️ MUY IMPORTANTE:**
- ✅ La página mostrará: "Esta página no funciona" o "Unable to connect"
- ✅ **¡Esto es completamente NORMAL!**
- ✅ **NO cierres la ventana todavía**

**Mira la barra de direcciones del navegador:**

```
┌────────────────────────────────────────────────────────────────┐
│ 🔒 http://localhost:8080/?code=4/0AXXXxxxxxxxxxxx&scope=https  │ 🔍
└────────────────────────────────────────────────────────────────┘
        └──────────────────┬───────────────────┘
                    COPIA SOLO ESTA PARTE
```

**Acción:**
1. Haz clic en la barra de direcciones
2. Busca la parte que dice `code=`
3. Copia desde **después** de `code=` hasta **antes** de `&scope`
4. Ejemplo: Si ves `?code=4/0AXXXxxxx123&scope=...`, copia solo `4/0AXXXxxxx123`

**Método rápido:**
1. Selecciona TODA la URL de la barra de direcciones
2. Cópiala completamente
3. Pégala en un bloc de notas
4. Extrae solo la parte del código

---

### **PASO 5: Pega el código en el terminal**

Vuelve a tu terminal de Codespaces:

```
🔑 STEP 2: Paste the authorization code here:
>>> _
```

**Acción:**
1. Haz clic donde está el cursor (`>>>`)
2. Pega el código (Ctrl+V / Cmd+V)
3. **Asegúrate de NO incluir:**
   - `?code=` al inicio
   - `&scope=...` al final
   - Espacios al principio o al final
4. Presiona **Enter**

---

### **PASO 6: ¡Éxito!**

Si todo salió bien, verás:

```
✅ Authorization successful! Token saved to token.json

☁️  Uploading eurusd_1min.csv to Google Drive...

================================================================================
✅ SUCCESS! File uploaded to Google Drive
================================================================================
📄 File: eurusd_1min.csv
📊 Records: 30,569
🆔 Drive ID: 1a2b3c4d5e6f...
🔗 View: https://drive.google.com/file/d/1a2b3c4d5e6f.../view
================================================================================
```

**¡Tu archivo ya está en Google Drive!** 🎉

---

## ❌ Problemas Comunes

### Problema 1: "Invalid code" o "Authorization failed"
**Causa:** El código expiró o tiene errores

**Solución:**
1. Presiona Ctrl+C para cancelar
2. Ejecuta el script de nuevo: `python main_with_rate_limiting.py`
3. Obtén un código nuevo (no reutilices el anterior)

### Problema 2: "No puedo copiar el código"
**Método alternativo:**
1. Cuando estés en `http://localhost:8080/?code=XXX`
2. Haz clic derecho en la barra de direcciones → Copiar
3. Pégalo en un bloc de notas
4. Encuentra el código manualmente:
   ```
   Ejemplo de URL completa:
   http://localhost:8080/?code=4/0AXXXxxx123abc&scope=https://...
   
   Tu código es: 4/0AXXXxxx123abc
   ```

### Problema 3: "La página no carga después de autorizar"
**¡Esto es NORMAL!**
- El navegador intenta conectarse a `localhost:8080`
- No hay servidor escuchando ahí (es solo para capturar el código)
- **Simplemente copia el código de la URL y sigue adelante**

### Problema 4: "Me aparece 'redirect_uri_mismatch'"
**Causa:** La configuración de OAuth no coincide

**Solución:**
1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Credenciales → Tu OAuth Client
3. Verifica que "URI de redirección autorizado" incluya:
   ```
   http://localhost:8080
   ```
4. Si no está, agrégalo y guarda
5. Reinicia el script

---

## 🔄 Próximas Ejecuciones

**Buena noticia:** Solo necesitas hacer esto **UNA VEZ**

Después de esta primera autorización, se creará un archivo `token.json` que guarda tus credenciales.

Las próximas veces que ejecutes el script:
- ✅ Se saltará la autorización automáticamente
- ✅ Usará el token guardado
- ✅ Subirá archivos directamente

**El token expira después de un tiempo**, así que eventualmente tendrás que repetir el proceso.

---

## 📱 ¿Necesitas Ayuda Visual?

### Flujo completo en 3 imágenes:

**1. Terminal → URL:**
```
[Tu terminal mostrando la URL] 
     ↓ Copiar
```

**2. Navegador → Autorización:**
```
[Pantalla de Google pidiendo permisos]
     ↓ Permitir
```

**3. URL → Código → Terminal:**
```
http://localhost:8080/?code=4/0AXXXxxx...
                           ↓ Copiar código
>>> [pegar aquí] → Enter
```

---

## 🆘 ¿Aún Atascado?

Si después de seguir todos estos pasos sigues teniendo problemas:

1. **Verifica tu archivo credentials.json:**
   ```bash
   cat credentials.json
   ```
   Debe contener `"redirect_uris":["http://localhost:8080"]`

2. **Prueba copiar la URL completa en el terminal:**
   A veces es más fácil copiar toda la URL, pegarla en el terminal,
   y luego extraer el código manualmente

3. **Revisa los permisos de tu proyecto de Google:**
   - El proyecto debe tener Google Drive API habilitada
   - Las credenciales OAuth deben estar configuradas para "Desktop app"

---

## 💡 Tip Pro

**Para evitar este proceso en futuras ejecuciones:**

1. Después de la primera autorización exitosa
2. **Guarda** el archivo `token.json` que se crea
3. Cada vez que ejecutes en un nuevo entorno, copia ese archivo
4. El script lo usará automáticamente sin pedir autorización

**⚠️ Advertencia:** `token.json` contiene tus credenciales, ¡mantenlo privado!

---

## ✅ Resumen Ultra-Rápido

1. 📋 Copia URL del terminal
2. 🌐 Pégala en navegador
3. 🔑 Permite acceso en Google
4. 📝 Copia código de URL (después de `code=`)
5. 💻 Pégalo en terminal y presiona Enter
6. 🎉 ¡Archivo en Google Drive!

---

¡Eso es todo! Una vez que completes estos pasos, tu archivo `eurusd_1min.csv` estará en tu Google Drive. 🚀
