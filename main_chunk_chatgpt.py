#!/usr/bin/env python3
"""
Pipeline completo:
- Descarga EURUSD (yfinance, 1m) en tandas de 7 días (último año)
- Guarda cada CSV intermedio
- Une en eurusd_data_<YYYYMMDD>.csv
- Sube el CSV final a Google Drive -> obtiene file_id + download_url
- Clona repo GitHub jsgastondatamt5/MT5, modifica Forrest.ipynb para usar el download_url
- Commit & push al repo (usa GITHUB_TOKEN)
- Empaqueta el notebook como kernel y hace `kaggle kernels push -p <dir>` para ejecutarlo
"""

import os
import sys
import json
import time
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf
import nbformat

# Google Drive / OAuth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

# -------------------------
# CONFIG - ajusta aquí si quieres
# -------------------------
load_dotenv()

# Google credentials (client_secrets.json)
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
TOKEN_FILE = os.getenv('TOKEN_FILE', 'token.json')
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# GitHub
GITHUB_REPO = "https://github.com/jsgastondatamt5/MT5.git"  # repo a clonar
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # required

# Kaggle
# Puedes poner el contenido de tu kaggle.json en la env var KAGGLE_JSON_CONTENT (string JSON),
# o tener ~/.kaggle/kaggle.json listo.
KAGGLE_JSON_CONTENT = os.getenv('KAGGLE_JSON_CONTENT', None)

# YFinance / batching
SYMBOL = "EURUSD=X"    # Yahoo symbol for EUR/USD
INTERVAL = "1m"
DAYS_PER_BATCH = 7
DAYS_TOTAL = 365

# Retardos
SLEEP_BETWEEN_BATCHES = 1.0  # segundos
KAGGLE_PUSH_TIMEOUT = 60 * 30  # 30 minutos timeout para `kaggle kernels push` (ajusta si quieres)

# Output filenames
NOTIFICATION_FILE = 'drive_file_info.json'

# -------------------------
# HELPERS Y FINISHED STEPS
# -------------------------

def download_batch(symbol, start_dt, end_dt, interval="1m"):
    """Descarga con yfinance un rango (start_dt inclusive, end_dt exclusive)."""
    print(f"Descargando {symbol} desde {start_dt.date()} hasta {end_dt.date()} (interval={interval})")
    try:
        df = yf.download(symbol, start=start_dt, end=end_dt, interval=interval, progress=False)
        if df is None or df.empty:
            print("  ⚠️  No hay datos en este rango.")
            return None
        df = df.reset_index()
        # normalizar nombre de columna de timestamp
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'Date' in df.columns:
            df = df.rename(columns={'Date': 'timestamp'})
        # Asegurar columna 'timestamp'
        if 'timestamp' not in df.columns:
            # si index era DatetimeIndex, ya se reseteó; si no, intentar crear
            df['timestamp'] = pd.to_datetime(df.iloc[:,0])
        return df
    except Exception as e:
        print(f"  ❌ Error al descargar: {e}")
        return None

def get_google_credentials(credentials_file, token_file, scopes):
    """
    Obtiene credenciales OAuth de Google (Drive).
    Si no existe token.json inicia autenticación interactiva (como tu script original).
    """
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refrescando token de Google...")
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(f"Client secrets file no encontrado: {credentials_file}")
            print("Iniciando flujo OAuth para Google Drive (abrir URL, pegar código)...")
            flow = Flow.from_client_secrets_file(
                credentials_file,
                scopes=scopes,
                redirect_uri='http://localhost:8080'
            )
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(auth_url)
            code = input("Pega el código de autorización aquí: ").strip()
            if not code:
                raise ValueError("No se proporcionó código de autorización")
            flow.fetch_token(code=code)
            creds = flow.credentials
            # Guardar token para reutilizar
            with open(token_file, 'w') as f:
                f.write(creds.to_json())
            print("Token guardado en", token_file)
    return creds

