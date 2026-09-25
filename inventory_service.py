from datetime import datetime
from sqlalchemy import select
from database.models import Material
from services.audit_service import audit

def create_material(db, user, data):
    if db.scalar(select(Material).where(Material.code == data["code"])):
        raise ValueError("El código del material ya existe.")
    m = Material(**data, last_movement=None)
    db.add(m); db.flush()
    audit(db, user, "CREATE", "MATERIALES", "Material", m.id, new=data, description=f"Creó material {m.code}")
    db.commit(); return m

def update_material(db, user, material_id, data):
    m = db.get(Material, material_id)
    if not m: raise ValueError("Material no encontrado.")
    old = {k: getattr(m, k) for k in data}
    for k,v in data.items(): setattr(m,k,v)
    audit(db,user,"UPDATE","MATERIALES","Material",m.id,old=old,new=data,description=f"Actualizó material {m.code}")
    db.commit(); return m

def inventory_summary(db):
    mats = db.scalars(select(Material)).all()
    return {"materials":len(mats), "value":sum((m.stock or 0)*(m.cost or 0) for m in mats), "critical":sum(m.criticality=="CRÍTICA" for m in mats), "out":sum((m.stock or 0)<=0 for m in mats), "low":sum((m.stock or 0)<= (m.reorder_point or m.min_stock or 0) for m in mats)}
