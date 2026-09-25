from database.database import SessionLocal
from database.models import AuditLog

def test_audit_exists():
    db=SessionLocal(); assert db.query(AuditLog).count()>0; db.close()
