import pytest
from database.database import SessionLocal
from database.models import User,Material
from services.movement_service import register_movement

def test_movement_updates_stock():
    db=SessionLocal(); u=db.query(User).filter_by(username="pytest_user").first(); m=db.query(Material).filter_by(code="PYTEST-1").first(); old=m.stock; register_movement(db,u,m.id,3,"CONSUMO"); assert m.stock==old-3; db.close()

def test_insufficient_stock():
    db=SessionLocal(); u=db.query(User).filter_by(username="pytest_user").first(); m=db.query(Material).filter_by(code="PYTEST-1").first();
    with pytest.raises(ValueError): register_movement(db,u,m.id,99999,"CONSUMO")
    db.close()
