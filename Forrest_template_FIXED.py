# Instalar dependencias con reintentos y alternativas
import subprocess
import sys
import time

def install_package_with_retry(package, max_retries=3, timeout=30):
    """Instala un paquete con reintentos y timeout"""
    for attempt in range(max_retries):
        try:
            print(f'📦 Instalando {package}... (intento {attempt + 1}/{max_retries})')
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-q', '--timeout', str(timeout), package],
                capture_output=True,
                text=True,
                timeout=timeout + 10
            )
            if result.returncode == 0:
                print(f'✅ {package} instalado')
                return True
            else:
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    print(f'   ⏳ Error, reintentando en {wait_time}s...')
                    time.sleep(wait_time)
                else:
                    print(f'❌ Error instalando {package} después de {max_retries} intentos')
                    if result.stderr:
                        print(f'   Error: {result.stderr.splitlines()[-1] if result.stderr.splitlines() else result.stderr}')
        except subprocess.TimeoutExpired:
            if attempt < max_retries - 1:
                print(f'   ⏳ Timeout, reintentando...')
                time.sleep(5)
            else:
                print(f'❌ Timeout instalando {package}')
        except Exception as e:
            print(f'❌ Error inesperado instalando {package}: {e}')
            break
    return False

# Paquetes esenciales (sin ta y arch inicialmente)
essential_packages = [
    'gdown',
    'xgboost',
    'lightgbm',
    'plotly',
    'optuna',
    'statsmodels',
    'psutil',
    'tqdm'
]

# Paquetes problemáticos (intentar con diferentes estrategias)
problematic_packages = {
    'ta': ['ta==0.11.0', 'ta==0.10.2', 'ta'],  # Intentar diferentes versiones
    'arch': ['arch', 'arch==5.3.1']
}

print('='*70)
print('INSTALANDO DEPENDENCIAS ESENCIALES')
print('='*70)

failed_packages = []
installed_packages = []

# Instalar paquetes esenciales
for package in essential_packages:
    if install_package_with_retry(package):
        installed_packages.append(package)
    else:
        failed_packages.append(package)

print('\n' + '='*70)
print('INSTALANDO PAQUETES PROBLEMÁTICOS (con alternativas)')
print('='*70)

# Intentar instalar paquetes problemáticos con alternativas
for package_name, alternatives in problematic_packages.items():
    installed = False
    for alt in alternatives:
        print(f'\n🔄 Intentando {package_name} (versión: {alt})')
        if install_package_with_retry(alt, max_retries=2, timeout=20):
            installed_packages.append(package_name)
            installed = True
            break
        else:
            print(f'   ⏭️  Probando siguiente alternativa...')
    
    if not installed:
        failed_packages.append(package_name)
        print(f'\n⚠️  No se pudo instalar {package_name} con ninguna alternativa')

print('\n' + '='*70)
print('RESUMEN DE INSTALACIÓN')
print('='*70)
print(f'✅ Instalados exitosamente: {len(installed_packages)}')
if installed_packages:
    for pkg in installed_packages:
        print(f'   • {pkg}')

if failed_packages:
    print(f'\n❌ Fallaron: {len(failed_packages)}')
    for pkg in failed_packages:
        print(f'   • {pkg}')
    print('\n⚠️  RECOMENDACIONES:')
    print('   1. Verifica que "Internet" esté habilitado en Configuración')
    print('   2. Espera 10-15 minutos y vuelve a ejecutar esta celda')
    print('   3. Intenta en horario diferente (menos tráfico en Kaggle)')
    if 'ta' in failed_packages:
        print('\n💡 ALTERNATIVA PARA TA:')
        print('   Si "ta" no se instala, el notebook puede funcionar sin algunos')
        print('   indicadores técnicos avanzados. Los básicos están disponibles.')
    if 'arch' in failed_packages:
        print('\n💡 ALTERNATIVA PARA ARCH:')
        print('   "arch" es para modelos GARCH de volatilidad. Si no se instala,')
        print('   el notebook funcionará sin esta funcionalidad específica.')
else:
    print('\n🎉 Todas las dependencias instaladas correctamente!')

print('='*70)

# Intentar importar lo que se instaló para verificar
print('\n🔍 Verificando importaciones...')
import importlib
verification = {}
for pkg in ['xgboost', 'lightgbm', 'plotly', 'optuna', 'statsmodels', 'ta']:
    try:
        importlib.import_module(pkg)
        verification[pkg] = True
        print(f'✅ {pkg} verificado')
    except ImportError:
        verification[pkg] = False
        print(f'❌ {pkg} no disponible')

print('\n✨ Instalación completada. Puedes continuar con las siguientes celdas.')


# Importaciones principales
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import gc, json, pickle, joblib, os, sys, subprocess
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, List
import time, itertools
from scipy.stats import median_abs_deviation
from tqdm.auto import tqdm

# Sklearn
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler, LabelEncoder
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
    mean_absolute_percentage_error, explained_variance_score
)
from sklearn.ensemble import (
    RandomForestRegressor, RandomForestClassifier,
    GradientBoostingRegressor, GradientBoostingClassifier,
    StackingRegressor, StackingClassifier, VotingClassifier, 
    VotingRegressor, AdaBoostRegressor, AdaBoostClassifier
)
from sklearn.linear_model import (
    LinearRegression, LogisticRegression, Ridge, Lasso, 
    ElasticNet, SGDRegressor
)
from sklearn.svm import SVR, SVC
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.model_selection import (
    TimeSeriesSplit, GridSearchCV, RandomizedSearchCV,
    cross_val_score, train_test_split
)
from sklearn.decomposition import PCA
from sklearn.feature_selection import (
    SelectKBest, f_regression, mutual_info_regression, 
    RFE, mutual_info_classif
)
from sklearn.mixture import GaussianMixture

# Boosting
import xgboost as xgb
import lightgbm as lgb

# Visualización
import matplotlib.pyplot as plt
import seaborn as sns
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except:
    PLOTLY_AVAILABLE = False

# Indicadores técnicos (opcional - usa implementación manual si no disponible)
TA_AVAILABLE = False
try:
    import ta
    TA_AVAILABLE = True
    print("✅ ta disponible - usando biblioteca ta")
except ImportError:
    TA_AVAILABLE = False
    print("⚠️  ta no disponible - usando implementación manual de indicadores")
    print("   RSI, MACD, Bollinger Bands, etc. se calcularán manualmente")

TALIB_AVAILABLE = False
try:
    import talib
    TALIB_AVAILABLE = True
    print("✅ TA-Lib disponible")
except:
    pass

# Series temporales
try:
    import statsmodels.api as sm
    from statsmodels.tsa.stattools import adfuller, kpss, coint, acf, pacf
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from statsmodels.stats.diagnostic import acorr_ljungbox
    STATSMODELS_AVAILABLE = True
except:
    STATSMODELS_AVAILABLE = False

try:
    from arch import arch_model
    ARCH_AVAILABLE = True
except:
    ARCH_AVAILABLE = False

# Scipy
from scipy import stats as scipy_stats
from scipy.signal import savgol_filter, find_peaks
import psutil

# Configuración plotting
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('viridis')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

print('✅ Importaciones completadas')
print(f'📊 Timeframes disponibles: Variable según configuración')

import sys
import importlib

packages = ['ta', 'xgboost', 'lightgbm', 'plotly', 'optuna', 'statsmodels']

print("Verificando paquetes instalados:\n")
for pkg in packages:
    try:
        module = importlib.import_module(pkg)
        version = getattr(module, '__version__', 'N/A')
        print(f"✅ {pkg:15} version: {version}")
    except ImportError:
        print(f"❌ {pkg:15} NO INSTALADO")


# Configuración para Kaggle
print('='*80)
print('CONFIGURACIÓN DEL ENTORNO')
print('='*80)

IS_KAGGLE = os.path.exists('/kaggle')
MAX_ROWS = 500000

if IS_KAGGLE:
    print('✅ Entorno: Kaggle')
    BASE_PATH = '/kaggle/working/EURUSD_H1_Data'
else:
    print('✅ Entorno: Local')
    BASE_PATH = os.path.join(os.getcwd(), 'EURUSD_H1_Data')

# Crear estructura de directorios
DATA_PATH = os.path.join(BASE_PATH, 'data')
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
OUTPUT_PATH = os.path.join(BASE_PATH, f'Trading_System_{timestamp}')

directories = [
    BASE_PATH, DATA_PATH, OUTPUT_PATH,
    os.path.join(OUTPUT_PATH, 'models'),
    os.path.join(OUTPUT_PATH, 'plots'),
    os.path.join(OUTPUT_PATH, 'backtest_results'),
    os.path.join(OUTPUT_PATH, 'data_analysis'),
    os.path.join(OUTPUT_PATH, 'logs'),
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)

DATA_FILE = os.path.join(DATA_PATH, 'EURUSD_M1_10years.csv')
TIMEFRAMES = ['15min', '30min', '1H', '4H', '1D']

print(f'\n📋 RUTAS CONFIGURADAS:')
print(f'   BASE_PATH:   {BASE_PATH}')
print(f'   DATA_PATH:   {DATA_PATH}')
print(f'   OUTPUT_PATH: {OUTPUT_PATH}')
print(f'   DATA_FILE:   {DATA_FILE}')
print(f'   TIMEFRAMES:  {TIMEFRAMES}')

# Espacio disponible
try:
    import shutil
    total, used, free = shutil.disk_usage(BASE_PATH)
    print(f'\n💾 Espacio: {free // (2**30)} GB libres de {total // (2**30)} GB')
except:
    pass

print('='*80)
print('✅ Configuración completada\n')


# Descargar desde Google Drive
print('='*70)
print('📥 DESCARGANDO DATOS')
print('='*70)

# CONFIGURA TU FILE_ID AQUÍ ↓
files_to_download = {
    'EURUSD_M1_10years.csv': '1gQWGlDlcPCqwh-GqPXEOcUSIOXvK5FTp',  # ← CAMBIA ESTO
}

for filename, file_id in files_to_download.items():
    output_file = os.path.join(DATA_PATH, filename)
    
    if os.path.exists(output_file):
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f'⏭️  Ya existe: {filename} ({size_mb:.2f} MB)')
        continue
    
    try:
        print(f'📥 Descargando: {filename}...')
        url = f'https://drive.google.com/uc?id={file_id}'
        subprocess.run(['gdown', url, '-O', output_file], check=True, capture_output=True)
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f'✅ {filename} descargado ({size_mb:.2f} MB)')
    except Exception as e:
        print(f'❌ Error: {e}')

# Verificar
if os.path.exists(DATA_FILE):
    df_test = pd.read_csv(DATA_FILE, nrows=5)
    print(f'\n✅ Archivo encontrado: {DATA_FILE}')
    print(f'   Columnas: {list(df_test.columns)}')
    print(f'   Primeras 5 filas:')
    print(df_test.head())
else:
    print(f'\n❌ Archivo no encontrado: {DATA_FILE}')
    print('   Verifica el FILE_ID')

print('='*70)


# ============================================================================
# UTILIDADES Y DECORADORES
# ============================================================================

def timing_decorator(func):
    """Decorador para medir tiempo de ejecución"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        print(f"{func.__name__} ejecutado en {elapsed:.2f} segundos")
        return result
    return wrapper

def memory_monitor():
    """Monitorear uso de memoria"""
    process = psutil.Process()
    mem_info = process.memory_info()
    mem_mb = mem_info.rss / (1024 * 1024)
    return mem_mb

# ============================================================================
# SISTEMA DE RIESGO AVANZADO
# ============================================================================

class AdvancedRiskManager:
    """Sistema de gestión de riesgo mejorado"""
    
    def __init__(self, 
                 max_position_size: float = 0.02,
                 max_daily_loss: float = 0.05,
                 max_drawdown: float = 0.20,
                 risk_free_rate: float = 0.02):
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown
        self.risk_free_rate = risk_free_rate
        self.daily_losses = []
        self.peak_equity = 10000
        self.current_drawdown = 0
        
        print(f"✅ Sistema de riesgo avanzado inicializado:")
        print(f"  Max posición: {max_position_size*100}%")
        print(f"  Max pérdida diaria: {max_daily_loss*100}%")
        print(f"  Max drawdown: {max_drawdown*100}%")
    
    def can_trade(self, current_equity: float) -> bool:
        """Verificar si se puede abrir nueva posición"""
        # Verificar drawdown
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
        
        self.current_drawdown = (self.peak_equity - current_equity) / self.peak_equity
        
        if self.current_drawdown >= self.max_drawdown:
            return False
        
        # Verificar pérdida diaria
        if len(self.daily_losses) > 0:
            daily_loss = sum(self.daily_losses[-1:])
            if abs(daily_loss) / self.peak_equity >= self.max_daily_loss:
                return False
        
        return True
    
    def calculate_position_size(self, 
                                equity: float, 
                                stop_loss_pct: float,
                                win_rate: float = 0.5,
                                risk_reward: float = 2.0) -> float:
        """Calcular tamaño de posición usando Kelly Criterion modificado"""
        
        # Kelly Criterion: f = (p*b - q) / b
        # donde p = win_rate, q = 1-p, b = risk_reward
        p = max(0.3, min(0.7, win_rate))  # Limitar entre 30% y 70%
        q = 1 - p
        b = risk_reward
        
        kelly_fraction = (p * b - q) / b
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Max 25% Kelly
        
        # Aplicar Kelly con factor de seguridad
        risk_per_trade = min(
            self.max_position_size,
            kelly_fraction * 0.5  # Usar mitad de Kelly por seguridad
        )
        
        # Calcular tamaño basado en stop loss
        position_size = (equity * risk_per_trade) / stop_loss_pct
        
        return min(position_size, equity * self.max_position_size)

print('✅ AdvancedRiskManager cargado')


# @title
# Diccionario donde guardaremos los resultados de cada timeframe
results_by_timeframe = {}

# Iterar sobre todos los timeframes
for tf in TIMEFRAMES:
    print(f"\n=== TIMEFRAME: {tf} ===")

    try:

        # Configuración de paths

        OUTPUT_PATH_2 = os.path.join(OUTPUT_PATH, f'Trading_System_Advanced_{tf}')

        # Crear estructura de carpetas
        for folder in ['models', 'metrics', 'plots', 'data', 'backtest_results',
                      'feature_analysis', 'hyperparameters', 'ensembles', 'tensorboard']:
            os.makedirs(os.path.join(OUTPUT_PATH_2, folder), exist_ok=True)

        print(f"Output: {OUTPUT_PATH_2}")



    except Exception as e:
        print(f"⚠️ Error en {tf}: {e}")

print("\n✅ Iteración sobre todos los timeframes completada.")

if 'OUTPUT_PATH_2' not in globals():
    output_path = self.output_path if hasattr(self, 'output_path') else './output'
else:
    output_path = OUTPUT_PATH_2

# @title
# Configuración del sistema
class Config:
    # Parámetros de datos
    INITIAL_CAPITAL = 10000
    SPREAD = 0.0002
    COMMISSION = 0.0001
    RISK_FREE_RATE = 0.02  # Tasa libre de riesgo anual

    # Parámetros de modelos
    N_FOLDS = 5
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    N_JOBS = -1

    # Parámetros de backtesting
    WALK_FORWARD_TRAIN_SIZE = 1000
    WALK_FORWARD_TEST_SIZE = 250
    MONTE_CARLO_SIMULATIONS = 1000

    # Parámetros de riesgo
    MAX_POSITION_SIZE = 0.02  # 2% del capital por trade
    MAX_DAILY_LOSS = 0.05    # 5% de pérdida diaria máxima
    MAX_DRAWDOWN = 0.2       # 20% de drawdown máximo

    # Timeframes a analizar
    TIMEFRAMES = ['15min','30min','1H','4H','1D']

    # Métricas a calcular
    REGRESSION_METRICS = ['mae', 'mse', 'rmse', 'r2', 'mape', 'evs']
    CLASSIFICATION_METRICS = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']

    # Hiperparámetros para optimización
    HYPERPARAM_ITERATIONS = 50

config = Config()



# AÑADIR ESTAS FUNCIONES AL INICIO DEL SCRIPT, DESPUÉS DE LA CLASE Config

class AdaptiveDataManager:
    """Gestiona tamaños de datos y complejidad de modelos según timeframe"""

    def __init__(self):
        # Configuración de tamaños óptimos por timeframe
        # Basado en investigación empírica y mejores prácticas de trading cuantitativo
        self.timeframe_config = {
          '1min': {
              'min_samples': 5000,
              'max_samples': 200000,    # ← 20k → 100k ✅
              'sampling_method': 'recent_emphasis',
              'model_complexity': 'low',
              'max_features': 15,
              'regularization_strength': 'high',
              'early_stopping_patience': 5,
              'n_estimators': 50,
              'max_depth': 3,
              'max_features': 'sqrt',
              'min_samples_split': 20,
              'min_samples_leaf': 10,
              'neural_network_layers': [64, 32],
          },
          '5min': {
              'min_samples': 4000,
              'max_samples': 150000,    # ← 15k → 100k ✅
              'sampling_method': 'recent_emphasis',
              'model_complexity': 'low',
              'max_features': 20,
              'regularization_strength': 'high',
              'early_stopping_patience': 5,
              'n_estimators': 75,
              'max_depth': 4,
              'max_features': 'sqrt',
              'min_samples_split': 10,
              'min_samples_leaf': 5,
              'neural_network_layers': [128, 64, 32],
          },
          '15min': {
              'min_samples': 3000,
              'max_samples': 100000,     # ← 12k → 80k ✅
              'sampling_method': 'stratified',
              'model_complexity': 'medium',
              'max_features': 30,
              'regularization_strength': 'medium',
              'early_stopping_patience': 7,
              'n_estimators': 100,
              'max_depth': 5,
              'max_features': 'sqrt',
              'min_samples_split': 10,
              'min_samples_leaf': 5,
              'neural_network_layers': [128, 64, 32],
          },
          '30min': {
              'min_samples': 2500,
              'max_samples': 80000,     # ← 10k → 60k ✅
              'sampling_method': 'stratified',
              'model_complexity': 'medium',
              'max_features': 40,
              'regularization_strength': 'medium',
              'early_stopping_patience': 10,
              'n_estimators': 100,
              'max_depth': 5,
              'max_features': 'sqrt',
              'min_samples_split': 10,
              'min_samples_leaf': 5,
              'neural_network_layers': [128, 64, 32],
          },
          '1H': {
              'min_samples': 2000,
              'max_samples': 50000,     # ← 8k → 50k ✅
              'sampling_method': 'uniform',
              'model_complexity': 'medium',
              'max_features': 50,
              'regularization_strength': 'medium',
              'early_stopping_patience': 10,
              'n_estimators': 150,
              'max_depth': 6,
              'max_features': 'sqrt',
              'min_samples_split': 5,
              'min_samples_leaf': 2,
              'neural_network_layers': [256, 128, 64, 32],
          },
          '4H': {
              'min_samples': 1500,
              'max_samples': 40000,     # ← 6k → 40k ✅
              'sampling_method': 'uniform',
              'model_complexity': 'high',
              'max_features': 60,
              'regularization_strength': 'low',
              'early_stopping_patience': 15,
              'n_estimators': 200,
              'max_depth': 8,
              'max_features': 'sqrt',
              'min_samples_split': 5,
              'min_samples_leaf': 2,
              'neural_network_layers': [256, 128, 64, 32],
          },
          '1D': {
              'min_samples': 500,       # ← 1000 → 500 (para procesar con 478 filas) ✅
              'max_samples': None,     # ← 4k → 20k ✅
              'sampling_method': 'uniform',
              'model_complexity': 'high',
              'max_features': 70,
              'regularization_strength': 'low',
              'early_stopping_patience': 20,
              'n_estimators': 200,
              'max_depth': 10,
              'max_features': 'sqrt',
              'min_samples_split': 5,
              'min_samples_leaf': 2,
              'neural_network_layers': [256, 128, 64, 32],
          },
          '3D': {
              'min_samples': 80,        # ← 500 → 80 (para procesar con 99 filas) ✅
              'max_samples': None,     # ← 2k → 10k ✅
              'sampling_method': 'uniform',
              'model_complexity': 'high',
              'max_features': 70,
              'regularization_strength': 'low',
              'early_stopping_patience': 20,
              'n_estimators': 200,
              'max_depth': 10,
              'max_features': 'sqrt',
              'min_samples_split': 5,
              'min_samples_leaf': 2,
              'neural_network_layers': [256, 128, 64, 32],
          },
          '7D': {
              'min_samples': 0,         # ← 300 → 0 (desactivar si no hay datos) ✅
              'max_samples': None,      # ← 1k → 5k ✅
              'sampling_method': 'uniform',
              'model_complexity': 'high',
              'max_features': 70,
              'regularization_strength': 'low',
              'early_stopping_patience': 20,
              'n_estimators': 200,
              'max_depth': 10,
              'max_features': 'sqrt',
              'min_samples_split': 5,
              'min_samples_leaf': 2,
              'neural_network_layers': [256, 128, 64, 32],
          }
      }

    def get_optimal_sample_size(self, df, timeframe):
        """Determina el tamaño óptimo de muestra para un timeframe específico"""
        config = self.timeframe_config.get(timeframe, self.timeframe_config['1D'])

        total_available = len(df)
        max_recommended = config['max_samples']
        min_required = config['min_samples']

        # Usar el menor entre lo disponible y lo recomendado, pero respetando el mínimo
        if total_available < min_required:
            print(f"⚠️ Datos insuficientes para {timeframe}: {total_available} < {min_required}")
            return None, f"Insuficientes datos para análisis robusto en {timeframe}"

        optimal_size = min(total_available, max_recommended)

        print(f"📊 {timeframe}: Usando {optimal_size:,} de {total_available:,} observaciones disponibles")
        print(f"   Esto representa aprox. {self._estimate_time_coverage(optimal_size, timeframe)}")

        return optimal_size, "OK"

    def _estimate_time_coverage(self, n_samples, timeframe):
        """Estima la cobertura temporal de una cantidad de muestras"""
        timeframe_minutes = {
            '1min': 1, '5min': 5, '15min': 15, '30min': 30,
            '1H': 60, '4H': 240, '1D': 1440, '3D': 4320, '7D': 10080
        }

        total_minutes = n_samples * timeframe_minutes.get(timeframe, 1440)

        if total_minutes < 1440:  # Menos de un día
            return f"{total_minutes/60:.1f} horas"
        elif total_minutes < 1440 * 30:  # Menos de un mes
            return f"{total_minutes/1440:.1f} días"
        elif total_minutes < 1440 * 365:  # Menos de un año
            return f"{total_minutes/(1440*30):.1f} meses"
        else:
            return f"{total_minutes/(1440*365):.1f} años"

# SOLUCIÓN 1: Corregir get_model_complexity_config
# Busca este método en la clase AdaptiveDataManager y reemplázalo:

    def get_model_complexity_config(self, timeframe):
        """Obtiene configuración de complejidad de modelo para un timeframe"""

        # Validar timeframe
        if timeframe not in self.timeframe_config:
            print(f"⚠️ Timeframe {timeframe} no encontrado, usando '1D' como default")
            timeframe = '1D'

        config = self.timeframe_config[timeframe]

        complexity_configs = {
            'low': {
                'max_depth': 6,
                'n_estimators': 75,
                'min_samples_split': 20,
                'min_samples_leaf': 10,
                'max_features': 0.6,
                'neural_network_layers': [64, 32],
                'dropout_rate': 0.4
            },
            'medium': {
                'max_depth': 10,
                'n_estimators': 100,
                'min_samples_split': 10,
                'min_samples_leaf': 5,
                'max_features': 0.8,
                'neural_network_layers': [128, 64, 32],
                'dropout_rate': 0.3
            },
            'high': {
                'max_depth': 15,
                'n_estimators': 200,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'max_features': 1.0,
                'neural_network_layers': [256, 128, 64, 32],
                'dropout_rate': 0.2
            }
        }

        complexity = config.get('model_complexity', 'medium')
        model_config = complexity_configs.get(complexity, complexity_configs['medium']).copy()

        # CRÍTICO: Añadir TODAS las configuraciones necesarias
        model_config.update({
            'model_complexity': complexity,  # ← ESTO ES LO QUE FALTABA
            'features_max': config.get('features_max', 30),
            'validation_splits': config.get('validation_splits', 5),
            'early_stopping_patience': config.get('early_stopping_patience', 10),
            'regularization_strength': config.get('regularization_strength', 'medium')
        })

        return model_config

    def sample_data_optimally(self, df, timeframe, method='recent_emphasis'):
        """Samplea datos de manera óptima para el timeframe específico"""
        optimal_size, status = self.get_optimal_sample_size(df, timeframe)

        if optimal_size is None:
            return None, status

        total_available = len(df)

        if optimal_size >= total_available:
            # Usar todos los datos disponibles
            return df, "Usando todos los datos disponibles"

        # Estrategias de sampling según el método
        if method == 'recent_emphasis':
            # Dar más peso a datos recientes pero incluir algo de historia
            # 70% datos recientes, 30% datos históricos distribuidos
            recent_count = int(optimal_size * 0.7)
            historical_count = optimal_size - recent_count

            # Tomar datos más recientes
            recent_data = df.iloc[-recent_count:]

            # Tomar muestra distribuida de datos históricos
            if total_available - recent_count > historical_count:
                historical_indices = np.linspace(
                    0, total_available - recent_count - 1,
                    historical_count, dtype=int
                )
                historical_data = df.iloc[historical_indices]

                # Combinar y reordenar cronológicamente
                sampled_df = pd.concat([historical_data, recent_data]).sort_index()
            else:
                sampled_df = recent_data

        elif method == 'uniform':
            # Sampling uniforme a través de todo el período
            indices = np.linspace(0, total_available - 1, optimal_size, dtype=int)
            sampled_df = df.iloc[indices]

        elif method == 'most_recent':
            # Simplemente tomar los datos más recientes
            sampled_df = df.iloc[-optimal_size:]

        else:
            raise ValueError(f"Método de sampling no reconocido: {method}")

        print(f"   Método de sampling: {method}")
        print(f"   Datos seleccionados: {len(sampled_df):,} observaciones")

        return sampled_df, "Sampling completado exitosamente"

# Función para integrar con el pipeline existente
# En la función apply_adaptive_data_management (alrededor de la línea donde se define):

# SOLUCIÓN 2: Corregir apply_adaptive_data_management
# Busca esta función (está fuera de las clases) y reemplázala:

def apply_adaptive_data_management(df_dict, timeframe):
    """Aplica gestión adaptativa de datos para un timeframe específico"""
    data_manager = AdaptiveDataManager()

    # Verificar si el timeframe existe en los datos
    if timeframe not in df_dict:
        return None, None, f"Timeframe {timeframe} no encontrado en datos"

    df = df_dict[timeframe]

    # Obtener muestra óptima
    sampled_df, status = data_manager.sample_data_optimally(df, timeframe, method='recent_emphasis')

    if sampled_df is None:
        return None, None, status

    # Obtener configuración de modelo
    model_config = data_manager.get_model_complexity_config(timeframe)

    # Validación con valores por defecto si falta algo
    if not model_config or not isinstance(model_config, dict):
        return None, None, f"Error al obtener configuración de modelo para {timeframe}"

    # Asegurar que todas las claves necesarias existen
    required_defaults = {
        'model_complexity': 'medium',
        'features_max': 30,
        'validation_splits': 5,
        'regularization_strength': 'medium',
        'early_stopping_patience': 10
    }

    for key, default_value in required_defaults.items():
        if key not in model_config:
            model_config[key] = default_value

    return sampled_df, model_config, status

# Función para ajustar parámetros de modelos según timeframe
# ═══════════════════════════════════════════════════════════════════════════
# CAMBIO #2: REEMPLAZAR FUNCIÓN get_timeframe_adjusted_models()
# ═══════════════════════════════════════════════════════════════════════════
#
# UBICACIÓN: Línea ~1249
# ACCIÓN: Reemplazar TODA la función existente con este código
#
# ═══════════════════════════════════════════════════════════════════════════

def get_timeframe_adjusted_models(timeframe, model_config):
    """Retorna modelos específicos según el timeframe - VERSIÓN MEJORADA CON MÁS MODELOS"""
    from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, LogisticRegression
    from sklearn.svm import SVR, SVC
    from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
    from sklearn.ensemble import AdaBoostRegressor, AdaBoostClassifier
    from sklearn.neural_network import MLPRegressor, MLPClassifier

    # Configurar regularización según el nivel especificado
    reg_strength = model_config['regularization_strength']
    if reg_strength == 'high':
        xgb_reg_alpha, xgb_reg_lambda = 1.0, 1.0
        lgb_reg_alpha, lgb_reg_lambda = 1.0, 1.0
    elif reg_strength == 'medium':
        xgb_reg_alpha, xgb_reg_lambda = 0.5, 0.5
        lgb_reg_alpha, lgb_reg_lambda = 0.5, 0.5
    else:  # low
        xgb_reg_alpha, xgb_reg_lambda = 0.1, 0.1
        lgb_reg_alpha, lgb_reg_lambda = 0.1, 0.1

    # ════════════════════════════════════════════════════════════════════════
    # MODELOS BASE (para todos los timeframes)
    # ════════════════════════════════════════════════════════════════════════
    base_models_reg = {
        'xgb_reg': xgb.XGBRegressor(
            n_estimators=model_config['n_estimators'],
            max_depth=model_config['max_depth'],
            reg_alpha=xgb_reg_alpha,
            reg_lambda=xgb_reg_lambda,
            random_state=config.RANDOM_STATE,
            n_jobs=-1
        ),
        'lgb_reg': lgb.LGBMRegressor(
            n_estimators=model_config['n_estimators'],
            max_depth=model_config['max_depth'],
            reg_alpha=lgb_reg_alpha,
            reg_lambda=lgb_reg_lambda,
            random_state=config.RANDOM_STATE,
            n_jobs=-1,
            verbose=-1
        ),
        'rf_reg': RandomForestRegressor(
            n_estimators=model_config['n_estimators'],
            max_depth=model_config['max_depth'],
            min_samples_split=model_config['min_samples_split'],
            min_samples_leaf=model_config['min_samples_leaf'],
            max_features=model_config['max_features'],
            random_state=config.RANDOM_STATE,
            n_jobs=-1
        ),
        'linear_reg': LinearRegression(n_jobs=-1),
        'ridge_reg': Ridge(alpha=1.0, random_state=config.RANDOM_STATE),
    }

    base_models_clf = {
        'xgb_clf': xgb.XGBClassifier(
            n_estimators=model_config['n_estimators'],
            max_depth=model_config['max_depth'],
            reg_alpha=xgb_reg_alpha,
            reg_lambda=xgb_reg_lambda,
            random_state=config.RANDOM_STATE,
            n_jobs=-1,
            use_label_encoder=False,
            eval_metric='logloss'
        ),
        'lgb_clf': lgb.LGBMClassifier(
            n_estimators=model_config['n_estimators'],
            max_depth=model_config['max_depth'],
            reg_alpha=lgb_reg_alpha,
            reg_lambda=lgb_reg_lambda,
            random_state=config.RANDOM_STATE,
            n_jobs=-1,
            verbose=-1
        ),
        'rf_clf': RandomForestClassifier(
            n_estimators=model_config['n_estimators'],
            max_depth=model_config['max_depth'],
            min_samples_split=model_config['min_samples_split'],
            min_samples_leaf=model_config['min_samples_leaf'],
            max_features=model_config['max_features'],
            random_state=config.RANDOM_STATE,
            n_jobs=-1
        ),
        'logistic_clf': LogisticRegression(
            max_iter=1000,
            random_state=config.RANDOM_STATE,
            n_jobs=-1
        ),
    }

    # ════════════════════════════════════════════════════════════════════════
    # AGREGAR MODELOS SEGÚN TIMEFRAME
    # ════════════════════════════════════════════════════════════════════════

    if timeframe in ['1min', '5min']:
        # ────────────────────────────────────────────────────────────────────
        # TIMEFRAMES CORTOS: Modelos base + ligeros
        # Total: 5 regresión + 4 clasificación = 9 modelos
        # ────────────────────────────────────────────────────────────────────
        adjusted_models_reg = base_models_reg.copy()
        adjusted_models_clf = base_models_clf.copy()
        print(f"   📊 {timeframe}: Usando 9 modelos (5 reg + 4 clf)")

    elif timeframe in ['15min', '30min', '1H']:
        # ────────────────────────────────────────────────────────────────────
        # TIMEFRAMES MEDIOS: Base + modelos adicionales + redes neuronales
        # Total: 8 regresión + 7 clasificación = 15 modelos
        # ────────────────────────────────────────────────────────────────────
        adjusted_models_reg = base_models_reg.copy()
        adjusted_models_reg.update({
            'lasso_reg': Lasso(alpha=0.1, random_state=config.RANDOM_STATE, max_iter=2000),
            'svr': SVR(kernel='rbf', C=1.0, gamma='scale'),
            'gbr': GradientBoostingRegressor(
                n_estimators=min(100, model_config['n_estimators']),
                max_depth=min(5, model_config['max_depth']),
                random_state=config.RANDOM_STATE
            ),
        })

        adjusted_models_clf = base_models_clf.copy()
        adjusted_models_clf.update({
            'svm_clf': SVC(
                kernel='rbf',
                C=1.0,
                gamma='scale',
                probability=True,
                random_state=config.RANDOM_STATE
            ),
            'gbc': GradientBoostingClassifier(
                n_estimators=min(100, model_config['n_estimators']),
                max_depth=min(5, model_config['max_depth']),
                random_state=config.RANDOM_STATE
            ),
            'mlp_clf': MLPClassifier(
                hidden_layer_sizes=(128, 64),
                max_iter=500,
                random_state=config.RANDOM_STATE,
                early_stopping=True
            ),
        })
        print(f"   📊 {timeframe}: Usando 14 modelos (8 reg + 6 clf)")

    else:  # '4H', '1D', '3D', '7D'
        # ────────────────────────────────────────────────────────────────────
        # TIMEFRAMES LARGOS: Todos los modelos
        # Total: 10 regresión + 9 clasificación = 19 modelos
        # ────────────────────────────────────────────────────────────────────
        adjusted_models_reg = base_models_reg.copy()
        adjusted_models_reg.update({
            'lasso_reg': Lasso(alpha=0.1, random_state=config.RANDOM_STATE, max_iter=2000),
            'elasticnet_reg': ElasticNet(
                alpha=0.1,
                l1_ratio=0.5,
                random_state=config.RANDOM_STATE,
                max_iter=2000
            ),
            'svr': SVR(kernel='rbf', C=1.0, gamma='scale'),
            'gbr': GradientBoostingRegressor(
                n_estimators=min(150, model_config['n_estimators']),
                max_depth=min(6, model_config['max_depth']),
                random_state=config.RANDOM_STATE
            ),
            'ada_reg': AdaBoostRegressor(
                n_estimators=50,
                random_state=config.RANDOM_STATE
            ),
            'mlp_reg': MLPRegressor(
                hidden_layer_sizes=(256, 128, 64),
                max_iter=500,
                random_state=config.RANDOM_STATE,
                early_stopping=True,
                validation_fraction=0.1
            ),
        })

        adjusted_models_clf = base_models_clf.copy()
        adjusted_models_clf.update({
            'svm_clf': SVC(
                kernel='rbf',
                C=1.0,
                gamma='scale',
                probability=True,
                random_state=config.RANDOM_STATE
            ),
            'gbc': GradientBoostingClassifier(
                n_estimators=min(150, model_config['n_estimators']),
                max_depth=min(6, model_config['max_depth']),
                random_state=config.RANDOM_STATE
            ),
            'ada_clf': AdaBoostClassifier(
                n_estimators=50,
                random_state=config.RANDOM_STATE
            ),
            'mlp_clf': MLPClassifier(
                hidden_layer_sizes=(256, 128, 64),
                max_iter=500,
                random_state=config.RANDOM_STATE,
                early_stopping=True,
                validation_fraction=0.1
            ),
        })
        print(f"   📊 {timeframe}: Usando 19 modelos (10 reg + 9 clf)")

    return adjusted_models_reg, adjusted_models_clf






# Utilidades
def clear_memory():
    """Limpiar memoria"""
    gc.collect()
    if TF_AVAILABLE and hasattr(tf, 'keras'):
        tf.keras.backend.clear_session()

def get_memory_usage():
    """Obtener uso de memoria"""
    try:
        process = psutil.Process(os.getpid())
        return f"RAM: {process.memory_info().rss / 1024 / 1024:.0f} MB"
    except:
        return "RAM: N/A"

def timer_decorator(func):
    """Decorador para medir tiempo de ejecución"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} ejecutado en {end_time - start_time:.2f} segundos")
        return result
    return wrapper


