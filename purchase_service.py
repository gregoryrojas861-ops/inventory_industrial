from datetime import datetime
from database.models import PurchaseOrder, PurchaseItem
from services.audit_service import audit

def create_purchase(db,user,code,supplier_id,items,expected_at=None):
    if not items: raise ValueError("La orden debe tener al menos un ítem.")
    po=PurchaseOrder(code=code,supplier_id=supplier_id,status="BORRADOR",expected_at=expected_at,total=sum(i["quantity"]*i["unit_cost"] for i in items)); db.add(po); db.flush()
    for i in items: db.add(PurchaseItem(purchase_id=po.id,material_id=i["material_id"],quantity=i["quantity"],unit_cost=i["unit_cost"]))
    audit(db,user,"CREATE","COMPRAS","PurchaseOrder",po.id,new={"code":code,"total":po.total},description=f"Creó orden {code}"); db.commit(); return po