def upload_to_drive(file_path, credentials, folder_id=None, make_public=True):
    """Sube file_path a Google Drive y opcionalmente hace público. Devuelve (file_id, web_view_link, download_url)."""
    service = build('drive', 'v3', credentials=credentials)
    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    file_id = file.get('id')
    web_link = file.get('webViewLink', f"https://drive.google.com/file/d/{file_id}/view")
    download_url = f"https://drive.google.com/uc?id={file_id}"
    if make_public:
        try:
            permission = {'type': 'anyone', 'role': 'reader'}
            service.permissions().create(fileId=file_id, body=permission, fields='id').execute()
            print("Archivo hecho público en Drive.")
        except Exception as e:
            print("No se pudo hacer público automáticamente:", e)
    return file_id, web_link, download_url

def save_file_info_locally(file_id, file_url, metadata, filename=NOTIFICATION_FILE):
    info = {
        "drive_file_id": file_id,
        "drive_file_url": file_url,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata
    }
    with open(filename, 'w') as f:
        json.dump(info, f, indent=2)
    print(f"Guardada info en {filename}")

# -------------------------
# GIT / GITHUB
# -------------------------

def clone_repo(repo_url, clone_to, github_token=None):
    """
    Clona repo_url a clone_to. Si github_token se proporciona y repo_url es HTTPS, lo inserta en la URL.
    """
    if os.path.exists(clone_to):
        print("La carpeta del repo ya existe, la borraré antes de clonar:", clone_to)
        shutil.rmtree(clone_to)
    url = repo_url
    if github_token and repo_url.startswith("https://github.com/"):
        # transformar a https://{token}@github.com/owner/repo.git
        url = repo_url.replace("https://", f"https://{github_token}@")
    print("Clonando repo:", url)
    res = subprocess.run(["git", "clone", url, clone_to], capture_output=True, text=True)
    if res.returncode != 0:
        print("Error clonando repo:", res.stderr)
        raise RuntimeError("git clone falló")
    print("Repo clonado en", clone_to)

def commit_and_push(repo_path, commit_message="Update Forrest with new Drive DATA_URL", github_token=None):
    """
    Hace commit y push en repo_path. Asume que la URL remota origin es la original,
    si github_token está presente reescribe origin temporalmente para usar token.
    """
    cwd = os.getcwd()
    os.chdir(repo_path)
    try:
        # Config mínima si no existe
        subprocess.run(["git", "config", "user.email", "auto@example.com"], check=True)
        subprocess.run(["git", "config", "user.name", "auto-user"], check=True)

        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=False)  # no falla si no hay cambios
        # push: si falla por permisos, intenta insertar token en origin
        res = subprocess.run(["git", "push", "origin", "HEAD"], capture_output=True, text=True)
        if res.returncode != 0:
            print("git push falló sin token, intentando añadir token a origin...")
            if not github_token:
                raise RuntimeError("Push falló y no hay GITHUB_TOKEN para reintentar.")
            # obtener origin URL
            p = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True)
            origin_url = p.stdout.strip()
            if origin_url.startswith("https://"):
                token_url = origin_url.replace("https://", f"https://{github_token}@")
                subprocess.run(["git", "remote", "set-url", "origin", token_url], check=True)
                subprocess.run(["git", "push", "origin", "HEAD"], check=True)
                # restaurar origin sin token (opcional)
                subprocess.run(["git", "remote", "set-url", "origin", origin_url], check=True)
            else:
                raise RuntimeError("Origin URL no es https, no puedo inyectar token.")
        print("Cambios empujados a remoto.")
    finally:
        os.chdir(cwd)

# -------------------------
# NOTEBOOK modification (nbformat)
# -------------------------

def find_notebook(repo_path, target_name="Forrest.ipynb"):
    """Busca recursivamente el notebook dentro del repo. Devuelve ruta o None."""
    for root, dirs, files in os.walk(repo_path):
        for f in files:
            if f.lower() == target_name.lower():
                return os.path.join(root, f)
    return None