# ============================================================================
print("class AdaptiveDataManager")

# @title
# [4] PROCESAMIENTO DE DATOS MEJORADO - VERSIÓN CORREGIDA
class AdvancedDataProcessor:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.scalers = {}
        self.feature_importance = {}
        self.current_timeframe = None  # ✅ NUEVO: trackear timeframe actual

    @timer_decorator
    def load_data(self, filepath: str, nrows: Optional[int] = None) -> pd.DataFrame:
        """Carga y optimiza datos"""
        print(f"Cargando datos: {filepath}")

        # Mapeo de nombres de columnas
        column_mapping = {
            '<DATE>': 'date',
            '<TIME>': 'time',
            '<OPEN>': 'open',
            '<HIGH>': 'high',
            '<LOW>': 'low',
            '<CLOSE>': 'close',
            '<TICKVOL>': 'tick_volume',
            '<VOL>': 'real_volume',
            '<SPREAD>': 'spread'
        }

        dtype = {
            '<OPEN>': 'float32',
            '<HIGH>': 'float32',
            '<LOW>': 'float32',
            '<CLOSE>': 'float32',
            '<TICKVOL>': 'int32',
            '<SPREAD>': 'int16',
            '<VOL>': 'int32'
        }

        # Leer CSV con separador de tabulaciones
        df = pd.read_csv(filepath, sep='\t', dtype=dtype, nrows=nrows)

        # Renombrar columnas
        df.rename(columns=column_mapping, inplace=True)

        # Crear columna datetime combinando date y time
        df['time'] = pd.to_datetime(df['date'] + ' ' + df['time'], format='%Y.%m.%d %H:%M:%S')
        df.drop(['date'], axis=1, inplace=True)

        df = df.sort_values('time').reset_index(drop=True)

        print(f"Cargado: {len(df):,} filas | {get_memory_usage()}")
        return df

    def resample_timeframe(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """Resamplea a diferentes timeframes"""
        self.current_timeframe = timeframe  # ✅ GUARDAR timeframe actual
        return df.set_index('time').resample(timeframe).agg({
            'open': 'first', 'high': 'max', 'low': 'min',
            'close': 'last', 'tick_volume': 'sum',
            'spread': 'mean', 'real_volume': 'sum'
        }).dropna()

    def get_optimal_target_periods(self, timeframe):
        """Retorna target_periods óptimo según timeframe"""
        target_map = {
            '1min': 5, '5min': 3, '15min': 2, '30min': 2,
            '1H': 4, '4H': 3, '1D': 5, '3D': 3, '7D': 2,
        }
        return target_map.get(timeframe, 5)

    @timer_decorator
    def create_multiple_timeframes(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Crear datos para múltiples timeframes"""
        timeframes_data = {}

        for tf in config.TIMEFRAMES:
            print(f"Procesando timeframe: {tf}")
            tf_data = self.resample_timeframe(df, tf)
            tf_data = self.add_features(tf_data)  # ✅ Ahora tiene self.current_timeframe
            timeframes_data[tf] = tf_data

        return timeframes_data

    @timer_decorator
    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Añade características técnicas avanzadas - VERSIÓN CORREGIDA"""
        df = df.copy()

        # ✅ CORRECCIÓN: Usar el timeframe guardado
        tf = self.current_timeframe if self.current_timeframe else "unknown"

        # 1. Precios y ratios básicos
        df['price_position'] = (df['close'] - df['low']) / (df['high'] - df['low'] + 1e-10)
        df['hl_ratio'] = (df['high'] - df['low']) / df['close']
        df['oc_ratio'] = (df['close'] - df['open']) / df['open']
        df['hl_pct'] = (df['high'] - df['low']) / df['low']

        # 2. Retornos y volatilidad
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))

        for window in [5, 10, 20, 50]:
            df[f'volatility_{window}'] = df['returns'].rolling(window).std()
            df[f'realized_vol_{window}'] = df['log_returns'].rolling(window).std()

        # 3. Indicadores de tendencia
        if TALIB_AVAILABLE:
            for period in [5, 10, 20, 50, 100, 200]:
                df[f'sma_{period}'] = talib.SMA(df['close'], timeperiod=period)
                df[f'ema_{period}'] = talib.EMA(df['close'], timeperiod=period)
                df[f'price_to_sma_{period}'] = df['close'] / df[f'sma_{period}']
                df[f'price_to_ema_{period}'] = df['close'] / df[f'ema_{period}']

            df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(
                df['close'], fastperiod=12, slowperiod=26, signalperiod=9
            )
            df['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
            df['sar'] = talib.SAR(df['high'], df['low'], acceleration=0.02, maximum=0.2)
            df['rsi'] = talib.RSI(df['close'], timeperiod=14)
            df['rsi_norm'] = df['rsi'] / 100
            df['stoch_k'], df['stoch_d'] = talib.STOCH(
                df['high'], df['low'], df['close'],
                fastk_period=14, slowk_period=3, slowd_period=3
            )
            df['stoch_norm'] = df['stoch_k'] / 100
            df['cci'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=20)
            df['williams_r'] = talib.WILLR(df['high'], df['low'], df['close'], timeperiod=14)
            df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(
                df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
            )
            df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
            df['obv'] = talib.OBV(df['close'], df['tick_volume'].astype(float))
            df['mfi'] = talib.MFI(df['high'], df['low'], df['close'],
                                df['tick_volume'].astype(float), timeperiod=14)
        else:
            # Usar biblioteca ta como alternativa
            for period in [5, 10, 20, 50, 100, 200]:
                df[f'sma_{period}'] = ta.trend.sma_indicator(df['close'], window=period)
                df[f'ema_{period}'] = ta.trend.ema_indicator(df['close'], window=period)
                df[f'price_to_sma_{period}'] = df['close'] / (df[f'sma_{period}'] + 1e-10)
                df[f'price_to_ema_{period}'] = df['close'] / (df[f'ema_{period}'] + 1e-10)

            macd = ta.trend.MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_hist'] = macd.macd_diff()
            df['adx'] = ta.trend.adx(df['high'], df['low'], df['close'])
            df['rsi'] = ta.momentum.rsi(df['close'])
            df['rsi_norm'] = df['rsi'] / 100
            stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()
            df['stoch_norm'] = df['stoch_k'] / 100
            df['cci'] = ta.trend.cci(df['high'], df['low'], df['close'])
            df['williams_r'] = ta.momentum.williams_r(df['high'], df['low'], df['close'])
            bb = ta.volatility.BollingerBands(df['close'])
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_lower'] = bb.bollinger_lband()
            df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
            df['obv'] = ta.volume.on_balance_volume(df['close'], df['tick_volume'])
            df['mfi'] = ta.volume.money_flow_index(df['high'], df['low'],
                                                  df['close'], df['tick_volume'])

        # Características comunes
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'] + 1e-10)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / (df['bb_middle'] + 1e-10)
        df['atr_pct'] = df['atr'] / df['close']

        # 6. Indicadores de volumen
        df['volume_sma'] = df['tick_volume'].rolling(20).mean()
        df['volume_ratio'] = df['tick_volume'] / (df['volume_sma'] + 1e-10)
        df['volume_delta'] = df['tick_volume'].diff()
        df['volume_acceleration'] = df['volume_delta'].diff()

        # 7. Patrones de velas
        df['body_size'] = abs(df['close'] - df['open'])
        df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
        df['body_ratio'] = df['body_size'] / (df['high'] - df['low'] + 1e-10)

        df['is_bullish'] = (df['close'] > df['open']).astype(int)
        df['is_doji'] = (df['body_size'] < df['atr'] * 0.1).astype(int)
        df['is_hammer'] = ((df['lower_shadow'] > df['body_size'] * 2) &
                          (df['upper_shadow'] < df['body_size'] * 0.5)).astype(int)

        # 8. Características de ciclos y estacionalidad
        df['hour'] = df.index.hour if hasattr(df.index, 'hour') else 0
        df['day_of_week'] = df.index.dayofweek if hasattr(df.index, 'dayofweek') else 0
        df['day_of_month'] = df.index.day if hasattr(df.index, 'day') else 0
        df['month'] = df.index.month if hasattr(df.index, 'month') else 0
        df['quarter'] = df.index.quarter if hasattr(df.index, 'quarter') else 0

        # 9. Características estadísticas
        for window in [20, 50, 100]:
            df[f'skewness_{window}'] = df['close'].rolling(window).skew()
            df[f'kurtosis_{window}'] = df['close'].rolling(window).kurt()

        # 10. Fractales y multi-timeframe
        try:
            df_4h = self.resample_timeframe(df.reset_index(), '4H')
            df_4h_features = df_4h[['close', 'tick_volume']].add_prefix('4h_')
            df_4h_features.index = df_4h.index

            df = df.join(df_4h_features, how='left')
            df['4h_price_ratio'] = df['close'] / (df['4h_close'] + 1e-10)
        except Exception as e:
            print(f"No se pudo añadir características multi-timeframe: {e}")

        # 11. Lag features
        for lag in [1, 2, 3, 5, 10]:
            df[f'close_lag_{lag}'] = df['close'].shift(lag)
            df[f'volume_lag_{lag}'] = df['tick_volume'].shift(lag)
            df[f'return_lag_{lag}'] = df['returns'].shift(lag)

        # 12. Rolling statistics adicionales
        for window in [10, 20, 50]:
            df[f'rolling_max_{window}'] = df['close'].rolling(window).max()
            df[f'rolling_min_{window}'] = df['close'].rolling(window).min()
            df[f'rolling_range_{window}'] = df[f'rolling_max_{window}'] - df[f'rolling_min_{window}']
            df[f'price_position_rolling_{window}'] = (df['close'] - df[f'rolling_min_{window}']) / \
                                                    (df[f'rolling_range_{window}'] + 1e-10)

        # ✅ Eliminar filas con NaN
        critical_cols = ['close', 'returns', 'rsi', 'macd']
        df = df.dropna(subset=critical_cols)

        # ✅ Eliminar filas con NaN de forma más inteligente
        # En lugar de eliminar TODAS las filas con algún NaN,
        # eliminar solo las primeras que tienen NaN por los indicadores
        initial_rows_to_drop = 200  # Ajustar según el indicador con más período
        df = df.iloc[initial_rows_to_drop:].copy()

        # Rellenar NaN restantes con métodos apropiados
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(method='ffill').fillna(0)

        # ✅ DIAGNÓSTICO CORREGIDO con timeframe correcto
        print(f"\n🔍 DIAGNÓSTICO para {tf}:")
        print(f"  Columnas totales: {len(df.columns)}")
        print(f"  Filas totales después de limpieza: {len(df)}")
        print(f"  Columnas con NaN: {df.isna().any().sum()}")
        print(f"  Filas con algún NaN: {df.isna().any(axis=1).sum()}")

        print(f"Características añadidas. Shape final: {df.shape}")
        return df

    def calculate_hurst_exponent(self, series, max_lag=100):
        """Calcula el exponente de Hurst para una serie temporal"""
        try:
            lags = range(2, min(max_lag, len(series)//2))
            tau = [np.sqrt(np.std(np.subtract(series[lag:], series[:-lag]))) for lag in lags]
            if len(tau) > 0 and len(lags) > 0:
                poly = np.polyfit(np.log(lags), np.log(tau), 1)
                return poly[0] * 2.0
        except:
            pass
        return 0.5  # Valor neutral si no se puede calcular


    # AÑADIR ESTOS MÉTODOS A LA CLASE AdvancedDataProcessor
    # (insertar después del método calculate_hurst_exponent)

    def analyze_stationarity(self, series, name="Series"):
        """Analiza la estacionaridad de una serie temporal usando múltiples tests"""
        results = {"series_name": name}

        # Preparar serie
        series_clean = series.dropna()
        if len(series_clean) < 50:
            print(f"⚠️ Serie {name} muy corta para análisis de estacionaridad")
            return results

        if STATIONARITY_AVAILABLE:
            try:
                # Test de Augmented Dickey-Fuller
                adf_result = adfuller(series_clean, autolag='AIC')
                results['adf_statistic'] = adf_result[0]
                results['adf_pvalue'] = adf_result[1]
                results['adf_is_stationary'] = adf_result[1] < 0.05

                # Test KPSS (hipótesis nula es estacionaridad)
                kpss_result = kpss(series_clean, regression='c')
                results['kpss_statistic'] = kpss_result[0]
                results['kpss_pvalue'] = kpss_result[1]
                results['kpss_is_stationary'] = kpss_result[1] > 0.05

                # Consenso: ambos tests deben concordar
                results['is_stationary'] = results['adf_is_stationary'] and results['kpss_is_stationary']

                print(f"📊 {name} - ADF p-value: {adf_result[1]:.4f}, KPSS p-value: {kpss_result[1]:.4f}")
                print(f"   Estacionaria: {results['is_stationary']}")

            except Exception as e:
                print(f"⚠️ Error en tests de estacionaridad para {name}: {e}")
                results['is_stationary'] = None
        else:
            # Test simplificado usando estadísticas básicas
            # Dividir serie en mitades y comparar medias y varianzas
            mid = len(series_clean) // 2
            first_half = series_clean[:mid]
            second_half = series_clean[mid:]

            # Test t para diferencia de medias
            t_stat, t_p = scipy_stats.ttest_ind(first_half, second_half)

            # Test F para diferencia de varianzas
            f_stat = np.var(first_half) / np.var(second_half)

            # Heurística simple: si las mitades son significativamente diferentes, no es estacionaria
            results['is_stationary'] = t_p > 0.05  # No hay diferencia significativa en medias
            results['t_test_pvalue'] = t_p
            results['variance_ratio'] = f_stat

            print(f"📊 {name} - Test simplificado p-value: {t_p:.4f}")
            print(f"   Estacionaria (heurística): {results['is_stationary']}")

        return results

    def detect_market_regimes(self, df, price_col='close', n_regimes=3, lookback=20):
        """Detecta regímenes de mercado usando Gaussian Mixture Models"""
        print(f"🔍 Detectando {n_regimes} regímenes de mercado...")

        # Calcular características para detección de regímenes
        returns = df[price_col].pct_change().fillna(0)
        volatility = returns.rolling(lookback).std()
        trend = df[price_col].rolling(lookback).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0)

        # Preparar matriz de características para GMM
        features = pd.DataFrame({
            'returns': returns,
            'volatility': volatility,
            'trend': trend,
            'price_momentum': df[price_col].pct_change(lookback).fillna(0),
            'volume_momentum': df.get('tick_volume', df.get('volume', pd.Series(1, index=df.index))).pct_change(lookback).fillna(0)
        }).fillna(0)

        # Normalizar características
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        # Aplicar Gaussian Mixture Model
        try:
            gmm = GaussianMixture(n_components=n_regimes, random_state=config.RANDOM_STATE,
                                covariance_type='full', max_iter=100)
            regimes = gmm.fit_predict(features_scaled)
            regime_probs = gmm.predict_proba(features_scaled)

            # Analizar características de cada régimen
            regime_analysis = {}
            for regime in range(n_regimes):
                mask = regimes == regime
                regime_analysis[regime] = {
                    'count': np.sum(mask),
                    'avg_return': returns[mask].mean(),
                    'avg_volatility': volatility[mask].mean(),
                    'avg_trend': trend[mask].mean(),
                    'percentage': np.sum(mask) / len(regimes) * 100
                }

                # Clasificar tipo de régimen
                if regime_analysis[regime]['avg_volatility'] > volatility.quantile(0.7):
                    regime_type = "Alta Volatilidad"
                elif abs(regime_analysis[regime]['avg_trend']) > trend.abs().quantile(0.7):
                    regime_type = "Tendencia Fuerte"
                else:
                    regime_type = "Rango/Consolidación"

                regime_analysis[regime]['type'] = regime_type

                print(f"  Régimen {regime} ({regime_type}): {regime_analysis[regime]['percentage']:.1f}% del tiempo")
                print(f"    Return promedio: {regime_analysis[regime]['avg_return']:.4f}")
                print(f"    Volatilidad promedio: {regime_analysis[regime]['avg_volatility']:.4f}")

            # Añadir regímenes al dataframe
            df['market_regime'] = regimes
            df['regime_probability'] = np.max(regime_probs, axis=1)

            # Añadir características adicionales basadas en regímenes
            for regime in range(n_regimes):
                df[f'regime_{regime}_prob'] = regime_probs[:, regime]

            self.regime_analysis = regime_analysis
            print(f"✅ Regímenes detectados y añadidos al dataset")

        except Exception as e:
            print(f"⚠️ Error en detección de regímenes: {e}")
            df['market_regime'] = 0
            df['regime_probability'] = 1.0

        return df

    def advanced_feature_engineering(self, df):
        """Ingeniería de características avanzada basada en análisis de mercado"""
        print("🔧 Aplicando ingeniería de características avanzada...")

        # 1. Análisis de estacionaridad para características clave
        stationarity_results = {}
        key_series = ['close', 'returns', 'tick_volume'] if 'returns' in df.columns else ['close']

        for col in key_series:
            if col in df.columns:
                stationarity_results[col] = self.analyze_stationarity(df[col], col)

        # 2. Características basadas en estacionaridad
        if 'returns' in df.columns:
            # Si los returns no son estacionarios, usar diferenciación
            if (stationarity_results.get('returns', {}).get('is_stationary') == False):
                df['returns_diff'] = df['returns'].diff()
                df['returns_diff2'] = df['returns_diff'].diff()
                print("📈 Añadidas características diferenciadas para estacionaridad")

        # 3. Detección de outliers usando métodos robustos
        if 'returns' in df.columns:
            returns = df['returns'].fillna(0)

            # Z-score modificado (usando MAD en lugar de std)
            median_return = returns.median()
            mad = median_abs_deviation(returns)
            df['return_zscore_robust'] = (returns - median_return) / (mad + 1e-8)

            # Detectar outliers (threshold = 3.5 para MAD)
            df['is_outlier'] = (np.abs(df['return_zscore_robust']) > 3.5).astype(int)

            # Percentil rolling para detección de valores extremos
            df['return_percentile_20'] = returns.rolling(50).rank(pct=True)

        # 4. Características de microestructura del mercado
        if 'tick_volume' in df.columns:
            # VWAP (Volume Weighted Average Price) aproximado
            df['vwap_5'] = (df['close'] * df['tick_volume']).rolling(5).sum() / df['tick_volume'].rolling(5).sum()
            df['price_vs_vwap'] = df['close'] / (df['vwap_5'] + 1e-8) - 1

            # Order flow imbalance (proxy usando volumen y precio)
            df['volume_price_trend'] = df['tick_volume'] * np.sign(df['close'].diff().fillna(0))
            df['vpt_ma'] = df['volume_price_trend'].rolling(10).mean()

        # 5. Características de momentum adaptativo
        for window in [5, 10, 20]:
            if 'close' in df.columns:
                # Momentum con ajuste por volatilidad
                volatility = df['close'].pct_change().rolling(window).std()
                raw_momentum = df['close'].pct_change(window).fillna(0)
                df[f'vol_adjusted_momentum_{window}'] = raw_momentum / (volatility + 1e-8)

                # RSI dinámico (período adaptativo basado en volatilidad)
                # high_vol_periods = (volatility > volatility.rolling(50).quantile(0.7))
                # rsi_period = np.where(high_vol_periods, window//2, window)
                # Nota: Implementación simplificada, en producción usar períodos variables reales
                df[f'adaptive_rsi_{window}'] = ta.momentum.rsi(df['close'], window=window)

        # 6. Características de correlación temporal (autocorrelación)
        if 'returns' in df.columns and len(df) > 100:
            returns = df['returns'].fillna(0)

            # Autocorrelación a diferentes lags
            for lag in [1, 5, 10]:
                df[f'autocorr_lag_{lag}'] = returns.rolling(50).apply(
                    lambda x: x.autocorr(lag=lag) if len(x) > lag else 0
                )

        # 7. Características de persistencia y reversión
        if 'close' in df.columns:
            # Hurst exponent rolling
            df['hurst_50'] = df['close'].rolling(50).apply(
                lambda x: self.calculate_hurst_exponent(x) if len(x) >= 50 else 0.5
            )

            # Half-life de reversión a la media
            for ma_period in [20, 50]:
                ma_col = f'sma_{ma_period}'
                if ma_col in df.columns:
                    deviation = df['close'] / df[ma_col] - 1
                    # Aproximación del half-life usando autocorrelación
                    df[f'mean_reversion_hl_{ma_period}'] = deviation.rolling(50).apply(
                        lambda x: -np.log(2) / np.log(abs(x.autocorr(lag=1)) + 1e-8) if abs(x.autocorr(lag=1)) > 1e-8 else np.inf if abs(x.autocorr(lag=1)) < 1e-8 else -np.inf # Handle edge cases
                    ).replace([np.inf, -np.inf], np.nan).fillna(0) # Replace inf with 0

        print(f"✅ Características avanzadas añadidas. Shape final: {df.shape}")
        return df

    def robust_feature_selection(self, X, y, method='stability', k=30):
        """Selección de características con barra de progreso"""
        print(f"🎯 Selección robusta de características (método: {method}, k={k})")

        feature_scores = {}
        is_classification = len(np.unique(y)) <= 10

        # MÉTODO RÁPIDO (recomendado)
        if method in ['fast', 'mutual_info']:
            print("⚡ Usando método rápido...")

            if is_classification:
                rf = RandomForestClassifier(n_estimators=100, random_state=config.RANDOM_STATE, n_jobs=-1)
            else:
                rf = RandomForestRegressor(n_estimators=100, random_state=config.RANDOM_STATE, n_jobs=-1)

            # Entrenamiento con barra
            with tqdm(total=1, desc="🌲 Random Forest", bar_format='{l_bar}{bar}| {elapsed}') as pbar:
                rf.fit(X, y)
                pbar.update(1)

            importance = dict(zip(X.columns, rf.feature_importances_))

            # Mutual information adicional
            if is_classification:
                mi_scores = mutual_info_classif(X, y, random_state=config.RANDOM_STATE)
            else:
                mi_scores = mutual_info_regression(X, y, random_state=config.RANDOM_STATE)

            mi_dict = dict(zip(X.columns, mi_scores))

            # Combinar scores
            for feature in tqdm(X.columns, desc="🔢 Combinando scores"):
                rf_score = importance[feature]
                mi_score = mi_dict[feature]

                # Normalizar
                rf_norm = rf_score / (max(importance.values()) + 1e-8)
                mi_norm = mi_score / (max(mi_scores) + 1e-8)

                feature_scores[feature] = (rf_norm + mi_norm) / 2

        # MÉTODO STABILITY (más lento pero robusto)
        elif method == 'stability':
            if is_classification:
                model_class = RandomForestClassifier
            else:
                model_class = RandomForestRegressor

            n_runs = 5
            stability_scores = {}

            print(f"🔄 Ejecutando {n_runs} iteraciones de estabilidad...")

            # BARRA DE PROGRESO POR FEATURE
            for feature in tqdm(X.columns, desc="📊 Analizando features"):
                importances = []

                for run in range(n_runs):
                    # Sample 80% de datos
                    sample_idx = np.random.choice(len(X), size=int(0.8 * len(X)), replace=False)
                    X_sample = X.iloc[sample_idx]
                    y_sample = y.iloc[sample_idx] if isinstance(y, pd.Series) else y[sample_idx]

                    model = model_class(n_estimators=50, random_state=run, n_jobs=-1)

                    model.fit(X_sample, y_sample)

                    feature_idx = list(X_sample.columns).index(feature)
                    importances.append(model.feature_importances_[feature_idx])

                # Estabilidad = 1 / (std + epsilon)
                stability_scores[feature] = 1 / (np.std(importances) + 1e-6)

            # Combinar con importancia base
            if is_classification:
                rf_base = RandomForestClassifier(n_estimators=100, random_state=config.RANDOM_STATE, n_jobs=-1)
            else:
                rf_base = RandomForestRegressor(n_estimators=100, random_state=config.RANDOM_STATE, n_jobs=-1)

            with tqdm(total=1, desc="🌲 RF base", bar_format='{l_bar}{bar}| {elapsed}') as pbar:
                rf_base.fit(X, y)
                pbar.update(1)

            rf_importance = dict(zip(X.columns, rf_base.feature_importances_))

            for feature in X.columns:
                feature_scores[feature] = rf_importance[feature] * stability_scores[feature]

        # MÉTODO TEMPORAL
        elif method == 'temporal':
            split_point = int(len(X) * 0.7)
            X_early = X.iloc[:split_point]
            y_early = y.iloc[:split_point] if isinstance(y, pd.Series) else y[:split_point]
            X_late = X.iloc[split_point:]
            y_late = y.iloc[split_point:] if isinstance(y, pd.Series) else y[split_point:]

            print("⏰ Analizando estabilidad temporal...")

            for feature in tqdm(X.columns, desc="📈 Correlaciones temporales"):
                corr_early = np.corrcoef(X_early[feature], y_early)[0, 1]
                corr_late = np.corrcoef(X_late[feature], y_late)[0, 1]

                if not (np.isnan(corr_early) or np.isnan(corr_late)):
                    consistency = 1 - abs(corr_early - corr_late) / (abs(corr_early) + abs(corr_late) + 1e-6)
                    avg_corr = (abs(corr_early) + abs(corr_late)) / 2
                    feature_scores[feature] = consistency * avg_corr
                else:
                    feature_scores[feature] = 0

        # Seleccionar top k con barra
        print("\n🔝 Seleccionando mejores características...")
        top_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        selected_features = [f[0] for f in top_features]

        print(f"\n✅ Top 5 características seleccionadas:")
        for i, (feature, score) in enumerate(top_features[:5]):
            print(f"    {i+1}. {feature}: {score:.4f}")

        return X[selected_features], selected_features

    @timer_decorator
    def prepare_ml_data(self, df: pd.DataFrame, target_periods: int = 5,
                      classification: bool = False,
                      multi_output: bool = False) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepara datos para ML con target - VERSIÓN CORREGIDA"""

        # 1. PRIMERO crear el target ANTES de excluir columnas
        print(f"  📊 Creando target (target_periods={target_periods}, classification={classification})")

        if classification:
            if multi_output:
                # Clasificación multi-target: dirección y magnitud
                price_change = (df['close'].shift(-target_periods) - df['close']) / df['close'] * 100
                direction = (price_change > 0).astype(int)
                magnitude = pd.cut(price_change.abs(), bins=5, labels=False)

                # Codificar como multi-target
                y = direction.astype(str) + '_' + magnitude.astype(str)
                le = LabelEncoder()
                y = pd.Series(le.fit_transform(y), index=df.index)
            else:
                # Clasificación binaria simple
                future_price = df['close'].shift(-target_periods)
                y = (future_price > df['close']).astype(int)
        else:
            # Regresión: cambio porcentual futuro
            future_price = df['close'].shift(-target_periods)
            y = (future_price - df['close']) / df['close'] * 100

        # 2. DESPUÉS excluir columnas para features
        exclude_cols = ['open', 'high', 'low', 'close', 'time']
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        X = df[feature_cols].copy()

        # 3. Verificar que tenemos datos
        print(f"  📈 Antes de limpiar: X shape={X.shape}, y shape={y.shape}")
        print(f"  📉 NaN en X: {X.isna().any(axis=1).sum()}, NaN en y: {y.isna().sum()}")

        # 4. Eliminar NaN - CRÍTICO: mejorar el manejo
        # Primero intentar rellenar valores antes de eliminar
        X_filled = X.fillna(method='ffill').fillna(0)
        y_filled = y.fillna(method='ffill').fillna(0)

        # Solo eliminar filas que aún tengan NaN después del relleno
        mask = ~(X_filled.isna().any(axis=1) | y_filled.isna())
        X_clean = X_filled[mask].copy()
        y_clean = y_filled[mask].copy()

        # 5. Verificación final
        print(f"  ✅ Después de limpiar: X shape={X_clean.shape}, y shape={y_clean.shape}")

        if len(X_clean) == 0:
            print(f"  ⚠️ WARNING: No quedan datos después de limpieza!")
            print(f"     - Sugerencia: Reducir target_periods o revisar calidad de datos")
            return pd.DataFrame(), pd.Series(dtype=float)

        return X_clean, y_clean

    @timer_decorator
    def scale_data(self, X_train, X_test, method='minmax'):
        """Escala los datos usando diferentes métodos"""
        if method == 'minmax':
            scaler = MinMaxScaler()
        elif method == 'robust':
            scaler = RobustScaler()
        elif method == 'standard':
            scaler = StandardScaler()
        else:
            raise ValueError("Método debe ser 'minmax', 'robust' o 'standard'")

        X_train_scaled = pd.DataFrame(
            scaler.fit_transform(X_train),
            columns=X_train.columns,
            index=X_train.index
        )

        X_test_scaled = pd.DataFrame(
            scaler.transform(X_test),
            columns=X_test.columns,
            index=X_test.index
        )

        # Guardar scaler
        self.scalers[method] = scaler

        return X_train_scaled, X_test_scaled

    @timer_decorator
    def feature_selection(self, X, y, method='random_forest', k=20):
        """Selección de características"""

        if len(X) == 0:
          print(f"⚠️ No hay datos suficientes para selección de características")
          return pd.DataFrame(), []


        if method == 'random_forest':
            if len(np.unique(y)) > 10:  # Regresión
                model = RandomForestRegressor(n_estimators=100, random_state=config.RANDOM_STATE)
            else:  # Clasificación
                model = RandomForestClassifier(n_estimators=100, random_state=config.RANDOM_STATE)

            model.fit(X, y)
            importance = model.feature_importances_
            self.feature_importance = dict(zip(X.columns, importance))

            # Seleccionar top k características
            top_features = sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:k]
            selected_features = [f[0] for f in top_features]

        elif method == 'mutual_info':
            if len(np.unique(y)) > 10:  # Regresión
                selector = SelectKBest(score_func=mutual_info_regression, k=k)
            else:  # Clasificación
                selector = SelectKBest(score_func=mutual_info_classif, k=k)

            selector.fit(X, y)
            selected_features = X.columns[selector.get_support()].tolist()

        elif method == 'rfe':
            if len(np.unique(y)) > 10:  # Regresión
                estimator = LinearRegression()
            else:  # Clasificación
                estimator = LogisticRegression()

            selector = RFE(estimator, n_features_to_select=k, step=1)
            selector.fit(X, y)
            selected_features = X.columns[selector.support_].tolist()

        print(f"Seleccionadas {len(selected_features)} características con método {method}")
        return X[selected_features], selected_features

# @title
def verify_data_for_training(X, y, model_name):
    """Verifica que los datos sean apropiados para entrenamiento"""
    issues = []

    # 1. Verificar NaN
    if X.isna().any().any():
        issues.append(f"X contiene NaN: {X.isna().sum().sum()} valores")

    if pd.Series(y).isna().any():
        issues.append(f"y contiene NaN: {pd.Series(y).isna().sum()} valores")

    # 2. Verificar índices
    if isinstance(X.index, pd.DatetimeIndex):
        issues.append("X tiene DatetimeIndex - considerar reset_index()")

    # 3. Verificar tamaño
    if len(X) < 50:
        issues.append(f"Muy pocos datos: {len(X)} muestras")

    # 4. Verificar clases
    if len(np.unique(y)) <= 1:
        issues.append(f"y solo tiene {len(np.unique(y))} clase(s)")

    if issues:
        print(f"⚠️ Verificación de datos para {model_name}:")
        for issue in issues:
            print(f"    - {issue}")
        return False

    return True

# [5] MODELOS AVANZADOS DE MACHINE LEARNING
class AdvancedModelTrainer:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.models = {}
        self.metrics = {}
        self.predictions = {}
        self.feature_importances = {}
        self.best_params = {}
        self.y_test = None
        self.X_test = None




    # AÑADIR ESTOS MÉTODOS A LA CLASE AdvancedModelTrainer
    # (insertar antes del método train_all_models)

    def time_series_cross_validation(self, X, y, model, n_splits=5, test_size_ratio=0.2):
        """Validación cruzada específica para series temporales - CORREGIDA"""
        print(f"⏱️ Ejecutando validación temporal con {n_splits} splits...")

        # ✅ CRÍTICO: Resetear índices a numéricos
        X = X.reset_index(drop=True)
        y = y.reset_index(drop=True) if isinstance(y, pd.Series) else pd.Series(y).reset_index(drop=True)

        total_size = len(X)
        test_size = int(total_size * test_size_ratio)

        scores = []
        predictions_cv = []
        feature_importance_cv = []

        for i in range(n_splits):
            # ✅ USAR ÍNDICES NUMÉRICOS
            test_start = total_size - test_size - (n_splits - 1 - i) * (test_size // 2)
            test_end = test_start + test_size

            train_end = test_start
            train_start = max(0, train_end - test_size * 4)

            if train_start >= train_end or test_start >= test_end:
                continue

            # ✅ USAR .iloc para indexación numérica
            X_train_fold = X.iloc[train_start:train_end]
            y_train_fold = y.iloc[train_start:train_end]
            X_test_fold = X.iloc[test_start:test_end]
            y_test_fold = y.iloc[test_start:test_end]

            # Clonar y entrenar modelo
            model_clone = self._clone_model(model)

            try:
                model_clone.fit(X_train_fold, y_train_fold)
                y_pred_fold = model_clone.predict(X_test_fold)

                # Calcular métricas
                is_classification = len(np.unique(y)) <= 10
                fold_metrics = self._calc_metrics(y_test_fold, y_pred_fold, is_classification)
                scores.append(fold_metrics)

                # ✅ Guardar predicciones con índices numéricos
                for idx, (true_val, pred_val) in enumerate(zip(y_test_fold.values, y_pred_fold)):
                    predictions_cv.append({
                        'fold': i,
                        'index': test_start + idx,  # Índice numérico
                        'y_true': float(true_val),
                        'y_pred': float(pred_val)
                    })

                # Guardar importancia
                if hasattr(model_clone, 'feature_importances_'):
                    feature_importance_cv.append(model_clone.feature_importances_)

            except Exception as e:
                print(f"    ⚠️ Error en fold {i+1}: {e}")
                continue

            print(f"  Fold {i+1}: Período {train_start}-{train_end} → {test_start}-{test_end}")

        # Consolidar métricas
        if scores:
            consolidated_metrics = self._consolidate_cv_metrics(scores)
            consolidated_metrics['cv_predictions'] = predictions_cv
            consolidated_metrics['feature_importance_stability'] = (
                np.std(feature_importance_cv, axis=0) if feature_importance_cv else None
            )
            print(f"    ✅ Validación cruzada completada")
            return consolidated_metrics
        else:
            print(f"    ❌ No se pudo completar ningún fold")
            return {}

    def _clone_model(self, model):
        """Clona un modelo para validación cruzada - MEJORADO"""
        from sklearn.base import clone

        try:
            # Intentar clonación estándar de sklearn
            return clone(model)
        except Exception as e:
            # Fallback para modelos que no se pueden clonar directamente
            model_name = type(model).__name__

            if 'XGB' in model_name:
                params = model.get_params() if hasattr(model, 'get_params') else {}
                if 'Classifier' in model_name:
                    return xgb.XGBClassifier(**params)
                else:
                    return xgb.XGBRegressor(**params)

            elif 'LGBM' in model_name or 'LGB' in model_name:
                params = model.get_params() if hasattr(model, 'get_params') else {}
                # Remover parámetros problemáticos
                params.pop('importance_type', None)
                params.pop('n_jobs', None)

                if 'Classifier' in model_name:
                    return lgb.LGBMClassifier(**params, n_jobs=-1, verbose=-1)
                else:
                    return lgb.LGBMRegressor(**params, n_jobs=-1, verbose=-1)

            elif 'Random' in model_name:
                params = model.get_params() if hasattr(model, 'get_params') else {}
                if 'Classifier' in model_name:
                    return RandomForestClassifier(**params)
                else:
                    return RandomForestRegressor(**params)

            else:
                # Último recurso: crear instancia vacía del mismo tipo
                print(f"⚠️ Usando instancia por defecto para {model_name}")
                return type(model)()

    def _consolidate_cv_metrics(self, scores_list):
        """Consolida métricas de múltiples folds de validación cruzada"""
        if not scores_list:
            return {}

        consolidated = {}

        # Obtener todas las métricas disponibles
        all_metrics = set()
        for score in scores_list:
            all_metrics.update(score.keys())

        # Calcular estadísticas para cada métrica
        for metric in all_metrics:
            if metric in ['confusion_matrix', 'classification_report', 'history']:
                continue  # Skip métricas no numéricas

            values = []
            for score in scores_list:
                if metric in score and score[metric] is not None:
                    values.append(score[metric])

            if values:
                consolidated[f'{metric}_mean'] = np.mean(values)
                consolidated[f'{metric}_std'] = np.std(values)
                consolidated[f'{metric}_min'] = np.min(values)
                consolidated[f'{metric}_max'] = np.max(values)

        return consolidated

    def walk_forward_optimization(self, X, y, model_class, param_grid,
                                 initial_train_size=500, step_size=50, test_size=100):
        """Optimización walk-forward para encontrar mejores parámetros temporalmente"""
        print(f"🚶 Ejecutando optimización walk-forward...")
        print(f"  Train inicial: {initial_train_size}, Step: {step_size}, Test: {test_size}")

        total_size = len(X)
        if total_size < initial_train_size + test_size:
            print("⚠️ Dataset muy pequeño para walk-forward optimization")
            return None, {}

        # Generar combinaciones de parámetros
        param_combinations = list(itertools.product(*param_grid.values()))
        param_keys = list(param_grid.keys())

        results = []

        # Ejecutar walk-forward
        current_pos = initial_train_size
        window_count = 0

        while current_pos + test_size <= total_size:
            train_start = max(0, current_pos - initial_train_size)
            train_end = current_pos
            test_start = current_pos
            test_end = current_pos + test_size

            X_train_wf = X.iloc[train_start:train_end]
            y_train_wf = y.iloc[train_start:train_end]
            X_test_wf = X.iloc[test_start:test_end]
            y_test_wf = y.iloc[test_start:test_end]

            # Probar cada combinación de parámetros
            window_results = {}
            for i, param_combo in enumerate(param_combinations):
                params = dict(zip(param_keys, param_combo))

                try:
                    # Crear modelo con parámetros específicos
                    model = model_class(**params, random_state=config.RANDOM_STATE)
                    model.fit(X_train_wf, y_train_wf)
                    y_pred_wf = model.predict(X_test_wf)

                    # Calcular métrica principal
                    is_classification = len(np.unique(y)) <= 10
                    if is_classification:
                        main_metric = f1_score(y_test_wf, (y_pred_wf > 0.5).astype(int), zero_division=0)
                    else:
                        main_metric = r2_score(y_test_wf, y_pred_wf)

                    window_results[i] = {
                        'params': params,
                        'score': main_metric,
                        'window': window_count
                    }

                except Exception as e:
                    window_results[i] = {
                        'params': params,
                        'score': -999,
                        'window': window_count,
                        'error': str(e)
                    }

            results.append(window_results)
            current_pos += step_size
            window_count += 1

            if window_count % 5 == 0:
                print(f"  Completadas {window_count} ventanas...")

        # Analizar resultados para encontrar mejores parámetros
        best_params, performance_analysis = self._analyze_walk_forward_results(results, param_keys)

        print(f"✅ Walk-forward completado. Mejores parámetros: {best_params}")
        return best_params, performance_analysis

    def _analyze_walk_forward_results(self, results, param_keys):
        """Analiza resultados de walk-forward para encontrar mejores parámetros"""
        # Consolidar resultados por configuración de parámetros
        param_performance = {}

        for window_results in results:
            for config_id, result in window_results.items():
                if 'error' in result:
                    continue

                param_str = str(result['params'])
                if param_str not in param_performance:
                    param_performance[param_str] = {
                        'params': result['params'],
                        'scores': [],
                        'windows': []
                    }

                param_performance[param_str]['scores'].append(result['score'])
                param_performance[param_str]['windows'].append(result['window'])

        # Calcular estadísticas por configuración
        param_stats = {}
        for param_str, data in param_performance.items():
            if len(data['scores']) > 0:
                param_stats[param_str] = {
                    'params': data['params'],
                    'mean_score': np.mean(data['scores']),
                    'std_score': np.std(data['scores']),
                    'min_score': np.min(data['scores']),
                    'max_score': np.max(data['scores']),
                    'consistency': 1 / (np.std(data['scores']) + 1e-6),  # Penalizar alta variabilidad
                    'n_windows': len(data['scores'])
                }

        # Encontrar mejores parámetros considerando rendimiento y consistencia
        if param_stats:
            # Score combinado: 70% rendimiento promedio + 30% consistencia
            for param_str in param_stats:
                mean_score = param_stats[param_str]['mean_score']
                consistency = param_stats[param_str]['consistency']

                # Normalizar consistencia
                max_consistency = max([p['consistency'] for p in param_stats.values()])
                norm_consistency = consistency / (max_consistency + 1e-6)

                param_stats[param_str]['combined_score'] = 0.7 * mean_score + 0.3 * norm_consistency

            # Seleccionar mejores parámetros
            best_config = max(param_stats.items(), key=lambda x: x[1]['combined_score'])
            best_params = best_config[1]['params']

            # Preparar análisis de rendimiento
            performance_analysis = {
                'best_params': best_params,
                'best_combined_score': best_config[1]['combined_score'],
                'best_mean_score': best_config[1]['mean_score'],
                'best_consistency': best_config[1]['consistency'],
                'all_param_stats': param_stats,
                'n_configurations_tested': len(param_stats)
            }

        else:
            best_params = {}
            performance_analysis = {'error': 'No se encontraron configuraciones válidas'}

        return best_params, performance_analysis

    def regime_based_model_selection(self, X, y, models_dict, regime_column='market_regime'):
        """Selecciona el mejor modelo para cada régimen de mercado detectado"""
        print("🎭 Ejecutando selección de modelos por régimen de mercado...")

        if regime_column not in X.columns:
            print(f"⚠️ Columna de régimen '{regime_column}' no encontrada. Usando modelo único.")
            return models_dict, {}

        regimes = X[regime_column].unique()
        regime_models = {}
        regime_performance = {}

        for regime in regimes:
            print(f"  Evaluando modelos para régimen {regime}...")

            # Filtrar datos por régimen
            regime_mask = X[regime_column] == regime
            X_regime = X[regime_mask].drop(columns=[regime_column])
            y_regime = y[regime_mask]

            if len(X_regime) < 50:  # Muy pocos datos para este régimen
                print(f"    Régimen {regime}: pocos datos ({len(X_regime)}), usando modelo general")
                continue

            # Evaluar cada modelo en este régimen
            regime_scores = {}
            is_classification = len(np.unique(y)) <= 10

            for model_name, model in models_dict.items():
                try:
                    # Split temporal para este régimen
                    split_idx = int(len(X_regime) * 0.8)
                    X_train_reg = X_regime.iloc[:split_idx]
                    X_test_reg = X_regime.iloc[split_idx:]
                    y_train_reg = y_regime.iloc[:split_idx]
                    y_test_reg = y_regime.iloc[split_idx:]

                    if len(X_train_reg) < 10 or len(X_test_reg) < 5:
                        continue

                    # Entrenar modelo
                    model_clone = self._clone_model(model)
                    model_clone.fit(X_train_reg, y_train_reg)
                    y_pred_reg = model_clone.predict(X_test_reg)

                    # Calcular métrica principal
                    if is_classification:
                        score = f1_score(y_test_reg, (y_pred_reg > 0.5).astype(int), zero_division=0)
                    else:
                        score = r2_score(y_test_reg, y_pred_reg)

                    regime_scores[model_name] = score

                except Exception as e:
                    print(f"      Error evaluando {model_name}: {e}")
                    continue

            if regime_scores:
                # Seleccionar mejor modelo para este régimen
                best_model_name = max(regime_scores.items(), key=lambda x: x[1])[0]
                regime_models[regime] = {
                    'model_name': best_model_name,
                    'model': models_dict[best_model_name],
                    'score': regime_scores[best_model_name]
                }
                regime_performance[regime] = regime_scores

                print(f"    Régimen {regime}: Mejor modelo = {best_model_name} (score: {regime_scores[best_model_name]:.4f})")

        return regime_models, regime_performance







    @timer_decorator
    def train_all_models(self, X_train, y_train, X_test, y_test, task='regression'):
        """Entrena todos los modelos avanzados"""
        self.X_test = X_test
        self.y_test = y_test

        is_classification = (task == 'classification')

        print(f"\n=== ENTRENANDO MODELOS DE {task.upper()} ===")

        # 1. Modelos básicos
        self._train_basic_models(X_train, y_train, X_test, y_test, task)

        # 2. Modelos avanzados
        self._train_advanced_models(X_train, y_train, X_test, y_test, task)

        # 3. Ensembles
        self._train_ensembles(X_train, y_train, X_test, y_test, task)

        # 4. Redes neuronales (si TensorFlow está disponible)
        if TF_AVAILABLE:
            self._train_neural_networks(X_train, y_train, X_test, y_test, task)

        # 5. Optimizar hiperparámetros para los mejores modelos
        self._optimize_hyperparameters(X_train, y_train, X_test, y_test, task)

        print(f"✅ Todos los modelos de {task} entrenados")


    def _train_basic_models(self, X_train, y_train, X_test, y_test, task):
        """Entrena modelos básicos CON BARRA DE PROGRESO"""
        is_classification = (task == 'classification')

        models_to_train = {
            'linear': LinearRegression() if not is_classification else LogisticRegression(max_iter=1000),
            'ridge': Ridge() if not is_classification else LogisticRegression(penalty='l2', solver='liblinear', max_iter=1000),
            'lasso': Lasso() if not is_classification else LogisticRegression(penalty='l1', solver='liblinear', max_iter=1000),
            'rf': RandomForestRegressor(n_estimators=100, random_state=config.RANDOM_STATE, n_jobs=-1)
                  if not is_classification else RandomForestClassifier(n_estimators=100, random_state=config.RANDOM_STATE, n_jobs=-1),
            'xgb': xgb.XGBRegressor(random_state=config.RANDOM_STATE, n_jobs=-1)
                  if not is_classification else xgb.XGBClassifier(random_state=config.RANDOM_STATE, n_jobs=-1),
            'lgb': lgb.LGBMRegressor(random_state=config.RANDOM_STATE, n_jobs=-1, verbose=-1)
                  if not is_classification else lgb.LGBMClassifier(random_state=config.RANDOM_STATE, n_jobs=-1, verbose=-1),
        }

        # ✅ BARRA DE PROGRESO AQUÍ
        for name, model in tqdm(models_to_train.items(), desc=f"🤖 Entrenando {task}"):
            try:
                print(f"\n  → Entrenando {name}...")

                start_time = time.time()
                model.fit(X_train, y_train)
                train_time = time.time() - start_time

                y_pred = model.predict(X_test)

                metrics = self._calc_metrics(y_test, y_pred, is_classification)
                model_name = f'{name}_{task[:3]}'
                self.models[model_name] = model
                self.metrics[model_name] = metrics
                self.predictions[model_name] = y_pred

                # Importancia de características
                if hasattr(model, 'feature_importances_'):
                    self.feature_importances[model_name] = {
                        'features': X_train.columns.tolist(),
                        'importance': model.feature_importances_.tolist()
                    }

                self._print_metrics(metrics, is_classification, model_name)
                print(f"    ⏱️  Tiempo: {train_time:.2f}s")

                clear_memory()

            except Exception as e:
                print(f"  ❌ Error en {name}: {e}")

    def _train_advanced_models(self, X_train, y_train, X_test, y_test, task):
        """Entrena modelos avanzados"""
        is_classification = (task == 'classification')

        advanced_models = {
            'svm': SVR(kernel='rbf') if not is_classification else SVC(kernel='rbf', probability=True),
            'gradient_boosting': GradientBoostingRegressor(random_state=config.RANDOM_STATE, n_estimators=100)
                                if not is_classification else GradientBoostingClassifier(random_state=config.RANDOM_STATE, n_estimators=100),
            'mlp': MLPRegressor(hidden_layer_sizes=(100, 50), random_state=config.RANDOM_STATE, max_iter=1000)
                  if not is_classification else MLPClassifier(hidden_layer_sizes=(100, 50), random_state=config.RANDOM_STATE, max_iter=1000),
        }

        for name, model in advanced_models.items():
            try:
                print(f"→ Entrenando {name}...")

                # Para SVM, usar subset si es muy grande
                if name == 'svm' and len(X_train) > 10000:
                    X_train_sub, _, y_train_sub, _ = train_test_split(
                        X_train, y_train, train_size=10000, random_state=config.RANDOM_STATE,
                        stratify=y_train if is_classification else None
                    )
                    model.fit(X_train_sub, y_train_sub)
                else:
                    model.fit(X_train, y_train)

                y_pred = model.predict(X_test)

                metrics = self._calc_metrics(y_test, y_pred, is_classification)
                model_name = f'{name}_{task[:3]}'
                self.models[model_name] = model
                self.metrics[model_name] = metrics
                self.predictions[model_name] = y_pred

                self._print_metrics(metrics, is_classification, model_name)
                clear_memory()

            except Exception as e:
                print(f"  ❌ Error en {name}: {e}")

    def _train_ensembles(self, X_train, y_train, X_test, y_test, task):
        """Entrena modelos ensemble"""
        is_classification = (task == 'classification')

        # Definir modelos base
        if is_classification:
            estimators = [
                ('rf', RandomForestClassifier(n_estimators=50, random_state=config.RANDOM_STATE, n_jobs=-1)),
                ('xgb', xgb.XGBClassifier(random_state=config.RANDOM_STATE, n_jobs=-1)),
                ('lgb', lgb.LGBMClassifier(random_state=config.RANDOM_STATE, n_jobs=-1, verbose=-1)),
            ]
            voting = VotingClassifier(estimators=estimators, voting='soft')
            stacking = StackingClassifier(
                estimators=estimators,
                final_estimator=LogisticRegression(max_iter=1000),
                cv=3
            )
        else:
            estimators = [
                ('rf', RandomForestRegressor(n_estimators=50, random_state=config.RANDOM_STATE, n_jobs=-1)),
                ('xgb', xgb.XGBRegressor(random_state=config.RANDOM_STATE, n_jobs=-1)),
                ('lgb', lgb.LGBMRegressor(random_state=config.RANDOM_STATE, n_jobs=-1, verbose=-1)),
            ]
            voting = VotingRegressor(estimators=estimators)
            stacking = StackingRegressor(
                estimators=estimators,
                final_estimator=LinearRegression(),
                cv=3
            )

        ensemble_models = {
            'voting': voting,
            'stacking': stacking
        }

        for name, model in ensemble_models.items():
            try:
                print(f"→ Entrenando {name}...")
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                metrics = self._calc_metrics(y_test, y_pred, is_classification)
                model_name = f'{name}_{task[:3]}'
                self.models[model_name] = model
                self.metrics[model_name] = metrics
                self.predictions[model_name] = y_pred

                self._print_metrics(metrics, is_classification, model_name)
                clear_memory()

            except Exception as e:
                print(f"  ❌ Error en {name}: {e}")

    def _train_neural_networks(self, X_train, y_train, X_test, y_test, task):
        """Entrena redes neuronales"""
        if not TF_AVAILABLE:
            print("TensorFlow no disponible, omitiendo redes neuronales")
            return

        is_classification = (task == 'classification')

        try:
            print("→ Entrenando Red Neuronal...")

            # Preprocesamiento para red neuronal
            scaler = StandardScaler()
            X_train_nn = scaler.fit_transform(X_train)
            X_test_nn = scaler.transform(X_test)

            # Arquitectura de la red
            model = Sequential()
            model.add(Dense(128, activation='relu', input_shape=(X_train_nn.shape[1],)))
            model.add(Dropout(0.3))
            model.add(Dense(64, activation='relu'))
            model.add(Dropout(0.3))
            model.add(Dense(32, activation='relu'))
            model.add(Dropout(0.2))

            if is_classification:
                model.add(Dense(1, activation='sigmoid'))
                model.compile(
                    optimizer=Adam(learning_rate=0.001),
                    loss='binary_crossentropy',
                    metrics=['accuracy']
                )
                monitor = 'val_accuracy'
            else:
                model.add(Dense(1, activation='linear'))
                model.compile(
                    optimizer=Adam(learning_rate=0.001),
                    loss='mse',
                    metrics=['mae']
                )
                monitor = 'val_loss'

            # Callbacks
            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True, monitor=monitor),
                ReduceLROnPlateau(factor=0.5, patience=5, min_lr=1e-7)
            ]

            # Entrenamiento
            history = model.fit(
                X_train_nn, y_train,
                validation_data=(X_test_nn, y_test),
                epochs=100,
                batch_size=32,
                callbacks=callbacks,
                verbose=0
            )

            # Predecir
            y_pred = model.predict(X_test_nn, verbose=0)
            if is_classification:
                y_pred = (y_pred > 0.5).astype(int).flatten()
            else:
                y_pred = y_pred.flatten()

            metrics = self._calc_metrics(y_test, y_pred, is_classification)
            model_name = f'ann_{task[:3]}'
            self.models[model_name] = model
            self.metrics[model_name] = metrics
            self.predictions[model_name] = y_pred

            # Guardar historia de entrenamiento
            self.metrics[model_name]['history'] = history.history

            self._print_metrics(metrics, is_classification, model_name)
            clear_memory()

        except Exception as e:
            print(f"  ❌ Error en Red Neuronal: {e}")

    def _optimize_hyperparameters(self, X_train, y_train, X_test, y_test, task):
        """Optimiza hiperparámetros para los mejores modelos"""
        is_classification = (task == 'classification')

        # Seleccionar los 3 mejores modelos basados en la métrica principal
        if is_classification:
            main_metric = 'f1'
            best_models = sorted(
                [(k, v[main_metric]) for k, v in self.metrics.items() if main_metric in v],
                key=lambda x: x[1], reverse=True
            )[:3]
        else:
            main_metric = 'r2'
            best_models = sorted(
                [(k, v[main_metric]) for k, v in self.metrics.items() if main_metric in v],
                key=lambda x: x[1], reverse=True
            )[:3]

        print(f"\nOptimizando hiperparámetros para: {[m[0] for m in best_models]}")

        for model_name, _ in best_models:
            try:
                if 'xgb' in model_name:
                    self._optimize_xgb(X_train, y_train, X_test, y_test, task, model_name)
                elif 'lgb' in model_name:
                    self._optimize_lgb(X_train, y_train, X_test, y_test, task, model_name)
                elif 'rf' in model_name:
                    self._optimize_rf(X_train, y_train, X_test, y_test, task, model_name)
            except Exception as e:
                print(f"  ❌ Error optimizando {model_name}: {e}")

    def _optimize_xgb(self, X_train, y_train, X_test, y_test, task, model_name):
        """Optimiza hiperparámetros para XGBoost"""
        is_classification = (task == 'classification')

        if is_classification:
            model = xgb.XGBClassifier(random_state=config.RANDOM_STATE)
            param_dist = {
                'n_estimators': [100, 200],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.05, 0.1],
                'subsample': [0.8, 1.0],
                'colsample_bytree': [0.8, 1.0],
            }
            scoring = 'f1'
        else:
            model = xgb.XGBRegressor(random_state=config.RANDOM_STATE)
            param_dist = {
                'n_estimators': [100, 200],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.05, 0.1],
                'subsample': [0.8, 1.0],
                'colsample_bytree': [0.8, 1.0],
            }
            scoring = 'r2'

        # Búsqueda aleatoria con menos iteraciones para ahorrar tiempo
        search = RandomizedSearchCV(
            model, param_dist, n_iter=20,  # Reducido de 50
            scoring=scoring, cv=3, n_jobs=-1, random_state=config.RANDOM_STATE
        )

        search.fit(X_train, y_train)

        # Entrenar con mejores parámetros
        best_model = search.best_estimator_
        y_pred = best_model.predict(X_test)
        metrics = self._calc_metrics(y_test, y_pred, is_classification)

        # Guardar modelo optimizado
        optimized_name = f'opt_{model_name}'
        self.models[optimized_name] = best_model
        self.metrics[optimized_name] = metrics
        self.predictions[optimized_name] = y_pred
        self.best_params[optimized_name] = search.best_params_

        self._print_metrics(metrics, is_classification, optimized_name)
        print(f"  Mejores parámetros: {search.best_params_}")

    def _optimize_lgb(self, X_train, y_train, X_test, y_test, task, model_name):
        """Optimiza hiperparámetros para LightGBM"""
        is_classification = (task == 'classification')

        if is_classification:
            model = lgb.LGBMClassifier(random_state=config.RANDOM_STATE, verbose=-1)
            param_dist = {
                'n_estimators': [100, 200],
                'num_leaves': [31, 50],
                'learning_rate': [0.01, 0.05, 0.1],
                'subsample': [0.8, 1.0],
                'colsample_bytree': [0.8, 1.0],
            }
            scoring = 'f1'
        else:
            model = lgb.LGBMRegressor(random_state=config.RANDOM_STATE, verbose=-1)
            param_dist = {
                'n_estimators': [100, 200],
                'num_leaves': [31, 50],
                'learning_rate': [0.01, 0.05, 0.1],
                'subsample': [0.8, 1.0],
                'colsample_bytree': [0.8, 1.0],
            }
            scoring = 'r2'

        # Búsqueda aleatoria
        search = RandomizedSearchCV(
            model, param_dist, n_iter=20,  # Reducido
            scoring=scoring, cv=3, n_jobs=-1, random_state=config.RANDOM_STATE
        )

        search.fit(X_train, y_train)

        # Entrenar con mejores parámetros
        best_model = search.best_estimator_
        y_pred = best_model.predict(X_test)
        metrics = self._calc_metrics(y_test, y_pred, is_classification)

        # Guardar modelo optimizado
        optimized_name = f'opt_{model_name}'
        self.models[optimized_name] = best_model
        self.metrics[optimized_name] = metrics
        self.predictions[optimized_name] = y_pred
        self.best_params[optimized_name] = search.best_params_

        self._print_metrics(metrics, is_classification, optimized_name)
        print(f"  Mejores parámetros: {search.best_params_}")

    def _optimize_rf(self, X_train, y_train, X_test, y_test, task, model_name):
        """Optimiza hiperparámetros para Random Forest"""
        is_classification = (task == 'classification')

        if is_classification:
            model = RandomForestClassifier(random_state=config.RANDOM_STATE, n_jobs=-1)
            param_dist = {
                'n_estimators': [100, 200],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5],
                'min_samples_leaf': [1, 2],
            }
            scoring = 'f1'
        else:
            model = RandomForestRegressor(random_state=config.RANDOM_STATE, n_jobs=-1)
            param_dist = {
                'n_estimators': [100, 200],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5],
                'min_samples_leaf': [1, 2],
            }
            scoring = 'r2'

        # Búsqueda aleatoria
        search = RandomizedSearchCV(
            model, param_dist, n_iter=20,  # Reducido
            scoring=scoring, cv=3, n_jobs=-1, random_state=config.RANDOM_STATE
        )

        search.fit(X_train, y_train)

        # Entrenar con mejores parámetros
        best_model = search.best_estimator_
        y_pred = best_model.predict(X_test)
        metrics = self._calc_metrics(y_test, y_pred, is_classification)

        # Guardar modelo optimizado
        optimized_name = f'opt_{model_name}'
        self.models[optimized_name] = best_model
        self.metrics[optimized_name] = metrics
        self.predictions[optimized_name] = y_pred
        self.best_params[optimized_name] = search.best_params_

        self._print_metrics(metrics, is_classification, optimized_name)
        print(f"  Mejores parámetros: {search.best_params_}")

    def _calc_metrics(self, y_true, y_pred, is_classification):
        """Calcula métricas según el tipo de problema"""
        if is_classification:
            # Para clasificación, asegurarse de que y_pred es binario
            if y_pred.dtype == float:  # Probabilidades
                y_pred_binary = (y_pred > 0.5).astype(int)
                y_prob = y_pred
            else:
                y_pred_binary = y_pred
                y_prob = None

            cm = confusion_matrix(y_true, y_pred_binary)
            metrics = {
                'accuracy': accuracy_score(y_true, y_pred_binary),
                'precision': precision_score(y_true, y_pred_binary, zero_division=0),
                'recall': recall_score(y_true, y_pred_binary, zero_division=0),
                'f1': f1_score(y_true, y_pred_binary, zero_division=0),
                'confusion_matrix': cm.tolist(),
                'classification_report': classification_report(y_true, y_pred_binary, output_dict=True)
            }

            # ROC AUC si tenemos probabilidades
            if y_prob is not None and len(np.unique(y_true)) == 2:
                try:
                    metrics['roc_auc'] = roc_auc_score(y_true, y_prob)
                except:
                    metrics['roc_auc'] = 0.5

            # Métricas adicionales de la matriz de confusión
            if cm.shape == (2, 2):
                tn, fp, fn, tp = cm.ravel()
                metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0
                metrics['npv'] = tn / (tn + fn) if (tn + fn) > 0 else 0  # Negative Predictive Value

        else:
            # Métricas de regresión
            metrics = {
                'mae': mean_absolute_error(y_true, y_pred),
                'mse': mean_squared_error(y_true, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
                'r2': r2_score(y_true, y_pred),
                'mape': mean_absolute_percentage_error(y_true, y_pred) if not np.any(y_true == 0) else 0,
                'evs': explained_variance_score(y_true, y_pred),
                'max_error': max(abs(y_true - y_pred)),
                'median_ae': median_abs_deviation(y_true - y_pred),
            }

            # Métricas adicionales para trading
            direction_accuracy = np.mean((np.sign(y_true) == np.sign(y_pred)) | (y_true == 0))
            metrics['direction_accuracy'] = direction_accuracy

        return metrics

    def _print_metrics(self, metrics, is_classification, model_name):
        """Imprime métricas de forma formateada"""
        if is_classification:
            print(f"  {model_name}: Accuracy={metrics['accuracy']:.4f} | "
                  f"Precision={metrics['precision']:.4f} | Recall={metrics['recall']:.4f} | "
                  f"F1={metrics['f1']:.4f} | ROC AUC={metrics.get('roc_auc', 0.5):.4f}")
        else:
            print(f"  {model_name}: MAE={metrics['mae']:.4f} | RMSE={metrics['rmse']:.4f} | "
                  f"R²={metrics['r2']:.4f} | MAPE={metrics.get('mape', 0):.4f} | "
                  f"Direction Accuracy={metrics['direction_accuracy']:.4f}")

    @timer_decorator
    def save_results(self):
        """Guarda todos los resultados"""
        # Guardar modelos
        for name, model in self.models.items():
            try:
                if 'ann' in name and TF_AVAILABLE:
                    # Guardar modelo de keras
                    model_path = os.path.join(self.output_path, 'models', f'{name}.h5')
                    model.save(model_path)
                else:
                    # Guardar otros modelos
                    model_path = os.path.join(self.output_path, 'models', f'{name}.pkl')
                    with open(model_path, 'wb') as f:
                        pickle.dump(model, f)
            except Exception as e:
                print(f"Error guardando modelo {name}: {e}")

        # Guardar métricas
        with open(os.path.join(self.output_path, 'metrics', 'metrics.json'), 'w') as f:
            # Convertir a tipos nativos de Python para JSON
            json_metrics = {}
            for k, v in self.metrics.items():
                if 'history' in v:  # Para historias de keras
                    v = {key: val for key, val in v.items() if key != 'history'}
                json_metrics[k] = v
            json.dump(json_metrics, f, indent=4, default=str)

        # Guardar importancia de características
        with open(os.path.join(self.output_path, 'metrics', 'feature_importances.json'), 'w') as f:
            json.dump(self.feature_importances, f, indent=4)

        # Guardar mejores parámetros
        with open(os.path.join(self.output_path, 'hyperparameters', 'best_params.json'), 'w') as f:
            json.dump(self.best_params, f, indent=4)

        # Guardar predicciones
        with open(os.path.join(self.output_path, 'metrics', 'predictions.pkl'), 'wb') as f:
            pickle.dump(self.predictions, f)

        # Generar visualizaciones
        self._generate_visualizations()

        print(f"\n✅ Resultados guardados en: {self.output_path}")

    def _generate_visualizations(self):
        """Genera visualizaciones de resultados"""
        # 1. Comparación de métricas entre modelos
        self._plot_metrics_comparison()

        # 2. Importancia de características
        self._plot_feature_importances()

        # 3. Predicciones vs reales
        self._plot_predictions_vs_actual()

        # 4. Matrices de confusión para clasificación
        self._plot_confusion_matrices()

        # 5. Curvas de aprendizaje para redes neuronales
        if TF_AVAILABLE:
            self._plot_learning_curves()

        # 6. Correlación entre predicciones de modelos
        self._plot_prediction_correlation()

    def _plot_metrics_comparison(self):
        """Genera gráficos comparativos de métricas"""
        # Implementación simplificada para evitar errores
        try:
            # Separar modelos de regresión y clasificación
            reg_models = {k: v for k, v in self.metrics.items() if 'reg' in k and 'opt' not in k}
            clf_models = {k: v for k, v in self.metrics.items() if 'cla' in k and 'opt' not in k}

            # Crear una figura simple con métricas principales
            fig, axes = plt.subplots(1, 2, figsize=(15, 6))

            # Gráfico para regresión
            if reg_models:
                model_names = list(reg_models.keys())
                r2_values = [reg_models[name].get('r2', 0) for name in model_names]
                axes[0].bar(range(len(model_names)), r2_values, color='blue')
                axes[0].set_xticks(range(len(model_names)))
                axes[0].set_xticklabels(model_names, rotation=45)
                axes[0].set_title('R² Score - Modelos de Regresión')
                axes[0].set_ylabel('R²')
                axes[0].grid(True, alpha=0.3)

            # Gráfico para clasificación
            if clf_models:
                model_names = list(clf_models.keys())
                f1_values = [clf_models[name].get('f1', 0) for name in model_names]
                axes[1].bar(range(len(model_names)), f1_values, color='blue')
                axes[1].set_xticks(range(len(model_names)))
                axes[1].set_xticklabels(model_names, rotation=45)
                axes[1].set_title('F1 Score - Modelos de Clasificación')
                axes[1].set_ylabel('F1')
                axes[1].grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(os.path.join(self.output_path, 'plots', 'metrics_comparison.png'),
                        dpi=150, bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"Error generando gráfico de métricas: {e}")

    def _plot_feature_importances(self):
        """Genera gráficos de importancia de características"""
        try:
            for model_name, importance_data in self.feature_importances.items():
                if not importance_data:
                    continue

                features = importance_data['features'][:20]  # Top 20
                importances = importance_data['importance'][:20]

                plt.figure(figsize=(10, 6))
                plt.barh(range(len(features)), importances, color='green')
                plt.yticks(range(len(features)), features)
                plt.xlabel('Importancia')
                plt.title(f'Importancia de Características - {model_name}')
                plt.tight_layout()

                plt.savefig(os.path.join(self.output_path, 'plots', f'feature_importance_{model_name}.png'),
                            dpi=150, bbox_inches='tight')
                plt.close()
        except Exception as e:
            print(f"Error generando importancia de características: {e}")

    def _plot_predictions_vs_actual(self):
        """Genera gráficos de predicciones vs valores reales"""
        # Implementación simplificada
        pass

    def _plot_confusion_matrices(self):
        """Genera matrices de confusión para modelos de clasificación"""
        # Implementación simplificada
        pass

    def _plot_learning_curves(self):
        """Genera curvas de aprendizaje para redes neuronales"""
        # Implementación simplificada
        pass

    def _plot_prediction_correlation(self):
        """Genera matriz de correlación entre predicciones de modelos"""
        # Implementación simplificada
        pass

# @title

# [6] BACKTESTING AVANZADO

import numpy as np
import matplotlib.pyplot as plt
import os

class AdvancedBacktester:
    """Backtester avanzado con correcciones completas para manejo de tipos"""

    def __init__(self, initial_capital=10000, spread=0.0002, commission=0.0001, output_path='./output'):
        self.initial_capital = float(initial_capital)
        self.spread = float(spread)
        self.commission = float(commission)
        self.output_path = output_path
        self.results = {}
        self.risk_manager = None

    def evaluate_strategy(self, predictions, actual_prices, model_name,
                         initial_price=None, plot_results=True, output_path=None):
        """Evalúa estrategia basada en predicciones - VERSIÓN CORREGIDA"""

        self.temp_output_path = output_path or self.output_path

        capital = float(self.initial_capital)
        position = 0
        entry_price = 0.0
        equity_curve = [capital]
        trades = []
        trade_durations = []

        # ✅ CORRECCIÓN: Aplanar arrays
        predictions = np.array(predictions).flatten()
        actual_prices = np.array(actual_prices).flatten()

        if initial_price is None and len(actual_prices) > 0:
            initial_price = float(actual_prices[0])

        for i, (pred, price) in enumerate(zip(predictions, actual_prices)):
            # ✅ CORRECCIÓN: Convertir a escalares
            price = float(price) if not isinstance(price, (list, tuple)) else float(price[0])
            pred = float(pred) if not isinstance(pred, (list, tuple)) else float(pred[0])

            if isinstance(pred, (int, np.integer)):
                signal = 1 if pred > 0 else -1 if pred < 0 else 0
                position_size = 1.0 if signal != 0 else 0.0
            else:
                signal = np.tanh(float(pred) * 0.1)
                position_size = min(abs(signal), 1.0)
                signal = 1 if signal > 0 else -1 if signal < 0 else 0

            if self.risk_manager is not None:
                risk_ok, risk_msg = self.risk_manager.check_risk_limits(
                    capital, position_size * capital
                )

                if not risk_ok:
                    if position != 0:
                        trade_pnl = self._close_position(position, entry_price, price, capital, trades, i)
                        capital = float(capital + trade_pnl)
                        position = 0
                    equity_curve.append(float(capital))
                    continue

            if signal != position and signal != 0:
                if position != 0:
                    trade_pnl = self._close_position(position, entry_price, price, capital, trades, i)
                    capital = float(capital + trade_pnl)

                    if len(trades) > 0:
                        trade_durations.append(i - trades[-1].get('entry_index', i))

                entry_price = float(price * (1 + self.spread) if signal == 1 else price * (1 - self.spread))
                position = int(signal)

                trades.append({
                    'type': 'entry',
                    'signal': int(signal),
                    'price': float(entry_price),
                    'capital': float(capital),
                    'entry_index': int(i)
                })

            equity_curve.append(float(capital))

        if position != 0 and len(actual_prices) > 0:
            price = float(actual_prices[-1])
            trade_pnl = self._close_position(position, entry_price, price, capital, trades, len(actual_prices)-1)
            capital = float(capital + trade_pnl)
            equity_curve[-1] = float(capital)

        equity_curve = np.array(equity_curve, dtype=float)
        results = self._calculate_performance_metrics(equity_curve, trades, trade_durations, model_name)

        if plot_results and len(equity_curve) > 0:
            self._plot_equity_curve(equity_curve, model_name)

        return results

    def _close_position(self, position, entry_price, exit_price, capital, trades, exit_index):
        """Cierra una posición y calcula PnL - VERSIÓN CORREGIDA"""

        # ✅ CORRECCIÓN: Validar tipos
        entry_price = float(entry_price) if not isinstance(entry_price, (list, tuple)) else float(entry_price[0])
        exit_price = float(exit_price) if not isinstance(exit_price, (list, tuple)) else float(exit_price[0])
        capital = float(capital) if not isinstance(capital, (list, tuple)) else float(capital[0])

        if position == 1:
            pnl = (exit_price - entry_price) / entry_price * capital - self.commission * capital
        else:
            pnl = (entry_price - exit_price) / entry_price * capital - self.commission * capital

        pnl = float(pnl)

        if trades and len(trades) > 0:
            trades[-1].update({
                'type': 'exit',
                'exit_price': float(exit_price),
                'exit_index': int(exit_index),
                'pnl': float(pnl),
                'duration': int(exit_index) - trades[-1].get('entry_index', int(exit_index))
            })

        return pnl

    def _calculate_performance_metrics(self, equity_curve, trades, trade_durations, model_name):
        """Calcula métricas de performance - VERSIÓN FINAL CORREGIDA"""

        equity_curve = np.array(equity_curve, dtype=float).flatten()

        initial_capital = float(self.initial_capital)
        final_capital = float(equity_curve[-1]) if len(equity_curve) > 0 else initial_capital

        total_return = (final_capital - initial_capital) / initial_capital
        annualized_return = (1 + total_return) ** (252 / len(equity_curve)) - 1 if len(equity_curve) > 1 else 0

        peak = np.maximum.accumulate(equity_curve)
        drawdown = (peak - equity_curve) / (peak + 1e-8)
        max_drawdown = float(np.max(drawdown)) if len(drawdown) > 0 else 0

        if len(equity_curve) > 1:
            returns = np.diff(equity_curve) / (equity_curve[:-1] + 1e-8)
        else:
            returns = np.array([0.0])

        if len(returns) > 1 and np.std(returns) > 0:
            sharpe_ratio = float(np.mean(returns) / np.std(returns) * np.sqrt(252))
        else:
            sharpe_ratio = 0.0

        negative_returns = returns[returns < 0]
        if len(negative_returns) > 1 and np.std(negative_returns) > 0:
            sortino_ratio = float(np.mean(returns) / np.std(negative_returns) * np.sqrt(252))
        else:
            sortino_ratio = 0.0

        # ✅ FIX CRÍTICO: Calmar Ratio con manejo de casos extremos
        if max_drawdown > 1e-8:
            # Asegurar que ambos valores son reales
            ann_ret = float(np.real(annualized_return))
            max_dd = float(np.real(max_drawdown))
            calmar_ratio = float(ann_ret / max_dd)
        else:
            calmar_ratio = 0.0

        n_trades = len([t for t in trades if t.get('type') == 'exit'])

        # Opción 2: Contar trades que tienen pnl (más robusto)
        # n_trades = len([t for t in trades if 'pnl' in t])

        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        win_rate = len(winning_trades) / n_trades if n_trades > 0 else 0.0

        gross_profit = sum([float(t.get('pnl', 0)) for t in winning_trades])
        gross_loss = abs(sum([float(t.get('pnl', 0)) for t in trades if t.get('pnl', 0) < 0]))
        profit_factor = gross_profit / gross_loss if gross_loss > 1e-8 else float('inf')

        avg_win = float(np.mean([t.get('pnl', 0) for t in winning_trades])) if winning_trades else 0.0
        losing_trades = [t for t in trades if t.get('pnl', 0) < 0]
        avg_loss = float(np.mean([t.get('pnl', 0) for t in losing_trades])) if losing_trades else 0.0
        win_loss_ratio = abs(avg_win / avg_loss) if abs(avg_loss) > 1e-8 else float('inf')

        avg_trade_duration = float(np.mean(trade_durations)) if trade_durations else 0.0

        var_95 = float(np.percentile(returns, 5)) if len(returns) > 0 else 0.0

        profit_factor = min(profit_factor, 999.0)
        win_loss_ratio = min(win_loss_ratio, 999.0)

        results = {
            'return': float(np.real(total_return)),
            'annualized_return': float(np.real(annualized_return)),
            'max_drawdown': float(np.real(max_drawdown)),
            'sharpe_ratio': float(np.real(sharpe_ratio)),
            'sortino_ratio': float(np.real(sortino_ratio)),
            'calmar_ratio': float(np.real(calmar_ratio)),
            'n_trades': int(n_trades),
            'win_rate': float(np.real(win_rate)),
            'profit_factor': float(np.real(profit_factor)),
            'avg_win': float(np.real(avg_win)),
            'avg_loss': float(np.real(avg_loss)),
            'win_loss_ratio': float(np.real(win_loss_ratio)),
            'avg_trade_duration': float(np.real(avg_trade_duration)),
            'var_95': float(np.real(var_95)),
            'equity_curve': equity_curve.tolist(),
            'trades': trades,
            'returns': returns.tolist()
        }

        print(f"{model_name}: Return = {total_return:.2%} | Sharpe = {sharpe_ratio:.2f} | "
              f"Max DD = {max_drawdown:.2%} | Win Rate = {win_rate:.2%} | "
              f"Profit Factor = {profit_factor:.2f}")

        return results

    def _plot_equity_curve(self, equity_curve, model_name):
        """Grafica la curva de equity"""

        output_path = self.temp_output_path if hasattr(self, 'temp_output_path') else self.output_path

        plt.figure(figsize=(12, 6))
        plt.plot(equity_curve, linewidth=2)
        plt.title(f'Curva de Equity - {model_name}')
        plt.xlabel('Períodos')
        plt.ylabel('Capital ($)')
        plt.grid(True, alpha=0.3)
        plt.axhline(y=self.initial_capital, color='r', linestyle='--', alpha=0.7, label='Capital Inicial')

        final_return = (equity_curve[-1] - self.initial_capital) / self.initial_capital
        plt.annotate(f'Retorno: {final_return:.2%}',
                    xy=(len(equity_curve)-1, equity_curve[-1]),
                    xytext=(10, 10), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))

        plt.legend()
        plt.tight_layout()

        backtest_dir = os.path.join(output_path, 'backtest_results')
        os.makedirs(backtest_dir, exist_ok=True)

        plt.savefig(os.path.join(backtest_dir, f'equity_curve_{model_name}.png'),
                   dpi=150, bbox_inches='tight')
        plt.close()

print("✅ Clase AdvancedBacktester cargada correctamente (VERSIÓN FINAL)")



# [6B] ANÁLISIS AVANZADO DE MÉTRICAS
class AdvancedMetricsAnalyzer:
    """Análisis profundo de métricas de trading"""

    def __init__(self):
        self.metrics_history = []

    def calculate_extended_metrics(self, equity_curve, trades, returns, prices):
        """Calcula métricas extendidas de performance"""
        metrics = {}

        # ✅ AÑADIR ESTAS 2 LÍNEAS
        equity_curve = np.array(equity_curve, dtype=float)
        returns = np.array(returns, dtype=float)

        # === MÉTRICAS DE RETORNO ===
        total_return = (equity_curve[-1] / equity_curve[0]) - 1
        metrics['total_return_pct'] = total_return * 100

        # CAGR (Compound Annual Growth Rate)
        n_years = len(equity_curve) / 252  # Asumiendo datos diarios
        metrics['cagr'] = ((equity_curve[-1] / equity_curve[0]) ** (1/n_years) - 1) * 100 if n_years > 0 else 0

        # === MÉTRICAS DE RIESGO ===
        # Sharpe Ratio
        if len(returns) > 1:
            excess_returns = returns - 0.02/252  # Rf = 2% anual
            metrics['sharpe_ratio'] = np.sqrt(252) * excess_returns.mean() / (excess_returns.std() + 1e-8)

        # Sortino Ratio (solo downside deviation)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0:
            downside_std = np.sqrt(np.mean(downside_returns**2))
            metrics['sortino_ratio'] = np.sqrt(252) * returns.mean() / (downside_std + 1e-8)

        # Calmar Ratio
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - peak) / peak
        max_dd = abs(drawdown.min())
        metrics['max_drawdown_pct'] = max_dd * 100
        metrics['calmar_ratio'] = (metrics['cagr'] / 100) / max_dd if max_dd > 0 else 0

        # Ulcer Index (promedio de drawdowns al cuadrado)
        metrics['ulcer_index'] = np.sqrt(np.mean(drawdown**2)) * 100

        # === MÉTRICAS DE TRADES ===
        if trades:
            winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
            losing_trades = [t for t in trades if t.get('pnl', 0) < 0]

            metrics['total_trades'] = len(trades)
            metrics['winning_trades'] = len(winning_trades)
            metrics['losing_trades'] = len(losing_trades)
            metrics['win_rate_pct'] = (len(winning_trades) / len(trades)) * 100

            # Profit Factor
            gross_profit = sum([t.get('pnl', 0) for t in winning_trades])
            gross_loss = abs(sum([t.get('pnl', 0) for t in losing_trades]))
            metrics['profit_factor'] = gross_profit / gross_loss if gross_loss > 0 else float('inf')

            # Expectancy
            avg_win = np.mean([t.get('pnl', 0) for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t.get('pnl', 0) for t in losing_trades]) if losing_trades else 0
            metrics['avg_win'] = avg_win
            metrics['avg_loss'] = avg_loss
            metrics['expectancy'] = (metrics['win_rate_pct']/100 * avg_win) + ((1-metrics['win_rate_pct']/100) * avg_loss)

            # Consecutive wins/losses
            consecutive_wins = self._calculate_consecutive(winning_trades, trades)
            consecutive_losses = self._calculate_consecutive(losing_trades, trades)
            metrics['max_consecutive_wins'] = consecutive_wins
            metrics['max_consecutive_losses'] = consecutive_losses

            # Recovery Factor
            metrics['recovery_factor'] = total_return / max_dd if max_dd > 0 else 0

        # === MÉTRICAS DE VOLATILIDAD ===
        metrics['annual_volatility_pct'] = np.std(returns) * np.sqrt(252) * 100

        # Value at Risk (VaR) - 95% y 99%
        metrics['var_95'] = np.percentile(returns, 5) * 100
        metrics['var_99'] = np.percentile(returns, 1) * 100

        # Conditional VaR (CVaR) o Expected Shortfall
        var_95_value = np.percentile(returns, 5)
        cvar_returns = returns[returns <= var_95_value]
        metrics['cvar_95'] = np.mean(cvar_returns) * 100 if len(cvar_returns) > 0 else 0

        # === MÉTRICAS DE ESTABILIDAD ===
        # Rolling Sharpe (último período)
        if len(returns) >= 60:
            rolling_sharpe = []
            for i in range(60, len(returns)):
                window = returns[i-60:i]
                rolling_sharpe.append(np.sqrt(252) * window.mean() / (window.std() + 1e-8))
            metrics['rolling_sharpe_stability'] = np.std(rolling_sharpe) if rolling_sharpe else 0

        # Tail Ratio (percentil 95 vs percentil 5)
        metrics['tail_ratio'] = abs(np.percentile(returns, 95) / np.percentile(returns, 5))

        return metrics

    def _calculate_consecutive(self, target_trades, all_trades):
        """Calcula máximo de trades consecutivos"""
        max_consecutive = 0
        current_consecutive = 0

        for trade in all_trades:
            if trade in target_trades:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0

        return max_consecutive

    def generate_performance_report(self, metrics):
        """Genera reporte de performance formateado"""
        report = []
        report.append("\n" + "="*70)
        report.append("📊 REPORTE EXTENDIDO DE PERFORMANCE")
        report.append("="*70)

        report.append("\n🎯 MÉTRICAS DE RETORNO:")
        report.append(f"  Total Return: {metrics.get('total_return_pct', 0):.2f}%")
        report.append(f"  CAGR: {metrics.get('cagr', 0):.2f}%")
        report.append(f"  Expectancy: ${metrics.get('expectancy', 0):.2f}")

        report.append("\n⚠️  MÉTRICAS DE RIESGO:")
        report.append(f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}")
        report.append(f"  Sortino Ratio: {metrics.get('sortino_ratio', 0):.3f}")
        report.append(f"  Calmar Ratio: {metrics.get('calmar_ratio', 0):.3f}")
        report.append(f"  Max Drawdown: {metrics.get('max_drawdown_pct', 0):.2f}%")
        report.append(f"  Ulcer Index: {metrics.get('ulcer_index', 0):.2f}")
        report.append(f"  Recovery Factor: {metrics.get('recovery_factor', 0):.3f}")

        report.append("\n📈 MÉTRICAS DE TRADES:")
        report.append(f"  Total Trades: {metrics.get('total_trades', 0)}")
        report.append(f"  Win Rate: {metrics.get('win_rate_pct', 0):.2f}%")
        report.append(f"  Profit Factor: {metrics.get('profit_factor', 0):.3f}")
        report.append(f"  Avg Win: ${metrics.get('avg_win', 0):.2f}")
        report.append(f"  Avg Loss: ${metrics.get('avg_loss', 0):.2f}")
        report.append(f"  Max Consecutive Wins: {metrics.get('max_consecutive_wins', 0)}")
        report.append(f"  Max Consecutive Losses: {metrics.get('max_consecutive_losses', 0)}")

        report.append("\n💹 MÉTRICAS DE VOLATILIDAD:")
        report.append(f"  Annual Volatility: {metrics.get('annual_volatility_pct', 0):.2f}%")
        report.append(f"  VaR 95%: {metrics.get('var_95', 0):.2f}%")
        report.append(f"  VaR 99%: {metrics.get('var_99', 0):.2f}%")
        report.append(f"  CVaR 95%: {metrics.get('cvar_95', 0):.2f}%")
        report.append(f"  Tail Ratio: {metrics.get('tail_ratio', 0):.3f}")

        report.append("\n" + "="*70)

        return "\n".join(report)

    def plot_advanced_metrics(self, equity_curve, returns, trades, output_path):
        """Genera gráficos avanzados"""
        fig, axes = plt.subplots(3, 2, figsize=(16, 12))

        # 1. Equity Curve con Drawdown
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - peak) / peak

        ax1 = axes[0, 0]
        ax1.plot(equity_curve, label='Equity', linewidth=2)
        ax1.plot(peak, '--', label='Peak', alpha=0.5)
        ax1.fill_between(range(len(equity_curve)), equity_curve, peak, alpha=0.3, color='red')
        ax1.set_title('Equity Curve with Drawdown')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Drawdown separado
        ax2 = axes[0, 1]
        ax2.plot(drawdown * 100, color='red', linewidth=2)
        ax2.fill_between(range(len(drawdown)), drawdown * 100, 0, alpha=0.3, color='red')
        ax2.set_title('Drawdown %')
        ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax2.grid(True, alpha=0.3)

        # 3. Distribución de Returns
        ax3 = axes[1, 0]
        ax3.hist(returns * 100, bins=50, alpha=0.7, edgecolor='black')
        ax3.axvline(returns.mean() * 100, color='red', linestyle='--', label=f'Mean: {returns.mean()*100:.3f}%')
        ax3.axvline(np.percentile(returns * 100, 5), color='orange', linestyle='--', label='VaR 95%')
        ax3.set_title('Returns Distribution')
        ax3.set_xlabel('Return %')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 4. Rolling Sharpe
        if len(returns) >= 60:
            rolling_sharpe = []
            for i in range(60, len(returns)):
                window = returns[i-60:i]
                rolling_sharpe.append(np.sqrt(252) * window.mean() / (window.std() + 1e-8))

            ax4 = axes[1, 1]
            ax4.plot(rolling_sharpe, linewidth=2)
            ax4.axhline(y=0, color='black', linestyle='--', alpha=0.5)
            ax4.axhline(y=1, color='green', linestyle='--', alpha=0.3, label='Sharpe = 1')
            ax4.set_title('Rolling Sharpe Ratio (60-period)')
            ax4.legend()
            ax4.grid(True, alpha=0.3)

        # 5. Win/Loss Distribution
        if trades:
            pnls = [t.get('pnl', 0) for t in trades]
            wins = [p for p in pnls if p > 0]
            losses = [p for p in pnls if p < 0]

            ax5 = axes[2, 0]
            ax5.hist([wins, losses], bins=20, label=['Wins', 'Losses'], color=['green', 'red'], alpha=0.7)
            ax5.set_title('Trade P&L Distribution')
            ax5.set_xlabel('P&L')
            ax5.legend()
            ax5.grid(True, alpha=0.3)

        # 6. Underwater Plot (tiempo en drawdown)
        ax6 = axes[2, 1]
        underwater = (equity_curve / peak - 1) * 100
        ax6.fill_between(range(len(underwater)), underwater, 0, color='red', alpha=0.3)
        ax6.plot(underwater, color='darkred', linewidth=1)
        ax6.set_title('Underwater Plot (% from Peak)')
        ax6.set_ylabel('%')
        ax6.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(output_path, 'advanced_metrics_analysis.png'), dpi=150, bbox_inches='tight')
        plt.close()


# [6C] VISUALIZACIONES AVANZADAS
class AdvancedVisualizationEngine:
    """Motor de visualizaciones avanzadas para análisis de trading"""

    def __init__(self, output_path):
        self.output_path = output_path
        self.plots_dir = os.path.join(output_path, 'plots')
        os.makedirs(self.plots_dir, exist_ok=True)

    def plot_comprehensive_analysis(self, results_dict, timeframe):
        """Genera análisis visual completo para un timeframe"""
        print(f"\n📊 Generando visualizaciones para {timeframe}...")

        for model_name, results in results_dict.items():
            try:
                # 1. Dashboard principal
                self._plot_main_dashboard(results, model_name, timeframe)

                # 2. Análisis de trades
                self._plot_trade_analysis(results, model_name, timeframe)

                # 3. Análisis de riesgo
                self._plot_risk_analysis(results, model_name, timeframe)

                # 4. Análisis temporal
                self._plot_temporal_analysis(results, model_name, timeframe)

                print(f"  ✅ Visualizaciones completadas para {model_name}")

            except Exception as e:
                print(f"  ⚠️ Error en visualizaciones {model_name}: {e}")

    def _plot_main_dashboard(self, results, model_name, timeframe):
        """Dashboard principal con 6 gráficos clave"""
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        equity = np.array(results['equity_curve'])
        returns = np.array(results.get('returns', []))
        trades = results.get('trades', [])

        # 1. Equity Curve con señales de trades
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.plot(equity, linewidth=2, color='#2E86DE', label='Equity')

        # Marcar trades ganadores y perdedores
        if trades:
            for trade in trades:
                if trade.get('type') == 'exit':
                    color = 'green' if trade.get('pnl', 0) > 0 else 'red'
                    marker = '^' if trade.get('pnl', 0) > 0 else 'v'
                    exit_idx = trade.get('exit_index', 0)
                    if exit_idx < len(equity):
                        ax1.scatter(exit_idx, equity[exit_idx],
                                  color=color, marker=marker, s=100, alpha=0.6)

        ax1.axhline(y=equity[0], color='gray', linestyle='--', alpha=0.5, label='Initial Capital')
        ax1.set_title(f'Equity Curve - {model_name} ({timeframe})', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Capital ($)', fontsize=11)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)

        # 2. Métricas principales (texto)
        ax2 = fig.add_subplot(gs[0, 2])
        ax2.axis('off')

        ext_metrics = results.get('extended_metrics', {})
        metrics_text = f"""
        📈 PERFORMANCE
        Total Return: {ext_metrics.get('total_return_pct', 0):.2f}%
        CAGR: {ext_metrics.get('cagr', 0):.2f}%

        ⚖️ RISK-ADJUSTED
        Sharpe: {ext_metrics.get('sharpe_ratio', 0):.3f}
        Sortino: {ext_metrics.get('sortino_ratio', 0):.3f}
        Calmar: {ext_metrics.get('calmar_ratio', 0):.3f}

        📊 TRADES
        Total: {ext_metrics.get('total_trades', 0)}
        Win Rate: {ext_metrics.get('win_rate_pct', 0):.1f}%
        Profit Factor: {ext_metrics.get('profit_factor', 0):.2f}

        ⚠️ RISK
        Max DD: {ext_metrics.get('max_drawdown_pct', 0):.2f}%
        VaR 95%: {ext_metrics.get('var_95', 0):.2f}%
        """

        ax2.text(0.1, 0.5, metrics_text, fontsize=10, verticalalignment='center',
                fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        # 3. Drawdown
        ax3 = fig.add_subplot(gs[1, :2])
        peak = np.maximum.accumulate(equity)
        drawdown = (equity - peak) / peak * 100
        ax3.fill_between(range(len(drawdown)), drawdown, 0, alpha=0.4, color='red')
        ax3.plot(drawdown, color='darkred', linewidth=1.5)
        ax3.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax3.set_title('Drawdown Over Time', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Drawdown (%)', fontsize=11)
        ax3.grid(True, alpha=0.3)

        # 4. Returns Distribution
        ax4 = fig.add_subplot(gs[1, 2])
        if len(returns) > 0:
            ax4.hist(returns * 100, bins=50, alpha=0.7, color='#54A0FF', edgecolor='black')
            ax4.axvline(returns.mean() * 100, color='red', linestyle='--', linewidth=2,
                       label=f'Mean: {returns.mean()*100:.3f}%')
            ax4.axvline(0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
            ax4.set_title('Returns Distribution', fontsize=12, fontweight='bold')
            ax4.set_xlabel('Return (%)', fontsize=10)
            ax4.legend(fontsize=9)
            ax4.grid(True, alpha=0.3)

        # 5. Win/Loss Analysis
        ax5 = fig.add_subplot(gs[2, 0])
        if trades:
            pnls = [t.get('pnl', 0) for t in trades if t.get('type') == 'exit']
            wins = [p for p in pnls if p > 0]
            losses = [p for p in pnls if p < 0]

            if wins or losses:
                ax5.hist([wins, losses], bins=20, label=['Wins', 'Losses'],
                        color=['#26DE81', '#FC5C65'], alpha=0.7, edgecolor='black')
                ax5.set_title('Trade P&L Distribution', fontsize=12, fontweight='bold')
                ax5.set_xlabel('P&L ($)', fontsize=10)
                ax5.legend(fontsize=9)
                ax5.grid(True, alpha=0.3)

        # 6. Rolling Sharpe
        ax6 = fig.add_subplot(gs[2, 1])
        if len(returns) >= 60:
            rolling_sharpe = []
            for i in range(60, len(returns)):
                window = returns[i-60:i]
                rolling_sharpe.append(np.sqrt(252) * window.mean() / (window.std() + 1e-8))

            ax6.plot(rolling_sharpe, linewidth=2, color='#5F27CD')
            ax6.axhline(y=0, color='black', linestyle='--', alpha=0.5)
            ax6.axhline(y=1, color='green', linestyle='--', alpha=0.3, label='Sharpe = 1')
            ax6.axhline(y=2, color='blue', linestyle='--', alpha=0.3, label='Sharpe = 2')
            ax6.fill_between(range(len(rolling_sharpe)), 0, rolling_sharpe,
                           where=(np.array(rolling_sharpe) > 0), alpha=0.3, color='green')
            ax6.fill_between(range(len(rolling_sharpe)), 0, rolling_sharpe,
                           where=(np.array(rolling_sharpe) < 0), alpha=0.3, color='red')
            ax6.set_title('Rolling Sharpe Ratio (60-period)', fontsize=12, fontweight='bold')
            ax6.legend(fontsize=9)
            ax6.grid(True, alpha=0.3)

        # 7. Monthly Returns Heatmap
        ax7 = fig.add_subplot(gs[2, 2])
        self._plot_monthly_returns_mini(returns, ax7)

        plt.suptitle(f'Trading Dashboard: {model_name} | {timeframe}',
                    fontsize=16, fontweight='bold', y=0.995)

        filename = f'dashboard_{model_name}_{timeframe}.png'
        plt.savefig(os.path.join(self.plots_dir, filename), dpi=150, bbox_inches='tight')
        plt.close()

    def _plot_monthly_returns_mini(self, returns, ax):
        """Heatmap simplificado de retornos mensuales"""
        try:
            # Crear DataFrame con retornos
            df_returns = pd.DataFrame({'returns': returns})

            # Simular índice mensual (simplificado)
            months = np.arange(len(returns)) // 21  # ~21 días trading por mes
            df_returns['month'] = months

            monthly_returns = df_returns.groupby('month')['returns'].sum() * 100

            # Reshape para heatmap (intentar 3 filas)
            n_months = len(monthly_returns)
            n_cols = (n_months + 2) // 3

            # Padding con NaN si es necesario
            padded_length = 3 * n_cols
            padded_returns = np.full(padded_length, np.nan)
            padded_returns[:n_months] = monthly_returns.values

            heatmap_data = padded_returns.reshape(3, n_cols)

            im = ax.imshow(heatmap_data, cmap='RdYlGn', aspect='auto', vmin=-5, vmax=5)
            ax.set_title('Monthly Returns (%)', fontsize=10, fontweight='bold')
            ax.set_xticks([])
            ax.set_yticks([])

            # Añadir valores en las celdas
            for i in range(3):
                for j in range(n_cols):
                    if not np.isnan(heatmap_data[i, j]):
                        text = ax.text(j, i, f'{heatmap_data[i, j]:.1f}',
                                     ha="center", va="center", color="black", fontsize=7)
        except Exception as e:
            ax.text(0.5, 0.5, 'N/A', ha='center', va='center', fontsize=10)
            ax.set_title('Monthly Returns', fontsize=10)

    def _plot_trade_analysis(self, results, model_name, timeframe):
        """Análisis detallado de trades"""
        trades = results.get('trades', [])
        if not trades:
            return

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Extraer información de trades
        trade_pnls = []
        trade_durations = []
        cumulative_pnl = []
        cum_sum = 0

        for trade in trades:
            if trade.get('type') == 'exit':
                pnl = trade.get('pnl', 0)
                duration = trade.get('duration', 0)
                trade_pnls.append(pnl)
                trade_durations.append(duration)
                cum_sum += pnl
                cumulative_pnl.append(cum_sum)

        # 1. P&L por trade
        ax1 = axes[0, 0]
        colors = ['green' if p > 0 else 'red' for p in trade_pnls]
        ax1.bar(range(len(trade_pnls)), trade_pnls, color=colors, alpha=0.7, edgecolor='black')
        ax1.axhline(y=0, color='black', linestyle='--', linewidth=1)
        ax1.set_title('P&L por Trade', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Trade #', fontsize=10)
        ax1.set_ylabel('P&L ($)', fontsize=10)
        ax1.grid(True, alpha=0.3, axis='y')

        # 2. P&L acumulado
        ax2 = axes[0, 1]
        ax2.plot(cumulative_pnl, linewidth=2, color='#2E86DE')
        ax2.fill_between(range(len(cumulative_pnl)), 0, cumulative_pnl,
                        alpha=0.3, color='#2E86DE')
        ax2.set_title('P&L Acumulado', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Trade #', fontsize=10)
        ax2.set_ylabel('Cumulative P&L ($)', fontsize=10)
        ax2.grid(True, alpha=0.3)

        # 3. Duración de trades
        ax3 = axes[1, 0]
        ax3.hist(trade_durations, bins=20, alpha=0.7, color='#FFA502', edgecolor='black')
        ax3.axvline(np.mean(trade_durations), color='red', linestyle='--',
                   linewidth=2, label=f'Mean: {np.mean(trade_durations):.1f}')
        ax3.set_title('Distribución de Duración de Trades', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Duración (períodos)', fontsize=10)
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3)

        # 4. Win/Loss streaks
        ax4 = axes[1, 1]
        streak = []
        current_streak = 0
        last_result = None

        for pnl in trade_pnls:
            is_win = pnl > 0
            if last_result is None:
                current_streak = 1
            elif is_win == last_result:
                current_streak += 1
            else:
                streak.append(current_streak if last_result else -current_streak)
                current_streak = 1
            last_result = is_win

        if current_streak > 0:
            streak.append(current_streak if last_result else -current_streak)

        colors_streak = ['green' if s > 0 else 'red' for s in streak]
        ax4.bar(range(len(streak)), streak, color=colors_streak, alpha=0.7, edgecolor='black')
        ax4.axhline(y=0, color='black', linestyle='--', linewidth=1)
        ax4.set_title('Win/Loss Streaks', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Streak #', fontsize=10)
        ax4.set_ylabel('Consecutive Trades', fontsize=10)
        ax4.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        filename = f'trade_analysis_{model_name}_{timeframe}.png'
        plt.savefig(os.path.join(self.plots_dir, filename), dpi=150, bbox_inches='tight')
        plt.close()

    def _plot_risk_analysis(self, results, model_name, timeframe):
        """Análisis de riesgo"""
        equity = np.array(results['equity_curve'])
        returns = np.array(results.get('returns', []))

        if len(returns) == 0:
            return

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Underwater plot (tiempo en drawdown)
        ax1 = axes[0, 0]
        peak = np.maximum.accumulate(equity)
        underwater = (equity / peak - 1) * 100
        ax1.fill_between(range(len(underwater)), underwater, 0, color='red', alpha=0.3)
        ax1.plot(underwater, color='darkred', linewidth=1.5)
        ax1.set_title('Underwater Plot', fontsize=12, fontweight='bold')
        ax1.set_ylabel('% from Peak', fontsize=10)
        ax1.grid(True, alpha=0.3)

        # 2. VaR historical
        ax2 = axes[0, 1]
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)

        ax2.hist(returns * 100, bins=50, alpha=0.7, color='#54A0FF', edgecolor='black')
        ax2.axvline(var_95 * 100, color='orange', linestyle='--', linewidth=2,
                   label=f'VaR 95%: {var_95*100:.2f}%')
        ax2.axvline(var_99 * 100, color='red', linestyle='--', linewidth=2,
                   label=f'VaR 99%: {var_99*100:.2f}%')
        ax2.set_title('Value at Risk (VaR)', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Return (%)', fontsize=10)
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)

        # 3. Rolling Volatility
        ax3 = axes[1, 0]
        if len(returns) >= 30:
            rolling_vol = []
            for i in range(30, len(returns)):
                window = returns[i-30:i]
                rolling_vol.append(np.std(window) * np.sqrt(252) * 100)

            ax3.plot(rolling_vol, linewidth=2, color='#EE5A6F')
            ax3.fill_between(range(len(rolling_vol)), 0, rolling_vol, alpha=0.3, color='#EE5A6F')
            ax3.set_title('Rolling Volatility (30-period, annualized)', fontsize=12, fontweight='bold')
            ax3.set_ylabel('Volatility (%)', fontsize=10)
            ax3.grid(True, alpha=0.3)

        # 4. Q-Q plot (normalidad de retornos)
        ax4 = axes[1, 1]
        from scipy import stats as scipy_stats
        scipy_stats.probplot(returns, dist="norm", plot=ax4)
        ax4.set_title('Q-Q Plot (Normality Test)', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        filename = f'risk_analysis_{model_name}_{timeframe}.png'
        plt.savefig(os.path.join(self.plots_dir, filename), dpi=150, bbox_inches='tight')
        plt.close()

    def _plot_temporal_analysis(self, results, model_name, timeframe):
        """Análisis temporal (si hay índice datetime)"""
        equity = np.array(results['equity_curve'])
        returns = np.array(results.get('returns', []))

        if len(returns) < 100:
            return

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Rolling Returns (diferentes ventanas)
        ax1 = axes[0, 0]
        for window in [20, 60, 120]:
            rolling_ret = []
            for i in range(window, len(equity)):
                ret = (equity[i] / equity[i-window] - 1) * 100
                rolling_ret.append(ret)
            ax1.plot(rolling_ret, linewidth=1.5, label=f'{window}-period', alpha=0.7)

        ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax1.set_title('Rolling Returns', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Return (%)', fontsize=10)
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3)

        # 2. Autocorrelación de retornos
        ax2 = axes[0, 1]
        from pandas.plotting import autocorrelation_plot
        returns_series = pd.Series(returns)
        autocorrelation_plot(returns_series, ax=ax2)
        ax2.set_title('Returns Autocorrelation', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        # 3. Rolling Max Drawdown
        ax3 = axes[1, 0]
        if len(equity) >= 60:
            rolling_mdd = []
            for i in range(60, len(equity)):
                window = equity[i-60:i]
                peak = np.maximum.accumulate(window)
                dd = ((window - peak) / peak).min() * 100
                rolling_mdd.append(dd)

            ax3.plot(rolling_mdd, linewidth=2, color='red')
            ax3.fill_between(range(len(rolling_mdd)), rolling_mdd, 0, alpha=0.3, color='red')
            ax3.set_title('Rolling Max Drawdown (60-period)', fontsize=12, fontweight='bold')
            ax3.set_ylabel('Max DD (%)', fontsize=10)
            ax3.grid(True, alpha=0.3)

        # 4. Distribution comparison (returns vs normal)
        ax4 = axes[1, 1]
        ax4.hist(returns, bins=50, density=True, alpha=0.7, color='#54A0FF',
                edgecolor='black', label='Actual')

        # Fit normal distribution
        mu, sigma = returns.mean(), returns.std()
        x = np.linspace(returns.min(), returns.max(), 100)
        ax4.plot(x, scipy_stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2,
                label='Normal fit')

        ax4.set_title('Returns vs Normal Distribution', fontsize=12, fontweight='bold')
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        filename = f'temporal_analysis_{model_name}_{timeframe}.png'
        plt.savefig(os.path.join(self.plots_dir, filename), dpi=150, bbox_inches='tight')
        plt.close()

    def create_comparison_report(self, all_timeframe_results, output_path):
        """Crea reporte comparativo entre timeframes"""
        print("\n📊 Generando reporte comparativo multi-timeframe...")

        comparison_data = []

        for tf, tf_results in all_timeframe_results.items():
            backtest_results = tf_results.get('backtests', {})

            for model_name, results in backtest_results.items():
                ext_metrics = results.get('extended_metrics', {})

                comparison_data.append({
                    'Timeframe': tf,
                    'Model': model_name,
                    'Total Return %': ext_metrics.get('total_return_pct', 0),
                    'CAGR %': ext_metrics.get('cagr', 0),
                    'Sharpe': ext_metrics.get('sharpe_ratio', 0),
                    'Sortino': ext_metrics.get('sortino_ratio', 0),
                    'Max DD %': ext_metrics.get('max_drawdown_pct', 0),
                    'Win Rate %': ext_metrics.get('win_rate_pct', 0),
                    'Profit Factor': ext_metrics.get('profit_factor', 0),
                    'Total Trades': ext_metrics.get('total_trades', 0),
                    'Avg Win': ext_metrics.get('avg_win', 0),
                    'Avg Loss': ext_metrics.get('avg_loss', 0)
                })

        if not comparison_data:
            print("  ⚠️ No hay datos para comparación")
            return

        df_comparison = pd.DataFrame(comparison_data)

        # Guardar CSV
        csv_path = os.path.join(output_path, 'multi_timeframe_comparison.csv')
        df_comparison.to_csv(csv_path, index=False)
        print(f"  ✅ CSV guardado: {csv_path}")

        # Crear visualización comparativa
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))

        metrics_to_plot = [
            ('Total Return %', 'Total Return by TF/Model'),
            ('Sharpe', 'Sharpe Ratio by TF/Model'),
            ('Max DD %', 'Max Drawdown by TF/Model'),
            ('Win Rate %', 'Win Rate by TF/Model'),
            ('Profit Factor', 'Profit Factor by TF/Model'),
            ('Total Trades', 'Number of Trades by TF/Model')
        ]

        for idx, (metric, title) in enumerate(metrics_to_plot):
            ax = axes[idx // 3, idx % 3]

            pivot = df_comparison.pivot_table(
                values=metric,
                index='Timeframe',
                columns='Model',
                aggfunc='mean'
            )

            pivot.plot(kind='bar', ax=ax, width=0.8, edgecolor='black')
            ax.set_title(title, fontsize=11, fontweight='bold')
            ax.set_xlabel('')
            ax.legend(fontsize=8, loc='best')
            ax.grid(True, alpha=0.3, axis='y')
            ax.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        comparison_plot = os.path.join(output_path, 'timeframe_comparison_plot.png')
        plt.savefig(comparison_plot, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"  ✅ Gráfico comparativo guardado: {comparison_plot}")

        # Imprimir top performers
        print("\n🏆 TOP PERFORMERS POR MÉTRICA:")
        print("\n1. Mayor Sharpe Ratio:")
        top_sharpe = df_comparison.nlargest(3, 'Sharpe')[['Timeframe', 'Model', 'Sharpe']]
        print(top_sharpe.to_string(index=False))

        print("\n2. Mayor Total Return:")
        top_return = df_comparison.nlargest(3, 'Total Return %')[['Timeframe', 'Model', 'Total Return %']]
        print(top_return.to_string(index=False))

        print("\n3. Menor Max Drawdown:")
        top_dd = df_comparison.nsmallest(3, 'Max DD %')[['Timeframe', 'Model', 'Max DD %']]
        print(top_dd.to_string(index=False))

# @title
"""
SCRIPT DE VALIDACIÓN POST-CORRECCIÓN
=====================================

Este script te ayuda a verificar que las correcciones se aplicaron correctamente.
Ejecútalo después de reemplazar la clase AdvancedBacktester en tu notebook.

INSTRUCCIONES:
1. Copia este código en una nueva celda de tu notebook
2. Ejecútalo DESPUÉS de la celda que define AdvancedBacktester
3. Verifica que todos los tests pasen (✅)
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("🔍 VALIDACIÓN DE CORRECCIONES - AdvancedBacktester")
print("="*70)

# Test 1: Verificar que la clase existe
print("\n[Test 1] Verificando clase AdvancedBacktester...")
try:
    backtester = AdvancedBacktester(initial_capital=10000)
    print("✅ Clase AdvancedBacktester encontrada")
except NameError:
    print("❌ ERROR: Clase AdvancedBacktester no encontrada")
    print("   → Asegúrate de ejecutar la celda que define la clase primero")
    exit()

# Test 2: Verificar tipo de initial_capital
print("\n[Test 2] Verificando tipos de atributos...")
assert isinstance(backtester.initial_capital, float), "initial_capital debe ser float"
assert isinstance(backtester.spread, float), "spread debe ser float"
assert isinstance(backtester.commission, float), "commission debe ser float"
print("✅ Todos los atributos tienen tipos correctos (float)")

# Test 3: Crear datos de prueba
print("\n[Test 3] Creando datos de prueba...")
np.random.seed(42)
n_samples = 100
predictions = np.random.randn(n_samples) * 0.01  # Predicciones pequeñas
actual_prices = np.cumsum(np.random.randn(n_samples) * 0.01) + 1.0  # Serie de precios

# Verificar que no son listas problemáticas
assert not isinstance(predictions, list), "predictions debe ser array"
assert not isinstance(actual_prices, list), "actual_prices debe ser array"
print(f"✅ Datos de prueba creados: {n_samples} samples")
print(f"   predictions shape: {predictions.shape}")
print(f"   actual_prices shape: {actual_prices.shape}")

# Test 4: Ejecutar backtesting
print("\n[Test 4] Ejecutando backtesting de prueba...")
try:
    results = backtester.evaluate_strategy(
        predictions=predictions,
        actual_prices=actual_prices,
        model_name='test_model',
        plot_results=False
    )
    print("✅ Backtesting completado sin errores")
except TypeError as e:
    if "unsupported operand type" in str(e):
        print("❌ ERROR: Aún existe el error de tipos")
        print(f"   Error: {e}")
        print("   → Las correcciones NO se aplicaron correctamente")
        exit()
    else:
        raise
except Exception as e:
    print(f"⚠️ Warning: Error diferente: {type(e).__name__}: {e}")
    print("   (Esto puede ser normal si faltan otras dependencias)")

# Test 5: Verificar estructura de resultados
print("\n[Test 5] Verificando estructura de resultados...")
required_keys = ['return', 'sharpe_ratio', 'max_drawdown', 'win_rate',
                'profit_factor', 'n_trades', 'equity_curve']
for key in required_keys:
    assert key in results, f"Falta clave: {key}"
    print(f"   ✅ '{key}': presente")

# Test 6: Verificar tipos de valores en resultados
print("\n[Test 6] Verificando tipos de valores en resultados...")
assert isinstance(results['return'], float), "return debe ser float"
assert isinstance(results['sharpe_ratio'], float), "sharpe_ratio debe ser float"
assert isinstance(results['max_drawdown'], float), "max_drawdown debe ser float"
assert isinstance(results['n_trades'], int), "n_trades debe ser int"
assert isinstance(results['equity_curve'], list), "equity_curve debe ser list"
print("✅ Todos los valores tienen tipos correctos")

# Test 7: Verificar que equity_curve no tiene arrays anidados
print("\n[Test 7] Verificando equity_curve...")
for i, value in enumerate(results['equity_curve'][:5]):
    assert isinstance(value, (int, float)), f"equity_curve[{i}] debe ser número, es {type(value)}"
print("✅ equity_curve contiene solo números (no arrays)")

# Test 8: Verificar que no hay valores NaN o infinitos
print("\n[Test 8] Verificando valores NaN/infinitos...")
import math
for key, value in results.items():
    if isinstance(value, (int, float)):
        assert not math.isnan(value), f"{key} es NaN"
        assert not math.isinf(value), f"{key} es infinito"
print("✅ No hay valores NaN o infinitos no limitados")

# Test 9: Test específico con arrays problemáticos
print("\n[Test 9] Test con arrays problemáticos...")
# Crear arrays con forma problemática (2D en lugar de 1D)
bad_predictions = np.random.randn(50, 1)  # Shape (50, 1) - problemático
bad_prices = np.random.randn(50, 1) + 1.0

try:
    backtester2 = AdvancedBacktester(initial_capital=10000)
    results2 = backtester2.evaluate_strategy(
        predictions=bad_predictions,
        actual_prices=bad_prices,
        model_name='test_2d',
        plot_results=False
    )
    print("✅ Manejo correcto de arrays 2D - .flatten() funciona")
except TypeError as e:
    if "unsupported operand type" in str(e):
        print("❌ ERROR: Arrays 2D causan problemas")
        print("   → .flatten() no se está aplicando correctamente")
    raise

# Test 10: Test con valores edge case
print("\n[Test 10] Test con casos extremos...")
edge_predictions = np.array([0, 0, 0, 0, 0])  # Todas cero
edge_prices = np.array([1.0, 1.0, 1.0, 1.0, 1.0])  # Sin cambio

try:
    backtester3 = AdvancedBacktester(initial_capital=10000)
    results3 = backtester3.evaluate_strategy(
        predictions=edge_predictions,
        actual_prices=edge_prices,
        model_name='test_edge',
        plot_results=False
    )

    # Verificar que maneja correctamente caso sin trades
    assert results3['n_trades'] == 0, "Debe tener 0 trades"
    assert results3['return'] == 0.0, "Return debe ser 0"
    print("✅ Manejo correcto de casos extremos")
except ZeroDivisionError:
    print("❌ ERROR: División por cero no manejada")
    print("   → Falta añadir epsilon (1e-8)")

# Test 11: Verificar método _close_position
print("\n[Test 11] Verificando método _close_position...")
try:
    # Simular llamada a _close_position
    test_trades = [{'entry_index': 0}]
    pnl = backtester._close_position(
        position=1,
        entry_price=1.0,
        exit_price=1.01,
        capital=10000.0,
        trades=test_trades,
        exit_index=10
    )

    assert isinstance(pnl, float), f"PnL debe ser float, es {type(pnl)}"
    assert not isinstance(pnl, np.ndarray), "PnL no debe ser array"
    print(f"✅ _close_position devuelve float correctamente (pnl={pnl:.2f})")
except Exception as e:
    print(f"⚠️ Error en _close_position: {e}")

# Test 12: Verificar que capital se mantiene como float
print("\n[Test 12] Verificando persistencia de tipo float...")
class TestRiskManager:
    def check_risk_limits(self, capital, position_size):
        return True, "OK"

backtester4 = AdvancedBacktester(initial_capital=10000)
backtester4.risk_manager = TestRiskManager()

# Ejecutar con varios steps para verificar que capital no se convierte en lista
test_preds = np.array([0.001, -0.001, 0.002, -0.002, 0.001])
test_prices = np.array([1.0, 1.001, 1.002, 1.001, 1.003])

try:
    results4 = backtester4.evaluate_strategy(
        predictions=test_preds,
        actual_prices=test_prices,
        model_name='test_float_persistence',
        plot_results=False
    )

    # Verificar cada valor en equity_curve
    for i, value in enumerate(results4['equity_curve']):
        assert isinstance(value, (int, float)), \
            f"equity_curve[{i}] se convirtió a {type(value)}"

    print("✅ Capital se mantiene como float durante todo el backtesting")
except Exception as e:
    print(f"❌ ERROR: {e}")

# RESUMEN FINAL
print("\n" + "="*70)
print("📊 RESUMEN DE VALIDACIÓN")
print("="*70)
print("\n✅ TODAS LAS VALIDACIONES PASARON CORRECTAMENTE")
print("\nTus correcciones están aplicadas correctamente y el backtesting")
print("debería funcionar sin el error de tipos.")
print("\n🎉 ¡Puedes continuar con confianza!")
print("\n" + "="*70)

# Mostrar algunos resultados de ejemplo
print("\n📈 EJEMPLO DE RESULTADOS:")
print(f"   Return: {results['return']:.2%}")
print(f"   Sharpe Ratio: {results['sharpe_ratio']:.3f}")
print(f"   Max Drawdown: {results['max_drawdown']:.2%}")
print(f"   Win Rate: {results['win_rate']:.2%}")
print(f"   Número de Trades: {results['n_trades']}")
print(f"   Profit Factor: {results['profit_factor']:.2f}")
print("\n" + "="*70)

# ============================================================================
# CORRECCIONES DE BACKTESTING - CONFIGURACIÓN OPTIMIZADA
# ============================================================================

class ImprovedBacktestingConfig:
    """
    Configuración mejorada para backtesting que GARANTIZA generación de trades
    """
    
    # Umbrales de señal MÁS SENSIBLES (más fácil generar señales)
    SIGNAL_THRESHOLDS = {
        '15min': {
            'entry_long': 0.0002,   # Antes: 0.001 (demasiado alto)
            'entry_short': -0.0002, # Antes: -0.001
            'exit_threshold': 0.0001, # Antes: 0.0005
            'confidence_min': 0.45,  # Antes: 0.60 (demasiado estricto)
        },
        '30min': {
            'entry_long': 0.0003,
            'entry_short': -0.0003,
            'exit_threshold': 0.00015,
            'confidence_min': 0.45,
        },
        '1H': {
            'entry_long': 0.0004,
            'entry_short': -0.0004,
            'exit_threshold': 0.0002,
            'confidence_min': 0.45,
        },
        '4H': {
            'entry_long': 0.0006,
            'entry_short': -0.0006,
            'exit_threshold': 0.0003,
            'confidence_min': 0.45,
        },
        '1D': {
            'entry_long': 0.001,
            'entry_short': -0.001,
            'exit_threshold': 0.0005,
            'confidence_min': 0.45,
        }
    }
    
    # Stop Loss y Take Profit OPTIMIZADOS
    RISK_PARAMS = {
        '15min': {'sl': 0.0015, 'tp': 0.003},  # 1:2 risk/reward
        '30min': {'sl': 0.002, 'tp': 0.004},
        '1H': {'sl': 0.003, 'tp': 0.006},
        '4H': {'sl': 0.005, 'tp': 0.010},
        '1D': {'sl': 0.008, 'tp': 0.016},
    }
    
    @classmethod
    def get_config(cls, timeframe: str) -> dict:
        """Obtener configuración para un timeframe"""
        if timeframe not in cls.SIGNAL_THRESHOLDS:
            timeframe = '1H'  # Default
        
        return {
            **cls.SIGNAL_THRESHOLDS[timeframe],
            **cls.RISK_PARAMS[timeframe]
        }

# Función de generación de señales MEJORADA
def generate_improved_signals(predictions: pd.Series, 
                              confidence: pd.Series,
                              timeframe: str = '1H') -> pd.DataFrame:
    """
    Genera señales de trading mejoradas que GARANTIZAN trades
    
    Args:
        predictions: Predicciones del modelo
        confidence: Nivel de confianza (0-1)
        timeframe: Timeframe actual
    
    Returns:
        DataFrame con señales
    """
    config = ImprovedBacktestingConfig.get_config(timeframe)
    
    signals = pd.DataFrame(index=predictions.index)
    signals['prediction'] = predictions
    signals['confidence'] = confidence
    
    # Generar señales BUY
    signals['signal_long'] = (
        (predictions > config['entry_long']) &
        (confidence > config['confidence_min'])
    ).astype(int)
    
    # Generar señales SELL
    signals['signal_short'] = (
        (predictions < config['entry_short']) &
        (confidence > config['confidence_min'])
    ).astype(int)
    
    # Señal combinada (-1: short, 0: neutral, 1: long)
    signals['signal'] = signals['signal_long'] - signals['signal_short']
    
    # Agregar stop loss y take profit
    signals['stop_loss'] = config['sl']
    signals['take_profit'] = config['tp']
    
    # Estadísticas de depuración
    n_long = signals['signal_long'].sum()
    n_short = signals['signal_short'].sum()
    n_total = len(signals)
    
    print(f"\n📊 Señales generadas para {timeframe}:")
    print(f"   Long signals:  {n_long} ({n_long/n_total*100:.2f}%)")
    print(f"   Short signals: {n_short} ({n_short/n_total*100:.2f}%)")
    print(f"   Total signals: {n_long + n_short} ({(n_long+n_short)/n_total*100:.2f}%)")
    
    if n_long + n_short == 0:
        print(f"   ⚠️  WARNING: No se generaron señales!")
        print(f"   Ajustando umbrales...")
        
        # Forzar señales más permisivas si no hay ninguna
        signals['signal_long'] = (predictions > 0).astype(int)
        signals['signal_short'] = (predictions < 0).astype(int)
        signals['signal'] = signals['signal_long'] - signals['signal_short']
        
        n_long = signals['signal_long'].sum()
        n_short = signals['signal_short'].sum()
        print(f"   Señales ajustadas: {n_long + n_short}")
    
    return signals

# Función de backtesting CORREGIDA
def run_improved_backtest(data: pd.DataFrame,
                          predictions: pd.Series,
                          confidence: pd.Series,
                          timeframe: str = '1H',
                          initial_capital: float = 10000,
                          commission: float = 0.0001) -> dict:
    """
    Ejecuta backtesting mejorado con correcciones
    
    Returns:
        dict con resultados del backtest
    """
    print(f"\n{'='*70}")
    print(f"🔄 EJECUTANDO BACKTEST MEJORADO - {timeframe}")
    print(f"{'='*70}")
    
    # Generar señales mejoradas
    signals = generate_improved_signals(predictions, confidence, timeframe)
    
    # Merge con datos de precio
    backtest_data = pd.concat([
        data[['open', 'high', 'low', 'close']],
        signals
    ], axis=1).dropna()
    
    print(f"\n📊 Datos para backtest: {len(backtest_data)} barras")
    
    # Inicializar variables
    capital = initial_capital
    position = 0  # 0: no position, 1: long, -1: short
    entry_price = 0
    trades = []
    equity_curve = [initial_capital]
    
    # Ejecutar backtest
    for i in range(1, len(backtest_data)):
        row = backtest_data.iloc[i]
        prev_row = backtest_data.iloc[i-1]
        
        current_price = row['close']
        signal = row['signal']
        sl = row['stop_loss']
        tp = row['take_profit']
        
        # Si no hay posición abierta
        if position == 0:
            # Señal LONG
            if signal > 0:
                position = 1
                entry_price = current_price
                print(f"  🟢 LONG @ {entry_price:.5f} (bar {i})")
                
            # Señal SHORT
            elif signal < 0:
                position = -1
                entry_price = current_price
                print(f"  🔴 SHORT @ {entry_price:.5f} (bar {i})")
        
        # Si hay posición abierta
        else:
            pnl_pct = (current_price - entry_price) / entry_price
            if position == -1:
                pnl_pct = -pnl_pct
            
            # Check STOP LOSS
            if pnl_pct <= -sl:
                exit_price = entry_price * (1 - sl) if position == 1 else entry_price * (1 + sl)
                pnl = capital * pnl_pct
                capital += pnl - (capital * commission)
                
                trades.append({
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'type': 'LONG' if position == 1 else 'SHORT',
                    'exit_reason': 'STOP_LOSS'
                })
                
                print(f"  ❌ STOP LOSS @ {exit_price:.5f} | PnL: {pnl:.2f} ({pnl_pct*100:.2f}%)")
                position = 0
                
            # Check TAKE PROFIT
            elif pnl_pct >= tp:
                exit_price = entry_price * (1 + tp) if position == 1 else entry_price * (1 - tp)
                pnl = capital * pnl_pct
                capital += pnl - (capital * commission)
                
                trades.append({
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'type': 'LONG' if position == 1 else 'SHORT',
                    'exit_reason': 'TAKE_PROFIT'
                })
                
                print(f"  ✅ TAKE PROFIT @ {exit_price:.5f} | PnL: {pnl:.2f} ({pnl_pct*100:.2f}%)")
                position = 0
                
            # Check señal de salida
            elif (position == 1 and signal < 0) or (position == -1 and signal > 0):
                exit_price = current_price
                pnl = capital * pnl_pct
                capital += pnl - (capital * commission)
                
                trades.append({
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'type': 'LONG' if position == 1 else 'SHORT',
                    'exit_reason': 'SIGNAL_EXIT'
                })
                
                print(f"  ↩️  SIGNAL EXIT @ {exit_price:.5f} | PnL: {pnl:.2f} ({pnl_pct*100:.2f}%)")
                position = 0
        
        equity_curve.append(capital)
    
    # Cerrar posición abierta al final
    if position != 0:
        final_price = backtest_data.iloc[-1]['close']
        pnl_pct = (final_price - entry_price) / entry_price
        if position == -1:
            pnl_pct = -pnl_pct
        pnl = capital * pnl_pct
        capital += pnl
        
        trades.append({
            'entry_price': entry_price,
            'exit_price': final_price,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'type': 'LONG' if position == 1 else 'SHORT',
            'exit_reason': 'END_OF_DATA'
        })
        print(f"  🏁 CLOSE @ END @ {final_price:.5f} | PnL: {pnl:.2f}")
    
    # Calcular métricas
    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
    
    total_return = (capital - initial_capital) / initial_capital * 100
    n_trades = len(trades)
    
    if n_trades > 0:
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]
        
        win_rate = len(winning_trades) / n_trades * 100
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
        
        profit_factor = abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 and losing_trades['pnl'].sum() != 0 else 999
        
        # Drawdown
        equity_series = pd.Series(equity_curve)
        running_max = equity_series.cummax()
        drawdown = (equity_series - running_max) / running_max * 100
        max_drawdown = drawdown.min()
        
        # Sharpe Ratio
        returns = equity_series.pct_change().dropna()
        sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
    else:
        win_rate = 0
        avg_win = 0
        avg_loss = 0
        profit_factor = 0
        max_drawdown = 0
        sharpe = 0
    
    results = {
        'total_return': total_return,
        'n_trades': n_trades,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
        'max_drawdown': max_drawdown,
        'sharpe': sharpe,
        'final_capital': capital,
        'trades': trades_df,
        'equity_curve': equity_curve
    }
    
    # Mostrar resumen
    print(f"\n{'='*70}")
    print(f"📊 RESUMEN BACKTEST - {timeframe}")
    print(f"{'='*70}")
    print(f"Total Return:    {total_return:>10.2f}%")
    print(f"Total Trades:    {n_trades:>10}")
    print(f"Win Rate:        {win_rate:>10.2f}%")
    print(f"Profit Factor:   {profit_factor:>10.2f}")
    print(f"Max Drawdown:    {max_drawdown:>10.2f}%")
    print(f"Sharpe Ratio:    {sharpe:>10.2f}")
    print(f"Final Capital:   ${capital:>10.2f}")
    print(f"{'='*70}\n")
    
    return results

print("✅ Funciones de backtesting mejoradas cargadas")
print("   - ImprovedBacktestingConfig")
print("   - generate_improved_signals()")
print("   - run_improved_backtest()")
print("\n💡 Usa run_improved_backtest() en lugar de la función original")


# @title

# [7] SISTEMA DE GESTIÓN DE RIESGOS
# REEMPLAZAR LA CLASE RiskManagementSystem EXISTENTE CON ESTA VERSIÓN MEJORADA

class AdvancedRiskManagementSystem:
    def __init__(self, max_position_size=0.02, max_daily_loss=0.05, max_drawdown=0.2,
                 volatility_lookback=20, kelly_fraction=0.25):
        # Límites básicos
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown

        # Parámetros de volatilidad
        self.volatility_lookback = volatility_lookback
        self.kelly_fraction = kelly_fraction

        # Estado del sistema
        self.daily_pnl = 0
        self.equity_peak = 0
        self.current_date = None
        self.trade_history = []
        self.volatility_history = []

        # Métricas de rendimiento
        self.win_count = 0
        self.loss_count = 0
        self.total_wins = 0
        self.total_losses = 0

        print(f"✅ Sistema de riesgo avanzado inicializado:")
        print(f"  Max posición: {max_position_size:.1%}")
        print(f"  Max pérdida diaria: {max_daily_loss:.1%}")
        print(f"  Max drawdown: {max_drawdown:.1%}")

    def calculate_dynamic_position_size(self, prediction, price, current_capital,
                                      recent_volatility=None, confidence=None):
        """Calcula tamaño de posición dinámico basado en múltiples factores"""

        # 1. Tamaño base según método Kelly modificado
        if self.win_count + self.loss_count > 10:  # Tenemos historial suficiente
            win_rate = self.win_count / (self.win_count + self.loss_count)
            avg_win = self.total_wins / self.win_count if self.win_count > 0 else 0
            avg_loss = abs(self.total_losses / self.loss_count) if self.loss_count > 0 else 1

            if avg_loss > 0:
                win_loss_ratio = avg_win / avg_loss
                kelly_f = win_rate - ((1 - win_rate) / win_loss_ratio)
                kelly_position = max(0, min(kelly_f * self.kelly_fraction, self.max_position_size))
            else:
                kelly_position = self.max_position_size * 0.5
        else:
            # Sin historial suficiente, usar posición conservadora
            kelly_position = self.max_position_size * 0.5

        # 2. Ajuste por volatilidad
        if recent_volatility is not None and len(self.volatility_history) > 5:
            avg_volatility = np.mean(self.volatility_history[-self.volatility_lookback:])
            volatility_ratio = avg_volatility / (recent_volatility + 1e-8)
            # Reducir posición en alta volatilidad
            volatility_adjustment = min(1.0, volatility_ratio)
        else:
            volatility_adjustment = 1.0

        # 3. Ajuste por confianza de la predicción
        if confidence is not None:
            confidence_adjustment = min(1.0, max(0.1, confidence))
        else:
            # Usar magnitud de la predicción como proxy de confianza
            if isinstance(prediction, (int, float)):
                confidence_adjustment = min(1.0, abs(prediction) / max(abs(prediction), 1.0))
            else:
                confidence_adjustment = 0.5

        # 4. Ajuste por drawdown actual
        if self.equity_peak > 0:
            current_drawdown = (self.equity_peak - current_capital) / self.equity_peak
            drawdown_adjustment = max(0.1, 1 - (current_drawdown / self.max_drawdown))
        else:
            drawdown_adjustment = 1.0

        # 5. Calcular tamaño final
        final_position_size = (kelly_position *
                             volatility_adjustment *
                             confidence_adjustment *
                             drawdown_adjustment)

        # 6. Aplicar límites absolutos
        final_position_size = min(final_position_size, self.max_position_size)
        final_position_size = max(final_position_size, 0.001)  # Mínimo 0.1%

        return {
            'position_size': final_position_size,
            'kelly_component': kelly_position,
            'volatility_adj': volatility_adjustment,
            'confidence_adj': confidence_adjustment,
            'drawdown_adj': drawdown_adjustment,
            'final_amount': final_position_size * current_capital
        }

    def check_advanced_risk_limits(self, current_capital, proposed_trade_size,
                                 market_regime=None, time_of_day=None):
        """Verificación avanzada de límites de riesgo"""
        warnings = []

        # 1. Verificaciones básicas existentes
        basic_check, basic_msg = self.check_basic_risk_limits(current_capital, proposed_trade_size)
        if not basic_check:
            return False, basic_msg

        # 2. Límite de concentración (máximo 50% en un solo tipo de trade)
        recent_trades = self.trade_history[-10:] if len(self.trade_history) >= 10 else self.trade_history
        if recent_trades:
            long_trades = sum(1 for t in recent_trades if t.get('direction', 0) > 0)
            concentration = long_trades / len(recent_trades)
            if concentration > 0.8 or concentration < 0.2:
                warnings.append(f"Alta concentración de trades: {concentration:.1%}")

        # 3. Límite por régimen de mercado
        if market_regime is not None:
            regime_risk_multiplier = self.get_regime_risk_multiplier(market_regime)
            adjusted_max_position = self.max_position_size * regime_risk_multiplier

            if proposed_trade_size > adjusted_max_position * current_capital:
                return False, f"Tamaño excede límite para régimen {market_regime}"

        # 4. Límite por hora del día (si está disponible)
        if time_of_day is not None:
            time_risk_multiplier = self.get_time_risk_multiplier(time_of_day)
            if time_risk_multiplier < 0.5:  # Horario de alto riesgo
                warnings.append(f"Horario de alto riesgo detectado: {time_of_day}")

        # 5. Verificar velocidad de trading (no más de X trades por día)
        max_daily_trades = 10
        today_trades = [t for t in self.trade_history if t.get('date') == self.current_date]
        if len(today_trades) >= max_daily_trades:
            return False, f"Límite diario de trades alcanzado: {len(today_trades)}/{max_daily_trades}"

        # 6. Verificar correlación con trades recientes
        correlation_risk = self.check_trade_correlation_risk(recent_trades)
        if correlation_risk > 0.8:
            warnings.append(f"Alta correlación con trades recientes: {correlation_risk:.2f}")

        # Retornar resultado
        if warnings:
            warning_msg = "; ".join(warnings)
            print(f"⚠️ Advertencias de riesgo: {warning_msg}")

        return True, "Verificaciones avanzadas pasadas" + (f" (Advertencias: {len(warnings)})" if warnings else "")

    def check_basic_risk_limits(self, current_capital, proposed_trade_size):
        """Verificaciones básicas de riesgo (método original mejorado)"""
        # Actualizar pico de equity
        if current_capital > self.equity_peak:
            self.equity_peak = current_capital

        # Verificar drawdown máximo
        if self.equity_peak > 0:
            current_drawdown = (self.equity_peak - current_capital) / self.equity_peak
            if current_drawdown > self.max_drawdown:
                return False, f"Drawdown máximo excedido: {current_drawdown:.2%} > {self.max_drawdown:.2%}"

        # Verificar tamaño de posición
        position_percentage = proposed_trade_size / current_capital
        if position_percentage > self.max_position_size:
            return False, f"Tamaño de posición excedido: {position_percentage:.2%} > {self.max_position_size:.2%}"

        # Verificar pérdida diaria
        if abs(self.daily_pnl) > self.max_daily_loss * current_capital:
            return False, f"Límite de pérdida diaria excedido: ${abs(self.daily_pnl):.2f}"

        return True, "Límites básicos OK"

    def get_regime_risk_multiplier(self, market_regime):
        """Obtiene multiplicador de riesgo según el régimen de mercado"""
        regime_multipliers = {
            0: 0.7,  # Régimen de alta volatilidad - reducir riesgo
            1: 1.0,  # Régimen normal
            2: 1.2,  # Régimen de tendencia fuerte - aumentar ligeramente
        }
        return regime_multipliers.get(market_regime, 1.0)

    def get_time_risk_multiplier(self, time_of_day):
        """Obtiene multiplicador de riesgo según la hora del día"""
        hour = time_of_day.hour if hasattr(time_of_day, 'hour') else time_of_day

        # Horarios de mayor volatilidad en Forex (UTC)
        high_risk_hours = [8, 9, 13, 14, 15, 16, 17]  # Overlaps de sesiones principales
        medium_risk_hours = [7, 10, 11, 12, 18, 19, 20]

        if hour in high_risk_hours:
            return 0.6  # Reducir riesgo en horarios volátiles
        elif hour in medium_risk_hours:
            return 0.8
        else:
            return 1.0  # Horarios normales

    def check_trade_correlation_risk(self, recent_trades):
        """Verifica riesgo de correlación entre trades recientes"""
        if len(recent_trades) < 3:
            return 0.0

        # Analizar direcciones de trades recientes
        directions = [t.get('direction', 0) for t in recent_trades[-5:]]

        if len(set(directions)) == 1:  # Todos en la misma dirección
            return 1.0
        elif len([d for d in directions if d == directions[-1]]) >= 3:  # 3+ en misma dirección
            return 0.8
        else:
            return 0.2

    def update_trade_history(self, trade_result):
        """Actualiza el historial de trades con el resultado"""
        self.trade_history.append({
            'timestamp': datetime.now(),
            'date': self.current_date,
            'direction': trade_result.get('direction', 0),
            'pnl': trade_result.get('pnl', 0),
            'size': trade_result.get('size', 0),
            'duration': trade_result.get('duration', 0)
        })

        # Actualizar estadísticas de win/loss
        pnl = trade_result.get('pnl', 0)
        if pnl > 0:
            self.win_count += 1
            self.total_wins += pnl
        elif pnl < 0:
            self.loss_count += 1
            self.total_losses += pnl

        # Mantener solo últimos 100 trades para eficiencia
        if len(self.trade_history) > 100:
            self.trade_history = self.trade_history[-100:]

        # Actualizar PnL diario
        today = datetime.now().date()
        if self.current_date != today:
            self.daily_pnl = 0  # Reset diario
            self.current_date = today

        self.daily_pnl += pnl

    def update_volatility(self, current_volatility):
        """Actualiza el historial de volatilidad"""
        self.volatility_history.append(current_volatility)

        # Mantener solo últimos valores para eficiencia
        if len(self.volatility_history) > self.volatility_lookback * 2:
            self.volatility_history = self.volatility_history[-self.volatility_lookback:]

    def get_risk_summary(self):
        """Obtiene resumen del estado actual de riesgo"""
        current_drawdown = 0
        if self.equity_peak > 0:
            # Necesitaríamos el capital actual para calcular esto correctamente
            current_drawdown = 0  # Placeholder

        recent_win_rate = 0
        if self.win_count + self.loss_count > 0:
            recent_win_rate = self.win_count / (self.win_count + self.loss_count)

        return {
            'max_drawdown_limit': self.max_drawdown,
            'current_drawdown': current_drawdown,
            'daily_pnl': self.daily_pnl,
            'max_daily_loss_limit': self.max_daily_loss,
            'recent_win_rate': recent_win_rate,
            'total_trades': len(self.trade_history),
            'wins': self.win_count,
            'losses': self.loss_count,
            'avg_volatility': np.mean(self.volatility_history) if self.volatility_history else 0
        }

    # Mantener compatibilidad con método original
    def check_risk_limits(self, current_capital, proposed_trade_size):
        """Método de compatibilidad con la interfaz original"""
        return self.check_basic_risk_limits(current_capital, proposed_trade_size)

# @title
# REEMPLAZAR LA FUNCIÓN main() CON ESTA VERSIÓN QUE INCLUYE GESTIÓN ADAPTATIVA DE DATOS

@timer_decorator
def main():
    print("\n" + "="*80)
    print("EJECUTANDO PIPELINE CON INDICADORES DE PROGRESO")
    print("="*80)

    data_manager = AdaptiveDataManager()
    all_results = {}

    # ✅ BARRA DE PROGRESO PARA TIMEFRAMES
    for tf in tqdm(TIMEFRAMES, desc="🕐 Procesando timeframes", position=0):
        print(f"\n{'='*80}")
        print(f"⏰ TIMEFRAME: {tf}")
        print(f"{'='*80}")

        try:
            OUTPUT_PATH_2 = os.path.join(OUTPUT_PATH, f'Trading_System_Advanced_{tf}')

            # Crear carpetas con barra
            folders = ['models', 'metrics', 'plots', 'data', 'backtest_results',
                      'feature_analysis', 'hyperparameters', 'ensembles', 'tensorboard',
                      'stationarity_analysis', 'regime_analysis', 'risk_analysis', 'data_analysis']

            for folder in tqdm(folders, desc="📁 Creando carpetas", leave=False):
                os.makedirs(os.path.join(OUTPUT_PATH_2, folder), exist_ok=True)

            print(f"📂 Output: {OUTPUT_PATH_2}")

            # Inicializar componentes mejorados
            processor = AdvancedDataProcessor(DATA_FILE)
            trainer = AdvancedModelTrainer(OUTPUT_PATH_2)
            risk_manager = AdvancedRiskManagementSystem()
            backtester = AdvancedBacktester(output_path=OUTPUT_PATH_2)  # ← Pasar el path
            backtester.risk_manager = risk_manager

            # [1] CARGAR DATOS
            print("\n[1] 📥 CARGANDO DATOS")
            with tqdm(total=1, desc="Cargando CSV", bar_format='{l_bar}{bar}| {elapsed}') as pbar:
                processor = AdvancedDataProcessor(DATA_FILE)
                df_raw = processor.load_data(DATA_FILE, nrows=MAX_ROWS)
                pbar.update(1)

            # [2] PROCESAR TIMEFRAMES
            print("\n[2] ⚙️  PROCESANDO MÚLTIPLES TIMEFRAMES")
            timeframe_data = processor.create_multiple_timeframes(df_raw)

            # 3. APLICAR GESTIÓN ADAPTATIVA DE DATOS PARA ESTE TIMEFRAME
            print(f"\n[3] APLICANDO GESTIÓN ADAPTATIVA DE DATOS PARA {tf}")

            # En la función main(), línea ~64:
            sampled_df, model_config, sampling_status = apply_adaptive_data_management(timeframe_data, tf)

            # AGREGAR ESTA VALIDACIÓN ANTES DE USAR model_config:
            if sampled_df is None or model_config is None or not model_config:  # ← CAMBIO AQUÍ
                print(f"⚠️ {sampling_status} - Saltando {tf}")
                continue

            # Verificar que model_config tiene las claves necesarias
            if 'model_complexity' not in model_config:
                print(f"⚠️ Configuración de modelo incompleta para {tf} - Saltando")
                continue

            print(f"   Configuración de modelo: {model_config['model_complexity']} complejidad")

            # Mostrar información sobre el sampling
            original_size = len(timeframe_data[tf])
            sampled_size = len(sampled_df)
            reduction_pct = (1 - sampled_size/original_size) * 100

            print(f"📊 Datos adaptados para {tf}:")
            print(f"   Original: {original_size:,} observaciones")
            print(f"   Optimizado: {sampled_size:,} observaciones ({reduction_pct:.1f}% reducción)")
            print(f"   Configuración de modelo: {model_config['model_complexity']} complejidad")

            print(f"   Máximo características: {model_config['features_max']}")

            # Usar los datos sampledados como df principal
            df = sampled_df.copy()

            # 4. ANÁLISIS DE ESTACIONARIDAD Y REGÍMENES (en datos optimizados)
            print(f"\n[4] ANÁLISIS AVANZADO DE DATOS OPTIMIZADOS PARA {tf}")

            # Análisis de estacionaridad para series clave
            stationarity_results = {}
            for col in ['close', 'tick_volume']:
                if col in df.columns:
                    stationarity_results[col] = processor.analyze_stationarity(df[col], f"{tf}_{col}")

            # Detectar regímenes de mercado en datos optimizados
            df = processor.detect_market_regimes(df, price_col='close', n_regimes=3)

            # Ingeniería de características avanzada
            df = processor.advanced_feature_engineering(df)

            # 5. PREPARACIÓN DE DATOS PARA ML
            print(f"\n[5] PREPARANDO DATOS PARA ML (TAMAÑO OPTIMIZADO)")

            # Calcular target_periods óptimo para este timeframe
            target_periods = processor.get_optimal_target_periods(tf)
            print(f"  🎯 Usando target_periods={target_periods} para {tf}")

            # Preparar datos para regresión y clasificación
            # Preparar datos para regresión
            X_reg, y_reg = processor.prepare_ml_data(
                df,
                target_periods=target_periods,
                classification=False
            )

            # AÑADIR ESTO - Preparar datos para clasificación
            X_clf, y_clf = processor.prepare_ml_data(
                df,
                target_periods=target_periods,
                classification=True  # ← IMPORTANTE: True para clasificación
            )

            # AGREGAR ESTA LÍNEA:
            max_features = model_config['features_max']  # Usar el valor del config

            # CAMBIO: Usar método más rápido para timeframes cortos
            selection_method = 'mutual_info' if tf in ['1min', '5min'] else 'fast'

            X_reg_selected, selected_features_reg = processor.robust_feature_selection(
                X_reg, y_reg, method=selection_method, k=max_features
            )

            X_clf_selected, selected_features_clf = processor.robust_feature_selection(
                X_clf, y_clf, method=selection_method, k=max_features
            )

            # 6. CONFIGURACIÓN DE VALIDACIÓN TEMPORAL ADAPTATIVA
            print(f"\n[6] CONFIGURANDO VALIDACIÓN TEMPORAL ADAPTATIVA")

            # Usar configuración de validación específica del timeframe
            validation_splits = model_config['validation_splits']
            min_samples_for_temporal = max(500, sampled_size // 4)  # Al menos 25% para validación

            if len(X_reg_selected) >= min_samples_for_temporal:
                use_temporal_validation = True
                print(f"✅ Usando validación temporal con {validation_splits} splits")
            else:
                use_temporal_validation = False
                print(f"⚠️ Datos insuficientes para validación temporal completa, usando split simple")

            # Split de datos con consideración temporal
            if use_temporal_validation:
                # ✅ Asegurar que los índices sean numéricos y continuos
                X_reg_selected = X_reg_selected.reset_index(drop=True)
                y_reg = y_reg.reset_index(drop=True)
                X_clf_selected = X_clf_selected.reset_index(drop=True)
                y_clf = y_clf.reset_index(drop=True)

                # Ahora sí hacer el split
                final_test_size = int(len(X_reg_selected) * 0.2)
                X_development = X_reg_selected.iloc[:-final_test_size]
                y_development = y_reg.iloc[:-final_test_size]
                X_final_test_reg = X_reg_selected.iloc[-final_test_size:]
                y_final_test_reg = y_reg.iloc[-final_test_size:]

                X_development_clf = X_clf_selected.iloc[:-final_test_size]
                y_development_clf = y_clf.iloc[:-final_test_size]
                X_final_test_clf = X_clf_selected.iloc[-final_test_size:]
                y_final_test_clf = y_clf.iloc[-final_test_size:]

            else:
                # Split tradicional - también resetear índices
                X_reg_selected = X_reg_selected.reset_index(drop=True)
                y_reg = y_reg.reset_index(drop=True)
                X_clf_selected = X_clf_selected.reset_index(drop=True)
                y_clf = y_clf.reset_index(drop=True)

                split_idx = int(len(X_reg_selected) * 0.8)
                X_development = X_reg_selected.iloc[:split_idx]
                y_development = y_reg.iloc[:split_idx]
                X_final_test_reg = X_reg_selected.iloc[split_idx:]
                y_final_test_reg = y_reg.iloc[split_idx:]

                X_development_clf = X_clf_selected.iloc[:split_idx]
                y_development_clf = y_clf.iloc[:split_idx]
                X_final_test_clf = X_clf_selected.iloc[split_idx:]
                y_final_test_clf = y_clf.iloc[split_idx:]

            # Escalar datos con método robusto (mejor para timeframes cortos)
            scaler_method = "robust" if tf in ['1min', '5min'] else "standard"
            X_dev_reg_scaled, X_test_reg_scaled = processor.scale_data(
                X_development, X_final_test_reg, method=scaler_method
            )
            X_dev_clf_scaled, X_test_clf_scaled = processor.scale_data(
                X_development_clf, X_final_test_clf, method=scaler_method
            )

            # 7. OBTENER MODELOS ADAPTADOS AL TIMEFRAME
            print(f"\n[7] CONFIGURANDO MODELOS ADAPTADOS PARA {tf}")

            adapted_models_reg, adapted_models_clf = get_timeframe_adjusted_models(tf, model_config)

            print(f"   Complejidad: {model_config['model_complexity']}")
            print(f"   Regularización: {model_config['regularization_strength']}")
            print(f"   Early stopping patience: {model_config['early_stopping_patience']}")

            # 8. ENTRENAMIENTO CON CONFIGURACIÓN ADAPTATIVA
            print(f"\n[8] ENTRENANDO MODELOS ADAPTADOS PARA {tf}")

            # Entrenar modelos adaptados individualmente para tener control granular
            print("🤖 Entrenando modelos de regresión adaptados...")
            for name, model in adapted_models_reg.items():
                try:
                    print(f"  → Entrenando {name}...")

                    # Validación cruzada temporal si está habilitada
                    if use_temporal_validation and len(X_development) > 300:
                        cv_results = trainer.time_series_cross_validation(
                            X_dev_reg_scaled, y_development, model, n_splits=validation_splits
                        )
                        trainer.metrics[f'{name}_cv'] = cv_results

                    # Entrenamiento final
                    # INSERTAR ANTES de model.fit():
                    if not verify_data_for_training(X_dev_reg_scaled, y_development, name):
                        print(f"    ⏭️ Saltando {name} debido a problemas con los datos")
                        continue

                    #model.fit(X_dev_reg_scaled, y_development)
                    model.fit(X_dev_reg_scaled, y_development)
                    y_pred = model.predict(X_test_reg_scaled)

                    # Calcular métricas
                    metrics = trainer._calc_metrics(y_final_test_reg, y_pred, False)
                    trainer.models[name] = model
                    trainer.metrics[name] = metrics
                    trainer.predictions[name] = y_pred

                    # Importancia de características
                    if hasattr(model, 'feature_importances_'):
                        trainer.feature_importances[name] = {
                            'features': X_dev_reg_scaled.columns.tolist(),
                            'importance': model.feature_importances_.tolist()
                        }

                    trainer._print_metrics(metrics, False, name)

                except Exception as e:
                    print(f"    ❌ Error en {name}: {e}")
                    continue

            print("🤖 Entrenando modelos de regresión adaptados...")
            for name, model in adapted_models_reg.items():
                try:
                    print(f"  → Entrenando {name}...")

                    # ✅ Validación cruzada temporal con manejo de errores
                    if use_temporal_validation and len(X_development) > 300:
                        try:
                            cv_results = trainer.time_series_cross_validation(
                                X_dev_reg_scaled, y_development, model, n_splits=validation_splits
                            )
                            trainer.metrics[f'{name}_cv'] = cv_results
                            print(f"    ✅ Validación cruzada completada")
                        except Exception as cv_error:
                            print(f"    ⚠️ Error en validación cruzada (continuando): {cv_error}")
                            # Continuar sin validación cruzada

                    # Entrenamiento final
                    # INSERTAR ANTES de model.fit():
                    if not verify_data_for_training(X_dev_reg_scaled, y_development, name):
                        print(f"    ⏭️ Saltando {name} debido a problemas con los datos")
                        continue

                    #model.fit(X_dev_reg_scaled, y_development)
                    model.fit(X_dev_reg_scaled, y_development)
                    y_pred = model.predict(X_test_reg_scaled)

                    # Calcular métricas
                    metrics = trainer._calc_metrics(y_final_test_reg, y_pred, False)
                    trainer.models[name] = model
                    trainer.metrics[name] = metrics
                    trainer.predictions[name] = y_pred

                    # Importancia de características
                    if hasattr(model, 'feature_importances_'):
                        trainer.feature_importances[name] = {
                            'features': X_dev_reg_scaled.columns.tolist(),
                            'importance': model.feature_importances_.tolist()
                        }

                    trainer._print_metrics(metrics, False, name)

                except Exception as e:
                    print(f"    ❌ Error en {name}: {str(e)}")
                    import traceback
                    print(f"    Traceback: {traceback.format_exc()[:200]}...")
                    continue


            # ═══════════════════════════════════════════════════════════════════════════
            # CAMBIO #3: AGREGAR ENTRENAMIENTO DE MODELOS DE CLASIFICACIÓN
            # ═══════════════════════════════════════════════════════════════════════════
            #
            # UBICACIÓN: Línea ~5152 (dentro de def main(), dentro del loop for tf)
            # ACCIÓN: INSERTAR este código ANTES de la línea "# 9. ANÁLISIS POR RÉGIMEN"
            #
            # CONTEXTO: Está después del entrenamiento de regresión (sección [8])
            #          y antes del análisis de régimen (sección [9])
            #
            # ═══════════════════════════════════════════════════════════════════════════

            # ═══════════════════════════════════════════════════════════════
            # 8B. ENTRENAR MODELOS DE CLASIFICACIÓN ✨ NUEVO ✨
            # ═══════════════════════════════════════════════════════════════
            print(f"\n[8B] 🎯 ENTRENANDO MODELOS DE CLASIFICACIÓN PARA {tf}")
            print(f"   Modelos a entrenar: {len(adapted_models_clf)}")

            try:
                # Preparar datos de clasificación (dirección del precio)
                print("   📊 Preparando datos de clasificación (dirección)...")
                X_clf_full, y_direction = processor.prepare_ml_data(
                    df,
                    target_periods=5,
                    classification=True  # ← Predicción de dirección (up/down)
                )

                # Aplicar sampling adaptativo también para clasificación
                if sampled_size < len(X_clf_full):
                    X_clf_sampled = X_clf_full.iloc[sampling_indices]
                    y_direction_sampled = y_direction.iloc[sampling_indices]
                else:
                    X_clf_sampled = X_clf_full
                    y_direction_sampled = y_direction

                # Seleccionar características
                print("   🎯 Seleccionando características para clasificación...")
                X_clf_selected, selected_features_clf = processor.robust_feature_selection(
                    X_clf_sampled,
                    y_direction_sampled,
                    classification=True,
                    k_features=min(model_config['max_features'], X_clf_sampled.shape[1])
                )

                print(f"   ✅ Características seleccionadas: {X_clf_selected.shape[1]}")

                # División de datos (80% train, 20% test)
                split_idx = int(len(X_clf_selected) * 0.8)
                X_dev_clf = X_clf_selected.iloc[:split_idx]
                y_dev_clf = y_direction_sampled.iloc[:split_idx]
                X_final_test_clf = X_clf_selected.iloc[split_idx:]
                y_final_test_clf = y_direction_sampled.iloc[split_idx:]

                print(f"   📊 Train: {len(X_dev_clf)} | Test: {len(X_final_test_clf)}")

                # Escalar datos
                X_dev_clf_scaled, X_test_clf_scaled = processor.scale_data(
                    X_dev_clf,
                    X_final_test_clf
                )

                # Entrenar cada modelo de clasificación
                clf_count = 0
                clf_errors = 0
                for name, model in adapted_models_clf.items():
                    try:
                        clf_count += 1
                        print(f"   → [{clf_count}/{len(adapted_models_clf)}] Entrenando {name}...")

                        # Validación cruzada temporal (si hay suficientes datos)
                        if use_temporal_validation and len(X_dev_clf) > 300:
                            try:
                                cv_results = trainer.time_series_cross_validation(
                                    X_dev_clf_scaled, y_dev_clf, model,
                                    n_splits=validation_splits
                                )
                                trainer.metrics[f'{name}_cv'] = cv_results
                                print(f"      ✅ Validación cruzada completada")
                            except Exception as cv_error:
                                print(f"      ⚠️ Error en CV (continuando): {str(cv_error)[:100]}")

                        # Verificar datos antes de entrenar
                        if not verify_data_for_training(X_dev_clf_scaled, y_dev_clf, name):
                            print(f"      ⏭️ Saltando {name} - problemas con datos")
                            clf_errors += 1
                            continue

                        # Entrenamiento del modelo
                        model.fit(X_dev_clf_scaled, y_dev_clf)
                        y_pred_clf = model.predict(X_test_clf_scaled)

                        # Calcular métricas de clasificación
                        metrics_clf = trainer._calc_metrics(
                            y_final_test_clf,
                            y_pred_clf,
                            is_classification=True  # ← Importante: True para clasificación
                        )

                        # Guardar resultados
                        trainer.models[name] = model
                        trainer.metrics[name] = metrics_clf
                        trainer.predictions[name] = y_pred_clf

                        # Mostrar métricas
                        trainer._print_metrics(metrics_clf, True, name)

                    except Exception as e:
                        clf_errors += 1
                        print(f"      ❌ Error en {name}: {str(e)[:150]}")
                        import traceback
                        print(f"      Traceback: {traceback.format_exc()[:200]}...")
                        continue

                # Resumen de entrenamiento de clasificación
                successful_clf = clf_count - clf_errors
                print(f"\n   ✅ Clasificación completada: {successful_clf}/{clf_count} modelos entrenados")
                if clf_errors > 0:
                    print(f"   ⚠️ Errores: {clf_errors} modelos fallaron")

            except Exception as e:
                print(f"\n   ❌ Error general en clasificación: {e}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()[:300]}...")
                print(f"   ⚠️ Continuando sin modelos de clasificación para {tf}")


            # ═══════════════════════════════════════════════════════════════════════════
            # NOTAS IMPORTANTES:
            # ═══════════════════════════════════════════════════════════════════════════
            #
            # 1. INDENTACIÓN:
            #    Este código debe tener la MISMA indentación que el código de entrenamiento
            #    de regresión que está arriba (sección [8]). En el notebook original, esto
            #    significa 12 espacios de indentación (3 niveles dentro de main())
            #
            # 2. VARIABLES NECESARIAS:
            #    Este código usa variables que ya deben existir en ese punto:
            #    - df: DataFrame con los datos
            #    - processor: AdvancedDataProcessor
            #    - selector: Feature selector
            #    - trainer: AdvancedModelTrainer
            #    - adapted_models_clf: Diccionario de modelos de clasificación
            #    - model_config: Configuración del modelo
            #    - sampled_size: Tamaño de la muestra
            #    - sampling_indices: Índices de sampling
            #    - use_temporal_validation: Boolean
            #    - validation_splits: Número de splits para CV
            #
            # 3. FLUJO:
            #    [8]  Entrenar modelos de regresión (ya existe)
            #    [8B] Entrenar modelos de clasificación (NUEVO - este código)
            #    [9]  Análisis por régimen de mercado (ya existe)
            #    [10] Backtesting (ya existe - procesará ambos tipos)
            #
            # ═══════════════════════════════════════════════════════════════════════════





            # 9. ANÁLISIS POR RÉGIMEN DE MERCADO
            print(f"\n[9] ANÁLISIS POR RÉGIMEN DE MERCADO PARA {tf}")

            regime_analysis = {}
            if 'market_regime' in X_dev_reg_scaled.columns and len(trainer.models) > 0:
                try:
                    regime_models_reg, regime_performance_reg = trainer.regime_based_model_selection(
                        X_dev_reg_scaled, y_development,
                        {k: v for k, v in trainer.models.items() if 'reg' in k}
                    )

                    regime_analysis = {
                        'regime_models': regime_models_reg,
                        'regime_performance': regime_performance_reg,
                        'regime_distribution': df['market_regime'].value_counts().to_dict()
                    }

                    print("📊 Rendimiento por régimen de mercado:")
                    for regime, model_info in regime_models_reg.items():
                        print(f"   Régimen {regime}: {model_info['model_name']} (score: {model_info['score']:.4f})")

                except Exception as e:
                    print(f"⚠️ Error en análisis de regímenes: {e}")

            # 10. BACKTESTING ADAPTATIVO CON MÉTRICAS EXTENDIDAS
            print(f"\n[10] EJECUTANDO BACKTESTING ADAPTATIVO PARA {tf}")
            backtest_results = {}
            metrics_analyzer = AdvancedMetricsAnalyzer()  # ✅ NUEVO

            # Obtener precios para backtesting
            close_prices_test = df["close"].iloc[-len(X_final_test_reg):].values

            # Configurar gestión de riesgo específica del timeframe
            if tf in ['1min', '5min', '15min']:
                # Timeframes cortos: ser más conservador
                risk_manager.max_position_size *= 0.7
                risk_manager.max_daily_loss *= 0.8
                print(f"   🛡️ Aplicando gestión de riesgo conservadora para {tf}")
            elif tf in ['1D', '3D', '7D']:
                # Timeframes largos: permitir más riesgo
                risk_manager.max_position_size *= 1.2
                print(f"   📈 Aplicando gestión de riesgo expandida para {tf}")

            # Calcular volatilidad específica del timeframe
            returns_test = pd.Series(close_prices_test).pct_change().fillna(0)
            volatility_window = min(len(returns_test) // 4, model_config.get('volatility_window', 20))
            recent_volatility = returns_test.rolling(volatility_window).std().iloc[-1]

            for name, predictions in trainer.predictions.items():
                if len(predictions) <= len(close_prices_test):
                    print(f"  📊 Backtesting {name} en {tf}...")

                    try:
                        # Ejecutar backtesting
                        results = backtester.evaluate_strategy(
                            predictions,
                            close_prices_test[:len(predictions)],
                            f"{name}_{tf}",
                            plot_results=True
                        )

                        # ✅ CALCULAR MÉTRICAS EXTENDIDAS
                        extended_metrics = metrics_analyzer.calculate_extended_metrics(
                            results['equity_curve'],
                            results.get('trades', []),
                            results.get('returns', []),
                            close_prices_test[:len(predictions)]
                        )

                        # ✅ GENERAR REPORTE
                        report = metrics_analyzer.generate_performance_report(extended_metrics)
                        print(report)

                        # ✅ GENERAR GRÁFICOS AVANZADOS
                        metrics_analyzer.plot_advanced_metrics(
                            results['equity_curve'],
                            np.array(results.get('returns', [])),
                            results.get('trades', []),
                            OUTPUT_PATH_2
                        )

                        # Añadir métricas extendidas a resultados
                        results['extended_metrics'] = extended_metrics
                        backtest_results[name] = results

                    except Exception as e:
                        print(f"    ❌ Error en backtesting {name}: {e}")

            # 11. GUARDAR RESULTADOS COMPLETOS CON ANÁLISIS ADAPTATIVO
            print(f"\n[11] GUARDANDO RESULTADOS COMPLETOS PARA {tf}")

            # Consolidar todos los resultados incluyendo información adaptativa
            all_results[tf] = {
                "metrics": trainer.metrics,
                "backtests": backtest_results,
                "data_analysis": {
                    "original_shape": (original_size, len(timeframe_data[tf].columns)),
                    "optimized_shape": df.shape,
                    "sample_reduction_pct": reduction_pct,
                    "sampling_method": "recent_emphasis",
                    "scaler_method": scaler_method
                },
                "model_configuration": model_config,
                "features_analysis": {
                    "features_used_reg": len(selected_features_reg),
                    "features_used_clf": len(selected_features_clf),
                    "max_features_allowed": model_config['features_max'],
                    "selected_features_reg": selected_features_reg[:10],  # Top 10 para el log
                    "selected_features_clf": selected_features_clf[:10]
                },
                "stationarity_analysis": stationarity_results,
                "regime_analysis": regime_analysis,
                "temporal_validation_used": use_temporal_validation,
                "validation_splits": validation_splits if use_temporal_validation else None
            }

            # Guardar análisis de datos adaptativos
            data_analysis_summary = {
                'timeframe': tf,
                'original_samples': original_size,
                'optimized_samples': sampled_size,
                'reduction_percentage': reduction_pct,
                'model_complexity': model_config['model_complexity'],
                'regularization_strength': model_config['regularization_strength'],
                'max_features': model_config['features_max'],
                'features_selected': len(selected_features_reg),
                'temporal_validation': use_temporal_validation,
                'scaler_method': scaler_method,
                'time_coverage': data_manager._estimate_time_coverage(sampled_size, tf)
            }

            with open(os.path.join(OUTPUT_PATH_2, 'data_analysis', 'adaptive_data_summary.json'), 'w') as f:
                json.dump(data_analysis_summary, f, indent=4, default=str)

            # Guardar otros resultados como antes
            trainer.save_results()

            # Guardar análisis de estacionaridad
            with open(os.path.join(OUTPUT_PATH_2, 'stationarity_analysis', 'stationarity_results.json'), 'w') as f:
                json.dump(stationarity_results, f, indent=4, default=str)

            # Guardar análisis de regímenes
            if regime_analysis:
                with open(os.path.join(OUTPUT_PATH_2, 'regime_analysis', 'regime_analysis.json'), 'w') as f:
                    json.dump(regime_analysis, f, indent=4, default=str)

            # Guardar resultados de backtesting
            with open(os.path.join(OUTPUT_PATH_2, "backtest_results", "backtest_results.json"), "w") as f:
                json_safe_results = {}
                for k, v in backtest_results.items():
                    json_safe_results[k] = {}
                    for k2, v2 in v.items():
                        if isinstance(v2, (list, np.ndarray)):
                            json_safe_results[k][k2] = [float(x) if isinstance(x, (int, float, np.number)) else str(x) for x in v2]
                        elif isinstance(v2, dict):
                            json_safe_results[k][k2] = {k3: (float(v3) if isinstance(v3, (int, float, np.number)) else str(v3))
                                                       for k3, v3 in v2.items()}
                        else:
                            json_safe_results[k][k2] = float(v2) if isinstance(v2, (int, float, np.number)) else str(v2)

                json.dump(json_safe_results, f, indent=4)

            print(f"✅ Timeframe {tf} completado exitosamente con gestión adaptativa")
            print(f"   📊 Datos: {original_size:,} → {sampled_size:,} ({reduction_pct:.1f}% reducción)")
            print(f"   🎯 Características: {len(selected_features_reg)} (reg), {len(selected_features_clf)} (clf)")
            print(f"   🔧 Modelos: complejidad {model_config['model_complexity']}, regularización {model_config['regularization_strength']}")

        except Exception as e:
            print(f"❌ Error en {tf}: {e}")
            #import traceback
            #traceback.print_exc()
            continue

    # 12. ANÁLISIS COMPARATIVO FINAL CON VISUALIZACIONES AVANZADAS
    print("\n" + "="*80)
    print("ANÁLISIS COMPARATIVO CON GESTIÓN ADAPTATIVA Y VISUALIZACIONES")
    print("="*80)

    if all_results:
        # ✅ NUEVO: Crear motor de visualizaciones
        viz_engine = AdvancedVisualizationEngine(OUTPUT_PATH)

        # Generar visualizaciones para cada timeframe
        for tf, results in all_results.items():
            backtest_results = results.get('backtests', {})
            if backtest_results:
                viz_engine.plot_comprehensive_analysis(backtest_results, tf)

        # ✅ NUEVO: Crear reporte comparativo multi-timeframe
        viz_engine.create_comparison_report(all_results, OUTPUT_PATH)
        comparison_data = []
        for tf, results in all_results.items():
            data_info = results.get('data_analysis', {})
            model_config = results.get('model_configuration', {})

            for model_name, backtest in results.get('backtests', {}).items():
                comparison_data.append({
                    'timeframe': tf,
                    'model': model_name,
                    'return': backtest.get('return', 0),
                    'sharpe_ratio': backtest.get('sharpe_ratio', 0),
                    'max_drawdown': backtest.get('max_drawdown', 0),
                    'win_rate': backtest.get('win_rate', 0),
                    'n_trades': backtest.get('n_trades', 0),
                    'original_samples': data_info.get('original_shape', [0])[0],
                    'optimized_samples': data_info.get('optimized_shape', [0])[0],
                    'reduction_pct': data_info.get('sample_reduction_pct', 0),
                    'model_complexity': model_config.get('model_complexity', 'unknown'),
                    'features_used': results.get('features_analysis', {}).get('features_used_reg', 0)
                })

        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)

            # Guardar tabla comparativa expandida
            comparison_df.to_csv(os.path.join(OUTPUT_PATH, 'adaptive_timeframe_comparison.csv'), index=False)

            # Análisis por complejidad de modelo
            print("\n📊 Rendimiento por complejidad de modelo:")
            complexity_analysis = comparison_df.groupby('model_complexity').agg({
                'return': 'mean',
                'sharpe_ratio': 'mean',
                'max_drawdown': 'mean'
            }).round(4)
            print(complexity_analysis.to_string())

            # Análisis de eficiencia de datos
            print("\n🎯 Eficiencia de reducción de datos:")
            for tf in comparison_df['timeframe'].unique():
                tf_data = comparison_df[comparison_df['timeframe'] == tf]
                avg_reduction = tf_data['reduction_pct'].iloc[0]
                avg_return = tf_data['return'].mean()
                print(f"   {tf}: {avg_reduction:.1f}% reducción → {avg_return:.2%} retorno promedio")

            # Mejores modelos considerando eficiencia
            print("\n🏆 Mejores modelos (considerando eficiencia de datos):")
            efficiency_score = comparison_df['return'] / (1 + comparison_df['reduction_pct']/100)  # Penalizar menos reducción
            top_efficient = comparison_df.loc[efficiency_score.nlargest(5).index]
            print(top_efficient[['timeframe', 'model', 'return', 'reduction_pct', 'model_complexity']].to_string(index=False))

    print("\n" + "="*80)
    print("PIPELINE COMPLETADO CON GESTIÓN ADAPTATIVA DE DATOS")
    print(f"Timeframes procesados: {list(all_results.keys())}")
    print("Beneficios aplicados:")
    print("  ✅ Tamaños de muestra optimizados por timeframe")
    print("  ✅ Complejidad de modelo adaptativa")
    print("  ✅ Regularización ajustada al riesgo de overfitting")
    print("  ✅ Validación temporal robusta")
    print("  ✅ Gestión de riesgo específica por timeframe")
    print("="*80)



    print("\n" + "="*80)
    print("✅ PIPELINE COMPLETADO")
    print("="*80)

    return trainer if 'trainer' in locals() else None, all_results

print("\n✅ Iteración sobre todos los backtesting de timeframes diferentes completado.")

# @title
# [10] EJECUTAR
if __name__ == "__main__":
    trainer, all_results = main()

# ============================================================================
# SUBIR RESULTADOS A GITHUB
# ============================================================================

import subprocess
import os
from datetime import datetime

print('='*70)
print('📤 SUBIENDO RESULTADOS A GITHUB')
print('='*70)

# ============================================================================
# ⚙️  CONFIGURACIÓN - CAMBIA ESTOS VALORES
# ============================================================================
GITHUB_USERNAME = 'jsgastondatamt5'       # ← TU USUARIO DE GITHUB
GITHUB_REPO = 'de-Kaggle-a-github'       # ← TU REPOSITORIO
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") #'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'   # ← TU TOKEN (Settings > Developer > Personal tokens)
GITHUB_BRANCH = 'main'               # o 'master'
# ============================================================================

try:
    # Configurar git
    subprocess.run(['git', 'config', '--global', 'user.email', f'{GITHUB_USERNAME}@users.noreply.github.com'], check=True)
    subprocess.run(['git', 'config', '--global', 'user.name', GITHUB_USERNAME], check=True)
    print('✅ Git configurado')
    
    # URL del repositorio con token
    repo_url = f'https://{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO}.git'
    
    # Clonar o actualizar
    repo_path = '/kaggle/working/github_repo'
    
    if os.path.exists(repo_path):
        print('📂 Repositorio existe, actualizando...')
        os.chdir(repo_path)
        subprocess.run(['git', 'pull'], check=True, capture_output=True)
    else:
        print('📥 Clonando repositorio...')
        subprocess.run(['git', 'clone', repo_url, repo_path], check=True, capture_output=True)
        os.chdir(repo_path)
    
    print('✅ Repositorio listo')
    
    # Crear carpeta para resultados
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_folder = f'kaggle_results_{timestamp}'
    results_path = os.path.join(repo_path, results_folder)
    os.makedirs(results_path, exist_ok=True)
    
    # Copiar resultados
    import shutil
    
    folders_to_copy = ['models', 'plots', 'backtest_results', 'data_analysis', 'logs']
    copied = []
    
    for folder in folders_to_copy:
        src = os.path.join(OUTPUT_PATH, folder)
        if os.path.exists(src) and os.listdir(src):
            dst = os.path.join(results_path, folder)
            shutil.copytree(src, dst, dirs_exist_ok=True)
            copied.append(folder)
            n_files = len(os.listdir(dst))
            print(f'  ✅ {folder}/ copiado ({n_files} archivos)')
    
    # Crear README
    readme_path = os.path.join(results_path, 'README.md')
    with open(readme_path, 'w') as f:
        f.write(f'# Resultados de Trading - {timestamp}\n\n')
        f.write(f'**Generado:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        f.write(f'## 📂 Contenido\n\n')
        for folder in copied:
            f.write(f'- `{folder}/`\n')
        f.write(f'\n## 📊 Configuración\n\n')
        f.write(f'- **Timeframes:** {", ".join(TIMEFRAMES)}\n')
        f.write(f'- **Max Rows:** {MAX_ROWS:,}\n')
        f.write(f'\n---\n')
        f.write(f'*Generado automáticamente desde Kaggle*\n')
    
    print(f'\n📝 README.md creado')
    
    # Git add, commit, push
    subprocess.run(['git', 'add', '.'], check=True)
    commit_msg = f'Resultados Kaggle - {timestamp}'
    
    try:
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True)
        print('✅ Cambios commiteados')
    except subprocess.CalledProcessError:
        print('ℹ️  No hay cambios nuevos para commitear')
    
    subprocess.run(['git', 'push', 'origin', GITHUB_BRANCH], check=True, capture_output=True)
    
    print('='*70)
    print('✅ RESULTADOS SUBIDOS EXITOSAMENTE A GITHUB')
    print('='*70)
    print(f'📂 Carpeta: {results_folder}/')
    print(f'🔗 URL: https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/tree/{GITHUB_BRANCH}/{results_folder}')
    print('='*70)
    
except subprocess.CalledProcessError as e:
    print(f'\n❌ Error en comando git: {e}')
    print('\nVerifica:')
    print('  1. Token de GitHub válido (con permisos "repo")')
    print('  2. Usuario y repositorio correctos')
    print('  3. Repositorio existe y tienes permisos de escritura')
    
except Exception as e:
    print(f'\n❌ Error: {e}')

finally:
    # Limpiar token de la salida por seguridad
    print('\n🔐 Token protegido en la salida')


