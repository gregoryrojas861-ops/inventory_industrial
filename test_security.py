from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import database.database as database_module
from data.sample_data import seed
from database.models import AuditLog, User
from services.inventory_service import create_material
from services.movement_service import register_movement
from utils.security import hash_password, verify_password, has_permission


def test_password():
    h = hash_password("Segura123!")
    assert verify_password("Segura123!", h)
    assert not verify_password("mal", h)


def test_auditor():
    assert has_permission("AUDITOR", "audit.read")
    assert not has_permission("AUDITOR", "inventory.write")


def test_database_url_respects_environment_override(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    assert database_module.build_database_url() == "sqlite:///:memory:"
    monkeypatch.delenv("DATABASE_URL", raising=False)


def test_material_and_movement_create_audit_logs():
    database_module.init_db()
    db = database_module.SessionLocal()
    username = f"audit_{uuid4().hex[:8]}"
    user = User(
        username=username,
        full_name="Auditor Test",
        password_hash=hash_password("Test1234!"),
        role="ADMINISTRADOR",
    )
    db.add(user)
    db.commit()

    material_code = f"MAT-{uuid4().hex[:8]}"
    material = create_material(
        db,
        user,
        {
            "code": material_code,
            "name": "Material de auditoría",
            "stock": 25,
            "cost": 2.5,
            "min_stock": 5,
            "max_stock": 100,
            "safety_stock": 8,
            "reorder_point": 10,
            "criticality": "MEDIA",
            "category": "Test",
            "unit": "unidad",
        },
    )

    assert db.query(AuditLog).filter_by(action="CREATE", module="MATERIALES", record_type="Material").count() >= 1

    register_movement(db, user, material.id, 3, "CONSUMO", reason="Prueba de auditoría")
    assert db.query(AuditLog).filter_by(action="MOVEMENT", module="MOVIMIENTOS").count() >= 1

    db.close()


def test_seed_does_not_create_default_admin_in_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEMO_MODE", "false")

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    database_module.Base.metadata.create_all(bind=engine)
    db = Session()

    assert seed(db) is False
    assert db.query(User).count() == 0

    db.close()