def insert_or_replace_dataurl_cell(nb_path, download_url):
    """
    Inserta al inicio del notebook una celda de código que define DATA_URL = "<download_url>".
    Si ya existe una celda que define DATA_URL se reemplaza su contenido.
    """
    print("Modificando notebook:", nb_path)
    nb = nbformat.read(nb_path, as_version=4)

    code_source = f'# Auto-inserted by pipeline\nDATA_URL = "{download_url}"\nprint("DATA_URL set to:", DATA_URL)\n'

    # Buscar si alguna celda contiene 'DATA_URL' asignación
    found = False
    for cell in nb.cells:
        if cell.cell_type == 'code' and 'DATA_URL' in cell.source:
            cell.source = code_source
            found = True
            break
    if not found:
        # Insertar nueva celda al principio
        new_cell = nbformat.v4.new_code_cell(code_source)
        nb.cells.insert(0, new_cell)

    nbformat.write(nb, nb_path)
    print("Notebook actualizado con DATA_URL.")

# -------------------------
# Kaggle kernel push
# -------------------------

def prepare_kaggle_credentials(kaggle_json_content=None):
    """
    Asegura que ~/.kaggle/kaggle.json exista con el contenido necesario.
    kaggle_json_content puede ser el JSON completo como string; si no se provee,
    el script asume que ya existe ~/.kaggle/kaggle.json.
    """
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(parents=True, exist_ok=True)
    kaggle_file = kaggle_dir / "kaggle.json"
    if kaggle_json_content:
        with open(kaggle_file, "w") as f:
            f.write(kaggle_json_content)
        os.chmod(kaggle_file, 0o600)
        print("Archivo ~/.kaggle/kaggle.json escrito desde KAGGLE_JSON_CONTENT.")
    else:
        if not kaggle_file.exists():
            raise FileNotFoundError("No se encontró ~/.kaggle/kaggle.json y KAGGLE_JSON_CONTENT no está definido.")
        print("Usando ~/.kaggle/kaggle.json existente.")

def create_kernel_package(notebook_path, kernel_dir, kernel_metadata=None):
    """
    Crea una carpeta con el notebook y un kernel-metadata.json mínimo para hacer push.
    kernel_metadata es dict; si no se provee se crea uno básico.
    """
    os.makedirs(kernel_dir, exist_ok=True)
    nb_name = os.path.basename(notebook_path)
    dest_nb = os.path.join(kernel_dir, nb_name)
    shutil.copy2(notebook_path, dest_nb)
    # metadata:
    if kernel_metadata is None:
        kernel_metadata = {
            "id": "jsgastonalgotrading/forrest",  # intentamos usar mismo id; si no tienes permiso cambia
            "title": "Forrest (auto-run)",
            "code_file": nb_name,
            "language": "python",
            "kernel_type": "notebook",
            "is_private": True
        }
    meta_path = os.path.join(kernel_dir, "kernel-metadata.json")
    with open(meta_path, "w") as f:
        json.dump(kernel_metadata, f, indent=2)
    print("Kernel package preparado en", kernel_dir)
    return kernel_dir

def push_kaggle_kernel(kernel_dir, timeout_seconds=KAGGLE_PUSH_TIMEOUT):
    """
    Ejecuta `kaggle kernels push -p <kernel_dir>`. Requiere que el CLI kaggle esté instalado.
    """
    print("Subiendo y ejecutando kernel en Kaggle (kaggle kernels push)...")
    cmd = ["kaggle", "kernels", "push", "-p", kernel_dir]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    start = time.time()
    # Stream output
    try:
        while True:
            line = proc.stdout.readline()
            if not line and proc.poll() is not None:
                break
            if line:
                print(line.rstrip())
            if time.time() - start > timeout_seconds:
                proc.kill()
                raise TimeoutError("kaggle kernels push excedió el timeout.")
        ret = proc.wait()
        if ret != 0:
            raise RuntimeError("kaggle kernels push falló. Revisa la salida anterior.")
        print("kaggle kernels push finalizó correctamente.")
    except Exception:
        proc.kill()
        raise

# -------------------------
# MAIN pipeline
# -------------------------

