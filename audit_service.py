import json
from database.models import AuditLog

def audit(db, user, action, module, record_type="", record_id="", old=None, new=None, description="", result="SUCCESS", ip="", session_id=""):
    log = AuditLog(user_id=getattr(user, "id", None), username=getattr(user, "username", "system"), role=getattr(user, "role", "SYSTEM"), action=action, module=module, record_type=record_type, record_id=str(record_id), old_value=json.dumps(old, default=str, ensure_ascii=False) if old is not None else "", new_value=json.dumps(new, default=str, ensure_ascii=False) if new is not None else "", description=description, result=result, ip_address=ip, session_id=session_id)
    db.add(log)
    return log
