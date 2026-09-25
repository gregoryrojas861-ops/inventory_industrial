import bcrypt
from functools import wraps

ROLES = {"ADMINISTRADOR", "SUPERVISOR", "ALMACENERO", "ANALISTA", "AUDITOR"}
PERMISSIONS = {
    "ADMINISTRADOR": {"*"},
    "SUPERVISOR": {"inventory.read", "inventory.write", "movements.read", "movements.write", "movements.approve", "purchases.*", "reports.read", "alerts.read", "audit.read", "physical.*", "quality.*", "kpi.read"},
    "ALMACENERO": {"inventory.read", "movements.read", "movements.write", "physical.read", "physical.write", "quality.read"},
    "ANALISTA": {"inventory.read", "movements.read", "reports.read", "alerts.read", "audit.read", "kpi.read", "ai.read", "purchases.read"},
    "AUDITOR": {"inventory.read", "movements.read", "purchases.read", "reports.read", "alerts.read", "audit.read", "physical.read", "quality.read", "kpi.read", "users.read"},
}

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except (ValueError, TypeError):
        return False

def has_permission(role: str, permission: str) -> bool:
    if role == "ADMINISTRADOR": return True
    perms = PERMISSIONS.get(role, set())
    if permission in perms: return True
    for p in perms:
        if p.endswith(".*") and permission.startswith(p[:-1]): return True
    return False