def main():
    # 1) Descargar en batches
    end_date = datetime.now()
    start_date = end_date - timedelta(days=DAYS_TOTAL)
    current = start_date
    batches = []
    batch_idx = 1

    print("Iniciando descarga EUR/USD en tandas de", DAYS_PER_BATCH, "días")
    while current < end_date:
        next_dt = min(current + timedelta(days=DAYS_PER_BATCH), end_date)
        df = download_batch(SYMBOL, current, next_dt, INTERVAL)
        batch_file = f"eurusd_batch_{batch_idx}_{current.date()}_to_{next_dt.date()}.csv"
        if df is not None and not df.empty:
            df.to_csv(batch_file, index=False)
            print("Guardado batch:", batch_file, len(df), "filas")
            batches.append(df)
        else:
            print("Batch sin datos:", current.date(), "->", next_dt.date())
        batch_idx += 1
        current = next_dt
        time.sleep(SLEEP_BETWEEN_BATCHES)

    if not batches:
        print("No se descargó ningún dato. Abortando.")
        return

    # 2) Unir y guardar final
    df_full = pd.concat(batches, ignore_index=True).sort_values("timestamp")
    output_file = f"eurusd_data_{datetime.now().strftime('%Y%m%d')}.csv"
    df_full.to_csv(output_file, index=False)
    size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print("Archivo final creado:", output_file, f"{len(df_full)} filas, {size_mb:.2f} MB")

    # 3) Subir a Google Drive
    creds = get_google_credentials(CREDENTIALS_FILE, TOKEN_FILE, SCOPES)
    file_id, web_view_link, download_url = upload_to_drive(output_file, creds, make_public=True)
    print("Subido a Drive: file_id=", file_id)
    metadata = {
        "symbol": SYMBOL,
        "batches": batch_idx - 1,
        "rows_total": len(df_full),
        "file_size_mb": round(size_mb, 2),
    }
    save_file_info_locally(file_id, download_url, metadata)

    # 4) Clonar repo GitHub
    tmpdir = tempfile.mkdtemp(prefix="mt5_repo_")
    try:
        clone_repo(GITHUB_REPO, tmpdir, github_token=GITHUB_TOKEN)

        # 5) localizar notebook Forrest.ipynb
        nb_path = find_notebook(tmpdir, target_name="Forrest.ipynb")
        if not nb_path:
            # intentar con nombre Forrest.ipynb (uploaded notebook name puede variar)
            print("No encontré Forrest.ipynb en el repo clonado. Buscando 'Forrest' en nombres...")
            # listar ficheros que contengan 'forrest' ignorando case
            possible = []
            for root, _, files in os.walk(tmpdir):
                for f in files:
                    if 'forrest' in f.lower() and f.lower().endswith('.ipynb'):
                        possible.append(os.path.join(root, f))
            if possible:
                nb_path = possible[0]
                print("Usando notebook encontrado:", nb_path)
            else:
                raise FileNotFoundError("No se encontró Forrest.ipynb en el repo clonado. Abortando.")

        # 6) modificar notebook para apuntar a Drive
        insert_or_replace_dataurl_cell(nb_path, download_url)

        # 7) commit & push
        commit_and_push(tmpdir, commit_message=f"Auto-update Forrest: DATA_URL -> {file_id}", github_token=GITHUB_TOKEN)

        # 8) preparar kaggle credentials
        prepare_kaggle_credentials(KAGGLE_JSON_CONTENT)

        # 9) crear paquete de kernel (notebook + kernel-metadata.json)
        kernel_pkg_dir = tempfile.mkdtemp(prefix="kaggle_kernel_")
        create_kernel_package(nb_path, kernel_pkg_dir, kernel_metadata={
            "id": "jsgastonalgotrading/forrest",  # si no tienes permiso de ese id, cambia
            "title": "Forrest (auto-run)",
            "code_file": os.path.basename(nb_path),
            "language": "python",
            "kernel_type": "notebook",
            "is_private": True
        })

        # 10) push & run kernel
        push_kaggle_kernel(kernel_pkg_dir)

        print("\n✅ Pipeline completado. Notebook modificado, empujado y ejecutado en Kaggle.")
        print("   Drive file_id:", file_id)
        print("   Drive download URL:", download_url)
    finally:
        # limpieza opcional: no borrar los CSV intermedios según tu petición original; solo limpia temporales
        try:
            shutil.rmtree(tmpdir)
            shutil.rmtree(kernel_pkg_dir)
        except Exception:
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
    except Exception as e:
        print("\nERROR:", e)
        import traceback
        traceback.print_exc()
        sys.exit(1)
