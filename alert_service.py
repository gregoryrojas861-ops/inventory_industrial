from datetime import datetime, timedelta
from sqlalchemy import select
from database.models import Material, Alert

def refresh_alerts(db):
    mats=db.scalars(select(Material)).all(); created=[]
    for m in mats:
        rules=[]
        if m.stock < 0: rules.append(("CRÍTICA","INVENTARIO_NEGATIVO",f"{m.code} tiene inventario negativo."))
        elif m.stock == 0: rules.append(("CRÍTICA","STOCK_AGOTADO",f"{m.code} está agotado."))
        elif m.stock <= max(m.reorder_point,m.min_stock): rules.append(("ADVERTENCIA","STOCK_BAJO",f"{m.code} está por debajo del punto de reorden."))
        if m.expiry_date:
            days=(m.expiry_date-datetime.utcnow()).days
            if days<0: rules.append(("CRÍTICA","VENCIDO",f"{m.code} está vencido."))
            elif days<=30: rules.append(("ADVERTENCIA","VENCIMIENTO",f"{m.code} vence en {days} días."))
        for level,typ,msg in rules:
            existing=db.scalar(select(Alert).where(Alert.material_id==m.id,Alert.alert_type==typ,Alert.resolved==False))
            if not existing:
                a=Alert(material_id=m.id,level=level,alert_type=typ,message=msg); db.add(a); created.append(a)
    db.commit(); return created
