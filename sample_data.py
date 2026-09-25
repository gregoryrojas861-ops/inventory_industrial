from datetime import datetime,timedelta
import random
from database.database import is_demo_mode
from database.models import User, Supplier, Warehouse, Material, Movement, Alert
from services.audit_service import audit
from utils.security import hash_password

def seed(db):
    if not is_demo_mode():
        return False
    if db.query(User).count()>0: return False
    admin=User(username="admin",full_name="Administrador Principal",password_hash=hash_password("Admin123!"),role="ADMINISTRADOR")
    db.add(admin)
    suppliers=[]
    for i in range(10):
        s=Supplier(code=f"SUP-{i+1:03}",name=f"Proveedor Industrial {i+1}",avg_lead_time=random.randint(2,15),on_time_rate=random.uniform(.75,.99)); db.add(s); suppliers.append(s)
    warehouses=[]
    for i in range(3):
        w=Warehouse(code=f"ALM-{i+1:02}",name=f"Almacén {i+1}",responsible=f"Responsable {i+1}"); db.add(w); warehouses.append(w)
    db.flush()
    cats=["Materia Prima","Insumos","Repuestos","Herramientas","Producto Terminado"]
    mats=[]
    for i in range(30):
        stock=random.randint(0,250); cost=round(random.uniform(5,250),2); m=Material(code=f"MAT-{i+1:03}",barcode=f"750000{i+1:06}",name=f"Material Industrial {i+1}",category=cats[i%5],unit="unidad",supplier_id=suppliers[i%10].id,cost=cost,stock=stock,min_stock=30,max_stock=300,safety_stock=20,reorder_point=50,warehouse_id=warehouses[i%3].id,location=f"Z{i%4+1}-E{i%10+1}",criticality=["BAJA","MEDIA","ALTA","CRÍTICA"][i%4],status="APROBADO",entry_date=datetime.utcnow()-timedelta(days=random.randint(1,180)),last_movement=datetime.utcnow()-timedelta(days=random.randint(0,60))); db.add(m); mats.append(m)
    db.flush()
    for i in range(100):
        m=random.choice(mats); qty=random.randint(1,20); typ=random.choice(["COMPRA","CONSUMO","PRODUCCIÓN","DEVOLUCIÓN"]); prev=m.stock; delta=qty if typ in {"COMPRA","PRODUCCIÓN","DEVOLUCIÓN"} else -min(qty,prev); m.stock=max(0,prev+delta); db.add(Movement(material_id=m.id,user_id=admin.id,warehouse_id=m.warehouse_id,movement_type=typ,reason="Datos de prueba",quantity=abs(delta),previous_stock=prev,resulting_stock=m.stock,created_at=datetime.utcnow()-timedelta(days=random.randint(0,120))))
    db.commit(); audit(db,admin,"SEED","SISTEMA",description="Generó datos ficticios de prueba"); db.commit(); return True
