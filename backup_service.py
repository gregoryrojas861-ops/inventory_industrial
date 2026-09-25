from pathlib import Path
from datetime import datetime
import shutil
from database.database import DB_PATH

def backup_database(folder="backups"):
    path=Path(folder); path.mkdir(exist_ok=True)
    target=path/f"inventario_{datetime.now():%Y%m%d_%H%M%S}.db"
    shutil.copy2(DB_PATH,target); return target

def restore_database(source):
    src=Path(source)
    if not src.exists(): raise FileNotFoundError("Respaldo no encontrado.")
    shutil.copy2(src,DB_PATH)
